---
title: "Claude Code CLIにおけるモデル選択メカニズムと構成管理アーキテクチャに関する包括的調査報告書"
date: 2026-02-13
layout: default
---

# Claude Code CLIにおけるモデル選択メカニズムと構成管理アーキテクチャに関する包括的調査報告書

## 1. エグゼクティブサマリー

本報告書は、Anthropic社が提供する開発者向けコマンドラインインターフェース（CLI）ツールである「Claude Code」の内部アーキテクチャ、特にモデル選択ロジックの動的・静的性質と、ユーザーによる手動設定の可能性について、技術的な観点から包括的に分析したものである。調査の結果、Claude Code CLIにおけるモデル定義は現状において**静的（Hardcoded）**な実装であることが判明した。`/model`コマンドで表示されるリストや、エイリアス（sonnet, opusなど）が指し示す具体的なモデルIDは、CLIのパッケージ内に埋め込まれており、AnthropicのAPIから動的に「利用可能なモデル一覧」を取得して表示しているわけではない。この設計は、ツールの安全性と動作保証を優先した結果であると推測されるが、同時にカスタムモデルや特定リージョン（AWS China等）のモデル利用を制限する要因ともなっている。

一方で、ユーザーによる**手動設定の柔軟性は極めて高い**ことが確認された。ユーザーは、セッションごとの一時的な切り替えから、環境変数によるデフォルト値の変更、さらにはプロジェクト単位やグローバルな設定ファイル（`settings.json`）を用いた永続的な構成管理まで、多層的な設定階層（Configuration Hierarchy）を通じてモデルの挙動を詳細に制御可能である。特に、計画（Planning）と実行（Execution）で異なるモデルを動的に切り替える`opusplan`モードや、思考プロセスを明示化するThinking Modeの構成は、単純なモデル指定を超えた高度なオーケストレーションを実現している。

本報告書では、これらのメカニズムをソースコードレベルの挙動分析、公式ドキュメントの解釈、およびコミュニティからの技術的検証を統合して詳述する。開発者やシステム管理者が、Claude Codeを自身のワークフローや組織のポリシーに合わせて最適化するための、実践的かつ網羅的なガイドラインを提供することを目的とする。

---

## 2. 序論：ターミナル統合型AIエージェントの台頭とモデル管理の重要性

ソフトウェア開発の現場において、AIアシスタントの利用形態は急速に進化している。従来のWebブラウザベースのチャットインターフェースや、IDE（統合開発環境）のプラグインによるコード補完から、より自律的で強力な権限を持つ「ターミナル統合型AIエージェント」へとパラダイムシフトが進行中である。Claude Codeはこの新世代のツールを代表する存在であり、開発者のローカル環境でシェルコマンドを実行し、ファイルシステムを直接操作し、複雑なエンジニアリングタスクを完遂する能力を持つ。

このような強力な権限を持つエージェントにおいて、「どのモデル（頭脳）を使用するか」という決定は、単なるテキスト生成の品質だけでなく、タスク遂行のコスト、速度、そして安全性に直結する重要な要素である。例えば、大規模なリファクタリングの計画には推論能力の高いモデル（Opus等）が必要とされる一方、単純な構文修正には高速で安価なモデル（Haiku等）が適している。また、企業ユースケースにおいては、利用可能なモデルをガバナンスの観点から制限する必要性も生じる。

### 2.1 調査の背景と目的

ユーザーからの「/modelコマンド実行時に読み込むモデルは動的か静的か？」という問いは、ツールの拡張性と将来性を評価する上で核心的な疑問である。もし動的であれば、API側で新しいモデルが公開された瞬間にCLIでも利用可能となるが、静的であればCLI自体のアップデートが必要となる。また、「手動で設定する方法はあるか？」という問いは、開発者が自身の環境に合わせてツールをカスタマイズできるか否か、ひいてはCI/CDパイプラインや特殊なネットワーク環境（プロキシ下や特定リージョン）での運用可能性に関わる実用的な課題である。

本報告書では、以下の3点を主要な調査項目として設定し、詳細な分析を行う。

1. **モデル選択ロジックの静的性質の検証**: CLIの挙動やGitHub上のIssue分析を通じた技術的裏付け。
2. **構成管理の階層構造と優先順位の解明**: 環境変数、CLIフラグ、設定ファイルが競合した際の解決ロジック。
3. **高度なモデル運用の実践**: `opusplan`やThinking Modeを含む、応用的な設定手法とベストプラクティス。

---

## 3. モデル選択ロジックの技術的分析：静的実装の実態

Claude Code CLIのモデル選択メカニズムについて、利用可能なリソース（GitHub Issue、ドキュメント、挙動報告）を基に分析を行った結果、その実装は**静的（Static）**であると断定できる。本章では、その証拠と技術的な背景、およびこの設計がもたらす制約について詳述する。

### 3.1 静的ハードコーディングの証拠

Claude Code CLI（`@anthropic-ai/claude-code`）が表示するモデルリストおよびエイリアスの解決ロジックは、CLIパッケージのソースコード内にハードコードされている。これは、CLIが起動時にAnthropicのサーバーに問い合わせて「現在利用可能なモデルリスト」を動的に取得・生成しているわけではないことを意味する。

#### 3.1.1 GitHub Issueによる技術的指摘

Claude CodeのGitHubリポジトリにおけるIssue #12969 [1] は、この静的性質を如実に示している。報告者は「Claude Code currently hardcodes the model selection logic（Claude Codeは現在、モデル選択ロジックをハードコードしている）」と明言しており、この実装により以下の具体的な問題が発生していると指摘している。

- **AWS Chinaリージョン等の利用不可**: AWS Bedrockの中国リージョン（cn-northwest-1, cn-north-1）では、グローバルリージョンとは異なるモデルIDの命名規則が採用されている場合がある。しかし、CLIが特定のモデルID文字列をハードコードして期待しているため、これら異なるIDを持つモデルを認識できず、利用できない状態にある。
- **カスタムファインチューニングモデルの排除**: 企業や組織が独自のデータでファインチューニングしたカスタムモデル（Custom Models）は、標準のモデルリストには含まれないIDを持つ。動的なリスト取得機能がないため、これらのモデルをメニューに表示させたり、エイリアスとして利用したりすることが困難である。
- **新モデルへの即応性の欠如**: 新しいモデル（例：Claude 3.6や3.7など）がAPIとしてリリースされたとしても、CLIのコード内で定義されたリストが更新されない限り、ユーザーはそのモデルを選択肢として見ることができない。これを利用するには、CLI自体のバージョンアップ（`npm update -g @anthropic-ai/claude-code`）を待つ必要がある。

#### 3.1.2 動的クエリ機能の欠如

Issue #12612 [2] では、「CLIからプログラム的に利用可能なモデルをクエリする方法がない」という機能要望が出されている。現状では、インタラクティブセッションを開始して`/model`と入力する以外にリストを確認する術がなく、これもAPIからの動的取得ではなく、内部定数の表示に過ぎないことが示唆されている。もしAPIから動的に取得しているのであれば、`claude model list`のようなコマンドの実装は技術的に容易であるはずだが、現状はその機能が存在しない。これは、CLIが「現在利用可能なモデル」を外部ソースから動的に取得する機能を持っていないことを裏付けている。

#### 3.1.3 ラッパーツールとの対比による証明

サードパーティ製のラッパーツールである「Claudish」[3] の仕様と比較することで、本家Claude Codeの静的性質がより鮮明になる。ClaudishはOpenRouter等のメタデータを動的にクエリし、その時点で利用可能なあらゆるモデル（他社モデル含む）をリスト化する機能を持つ。このツールの説明において「No more hardcoded lists（もはやハードコードされたリストはない）」と謳われていることは、逆説的に本家Claude Codeがハードコードされたリストに依存していることを証明している。

### 3.2 静的実装の技術的意図とメリット

なぜAnthropicの開発チームは、拡張性に優れた動的取得ではなく、保守コストのかかる静的ハードコードを採用したのか。これには、Claude Code特有の「エージェンティック」な性質に起因するいくつかの合理的な理由が推測される。

1. **エージェンシーの品質保証（Quality Assurance of Agency）**:
   Claude Codeは単にユーザーとチャットするだけでなく、ファイル編集（Edit）、検索（Grep）、コマンド実行（Bash）といった「ツール」を使用する。モデルのバージョンによって、これらのツール定義（JSON Schema）の解釈能力や、複雑な手順の遂行能力は大きく異なる。未検証の新しいモデルや、能力の低いモデルが動的にリストに追加されてしまうと、ツール使用の失敗（例えば、ファイルを破壊的に編集してしまう、無限ループに陥るなど）を引き起こすリスクがある。開発チームが検証済みのモデルのみをホワイトリスト化することで、エージェントとしての最低限の挙動品質を保証していると考えられる。
2. **エイリアスによる抽象化の安定性**: `sonnet`や`opus`といったエイリアスは、常に「そのCLIバージョンにおいて最も安定して動作する推奨バージョン」を指すように設計されている [4]。動的に最新モデルを割り当てると、API側の仕様変更によってCLIの動作が突然不安定になる可能性がある。静的マッピングにより、CLIのバージョンとモデルのバージョンの適合性をコントロールしている。
3. **オフライン動作とレイテンシの排除**:
   CLIツールのUXとして、起動速度は極めて重要である。コマンドを実行するたび、あるいは設定メニューを開くたびに外部APIへモデルリストを取得しに行くと、ネットワーク遅延が発生し、操作感が損なわれる。また、完全にオフラインの状態（ローカルの設定確認など）でもメニューが表示できる利点がある。

### 3.3 動的要素の例外：Opusplanの挙動

モデルの「リスト」自体は静的であるが、実行時のモデル選択挙動には動的な要素が含まれている。特筆すべきは`opusplan`モードである。

- **動的スイッチング**: `opusplan`を選択すると、CLIはタスクのフェーズを認識し、計画（Plan）段階ではOpusモデルを、実行（Execution）段階ではSonnetモデルを自動的に使い分ける [4]。
- **決定論的ではない振る舞い**: この切り替えはユーザーが明示的に「今から実行フェーズ」と指示するものではなく、エージェントが自律的に判断する場合がある。しかし、この「OpusとSonnetを使う」という組み合わせのロジック自体は、やはりCLI内に静的に定義されており、ユーザーが「計画はSonnet、実行はHaiku」のように動的に構成を変更する公式なUIは提供されていない（後述の環境変数によるハックを除く）。

---

## 4. 構成管理の階層構造と優先順位（Configuration Hierarchy）

Claude Codeは、モデルを含む設定の管理において、非常に柔軟かつ厳密な「階層構造（Hierarchy）」を採用している。ユーザーが手動でモデルを設定する場合、どの設定が優先されるか（Precedence）を理解することが不可欠である。設定が競合した場合、より具体的（Specific）あるいは一時的（Transient）な設定が、より一般的（General）あるいは永続的（Permanent）な設定を上書きする原則がある [4]。

### 4.1 設定スコープの全体像

以下の表は、Claude Codeにおける設定スコープを優先順位の高い順（競合時に勝つ順）に整理したものである。

| 優先順位 | スコープ名称 | 設定方法/場所 | 適用範囲 | 特徴・用途 |
| :--- | :--- | :--- | :--- | :--- |
| **1 (最高)** | **インタラクティブ** | セッション内 `/model` コマンド | 現在のセッションのみ | 一時的な切り替え。再起動でリセットされる。 |
| **2** | **CLIフラグ** | 起動時引数 `--model` | 起動したプロセスのみ | 特定のタスク実行時の一時的な指定。CI/CDでの利用。 |
| **3** | **環境変数** | `ANTHROPIC_MODEL` 等 | シェルセッション/システム | 永続的なデフォルト変更。スクリプトからの制御。 |
| **4** | **ローカル設定** | `.claude/settings.local.json` | 現在のプロジェクト | 個人固有の設定。Gitにはコミットしない（gitignore）。 |
| **5** | **プロジェクト設定** | `.claude/settings.json` | 現在のプロジェクト | チーム共有の設定。Gitにコミットして共有する。 |
| **6** | **ユーザー設定** | `~/.claude/settings.json` | 全プロジェクト（ユーザー単位） | ユーザー個人のグローバルなデフォルト設定。 |
| **7 (最低)** | **管理設定** | `managed-settings.json` | システム全体（全ユーザー） | IT部門による強制設定。通常はベースラインとして機能。 |

※ 管理設定（Managed Settings）は、特定の設定（`allowManagedPermissionRulesOnly`等）と組み合わせることで、下位の設定による上書きを禁止（強制）することも可能である [5]。

### 4.2 各スコープの詳細とモデル設定への影響

#### 4.2.1 インタラクティブコマンド（Interactive Commands）

セッション中に `/model` を入力して表示されるメニューからモデルを選択する操作は、他のすべての設定（起動時のフラグや設定ファイル）を即座に上書きする。

- **動的性**: ユーザー体験としては動的だが、選択肢のリスト自体は前述の通り静的である。
- **持続性**: この変更はメモリ上にのみ保持され、CLIを終了（`/exit`）すると失われる。次回起動時は再び設定ファイルやフラグに従う。

#### 4.2.2 CLIフラグ（Command Line Flags）

`claude --model claude-opus-4-6` のように起動時に指定する。

- **用途**: 普段はコスト重視でhaikuを使っているが、今から行うリファクタリングだけはopusを使いたい、といった場合に便利である。
- **優先度**: 環境変数や`settings.json`よりも強いため、エイリアス設定などを一時的に無視して特定のモデルIDを強制適用する際に役立つ。

#### 4.2.3 環境変数（Environment Variables）

Unix系OSにおける標準的な構成手法であり、`ANTHROPIC_MODEL` などの変数をエクスポートすることで設定する [4]。

- **隠れた強力機能**: 特に `ANTHROPIC_DEFAULT_OPUS_MODEL` のような変数は、CLI内部のエイリアス定義をオーバーライドできる可能性がある（後述）。これにより、CLIのコードを書き換えずに「静的リスト」の実体を差し替えることができる。

#### 4.2.4 設定ファイル（JSON Settings）

最も一般的かつ推奨される設定方法である。JSON形式で記述され、スキーマバリデーションが可能である。

- **プロジェクト設定 (.claude/settings.json)**: チームで開発する際、「このプロジェクトは複雑なので全員Opusを使う」あるいは「予算が限られているのでSonnetに統一する」といったポリシーをコードベースに同梱できる。
- **ローカル設定 (.claude/settings.local.json)**: チームの規定はSonnetだが、自分は個人的に契約しているAPIキーでOpusを使いたい、といった場合にチーム設定を上書きできる。

---

## 5. 手動設定（Manual Configuration）の詳細ガイド

ユーザーが手動でモデルを設定するための具体的な手順を、各レイヤーごとに解説する。ここでは、公式ドキュメントには散在している情報を統合し、実践的な設定スニペットを提供する。

### 5.1 JSON設定ファイルによる構成

設定ファイルはJSON形式であり、公式のJSON Schemaを利用することでエディタの補完機能が利用できる。

#### 5.1.1 スキーマの適用

VS Codeなどのエディタで編集する際、ファイルの先頭に `$schema` プロパティを追加することで、有効なキーや値の候補が表示されるようになる [7]。

**推奨される settings.json の基本構造:**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-sonnet-4-5-20250929",
  "permissions": {
    "allow": [],
    "ask": []
  },
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-6"
  }
}
```

#### 5.1.2 model フィールドの指定

`model` キーには、エイリアスまたは具体的なモデルIDを指定する。

- **エイリアス指定**:
  ```json
  "model": "sonnet"
  ```
  最も一般的な設定。CLIのバージョンアップに合わせて自動的にその時点の最新Sonnetが使用されるため、メンテナンスフリーである。
- **モデルID指定（Pinning）**:
  ```json
  "model": "claude-3-5-sonnet-20241022"
  ```
  特定のバージョンに固定したい場合に使用する。CLIがアップデートされても、この設定がある限り古いモデルを使い続けることができる（APIが提供されている限り）。
- **Opusplan指定**:
  ```json
  "model": "opusplan"
  ```
  計画と実行でモデルを使い分けるモードをデフォルトにする。

### 5.2 環境変数による高度な制御

設定ファイルでは記述しきれない、あるいは設定ファイルよりも優先させたいシステムレベルの設定には環境変数を使用する。以下は、Claude Codeが認識する主要なモデル関連の環境変数である [4]。

| 環境変数名 | 説明・用途 | 設定例 |
| :--- | :--- | :--- |
| `ANTHROPIC_MODEL` | デフォルトで使用するモデルを指定する。settings.jsonのmodel値よりも優先される。 | `export ANTHROPIC_MODEL="opus"` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `opus` および `opusplan` の計画フェーズで使用されるモデルIDをオーバーライドする。 | `export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-3-7-opus-2025..."` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `sonnet` および `opusplan` の実行フェーズで使用されるモデルIDをオーバーライドする。 | `export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-3-5-sonnet-..."` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `haiku` エイリアスが指すモデルIDをオーバーライドする。 | `export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-3-5-haiku-..."` |
| `CLAUDE_CODE_SUBAGENT_MODEL` | サブエージェントが使用するデフォルトモデルを指定する [4]。 | `export CLAUDE_CODE_SUBAGENT_MODEL="sonnet"` |

#### 実践テクニック：Opusplanのカスタマイズ

`opusplan` モードは通常「Opusで計画、Sonnetで実行」であるが、環境変数を組み合わせることでこの挙動をハックできる。

例えば、「計画にはSonnetを使い、実行にはHaikuを使いたい（コスト最優先プラン）」場合、以下のように設定することで擬似的に実現できる可能性がある。

```bash
# OpusのふりをしてSonnetを指定
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-3-5-sonnet-20241022"
# SonnetのふりをしてHaikuを指定
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-3-5-haiku-20241022"
# モデルとしてopusplanを指定
claude --model opusplan
```

これにより、CLIは内部ロジック通り「Opusで計画、Sonnetで実行」しようとするが、実体としてはユーザーが環境変数で差し替えたモデルが呼び出されることになる。これは静的なCLIの制約を動的に突破する有効な手段である。

### 5.3 企業・組織向け管理設定（Managed Settings）

企業導入において、全社的なポリシーを適用する場合は `managed-settings.json` を使用する。

- **配置パス**:
  - **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
  - **Linux**: `/etc/claude-code/managed-settings.json`
  - **Windows**: `C:\Program Files\ClaudeCode\managed-settings.json`
- **記述例**:
  ```json
  {
    "model": "claude-sonnet-4-5-20250929",
    "allowManagedPermissionRulesOnly": true,
    "permissions": {
      "deny": []
    }
  }
  ```
  この設定ファイルが存在すると、ユーザーは勝手にモデルを変更して高額な請求を発生させたり、許可されていない外部通信を行ったりすることが防げる。

---

## 6. 高度なモデルオーケストレーション：OpusplanとThinking Mode

Claude Codeの真価は、単一のモデルを使用するだけでなく、タスクの性質に応じてモデルの特性を使い分けるオーケストレーション能力にある。ここでは、手動設定によって制御可能な高度な機能について解説する。

### 6.1 Opusplan：ハイブリッド・エージェンシー

`opusplan` は、Anthropicが提唱する「計画と実行の分離」を具現化したモードである。

- **メカニズム**:
  1. ユーザーから複雑なタスク（例：「認証システム全体のリファクタリング」）を受け取ると、まず**計画フェーズ**に入る。ここでは推論能力に優れたOpusモデルが使用され、ファイル構造の解析、影響範囲の特定、ステップバイステップの実行計画（Markdown形式）の作成を行う。
  2. 計画がユーザーに承認されると、**実行フェーズ**に移行する。ここではコーディング速度とコストパフォーマンスに優れたSonnetモデルが、計画書に従って各ファイルの編集やテスト実行を行う。
  3. 必要に応じて計画の見直しが発生した場合、再びOpusが呼び出される可能性がある。
- **設定のポイント**:
  前述の通り、`ANTHROPIC_DEFAULT_OPUS_MODEL` 等の環境変数を利用することで、この「計画役」と「実行役」の配役を変更できる。将来的にさらに高性能なモデルが出た際、CLIの更新を待たずにこの変数で新モデルを計画役にアサインすることで、いち早くその恩恵を受けることができる。

### 6.2 Thinking Mode（拡張思考）の構成

Claude 3.7（仮称）やOpus 4.5以降で導入されている「Thinking Mode（思考モード）」は、モデルが回答を出力する前に内部的な思考プロセス（Chain of Thought）を出力・展開する機能である。これにより、複雑な推論タスクの精度が劇的に向上する [10]。

- **有効化と設定**:
  一部のモデル（Opus 4.5等）ではデフォルトで有効化されている場合があるが、手動で制御する方法も存在する。
  - **CLIフラグ**: `--betas interleaved-thinking` のように、ベータ機能フラグを通じてAPIヘッダーに指示を送る方法 [12]。
  - **設定ファイル**: `settings.json` に `alwaysThinkingEnabled: true` のようなキーを設定する（バージョンによりサポート状況が異なるため、JSONスキーマでの確認が推奨される） [5]。
  - **思考予算（Thinking Budget）**: 思考に使用するトークン量の上限を設定するパラメータもAPIレベルでは存在するが、CLIからの直接的な制御方法は現状ではベータフラグ経由となることが多い。

---

## 7. 拡張性とコミュニティによる回避策（Workarounds）

本家Claude Codeの静的な制約に不満を持つユーザーのために、コミュニティベースでの回避策や拡張ツールが開発されている。これらは公式のサポート外であるが、動的なモデル選択を実現する手段として重要である。

### 7.1 ラッパーツール「Claudish」の活用

「Claudish」は、Claude CodeのCLIをラップし、通信をインターセプトまたはプロキシすることで機能拡張を行うツールである [3]。

- **動的モデルリスト**: ClaudishはOpenRouter等のAPIを利用して、その時点で利用可能なモデルリストを動的に取得する。これにより、Anthropic以外のモデル（例：Google Gemini, OpenAI GPT-4o, DeepSeekなど）もClaude Codeのインターフェースから利用可能にする。
- **メタデータの注入**: Claude Codeが内部で持っているモデルごとのトークン制限やツール定義といったメタデータを、外部APIからの情報で動的に置換・注入することで、未知のモデルでもエラーなく動作させる工夫がなされている。

### 7.2 ソースコードのパッチ適用

Claude CodeはNode.js製のツールであり、インストールされた実体はJavaScriptファイル（`cli.js`）である。一部の上級ユーザーは、このファイルを直接編集（パッチ適用）することで、システムプロンプトの削減やモデルリストの書き換えを行っている [13]。

- **手法**: `npm root -g` でインストール先を特定し、`cli.js` 内のモデル定義配列を直接書き換える。
- **リスク**: アップデートのたびに上書きされるため、永続性はない。また、動作保証外となる。

---

## 8. 結論と推奨事項

本調査により、Claude Code CLIにおけるモデル読み込みと構成管理の全容が明らかになった。

1. **静的実装の現実**: `/model`コマンドのモデルリストは静的であり、動的なAPI取得ではない。新モデルの利用にはCLIのアップデートが基本となる。
2. **手動設定の強力な柔軟性**: 静的リストの裏側で、環境変数や`settings.json`を駆使することで、ユーザーはモデルIDのオーバーライドやデフォルト設定の変更を自在に行うことができる。
3. **推奨される運用フロー**:
   - **個人開発者**: `~/.claude/settings.json` に `model: "sonnet"` または `model: "opusplan"` を設定し、日常的な手間を省く。
   - **チーム開発**: `.claude/settings.json` をリポジトリに含め、プロジェクトの特性（難易度・予算）に合わせたモデルをチーム全体で強制する。
   - **最新モデルへの追従**: CLIのアップデートをこまめに行う（`npm update`）。待てない場合は `ANTHROPIC_DEFAULT_...` 環境変数を利用して強制的に新モデルIDをマッピングする。

Claude Codeは「静的な安全性」と「設定による柔軟性」のバランスの上に成り立っている。ユーザーはこの仕組みを理解することで、ツールの能力を最大限に引き出し、自身の開発ワークフローに完全に適合させることが可能である。

---

**参考文献リスト**

#### 引用文献

1. [FEATURE] Make Claude model ID fully configurable (including ..., 2月 10, 2026にアクセス、 [https://github.com/anthropics/claude-code/issues/12969](https://github.com/anthropics/claude-code/issues/12969)
2. [Feature Request] Add 'claude model list' CLI command for non-interactive model queries · Issue #12612 · anthropics/claude-code - GitHub, 2月 10, 2026にアクセス、 [https://github.com/anthropics/claude-code/issues/12612](https://github.com/anthropics/claude-code/issues/12612)
3. MadAppGang/claudish: Claude Code. Any Model. The most powerful AI coding agent now speaks every language. - GitHub, 2月 10, 2026にアクセス、 [https://github.com/MadAppGang/claudish](https://github.com/MadAppGang/claudish)
4. Model configuration - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/model-config](https://code.claude.com/docs/en/model-config)
5. Claude Code settings - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
6. Claude Code CLI Environment Variables - GitHub Gist, 2月 10, 2026にアクセス、 [https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)
7. How Claude Code Manages Local Storage for AI Agents - Milvus Blog, 2月 10, 2026にアクセス、 [https://milvus.io/blog/why-claude-code-feels-so-stable-a-developers-deep-dive-into-its-local-storage-design.md](https://milvus.io/blog/why-claude-code-feels-so-stable-a-developers-deep-dive-into-its-local-storage-design.md)
8. Settings types or JSON Schema · Issue #2783 · anthropics/claude-code - GitHub, 2月 10, 2026にアクセス、 [https://github.com/anthropics/claude-code/issues/2783](https://github.com/anthropics/claude-code/issues/2783)
9. MCP Task Logger | MCP Servers - LobeHub, 2月 10, 2026にアクセス、 [https://lobehub.com/mcp/withoutfanfare-mcp-task-logger](https://lobehub.com/mcp/withoutfanfare-mcp-task-logger)
10. The Complete Claude Code CLI Guide - Live & Auto-Updated Every 2 Days - GitHub, 2月 10, 2026にアクセス、 [https://github.com/Cranot/claude-code-guide](https://github.com/Cranot/claude-code-guide)
11. The "think" tool: Enabling Claude to stop and think in complex tool use situations - Anthropic, 2月 10, 2026にアクセス、 [https://www.anthropic.com/engineering/claude-think-tool](https://www.anthropic.com/engineering/claude-think-tool)
12. CLI reference - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)
13. 25 Claude Code Tips from 11 Months of Intense Use : r/ClaudeAI - Reddit, 2月 10, 2026にアクセス、 [https://www.reddit.com/r/ClaudeAI/comments/1qgccgs/25_claude_code_tips_from_11_months_of_intense_use/](https://www.reddit.com/r/ClaudeAI/comments/1qgccgs/25_claude_code_tips_from_11_months_of_intense_use/)
14. Claude Code overview - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview)
15. Introducing advanced tool use on the Claude Developer Platform - Anthropic, 2月 10, 2026にアクセス、 [https://www.anthropic.com/engineering/advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use)
16. Claude Code CLI Cheatsheet: config, commands, prompts, + best practices - Shipyard.build, 2月 10, 2026にアクセス、 [https://shipyard.build/blog/claude-code-cheat-sheet/](https://shipyard.build/blog/claude-code-cheat-sheet/)
17. Troubleshooting - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/troubleshooting](https://code.claude.com/docs/en/troubleshooting)
18. Claude Code model configuration | Claude Help Center, 2月 10, 2026にアクセス、 [https://support.claude.com/en/articles/11940350-claude-code-model-configuration](https://support.claude.com/en/articles/11940350-claude-code-model-configuration)
19. How Claude Code works - Claude Code Docs, 2月 10, 2026にアクセス、 [https://code.claude.com/docs/en/how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works)
