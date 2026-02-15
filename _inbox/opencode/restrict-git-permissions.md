---
title: "oh-my-opencodeにおけるGit権限分離とgit_masterロールの高度な運用設計"
date: 2026-02-13
layout: default
---

# oh-my-opencodeにおけるGit権限分離とgit_masterロールの高度な運用設計

## 1. 序論：自律型AIエージェントと権限管理のパラダイムシフト

ソフトウェア開発の現場において、AIコーディングアシスタントの役割は、単なるコード補完から、リポジトリ全体を管理・操作する自律型エージェントへと急速に進化しています。OpenCode
1 はその先駆的なプラットフォームであり、特にその拡張フレームワークである oh-my-opencode
(OMO)
3 は、単一のAIモデルではなく、複数の専門特化型エージェント（Sisyphus、Prometheus、Librarianなど）が協調して開発を行う「オーケストレーション」の概念を導入しました。Sisyphus
3 と呼ばれるメインオーケストレーターが、エンジニアリングマネージャーのようにタスクを分解し、それぞれの専門領域を持つサブエージェントに作業を委譲するこのアーキテクチャは、人間の開発チームの構造を模倣しています。

しかし、このような自律性の向上は、同時に重大なセキュリティとガバナンスの課題をもたらします。特にバージョン管理システム（Git）へのアクセス権限は、プロジェクトの整合性を維持する上で最もクリティカルな要素です。開発者が「AIにコードを書かせたい」と望む一方で、「AIに勝手にコミットやプッシュをさせたくない」、あるいは「Git操作の専門知識を持つ特定のAIロールにのみ、履歴の変更を許可したい」と考えるのは、最小権限の原則（Least
Privilege）に基づけば極めて自然な要求です 5。

本レポートは、oh-my-opencode 環境において、メインエージェントであるSisyphusや他の汎用的なビルドエージェントからのGit操作を厳格に制限しつつ、git_master
7 と呼ばれる特定のスキルセットを持つエンティティに対してのみ、Git操作のフル権限（Full
Privileges）を付与するための技術的実装詳細、アーキテクチャ設計、および運用戦略を網羅的に解説するものです。

### 1.1 問題の所在と技術的制約

ユーザーの要件である「git_masterにだけgit操作をフル権限与えたい」という要望を実現するには、OMOのアーキテクチャにおける「エージェント（Agent）」と「スキル（Skill）」の根本的な違いを理解し、OpenCodeの権限システム（Permission
System）の仕様と照らし合わせる必要があります。

| コンポーネント                  | 定義と役割                                                                       | 権限設定の適用範囲                                                                   |
| :------------------------------ | :------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| **Agent** (例: Sisyphus, Build) | LLMのペルソナであり、対話の主体。                                                | 権限設定（permissionオブジェクト）は主にエージェント単位でオーバーライド可能 5。     |
| **Skill** (例: git-master)      | 特定のタスク遂行に必要な知識とツールの集合体。エージェントに「装備」されるもの。 | スキル自体は独立した実行主体ではないため、通常は権限設定の直接の対象とはならない 5。 |
| **Tool** (例: bash, edit)       | OSや外部システムと対話するための実行機能。                                       | 権限設定の最小単位。allow, ask, deny の3状態で制御される 5。                         |

ここで最大の技術的障壁となるのが、git_master が OMO のデフォルト構成において独立した「エージェント」ではなく、「スキル」として定義されている点です 10。OpenCodeの権限システムは、主にツール（bashなど）へのアクセスをグローバル設定、あるいはエージェントごとのオーバーライドとして定義します 5。したがって、「git_masterスキルを持っている時だけGitを許可する」という動的な権限付与は、標準的なJSON設定だけでは実現が困難な場合があります。

この制約を突破するためには、git_master スキルを専門に行使するための「特権エージェント（Privileged
Agent）」を定義し、メインオーケストレーターであるSisyphusからのGit操作を禁止した上で、Git操作が必要な場合は必ずその特権エージェントへタスクを委譲（Delegate）させるという、「委譲ベースの権限分離モデル（Delegation-Based
Role Separation Model）」を構築する必要があります。

## 2. OpenCode権限システムの深層分析

実装戦略を詳述する前に、OpenCodeおよびOMOが採用している権限システムのメカニズムを深く掘り下げます。バージョン1.1.1以降、従来のシンプルな tools:
boolean 設定は非推奨となり、より粒度の高い permission オブジェクトへと移行しました 5。この変更は、今回のような高度なRBACを実現するための基盤となっています。

### 2.1 Permissionオブジェクトの構造と評価ロジック

権限設定は opencode.json または oh-my-opencode.json 内に記述され、グローバルスコープとエージェントスコープの2層で管理されます。

JSON

```json
"permission": {
  "*": "ask",
  "bash": {
    "*": "ask",
    "git *": "allow",
    "rm *": "deny"
  }
}
```
この設定において最も重要なのは、ルール評価の優先順位です。OpenCodeのドキュメントによれば、ルールはパターンマッチングによって評価され、「最後にマッチしたルールが適用される（last
matching rule
wins）」というロジックが採用されています 5。これは、一般的なファイアウォールのルール（最初にマッチしたものが適用）とは逆の挙動である可能性が高く、設定記述順序に細心の注意を払う必要があります。しかし、多くのJSONパーサはキーの順序を保証しないため、OpenCodeの実装では「より具体的なパターン（specific
pattern）」が「ワイルドカード（wildcard）」よりも優先される、あるいは配列として定義する場合の順序依存性を考慮する必要があります。ドキュメントの例 5 では、キャッチオールの * を最初に置き、その後に具体的な例外を記述するパターンが推奨されています。

### 2.2 Bashコマンドの粒度制御

git 操作を制御するためには、bash ツールに対する権限を細分化する必要があります。単に "bash":
"allow" とすれば全てのシェルコマンドが許可されますが、これでは rm -rf
/ のような破壊的操作も許可してしまいます。

今回の要件では、以下のような制御が求められます：

1. **Sisyphus (Main Agent):**
   git コマンドを含む全てのシェル操作に対して、原則として ask（確認）または deny（禁止）を適用する。ただし、状況把握のための git
   status や git
   log など、副作用のない（Read-Onlyな）コマンドは許可しても良いかもしれない。
2. **Git Master (Target Role):** git commit, git push, git
   rebase を含むあらゆる git コマンドに対して allow（無確認実行）を適用する。

この粒度を実現するためには、グロブパターン（Glob
Patterns）を用いた設定が不可欠です。git * は git で始まる全てのコマンドにマッチしますが、git
commit * のようにさらに詳細なサブコマンド単位での制御も可能です 5。

### 2.3 エージェントごとの権限オーバーライド

OpenCodeの権限システムにおける「切り札」は、エージェント定義内での権限オーバーライド機能です 5。

JSON

```json
"agent": {
  "build": {
    "permission": {
      "bash": { "git *": "deny" }
    }
  }
}
```
この設定により、特定の ID を持つエージェントに対してのみ、グローバル設定とは異なる権限ポリシーを適用できます。OMO においては、sisyphus がメインのエージェント ID となり、他にも prometheus
(planner) や librarian などのエージェントが存在します 10。したがって、Sisyphus に対しては厳格な制限を課し、別途定義した git-executor エージェントに対しては緩和された権限を与えることが、アーキテクチャ上の正解となります。

## 3. oh-my-opencodeアーキテクチャとgit_masterの正体

oh-my-opencode は単なる設定ファイル群ではなく、OpenCode の機能を拡張するためのプラグイン的な性質を持ちます。特に git_master の扱いについては、ソースコードレベルでの理解が必要です。

### 3.1 スキル（Skill）としての git_master

リサーチ資料 8 によれば、git_master は「Atomic
commits（原子的コミット）」、「rebase/squash
workflows（リベース/スカッシュフロー）」、「history
search（履歴検索）」を専門とする**スキル**として実装されています。

スキルがロードされると、そのスキル専用のプロンプト（System Prompt
Injection）がエージェントのコンテキストに追加されます 9。

- **Prompt Instruction:** "MUST USE for ANY git
  operations."（あらゆるGit操作に使用しなければならない）8。
- **Triggers:** commit, rebase, squash,
  blame などのキーワードに反応して発動します 8。

ここで重要なのは、スキル自体は「権限」を持たないということです。スキルはあくまで「知識（Knowledge）」と「手順（Procedure）」のセットであり、それを実行するのは「エージェント」です。したがって、「git_masterスキルを使っている時だけ権限を与える」という動的な制御は、OpenCodeの標準機能では直接的にサポートされていません（v1.1.1時点）。

### 3.2 Sisyphusの委譲モデル

Sisyphusは「エンジニアリングマネージャー」としての役割を担い、タスクをサブエージェントに委譲（Delegate）する能力を持っています 3。OMO では task ツール（または delegate_task）を使用して、特定のカテゴリ（Category）やスキルを指定したサブタスクを作成します 9。

推奨される使用法として、task(category='quick',
load_skills=['git-master']) というパターンが提示されています 7。これは、「Quick」カテゴリのエージェントを生成し、そのエージェントに git-master スキルを持たせて実行させることを意味します。この「委譲先のサブエージェント」こそが、今回権限を与えるべきターゲットとなります。

## 4. 実装戦略フェーズ1：構成ファイルによる権限分離設計

ここからは、具体的な実装手順に入ります。まず、oh-my-opencode.json を編集し、エージェント定義と権限マトリクスを構築します。

### 4.1 Git操作専用エージェントの定義

既存の sisyphus エージェントに git_master スキルをロードさせるだけでは、Sisyphus 自体の権限制限に引っかかってしまいます。そこで、Git操作専用の「特権エージェント（Privileged
Agent）」を定義します。ここでは便宜上、このエージェントを git-executor と命名します。

**設定ファイルパス:**

- プロジェクトローカル: .opencode/oh-my-opencode.json
- ユーザーグローバル: ~/.config/opencode/oh-my-opencode.json

**JSON構成（oh-my-opencode.json）:**

コード スニペット

```json
{
  "$schema":
  "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json",

  // 1. エージェント定義
  "agents": {
    // 【制限対象】メインオーケストレーター (Sisyphus)
    "sisyphus": {
      "permission": {
        "bash": {
          // 安全な参照系コマンドのみ許可
          "git status": "allow",
          "git log*": "allow",
          "git diff*": "allow",
          "git show*": "allow",
          "git branch": "allow",
          // それ以外の全てのGitコマンド（変更を伴うもの）を禁止
          "git *": "deny",
          // その他のコマンドはデフォルト（ask）またはグローバル設定に従う
          "*": "ask"
        }
      }
    },

    // 【制限対象】デフォルトのビルドエージェント
    "build": {
      "permission": {
        "bash": {
          "git *": "deny"
        }
      }
    },

    // 【特権対象】Git操作専用エージェント (Git Executor)
    "git-executor": {
      // 高性能なモデルを指定（コミットメッセージの品質確保のため）
      "model": "anthropic/claude-3-5-sonnet-20241022",
      "description": "Git操作の専門家。バージョン管理に関する完全な権限を持つ。",
      "prompt_append": "あなたはGit Masterです。リポジトリの履歴を管理する唯一の権限を持っています。Sisyphusからの委譲を受けて、コミット、プッシュ、リベースなどの操作を実行します。常にAtomicなコミットを心がけてください。",
      "permission": {
        "bash": {
          // 全てのGit操作を許可
          "git *": "allow"
        }
      }
    }

  },

  // 2. git_masterスキルの設定
  "git_master": {
    "commit_footer": true,
    "include_co_authored_by": true
  },

  // 3. カテゴリ設定 (委譲のルーティング用)
  "categories": {
    "version-control": {
      "model": "anthropic/claude-3-5-sonnet-20241022",
      "prompt_append": "Git操作に特化したコンテキストで実行されます。"
    }
  }
}
```
### 4.2 権限設定の詳細解説

この設定により、以下の挙動が強制されます。

1. **Sisyphusの無力化:**
   Sisyphusがユーザーの指示（例：「バグ修正してコミットして」）を受けて直接 git
   commit を実行しようとすると、OpenCodeのシステムが介入し、「Permission
   Denied」エラー、あるいはユーザーへの承認要求（ask設定の場合）が発生します。ここで deny に設定しておけば、物理的に実行不可能となります。
2. **Git Executorの特権化:**
   git-executor エージェントとして起動されたセッション内では、git で始まる全てのコマンドが allow（無確認実行）されます。これにより、コミットメッセージの作成からプッシュまでの一連のフローがノンストップで実行されます。

しかし、これだけでは不十分です。Sisyphusは「自分がコミットできない」ことを知りません。エラーに遭遇してから「困った」と報告してくるだけでしょう。Sisyphusに対して「Git操作が必要な時は、自分でやらずに git-executor に頼め」という行動指針（Policy）を植え付ける必要があります。

## 5. 実装戦略フェーズ2：プロンプトエンジニアリングによる委譲の強制

構成ファイルによる制限は「ハードガードレール（Hard
Guardrail）」ですが、AIがそのガードレールにぶつかる前に正しい道を歩ませる「ソフトガイド（Soft
Guide）」が必要です。これには AGENTS.md を使用します。

### 5.1 AGENTS.md によるルール注入

AGENTS.md は、プロジェクト固有またはグローバルな指示をエージェントのシステムプロンプトに追加するためのファイルです 14。ここに「Git操作の委譲プロトコル」を記述します。

**ファイルパス:** .opencode/AGENTS.md (プロジェクトルート推奨)

## プロジェクト運用ルールとGit操作プロトコル

## 1. 権限と役割分担

このプロジェクトでは、**権限分離（Separation of
Duties）**が厳格に適用されています。

- **Sisyphus (あなた):**
  コードの作成、修正、テスト実行、計画立案を担当します。しかし、**Gitによる変更操作（add,
  commit, push, rebase等）の権限は剥奪されています**。
- **Git Executor (git-master):**
  バージョン管理操作を行う唯一の権限を持つ専門エージェントです。

## 2. Git操作の委譲フロー (CRITICAL)

ユーザーから「コミットして」「プッシュして」などの指示があった場合、または作業の区切りとしてコミットが必要と判断した場合、あなたは**絶対に自分で git コマンドを実行してはいけません**。代わりに、以下の手順でタスクを委譲してください。

### 手順

1. 現在の変更内容を git status や git
   diff で確認する（これは許可されています）。
2. task ツールを使用して、サブエージェントを呼び出します。
3. task ツールの引数は必ず以下のように設定してください：
   - subagent_type: "git-executor" (設定ファイルで定義したID)
   - load_skills: ["git-master"] (git_masterスキルをロード)
   - prompt: 具体的な指示（例:
     "src/auth.tsの修正をコミットしてください。メッセージは'feat: 認証ロジックの修正'としてください"）

### 禁止事項

- ❌ git commit... を直接実行する -> 権限エラーになります。
- ❌ git push... を直接実行する -> 権限エラーになります。
- ❌ 汎用エージェント（build,
  general）にGit操作を委譲する -> 彼らも権限を持っていません。

## 3. コミットメッセージの基準

git-master スキルを使用する際は、以下の基準を遵守させてください。

- Conventional Commits 形式 (feat, fix, chore, etc.)
- Atomic Commits (論理的単位での分割)

このプロンプトにより、Sisyphusは自身の制約を認識し、適切なエージェント（git-executor）を呼び出すという「思考の回路」を獲得します。

## 6. 実装戦略フェーズ3：フックと環境変数による多層防御

JSON設定とプロンプトだけで多くのケースはカバーできますが、より堅牢なセキュリティ、あるいは「ユーザーが誤ってターミナルで実行する」ケースなども含めた包括的な制御を行うために、フック（Hooks）やGit自体のフック機能を活用します。

### 6.1 PreToolUse フックによる動的制御

OpenCode (Claude
Code互換) のフックシステムを利用して、ツール実行直前にプログラム的なチェックを行うことが可能です 7。これにより、静的なJSON設定では表現しきれない複雑なロジック（例：「夜間はコミット禁止」など）も実装できますが、ここでは「エージェントIDの検証」を行います。

**設定ファイル:** ~/.claude/settings.json

JSON

```json
{
  "hooks": {
    "PreToolUse":
  }
]
}
}
```
このスクリプト verify_git_permission.js 内で、実行されようとしているコマンドが git であり、かつ現在のエージェントIDが git-executor でない場合、終了コード1（エラー）を返して実行をブロックします。ただし、OMO が AGENT_ID を環境変数としてフックに渡しているかどうかの検証が必要です（リサーチ資料 15 では CI などの変数は確認されていますが、エージェントIDの明示的な記載はありません）。したがって、この方法は「可能であれば実装する」オプションとなります。

### 6.2 Git Hooks (pre-commit/pre-push) による最終防衛ライン

OpenCodeの外側、つまりGitリポジトリ自体の設定として、特定の環境変数を持たないプロセスからのコミットを拒否することも有効です。

OMO はサブエージェントを実行する際、環境変数を注入することができます。git-executor の定義に環境変数を追加できれば理想的ですが、現在のスキーマ 10 ではエージェント定義内での環境変数注入が明示的にサポートされているかは不明確です。しかし、git_master スキル自体が環境変数に依存する挙動（GIT_EDITOR など）を持っていることから 15、非対話モード（Non-Interactive
Mode）判定ロジックを逆手に取ることが可能です。

例えば、Sisyphusが実行するシェルは対話的（Interactive）と見なされる一方、task で裏で走るエージェントは非対話的（Non-Interactive）として扱われる場合があります。この差異を利用して pre-commit フックで制御することも考えられますが、誤検知のリスクが高いため、基本的には
## 4.1 のJSON設定による制御を主軸とすべきです

## 7. 運用シナリオとワークフローの詳細

構築したシステムがどのように機能するか、具体的なシナリオでシミュレーションします。

### シナリオA：日常的なバグ修正とコミット

1. **ユーザー指示:**
   「src/login.ts のバリデーションバグを修正して、修正が完了したらコミットしてください。」
2. **Sisyphusの思考:**
   - (計画)
     src/login.ts を読み込む -> 修正する -> テストする。ここまでは自分の権限（read,
     edit, bash:npm test）で実行可能。
   - (制約確認) コミットが必要だが、自分には git
     commit の権限がない。AGENTS.md の指示に従い、git-executor に委譲する必要がある。
3. **Sisyphusの実行:**
   - read("src/login.ts")
   - edit("src/login.ts",...)
   - bash("npm test") -> Pass.
   - task(subagent_type="git-executor", load_skills=["git-master"],
     prompt="src/login.tsの修正をコミットしてください。メッセージは 'fix: ログインバリデーションのバグ修正' です。")
4. **Git Executorの起動:**
   - OMOが git-executor を初期化。権限設定 bash: { "git *": "allow"
     } が適用される。
   - git-master スキルがロードされる。
5. **Git Executorの実行:**
   - git status -> 変更検知。
   - git add src/login.ts -> 許可されているため実行成功。
   - git commit -m "fix:..." -> 許可されているため実行成功。
   - Sisyphusに「コミット完了」を報告して終了。
6. **Sisyphusの報告:** ユーザーに「修正とコミットが完了しました」と報告。

### シナリオB：リベースが必要な場合 (高度な運用)

ユーザーが「mainブランチを取り込んでリベースして」と指示した場合、Sisyphusはこの複雑な操作も委譲しなければなりません。git_master スキルは「Rebase
Surgeon（リベース外科医）」としての機能も持っているため 8、git-executor は競合が発生した場合でも、その特権を使って git
rebase --continue や git
add を駆使して解決を図ることができます。Sisyphusがこれをやろうとすると、途中の git
add で権限エラーになり、リポジトリが中途半端な状態（DETACHED
HEADやrebase進行中）で止まってしまうリスクがありますが、権限分離によってそのリスクを回避できます。

## 8. トラブルシューティングと診断

この高度な設定は複雑であるため、いくつかの問題が発生する可能性があります。

### 8.1 "Unauthorized" エラーが発生する場合

delegate_task を実行した際に Failed to create session:
Unauthorized というエラーが出る場合 16、これは委譲先のエージェントで使用しようとしているモデル（例：Claude
3.5
Sonnet）に対する認証情報が、サブセッションに正しく引き継がれていない可能性があります。特に、OMO のプラグイン（例：opencode-antigravity-auth）を使用している場合、プロバイダーごとの認証スコープを確認する必要があります。解決策としては、git-executor に割り当てるモデルを、確実に認証済みで利用可能なもの（例：ユーザーがログイン済みのAnthropicモデルや、APIキー設定済みのOpenAIモデル）に固定することです。

### 8.2 スキルがロードされない場合

disabled_skills 設定に誤って git-master が含まれていないか確認してください 10。また、環境変数 OPENCODE_CONFIG_DIR をカスタムしている場合、スキル定義ファイルのパス解決に失敗することがあります 18。opencode
doctor コマンドを使用して、設定ファイルの読み込み状況とスキルの認識状況を診断することを推奨します。

### 8.3 無限委譲ループ (Doom Loop)

Sisyphusが「コミットしたい」->「委譲する」->「委譲先が失敗する（設定ミスなどで）」->「Sisyphusが自分でやろうとする」->「権限エラー」->「また委譲しようとする」というループに陥る可能性があります。これを防ぐには、doom_loop 検出設定を適切に行うとともに 10、git-executor からのエラー戻り値をSisyphusが正しく解釈し、ユーザーに助けを求めるようにプロンプトで指示する必要があります。

## 9. 結論と将来の展望

oh-my-opencode における git_master への権限分離は、JSON設定による「エージェント定義」と「権限マトリクス」、そして AGENTS.md による「委譲プロトコル」の組み合わせによって、完全に実現可能です。この構成は、単に「誤操作を防ぐ」だけでなく、Git操作という専門性の高いタスクを専用のロールに切り出すことで、メインエージェントのコンテキスト汚染を防ぎ、開発プロセス全体の品質と安定性を向上させる効果があります。

今後の OpenCode の進化において、コンテキストハンドオフ（Context
Handoff）機能 19 が強化されれば、Sisyphus から git-executor への文脈（なぜこの変更をしたのか、どういう意図か）の伝達がよりスムーズになり、コミットメッセージの品質はさらに向上するでしょう。本レポートで示した設計は、来るべき「マルチエージェント協調開発時代」におけるスタンダードな運用モデルの一つとなると確信します。

### ---

**表1: エージェント別権限設定マトリクス (推奨構成)**

| エージェント     | 役割               | Bash権限 (git 関連)                                                           | 編集権限 (edit)        | 意図・設計思想                                                 |
| :--------------- | :----------------- | :---------------------------------------------------------------------------- | :--------------------- | :------------------------------------------------------------- |
| **Sisyphus**     | オーケストレーター | git status, log, diff のみ **Allow**。 その他 (commit, push 等) は **Deny**。 | **Allow**              | 状況把握は許可するが、履歴変更は禁止。思考と実装に集中させる。 |
| **Build**        | 実装担当           | git * 全て **Deny**。                                                        | **Allow**              | コードを書くことのみに専念。Git操作は管轄外とする。            |
| **Git Executor** | バージョン管理担当 | git * 全て **Allow**。                                                       | **Allow** (競合解決用) | git_master スキルを行使するための特権コンテナ。                |

### 表2: 主要な設定ファイルと役割

| ファイルパス                            | 役割                                     | 設定項目例                          |
| :-------------------------------------- | :--------------------------------------- | :---------------------------------- |
| ~/.config/opencode/oh-my-opencode.json | エージェント定義と権限のハード強制       | agents, permission, categories      |
| .opencode/AGENTS.md                     | エージェントへの行動指針（ソフトガイド） | 「Git操作は必ず委譲せよ」という指示 |
| ~/.claude/settings.json                | フックによる動的制御（オプション）       | PreToolUse でのコマンド監視         |

この設計を実装することで、ユーザーの要望である「git_master（を装備したエージェント）にだけフル権限を与える」環境が完成します。

### 引用文献

1. opencode-ai/opencode: A powerful AI coding agent. Built for the terminal. -
   GitHub, 2月 10, 2026にアクセス、
   [https://github.com/opencode-ai/opencode](https://github.com/opencode-ai/opencode)
2. OpenCode | The open source AI coding agent, 2月 10, 2026にアクセス、
   [https://opencode.ai/](https://opencode.ai/)
3. Oh My OpenCode (5 SUPER Agent/MCP/Prompt Config): This makes OPENCODE - A
   BEAST! REALLY GOOD Agents, 2月 10, 2026にアクセス、
   [https://www.youtube.com/watch?v=uuV1DcvObsg](https://www.youtube.com/watch?v=uuV1DcvObsg)
4. code-yeongyu/oh-my-opencode: the best agent harness - GitHub, 2月 10,
   2026にアクセス、
   [https://github.com/code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)
5. Permissions - OpenCode, 2月 10, 2026にアクセス、
   [https://opencode.ai/docs/permissions/](https://opencode.ai/docs/permissions/)
6. [Bug]: Sisyphus is insane, and driving me crazy - System Instructions and
   Hooks Need Refinement · Issue #1052 · code-yeongyu/oh-my-opencode - GitHub,
   2月 10, 2026にアクセス、
   [https://github.com/code-yeongyu/oh-my-opencode/issues/1052](https://github.com/code-yeongyu/oh-my-opencode/issues/1052)
7. @reinamaccredy/oh-my-opencode - NPM, 2月 10, 2026にアクセス、
   [https://www.npmjs.com/package/@reinamaccredy/oh-my-opencode?activeTab=dependents](https://www.npmjs.com/package/@reinamaccredy/oh-my-opencode?activeTab=dependents)
8. oh-my-opencode/docs/features.md at dev - GitHub, 2月 10, 2026にアクセス、
   [https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/features.md](https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/features.md)
9. oh-my-opencode/docs/category-skill-guide.md at dev - GitHub, 2月 10,
   2026にアクセス、
   [https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/category-skill-guide.md](https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/category-skill-guide.md)
10. oh-my-opencode/docs/configurations.md at dev - GitHub, 2月 10,
    2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/configurations.md](https://github.com/code-yeongyu/oh-my-opencode/blob/dev/docs/configurations.md)
11. @reinamaccredy/oh-my-opencode - npm, 2月 10, 2026にアクセス、
    [https://www.npmjs.com/package/@reinamaccredy/oh-my-opencode](https://www.npmjs.com/package/@reinamaccredy/oh-my-opencode)
12. Agents - OpenCode, 2月 10, 2026にアクセス、
    [https://opencode.ai/docs/agents/](https://opencode.ai/docs/agents/)
13. oh-my-opencode/AGENTS.md at dev - GitHub, 2月 10, 2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/blob/dev/AGENTS.md](https://github.com/code-yeongyu/oh-my-opencode/blob/dev/AGENTS.md)
14. Rules | OpenCode, 2月 10, 2026にアクセス、
    [https://opencode.ai/docs/rules/](https://opencode.ai/docs/rules/)
15. non-interactive-env hook: clarification on intended behavior · Issue #522
    - GitHub, 2月 10, 2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/issues/522](https://github.com/code-yeongyu/oh-my-opencode/issues/522)
16. [Bug]: delegate_task tool fails with 'Unauthorized' while task tool works
    #1215 - GitHub, 2月 10, 2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/issues/1215](https://github.com/code-yeongyu/oh-my-opencode/issues/1215)
17. [Bug]: It is not possible to disable built-in skills and use custom
    skills. · Issue #1202 · code-yeongyu/oh-my-opencode - GitHub, 2月 10,
    2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/issues/1202](https://github.com/code-yeongyu/oh-my-opencode/issues/1202)
18. [Feature]: Please support recognizing the 'skills' in the opencode custom
    configuration directory. #810 - GitHub, 2月 10, 2026にアクセス、
    [https://github.com/code-yeongyu/oh-my-opencode/issues/810](https://github.com/code-yeongyu/oh-my-opencode/issues/810)
19. code-yeongyu/oh-my-opencode v3.4.0 on GitHub - NewReleases.io, 2月 10,
    2026にアクセス、
    [https://newreleases.io/project/github/code-yeongyu/oh-my-opencode/release/v3.4.0](https://newreleases.io/project/github/code-yeongyu/oh-my-opencode/release/v3.4.0)
