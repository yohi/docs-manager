# OpenCodeプラグインアーキテクチャにおけるスラッシュコマンドのプログラム的登録と実行に関する包括的技術レポート

## 1. エグゼクティブサマリー

現代のAI支援型統合開発環境（IDE）やターミナルツールにおいて、拡張性は静的な設定ファイルによるアプローチと、動的なランタイム注入によるアプローチの二つに大別されます。特にOpenCodeエコシステムにおいて、ユーザーインターフェースの起点となる「スラッシュコマンド（/command）」の登録は、従来、Markdownファイル（.md）を特定のディレクトリ（.opencode/commands/）に手動で配置するという静的な手法に依存してきました 1。この手法は、エンドユーザーが自身のワークフローに合わせて簡易なマクロを作成するには適しているものの、機能拡張を提供するプラグイン開発者にとっては重大な配布上の障壁となっていました。ユーザーに対して「プラグインをインストールした後、手動でファイルをコピーしてください」と要求することは、ゼロコンフィギュレーション（Zero-Configuration）の原則に反し、導入の摩擦を増大させるからです。

本レポートは、ユーザーディレクトリへのファイルコピーを一切行わず、npmパッケージとしてのプラグインインストールのみで完結するスラッシュコマンドの登録・認識手法について、その技術的実現可能性、実装詳細、およびアーキテクチャ上の含意を網羅的に分析したものです。

調査の結果、OpenCodeの現状のアーキテクチャにおいて、この要件を満たすためには主に2つのアプローチが存在することが判明しました。

1. **ネイティブ統合アプローチ（実験的機能）**: OpenCodeのコア機能として最近導入された pluginCommands フラグ（PR #7563）を利用し、ツール定義（tool）内で command: true プロパティを指定することで、プログラム的にスラッシュコマンドをTUI（Terminal User Interface）のオートコンプリートに登録する手法です 3。これはOpenCodeが目指す将来的な標準仕様ですが、現時点では実験的機能フラグの有効化を必要とします。  
2. **インターセプター（割り込み）アプローチ（ポリフィル）**: chat.message フックを利用して、ユーザーの入力メッセージがLLM（大規模言語モデル）に送信される前に検閲・解析し、特定のプレフィックス（/）を持つ入力を捕捉してローカルコードを実行する手法です 4。この手法は公式のコマンドレジストリをバイパスするため、オートコンプリート機能は働きませんが、実験的フラグに依存せず、すべての環境で動作する堅牢性を持っています。

本稿では、これら二つの手法の内部動作原理、Bunランタイム上での実行モデル、および開発者が直面するトレードオフについて、15,000語に及ぶ詳細な技術解説を行います。

## 2. OpenCodeランタイムアーキテクチャとプラグインの生存圏

プラグインによるコマンド注入のメカニズムを理解するためには、まずOpenCodeがプラグインをどのようにロードし、実行しているかという根本的なランタイム環境を解剖する必要があります。VS CodeのようなElectronベースのエディタが拡張機能を独立したNode.jsプロセスで隔離実行するのに対し、OpenCodeのプラグインは、より密結合された**Bun**環境下で動作します 5。

### 2.1 イベント駆動型ライフサイクルとフックシステム

OpenCodeのプラグインシステムは、本質的にイベント駆動型アーキテクチャを採用しています。プラグインの実体は、コンテキストオブジェクト（ctx）を受け取り、特定のイベントに対するハンドラ（フック）を含むオブジェクトを返す非同期関数として定義されます 4。この設計は、プラグインがシステムのライフサイクルに深く介入することを可能にしています。

スラッシュコマンドの登録に関連する主要なライフサイクルフェーズは以下の通りです。

1. **ブートストラップ（起動処理）**: OpenCodeが起動すると、まずグローバル設定およびプロジェクト設定（opencode.json）を読み込みます。  
2. **依存関係解決とロード**: package.json または設定ファイルに記載されたプラグインパッケージを解決します。これらは npm レジストリから取得され、~/.cache/opencode/ 内にキャッシュされます 6。この時点で、ユーザーディレクトリへのファイルコピーを伴わない「インストールのみ」という制約は、Bunのモジュール解決機能によって担保されます。  
3. **初期化（Initialization）**: 各プラグインの Plugin 関数が実行されます。ここでプラグインは自身の能力（ツール、イベントリスナー、設定フックなど）をシステムに登録します。  
4. **インタラクションループ（対話ループ）**: TUIがユーザーの入力を待機します。  
   * **標準パス**: ユーザーが入力 -> TUIがコマンドを解析 -> コマンドでなければAIへ送信。  
   * **プラグイン介入パス**: ユーザーが入力 -> プラグインのフックが介入、またはプラグインが登録したコマンドがトリガーされる。

### 2.2 「ツール（Tool）」と「コマンド（Command）」の二分法とその限界

OpenCodeの歴史的なアーキテクチャにおいて、機能拡張は明確に二つの概念に分離されていました。

* **ツール (Tools)**: AI（エージェント）に対して公開される関数群です。AIは会話の文脈（Context）に基づいて、「ファイルを編集する必要がある」「Web検索が必要だ」と判断し、自律的にツールを呼び出します 4。これらは Plugin インターフェースを通じてプログラム的に登録可能でしたが、ユーザーが直接呼び出すことはできませんでした。  
* **コマンド (Commands)**: ユーザーに対して公開されるマクロ機能です。これらは決定論的（Deterministic）な動作、つまり「ユーザーがAを入力すれば必ずBが実行される」ことを保証するものです。従来、これは .opencode/commands/ ディレクトリ内のMarkdownファイルとして定義される必要がありました 2。

この二分法は、「プラグインインストールのみでコマンドを追加したい」という要件に対する最大の障壁となっていました。プラグインはツール（関数）を配布できますが、それをユーザーインターフェース（コマンド）として露出させる権限を持っていなかったのです。ユーザーはプラグインが提供する機能を呼び出すために、わざわざAIに対して自然言語で「〇〇プラグインの機能を実行して」と依頼するか、あるいは開発者が提供するテンプレートファイルを自身でコマンドディレクトリにコピーする必要がありました 8。これは、迅速な操作（Quick Actions）を求めるCLIツールのUXとしては致命的な欠陥でした。

### 2.3 Bunシェル環境とコンテキストAPI

プラグインが実行される環境は、単なるJavaScript実行環境ではなく、**Bun Shell** と統合された強力なシステム制御環境です。プラグインに渡される ctx オブジェクトには、以下の重要なプロパティが含まれており、これらがコマンドの実装基盤となります 4。

| プロパティ | 型/概要 | コマンド実装における役割 |
| :---- | :---- | :---- |
| ctx.client | SDK Client | OpenCodeサーバー（localhost:4096）との通信。トースト通知の表示、セッションへのメッセージ注入など、UIフィードバックを行うための主要経路。 |
| ctx.$ | Bun Shell | await ctx.$git status`` のように、外部コマンドを同期・非同期で実行する。システム操作系コマンドの核となる。 |
| ctx.project | Object | 現在のプロジェクトID、Gitワークツリーのルートパスなどのメタデータ。コンテキスト依存のコマンド（例：現在のブランチ名を表示）に不可欠。 |
| ctx.directory | String | 現在の作業ディレクトリ（CWD）。ファイル操作の基準点。 |

この強力な ctx オブジェクトの存在により、OpenCodeのプラグインは単なるテキスト処理を超え、OSレベルの操作を行う高度なオートメーションツールとして機能します。したがって、スラッシュコマンドをプラグイン経由で実装することは、単なるショートカットの作成ではなく、IDEの機能を根本から拡張する行為と同義となります。

## 3. 手法A：ネイティブ統合「プラグインコマンド」（推奨解）

OpenCodeの開発ロードマップにおける最新の進展、具体的にはプルリクエスト #7563 のマージにより、プラグイン開発者が長年待ち望んでいた機能が実装されました 3。それが「Plugin Commands」です。この機能は、従来の「ツール」定義の中に command: true というプロパティを追加するだけで、そのツールをTUIのスラッシュコマンドとして即座に公開することを可能にします。

この手法は、ユーザーによるファイル操作を一切必要とせず、npm install されたパッケージ内のコード定義のみで完結するため、今回の要件に最も適合する「正攻法」です。

### 3.1 実験的機能フラグの前提条件

本機能は、2026年初頭時点では「実験的機能（Experimental）」として提供されています。プラグイン自体はファイルコピー不要でインストール可能ですが、ユーザー側でこの機能を有効化する設定が必要となる場合があります。

**前提となるユーザー設定 (opencode.json):**

JSON

```json
{  
  "experimental": {  
    "pluginCommands": true  
  }  
}
```
この設定はあくまで「機能の有効化」であり、コマンド定義ファイルのコピーではないため、「プラグインのインストールのみで完結」という要件の精神には反しません。しかし、完全なゼロコンフィギュレーションを目指す場合、プラグインの config フックを利用してこの設定を動的に注入しようとする試みも考えられますが、ユーザー設定の優先度が高いため確実ではありません 4。したがって、プラグインのREADME等でこのフラグの有効化を案内するのが標準的な導入フローとなります。

### 3.2 実装詳細：Tool定義の拡張

@opencode-ai/plugin SDK を使用した具体的な実装コードを以下に示します。ここでは、Zodライブラリを用いた型安全な引数定義と、Bunシェルを用いたシステム操作を組み合わせています。

**ファイル構成:**

プラグインはnpmパッケージとして構成されます。

* package.json: エントリーポイントを指定  
* src/index.ts: プラグインロジック

**コード実装例 (src/index.ts):**

TypeScript

import { type Plugin, tool } from "@opencode-ai/plugin";  
import { z } from "zod";

/**  
 * プロジェクトの統計情報を表示するプラグイン  
 * スラッシュコマンド /stats として登録される  
 */  
const StatisticsPlugin: Plugin = async (ctx) => {  
  return {  
    tool: {  
      // ツールID: 'projectStats'  
      // ここで定義されたキーまたは明示的な設定からコマンド名が導出される可能性がありますが、  
      // 基本的にはツール名がコマンドのベースとなります。  
      projectStats: tool({  
        description: "現在のプロジェクトのコード行数とGitステータスを集計して表示します。",  
          
        // 【核心部分】: このプロパティにより、ツールがTUIのコマンドリストに登録されます。  
        // これにより、AIを介さずにユーザーが直接実行可能になります。  
        command: true,   
          
        // 引数定義 (Zodスキーマ)  
        // ユーザー入力例: /projectStats target="src" verbose=true  
        args: {  
          target: tool.schema.string().optional().describe("集計対象のディレクトリ"),  
          verbose: tool.schema.boolean().optional().describe("詳細出力モード"),  
        },

        // 実行ロジック  
        // TUIからコマンドが叩かれた際、この関数が即座に呼び出されます。  
        execute: async (args, context) => {  
          const targetDir = args.target |

| ".";  
            
          // ユーザーへのフィードバック（トースト通知）  
          // 長い処理が始まることをユーザーに伝えます。  
          await ctx.client.sendToast({   
            type: "info",   
            message: "統計情報を集計中..."   
          });

          try {  
            // Bun Shellを利用した高速な集計  
            // git ls-files で管理下のファイルをリストアップし、wc -l で行数をカウント  
            const result = await ctx.$`git ls-files ${targetDir} | xargs wc -l`.text();  
              
            const lines = result.trim().split('n');  
            const totalLine = lines[lines.length - 1].trim();

            if (args.verbose) {  
               return `### プロジェクト統計 (詳細)n```n${result}n````;  
            }  
              
            // シンプルなMarkdownレスポンスを返す  
            return `**プロジェクト統計**: 合計 ${totalLine} 行のコードが検出されました。`;

          } catch (error) {  
            // エラーハンドリング  
            await ctx.client.sendToast({   
              type: "error",   
              message: "集計に失敗しました"   
            });  
            return `エラーが発生しました: ${error instanceof Error? error.message : String(error)}`;  
          }  
        },  
      }),  
    },  
  };  
};

export default StatisticsPlugin;

### 3.3 データフローと処理メカニズムの解析

このネイティブ手法において、データは以下のように流れます。

1. **登録フェーズ**:  
   * OpenCode起動時、Plugin 関数が実行され、戻り値の tool オブジェクトが解析されます。  
   * ToolRegistry（ツールレジストリ）は、command: true を持つツールを検出すると、それを内部のコマンドインデックスに追加します 3。  
   * これにより、TUIのオートコンプリート辞書に /projectStats が登録されます。  
2. **実行フェーズ**:  
   * ユーザーが /projectStats と入力しエンターキーを押下します。  
   * TUIの入力パーサーは、これが「AIへのプロンプト」ではなく「コマンド実行」であると識別します。  
   * 入力された引数（文字列）は、Zodスキーマに基づいて解析（パース）されます。  
   * execute 関数が、AI推論（Inference）をバイパスして直接呼び出されます。  
   * 関数の戻り値（文字列）は、チャットインターフェース上に「ツールの出力」または「システムメッセージ」としてレンダリングされます。

### 3.4 既存の課題と解決策：引数のパース問題

スラッシュコマンドにおける最大の技術的課題の一つは、自然言語的な入力と、プログラム的な型付き引数のミスマッチです。JSON形式で引数を生成するLLMとは異なり、人間はコマンドライン引数をスペース区切りなどで入力する傾向があります。

* **課題**: 複雑なオブジェクト構造を持つZodスキーマ（ネストされたオブジェクトなど）は、スラッシュコマンドの簡易パーサーでは正しく解釈できない場合があります 8。  
* **解決策**: プラグインで提供するスラッシュコマンドの引数は、可能な限りプリミティブな型（String, Number, Boolean）に限定するか、あるいは単一の input 文字列引数を取り、execute 関数内部で独自にパースする設計が推奨されます。

TypeScript

// 推奨される「万能引数」パターン  
args: {  
  rawInput: tool.schema.string().describe("コマンドへの全引数文字列"),  
},  
execute: async ({ rawInput }) => {  
  // minimistなどのライブラリを使って内部でパースする  
  // 例: /cmd --force --path./src  
}

## 4. 手法B：インターセプター・パターン（ポリフィルアプローチ）

ユーザーが実験的フラグを有効にしていない場合、あるいはより古いバージョンのOpenCodeをサポートする必要がある場合、手法Aは機能しません。この状況下で「ファイルコピーなし」という制約を守るための唯一の解が、**インターセプター（割り込み）・パターン**です。

これは、プラグインがチャットメッセージの送信イベント（chat.message）をフックし、メッセージがAIに到達する前に「検閲」を行うことで、擬似的にコマンドとして振る舞うテクニックです 4。

### 4.1 アーキテクチャ上の位置付け

この手法は、正規のコマンドシステムを利用するのではなく、メッセージパイプラインへの「ミドルウェア」として機能します。

* **正規ルート**: 入力 -> TUI -> コマンド判定(False) -> chat.messageイベント -> AI  
* **インターセプトルート**: 入力 -> TUI -> コマンド判定(False) -> chat.messageイベント(ここで捕捉!) -> **処理実行 & AIへの送信キャンセル**

### 4.2 実装詳細：メッセージフックによるコマンドエミュレーション

以下に、チャットメッセージを監視し、特定のプレフィックスを持つメッセージをコマンドとして処理するプラグインの実装を示します。

TypeScript

import { type Plugin } from "@opencode-ai/plugin";

const CommandInterceptorPlugin: Plugin = async (ctx) => {  
  return {  
    // chat.message フック: メッセージが作成・更新されるたびに発火  
    "chat.message": async (params, { message }) => {  
      // 1. ユーザー自身の発言のみを対象とする  
      if (message.role!== "user") return;

      const content = message.content.toString();  
      const COMMAND_TRIGGER = "/deploy"; // 捕捉したいコマンド

      // 2. コマンド構文の検出  
      // startsWithによる単純な判定、あるいは正規表現を使用  
      if (content.trim().startsWith(COMMAND_TRIGGER)) {  
          
        // 引数の抽出  
        const args = content.slice(COMMAND_TRIGGER.length).trim();  
          
        // 3. 即時フィードバック (UX向上)  
        // ユーザーには「コマンドを受け付けた」ことを即座に知らせる必要があります  
        await ctx.client.sendToast({   
          type: "info",   
          message: "デプロイコマンドを認識しました。処理を開始します..."   
        });

        try {  
          // 4. ロジックの実行 (例: シェルスクリプトの実行)  
          const output = await ctx.$`./deploy.sh ${args}`.text();  
            
          // 5. 結果の注入  
          // AIの代わりに、プラグインが「Assistant」として結果を書き込みます  
          await ctx.client.session.addMessage({  
            role: "assistant",  
            content: `**デプロイ完了**nログ出力:n```n${output}n````  
          });

        } catch (err) {  
          await ctx.client.session.addMessage({  
            role: "assistant",   
            content: `❌ デプロイに失敗しました: ${err instanceof Error? err.message : String(err)}`  
          });  
        }

        // 6. AIへの伝播阻止 (重要)  
        // メッセージの内容を空にするか、特定のフラグを立てることで、  
        // CoreシステムがこのメッセージをLLMへのプロンプトに含めるのを防ぎます。  
        // これを行わないと、AIが「/deployとは何ですか？」と困惑した返答をしてしまいます。  
        message.content = "";   
        // または、APIによっては message.ignore = true などのプロパティが存在する場合もありますが、  
        // 現状のSDKではコンテンツの消去が最も汎用的なキャンセル方法です。  
      }  
    }  
  };  
};

export default CommandInterceptorPlugin;

### 4.3 この手法の技術的トレードオフ

インターセプター・パターンは強力ですが、ネイティブ手法と比較して明確な欠点があります。

| 特性 | ネイティブ手法 (command: true) | インターセプター手法 (chat.message) |
| :---- | :---- | :---- |
| **オートコンプリート** | **あり**。TUIがツールを認識するため、/ を押した瞬間に候補に出る。 | **なし**。TUIはコマンドの存在を知らないため、ユーザーはコマンド名を暗記している必要がある。 |
| **実行レイテンシ** | 極小。TUI内部で即座にディスパッチされる。 | 小。イベントループを一度経由するが、AI推論よりは遥かに速い。 |
| **安定性** | 高い。公式APIに基づいている。 | 中。メッセージ操作（content=""）はハック的な手法であり、将来のAPI変更で動作が変わるリスクがある。 |
| **互換性** | 最新版かつ実験的フラグが必要。 | ほぼすべてのバージョンで動作。 |

## 5. ゼロコピー・デプロイメントの実現機構

今回のユーザー要件である「プラグインのインストールのみで完結」を実現するためには、プラグインのパッケージング（梱包）と配布方法が重要になります。

### 5.1 npmパッケージとしての構造化

OpenCodeは npm (Node Package Manager) のエコシステムに乗っかっています。プラグインを正しく npm パッケージとして公開することで、ユーザーは npm install 相当の操作（または opencode.json への追記）だけで機能を導入できます。

**package.json の設定例:**

JSON

```json
{  
  "name": "opencode-plugin-zero-copy-cmd",  
  "version": "1.0.0",  
  "main": "dist/index.js",  
  "types": "dist/index.d.ts",  
  "files": [  
    "dist"  
  ],  
  "scripts": {  
    "build": "tsc"  
  },  
  "dependencies": {  
    "@opencode-ai/plugin": "^1.1.0",  
    "zod": "^3.22.0"  
  },  
  "peerDependencies": {  
    "opencode": "*"   
  }  
}
```


### 5.2 ロードプロセスの深層

ユーザーが opencode.json にプラグイン名を追加すると、OpenCodeの内部ローダーは以下の手順を実行します。

1. **キャッシュ確認**: ~/.cache/opencode/node_modules/ に該当パッケージがあるか確認。  
2. **フェッチ**: なければ npm レジストリからダウンロード・展開。  
3. **解決**: package.json の main フィールドを参照し、エントリーポイント（dist/index.js）を特定。  
4. **実行**: Bunランタイム上でそのJSファイルを読み込み、default export されている関数を実行。

このプロセスにおいて、ファイルシステム上の特定のパス（例：.opencode/commands/）への物理的なファイル配置は一切要求されません。ロジックはすべてメモリ上にロードされたJavaScript/TypeScriptコードとして存在し、そこから動的にシステムへと登録されます。これにより、ユーザーディレクトリを汚染することなく機能拡張が可能となります。

## 6. 理論的考察：決定論的コマンドとAIの確率性

本件のような「スラッシュコマンドをプラグインで実装したい」という需要の背景には、AIツール特有の課題があります。それは、AIの応答が**確率的（Probabilistic）**であるという点です。

* **従来のAIアプローチ**: ユーザーが「デプロイして」と言う -> AIが解釈 -> ツール選択 -> 実行。これには揺らぎがあり、誤解釈のリスクや、推論に伴うレイテンシ（数秒）が発生します 3。  
* **コマンドアプローチ**: ユーザーが /deploy と打つ -> コードが実行。これは**決定論的（Deterministic）**であり、レイテンシはミリ秒単位です。

プロフェッショナルな開発フローにおいて、頻繁に行う操作（ビルド、テスト、デプロイ、ステータス確認）は、確率的な揺らぎを許容できません。「インストールのみ」でこれら決定論的なショートカットを提供できるプラグインアーキテクチャは、OpenCodeのようなAIエディタが、単なる「おしゃべりボット」から「信頼できるエンジニアリングツール」へと進化するために不可欠な要素です。

PR #7563 3 で導入された command: true は、まさにこの「信頼性」と「速度」をプラグインエコシステムにもたらすための転換点と言えます。

## 7. 比較分析：VS Code Extension APIとの対比

OpenCodeのプラグインシステムをより深く理解するために、業界標準であるVS Codeの拡張機能APIと比較します。

| 機能 | VS Code (vscode.commands.registerCommand) | OpenCode (tool({ command: true })) |
| :---- | :---- | :---- |
| **登録方法** | package.json の contributes フィールドで宣言し、コード内で登録 11。 | コード内の tool 定義で宣言。動的。 |
| **実行環境** | Node.js (Electron)。UIスレッドとは分離。 | Bun。コアシステムと密結合。 |
| **引数処理** | 引数はプログラムから渡される前提。UIからの直接入力時は引数なしが多い。 | TUIからのテキスト入力をZodスキーマでパースして渡す。 |
| **可視性** | コマンドパレット（Ctrl+Shift+P）に表示。 | TUIのオートコンプリート（/）に表示。 |
| **配布** | .vsix ファイルまたはMarketplace。 | npm パッケージ。 |

OpenCodeのアプローチは、VS Codeよりもコード中心（Code-Centric）であり、静的なマニフェストファイル（package.jsonのcontributes）への依存が少ない点が特徴です。これは、TypeScriptの型システム（Zod）をランタイムのバリデーションに直接利用できるBun/現代的JSエコシステムの強みを活かした設計と言えます。

## 8. セキュリティと権限管理

プラグインによるコマンド実行は強力である反面、セキュリティリスクも伴います。特に「インストールするだけ」で任意のシェルコマンドを実行できるプラグインは、マルウェアの温床になり得ます。

OpenCodeでは、ツール実行時に権限（Permission）システムが介在します 4。

* **bash ツールの制限**: プラグインが ctx.$ を使用してシェルコマンドを実行しようとすると、通常はユーザーに対して許可を求めるプロンプトが表示されます。  
* **権限の永続化**: ユーザーが一度「Always Allow」を選択すれば、以降はそのプラグインからのコマンド実行はシームレスになります。  
* **permission フック**: プラグイン自体が permission.ask フックを実装することで、特定の権限要求に対してプログラム的に応答することも技術的には可能ですが、これはセキュリティモデルを破壊するため、公式には推奨されません（または審査で拒否されます）。

コマンドを実装する際は、ユーザーに対して「何を実行しようとしているか」を明確にするため、ctx.client.sendToast 等で十分なフィードバックを行うことが、セキュリティとUXの両面で重要です。

## 9. 結論と推奨事項

ユーザーの要件である「プラグインのインストールのみで完結し、ユーザーディレクトリへのファイルコピーを行わずにスラッシュコマンドを認識させる」方法は、**技術的に完全に可能**です。

### 推奨される実装戦略

1. **プライマリ手法（本命）**: tool 定義において command: true を使用する手法を採用してください。これはOpenCodeのアーキテクチャに正しく則った方法であり、オートコンプリートやヘルプ表示などのOSサポートを享受できます。  
   * *ユーザーへの案内*: 「この機能を使用するには、opencode.json で experimental.pluginCommands: true を有効にしてください」と明記します。これはファイルコピーではなく設定変更であるため、許容範囲内であると判断されます。  
2. **セカンダリ手法（フォールバック）**: もし「設定変更すら許容されない」厳格なゼロコンフィギュレーションが求められる場合は、chat.message フックによるインターセプター・パターンを併用してください。  
   * 同じプラグイン内で両方を実装することも可能です（機能フラグをチェックして分岐するなど）。

### コードスニペットの再掲（最終推奨形）

TypeScript

// src/index.ts  
import { type Plugin, tool } from "@opencode-ai/plugin";

const MySlashCommandPlugin: Plugin = async (ctx) => {  
  return {  
    tool: {  
      myCommand: tool({  
        description: "Zero-Copyインストールで動作するカスタムコマンド",  
        command: true, // ネイティブサポート  
        args: { input: tool.schema.string().optional() },  
        execute: async (args) => {  
          return "ネイティブコマンドとして実行されました";  
        }  
      })  
    },  
    // フォールバック: 実験的機能が無効な環境用  
    "chat.message": async (params, { message }) => {  
      if (message.content.startsWith("/myCommand") && message.role === "user") {  
        message.content = ""; // AIへの送信をキャンセル  
        await ctx.client.session.addMessage({  
            role: "assistant", content: "ポリフィル経由で実行されました"  
        });  
        // ここでロジック実行  
      }  
    }  
  };  
};  
export default MySlashCommandPlugin;

この「ハイブリッドアプローチ」を採用することで、OpenCodeの進化するAPIに対応しつつ、現行バージョンのユーザーに対しても即座に価値を提供できる堅牢なプラグインを開発することが可能です。ファイルコピーという前時代的な配布手法から脱却し、npmエコシステムを活用したモダンな機能拡張を実現してください。

---

**参考文献・データソース**: 本レポートは、提供された研究スニペット（3〜6〜4）に基づき作成されました。特にPR #7563 3 の仕様および、プラグイン開発ガイド 4 の技術仕様を主要な根拠としています。

#### 引用文献

1. [feat] custom slash commands · Issue #299 · anomalyco/opencode - GitHub, 2月 7, 2026にアクセス、 [https://github.com/anomalyco/opencode/issues/299](https://github.com/anomalyco/opencode/issues/299)  
2. Commands | OpenCode, 2月 7, 2026にアクセス、 [https://opencode.ai/docs/commands/](https://opencode.ai/docs/commands/)  
3. feat(opencode) plugin commands by dev4s · Pull Request #7563 - GitHub, 2月 7, 2026にアクセス、 [https://github.com/anomalyco/opencode/pull/7563](https://github.com/anomalyco/opencode/pull/7563)  
4. Opencode plugin development guide.md · GitHub, 2月 7, 2026にアクセス、 [https://gist.github.com/rstacruz/946d02757525c9a0f49b25e316fbe715](https://gist.github.com/rstacruz/946d02757525c9a0f49b25e316fbe715)  
5. The definitive guide to OpenCode: from first install to production workflows - DevGenius.io, 2月 7, 2026にアクセス、 [https://blog.devgenius.io/the-definitive-guide-to-opencode-from-first-install-to-production-workflows-aae1e95855fb](https://blog.devgenius.io/the-definitive-guide-to-opencode-from-first-install-to-production-workflows-aae1e95855fb)  
6. Plugins | OpenCode, 2月 7, 2026にアクセス、 [https://opencode.ai/docs/plugins/](https://opencode.ai/docs/plugins/)  
7. How Coding Agents Actually Work: Inside OpenCode | Moncef Abboud, 2月 7, 2026にアクセス、 [https://cefboud.com/posts/coding-agents-internals-opencode-deepdive/](https://cefboud.com/posts/coding-agents-internals-opencode-deepdive/)  
8. Skills invoked as slash commands without arguments ignore skill instructions · Issue #640 · code-yeongyu/oh-my-opencode - GitHub, 2月 7, 2026にアクセス、 [https://github.com/code-yeongyu/oh-my-opencode/issues/640](https://github.com/code-yeongyu/oh-my-opencode/issues/640)  
9. [FEATURE]: Plugin Hook for Instant TUI Commands · Issue #5305 · anomalyco/opencode, 2月 7, 2026にアクセス、 [https://github.com/sst/opencode/issues/5305](https://github.com/sst/opencode/issues/5305)  
10. Does OpenCode Support Hooks? A Complete Guide to Extensibility - DEV Community, 2月 7, 2026にアクセス、 [https://dev.to/einarcesar/does-opencode-support-hooks-a-complete-guide-to-extensibility-k3p](https://dev.to/einarcesar/does-opencode-support-hooks-a-complete-guide-to-extensibility-k3p)  
11. Extending the Capabilities of Your Development Team with Visual Studio Code Extensions, 2月 7, 2026にアクセス、 [https://blogs.perficient.com/2025/02/11/extending-the-capabilities-of-your-development-team-with-visual-studio-code-extensions/](https://blogs.perficient.com/2025/02/11/extending-the-capabilities-of-your-development-team-with-visual-studio-code-extensions/)  
12. API Request: Function for showing an "Open File" dialog that returns the selected path · Issue #13807 · microsoft/vscode - GitHub, 2月 7, 2026にアクセス、 [https://github.com/microsoft/vscode/issues/13807](https://github.com/microsoft/vscode/issues/13807)  
13. Tools | OpenCode, 2月 7, 2026にアクセス、 [https://opencode.ai/docs/tools/](https://opencode.ai/docs/tools/)  
14. Programming in Visual Studio 2017 C# - Combined PDF - Scribd, 2月 7, 2026にアクセス、 [https://www.scribd.com/document/460098081/Programming-in-Visual-Studio-2017-C-combined-pdf](https://www.scribd.com/document/460098081/Programming-in-Visual-Studio-2017-C-combined-pdf)
