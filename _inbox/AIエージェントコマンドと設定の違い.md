# **AI駆動型開発環境におけるインタラクション・プロトコルとコンテキストアーキテクチャの包括的分析**

## **エグゼクティブサマリー**

ソフトウェア開発のパラダイムは、従来の統合開発環境（IDE）から、大規模言語モデル（LLM）を中核に据えた「エージェンティック（Agentic）開発環境」へと急速に移行している。Claude CodeやCursor IDE、Roo Codeといった先進的なツールは、単なるコード補完機能を超え、開発者の意図を理解し、自律的にタスクを遂行する能力を獲得しつつある。この進化に伴い、人間とAIエージェント間のコミュニケーションを制御するための新たなインターフェース規格とコンテキスト管理手法が確立されつつある。

本レポートは、現代のAI開発環境における主要な制御メカニズムである「カスタム（スラッシュ）コマンド」、「@コマンド（コンテキスト注入）」、「自然言語入力（ノーコードコマンド）」、および「スキル（Skills）」の技術的特質と相互運用性を徹底的に分析するものである。また、プロジェクト固有のコンテキストを永続化するための設定ファイル標準として注目されるAGENTS.md（一部コミュニティではAGENTES.mdとして言及）と、既存のCLAUDE.mdや.cursorrulesとの構造的差異および優先順位について詳述する。

分析の結果、これらの要素は独立した機能ではなく、AIの推論能力を最大限に引き出すための階層的な「コンテキスト・エンジニアリング・スタック」として機能していることが明らかになった。スラッシュコマンドは「手続き的（Procedural）」な操作を、@コマンドは「参照的（Referential）」なデータ注入を、そしてAGENTS.mdやスキルは「宣言的（Declarative）」な知識ベースを提供することで、確率的なLLMの挙動に決定論的な枠組みを与えている1。

## ---

**1\. イントロダクション：エージェンティック開発へのパラダイムシフト**

AIコーディングアシスタントの役割は、「副操縦士（Copilot）」から「自律的エージェント（Autonomous Agent）」へと進化している。この変化において最も重要な課題は、開発者の暗黙的な知識やプロジェクト固有の制約、そして一時的なタスクの文脈を、いかに効率的かつ正確にAIモデルのコンテキストウィンドウへ伝達するかという点にある4。

従来、この伝達は長大な「プロンプトエンジニアリング」に依存していたが、最新のツールチェーンでは、より構造化されたインターフェースが採用されている。これらは、開発者がAIに対して「何を実行すべきか（Action）」、「何を参照すべきか（Context）」、「どのようなルールに従うべきか（Constraint）」を明確に区別して指示するためのプロトコルである。

本稿では、以下の主要な構成要素を軸に、各ツールの実装と思想の違いを解明する。

1. **スラッシュコマンド (/)**: 明示的なアクションのトリガー。  
2. **@コマンド (@)**: 動的なコンテキスト注入メカニズム。  
3. **自然言語入力**: 暗黙的な意図の伝達と推論の開始。  
4. **スキル (SKILL.md)**: エージェントに付与される再利用可能な能力。  
5. **設定標準 (AGENTS.md / CLAUDE.md)**: プロジェクトの憲法となる永続的コンテキスト。

## ---

**2\. インタラクション・モダリティの深層分析**

AIエージェントとの対話は、単一のテキスト入力欄を通じて行われるが、その内部処理は入力のプレフィックス（接頭辞）によって大きく異なるパイプラインを辿る。ここでは、主要な3つのインタラクションモードについて、その技術的実装とユーザー体験への影響を分析する。

### **2.1 スラッシュコマンド (/)：決定論的制御レイヤー**

スラッシュコマンドは、IRCやSlackなどのチャットインターフェースから継承された、最も原始的かつ強力な制御メカニズムである。これはAIに対して「考える」ことではなく、「実行する」ことを指示するために使用される。

#### **2.1.1 機能的役割と決定論性**

スラッシュコマンドの最大の特徴は、その**決定論的（Deterministic）な性質**にある。通常のプロンプトがLLMによる確率的な解釈に依存するのに対し、スラッシュコマンドは通常、システム側のハードコードされた関数や、事前に定義されたスクリプトへ直接マッピングされる。これにより、開発者はセッションの管理、モードの切り替え、あるいは定型的なタスクの実行を確実に行うことができる1。

例えば、Cursorにおける/editやClaude Codeにおける/clearは、LLMの推論を介さずに（あるいは推論の方向性を強制的に固定して）即座にシステムアクションを引き起こす。

#### **2.1.2 ツール別実装の比較**

| 特徴 | Claude Code (CLI) | Cursor IDE (GUI) |
| :---- | :---- | :---- |
| **主な用途** | セッション管理、設定変更、定型プロンプトの呼び出し | エージェントモード切替、特定機能（Composer等）の起動 |
| **定義場所** | .claude/commands/\*.md | .cursor/commands/\*.md |
| **引数処理** | Bash風の変数展開 ($1, $ARGUMENTS) | プロンプト内での自然言語的な補完 |
| **実行能力** | シェルコマンドの直接実行 (\!git status) が可能 | 主にIDE機能の呼び出しやプロンプトテンプレート |
| **拡張性** | 高い（任意のMarkdownファイルをコマンド化可能） | 高い（チーム共有可能なコマンドとして定義可能） |

#### **2.1.3 カスタムコマンドのアーキテクチャ**

Claude CodeおよびCursorは、ユーザーが独自のコマンドを定義することを可能にしている。これは「プロンプトのエイリアス」以上の機能を持つ。

* **Claude Codeの場合**: .claude/commands/ディレクトリにMarkdownファイルを配置することでコマンドを作成する。ファイル名がそのままコマンド名となり（例: review.md \-\> /review）、ファイル内のフロントマター（YAML形式のメタデータ）でコマンドの説明や引数の扱いを定義する。特筆すべきは、Markdown内で\!を使用することでシェルコマンドを実行し、その出力をプロンプトに動的に埋め込める点である5。これにより、「Gitの差分を取得して要約する」といった動的なタスクを/diff-summaryのような単一コマンドで実行可能にする。  
* **Cursorの場合**: .cursor/commands/ディレクトリを使用し、同様にMarkdownベースで定義する。Cursorのカスタムコマンドは、チーム全体で共有される「再利用可能なワークフロー」としての側面が強く、コードレビューの基準や特定のテスト手順などを標準化するために用いられる7。

### **2.2 @コマンド (@)：動的コンテキスト注入レイヤー**

@コマンド（メンション）は、RAG（Retrieval-Augmented Generation）をユーザー主導で行うためのインターフェースである。これは、AIに対して「何を見るべきか」を明示的に指示するポインターとして機能する。

#### **2.2.1 コンテキストウィンドウの効率化**

LLMのコンテキストウィンドウは有限であり、トークン数にはコストがかかる。そのため、プロジェクト全体のファイルを常に読み込ませることは現実的ではない。@コマンドは、必要な情報だけを「ジャストインタイム」でコンテキストに注入することを可能にする8。

#### **2.2.2 参照の粒度と多様性**

Cursorはこの分野で最も先進的な実装を持っており、単なるファイル参照を超えた多様なシンボル解決を提供する。

* **@Files / @Folders**: ファイルやディレクトリ全体を参照する。Cursorはディレクトリ構造のサマリーを生成し、AIに全体像を把握させる機能を持つ9。  
* **@Code**: ファイル全体ではなく、特定の関数やクラス定義のみを抽出して参照する。これにより、トークン消費を抑えつつ、必要なロジックだけをAIに提示できる9。  
* **@Docs**: 外部ドキュメント（例: React, AWS, Stripe）をインデックス化し、その内容を知識ベースとして利用する。ユーザーは独自のURLを追加してカスタムドキュメントを作成することも可能である9。  
* **@Web**: インターネット検索を実行し、最新情報を取得する。  
* **@Git**: Gitのコミット履歴や差分情報をコンテキストに追加する。

一方、Claude CodeにおいてもCLIベースながら@によるファイル参照がサポートされており、タブ補完によるパス入力が可能となっている8。これは、以前のパイプ処理（cat file | claude）に代わる、より直感的なコンテキスト指定方法として定着しつつある。

### **2.3 自然言語入力（コマンドなし）：意図推論レイヤー**

プレフィックスを伴わない通常の入力は、LLMの純粋な推論能力に委ねられる領域である。しかし、最新のエージェントでは、この自然言語入力も高度な「ルーター」システムによって解析されている。

#### **2.3.1 意図の分類とツール呼び出し**

ユーザーが「このバグを直して」と入力した場合、エージェントは背後で以下のようなプロセスを実行する。

1. **意図解析**: ユーザーが求めているのはコード生成か、説明か、デバッグか。  
2. **コンテキスト検索**: 関連するファイルはどれか（自動的なRAG）。  
3. **ツール実行**: テストを実行する必要があるか、ファイルを読み込む必要があるか。

Claude CodeやCursorのエージェントモードは、自然言語の指示から自律的に必要なコマンド（grep, ls, ファイル読み込みなど）を判断し実行する能力（Function Calling/Tool Use）を持っている3。つまり、ユーザーが明示的にスラッシュコマンドを使用しなくても、AIが内部的に同等の操作を行う場合がある。この「暗黙的なコマンド実行」こそが、エージェントの自律性を定義づける要素である。

## ---

**3\. スキル（Skills）とSKILL.md：手続き的知識の標準化**

2026年初頭にかけて、Claude CodeやCursorなどの主要ツールで急速に採用が進んでいるのが「スキル（Skills）」という概念である。これは、AIに対して「何を知っているか（知識）」ではなく、「どう振る舞うべきか（手順）」を教えるためのメカニズムである5。

### **3.1 SKILL.mdの構造と役割**

スキルは通常、.claude/skills/や.cursor/skills/といったディレクトリ内に配置されたフォルダとして管理され、その中核となるのがSKILL.mdファイルである。

* **構成要素**:  
  * **フロントマター**: スキルの名称、説明、使用可能なツール（allowed-tools）、自動読み込みの可否などを定義するYAMLブロック。  
  * **手順（Instructions）**: AIがそのスキルを実行する際の具体的なステップバイステップの指示。  
  * **補助スクリプト**: スキル実行時に呼び出されるシェルスクリプトやテンプレートファイル5。

### **3.2 宣言的ルールとの違い**

従来のCLAUDE.mdや.cursorrulesが「プロジェクト全体の一般的なルール（例：インデントはスペース4つ）」を定義するのに対し、スキルは「特定のタスクを実行するための具体的な能力（例：コンポーネントのテストを作成し、実行し、エラーがあれば修正する）」を定義する12。

### **3.3 動的ディスカバリー（Dynamic Discovery）**

スキルの最大の特徴は、AIが必要に応じてそれらを**自律的に発見・ロードできる**点にある。ユーザーが「この機能をデプロイして」と指示した際、エージェントは登録されたスキルの中からdeploy-featureというスキルを見つけ出し、その定義に従って作業を開始する14。これにより、人間が全ての手順を逐一プロンプトに入力する必要がなくなり、また、コンテキストウィンドウを常時圧迫することなく高度な機能を持たせることが可能になる。

### **3.4 相互運用性**

SKILL.mdは「Agent Skills」標準としてオープンな仕様策定が進んでおり、Claude Codeで作成したスキルをCursorや他のエージェントでも（軽微な調整で）利用できるようにする動きがある5。これにより、開発者はツールごとにワークフローを再定義する手間から解放される。

## ---

**4\. コンテキスト設定ファイルとAGENTS.md：永続的ルールの標準化**

プロジェクト固有のルールや文脈をAIに共有するための設定ファイルは、現在「構成ファイル戦争（Configuration War）」とも呼べる状況にある。各ツールが独自の形式（CLAUDE.md, .cursorrules, .roomodes）を持つ中で、統一規格として浮上しているのがAGENTS.mdである。

### **4.1 AGENTS.md（およびAGENTES.md）の正体**

ユーザーのクエリに含まれるAGENTES.mdについて、調査に基づき明確化する。これは技術的には\*\*AGENTS.md\*\*（英語の複数形）が正式な標準規格であり、AGENTES.md（スペイン語やポルトガル語の複数形、あるいは単なるタイプミス）はその変種や誤記として流通しているものである16。

しかし、非英語圏のコミュニティや一部の文脈ではAGENTES.mdとして言及されることがあり、実質的にはAGENTS.mdと同じ「エージェントのためのREADME」という役割を指している。開発現場では、ツール側の互換性を考慮し、正式なAGENTS.mdを使用するか、シンボリックリンクを用いて両方に対応させることが推奨される。

### **4.2 AGENTS.mdの目的と構造**

AGENTS.mdは、人間向けのREADME.mdに対して、**AIエージェント向けのプロジェクト説明書**として設計されている。Linux Foundation傘下のAgentic AI Foundationによって管理されるオープンフォーマットである18。

#### **4.2.1 主要なセクション**

AGENTS.mdは、AIがプロジェクトを理解し、適切にコードを生成するために必要な情報を構造化して記述する。

* **\# Behaviors (振る舞い)**: エージェントに期待される行動規範（例：「既存のコードを削除する際は必ず確認すること」「コミットメッセージはConventional Commitsに従うこと」）。  
* **\# Architecture (アーキテクチャ)**: 使用している技術スタック、ディレクトリ構造の意図、デザインパターン。  
* **\# Testing (テスト)**: テストの実行コマンド、カバレッジの要件。  
* **\# Setup (セットアップ)**: 環境構築の手順（エージェントが環境を自律的に修正する場合に利用）。

#### **4.2.2 ツールの対応状況**

AGENTS.mdは特定のベンダーに依存しない標準として設計されており、複数のツールが対応を表明している。

* **Roo Code**: ネイティブサポートしており、プロジェクトルートのAGENTS.mdを自動的に読み込む20。  
* **OpenCode**: /initコマンドでAGENTS.mdを生成・利用する21。  
* **Zed Editor**: .rulesなどの独自ファイルがない場合、フォールバックとしてAGENTS.mdを読み込む18。  
* **Aider**: 設定により読み込み可能20。  
* **Cursor / Claude Code**: 現時点ではネイティブの第一候補ではないが、CLAUDE.mdや.cursorrules内から参照させるか、シンボリックリンクを作成することで利用可能である。

### **4.3 競合する設定ファイルとの比較 (CLAUDE.md vs .cursorrules)**

| ファイル名 | 対象ツール | 主な特徴 | 優先順位・挙動 |
| :---- | :---- | :---- | :---- |
| **CLAUDE.md** | Claude Code | プロジェクト構造、コマンド、スタイルを記述。ディレクトリ階層ごとのオーバーライドが可能。 | \~/.claude/CLAUDE.md (Global) \< ./CLAUDE.md (Project) 22 |
| **.cursorrules** | Cursor IDE | モデルの挙動制御に特化（「冗長な説明を省け」など）。プロンプト最適化の側面が強い。 | プロジェクトルートに配置。AIのシステムプロンプトに常時追加される。 |
| **AGENTS.md** | 汎用 (Roo, etc.) | ツール非依存の標準規格。プロジェクトの「知識」と「ルール」を分離して記述することを推奨。 | 対応ツールでは自動読み込み。未対応ツールでも参照ファイルとして利用可能。 |

現在、多くの開発者はツールのロックイン（特定のツールに依存すること）を避けるため、プロジェクトの核心的なルールをAGENTS.mdに記述し、各ツールの独自設定ファイル（.cursorrules等）からはAGENTS.mdを参照するように構成する「階層的設定戦略」を採用し始めている23。

## ---

**5\. 比較と統合：最適なワークフローの構築**

これまでに解説した各要素は、排他的なものではなく、相互に補完し合う関係にある。以下の表は、それぞれの機能領域を整理したものである。

### **5.1 機能マトリクス比較**

| 機能カテゴリ | コマンド / 要素 | 主な役割 | データの流れ |
| :---- | :---- | :---- | :---- |
| **実行制御** | **スラッシュコマンド (/)** | 「今すぐこれを実行せよ」。マクロ、設定変更、定型タスクの起動。 | ユーザー → システム/スクリプト |
| **文脈参照** | **@コマンド (@)** | 「これを見て考えよ」。ファイル、ドキュメント、Web情報の動的注入。 | データソース → LLMコンテキスト |
| **意図伝達** | **自然言語 (Prefixなし)** | 「これを達成せよ」。複雑な推論、計画立案、自律的なツール使用。 | ユーザー → LLM推論エンジン |
| **手順知識** | **スキル (SKILL.md)** | 「この手順で実行せよ」。特定のタスク（デプロイ、テスト作成）の標準化。 | スキル定義 → エージェント実行計画 |
| **永続ルール** | **AGENTS.md / CLAUDE.md** | 「このルールに従え」。コーディング規約、アーキテクチャの制約。 | プロジェクト設定 → システムプロンプト |

### **5.2 統合的な開発ワークフローの例**

現代的なAI開発フローでは、これらの要素が以下のように組み合わされる。

1. **環境設定**: プロジェクトルートに\*\*AGENTS.md\*\*を配置し、コーディング規約（TypeScriptの使用、エラー処理の方針など）を定義する。  
2. **タスク開始**: ユーザーは**自然言語**で「認証機能のリファクタリングをして」と指示する。  
3. **コンテキスト注入**: 指示の中で「\*\*@auth.ts**と**@UserSchema\*\*を参照して」と加え、必要な情報を明示的に与える。  
4. **スキル活用**: エージェントは内部的にリファクタリングの手順を知るために、登録された\*\*スキル（/refactor-guideなど）\*\*を参照し、安全な手順（テスト作成→変更→テスト実行）に従う。  
5. **コマンド実行**: エージェントは必要に応じて**スラッシュコマンド**（CLIツール経由の\!git commitなど）を実行し、作業を完了させる。

## ---

**6\. 結論：コンテキスト・エンジニアリングの時代へ**

本レポートの分析から、AI開発ツールの進化は、単なる「チャットボットの高性能化」ではなく、「コンテキスト・エンジニアリング（Context Engineering）」という新たな領域の確立に向かっていることがわかる。

* **スラッシュコマンド**と\*\*@コマンド\*\*は、人間がAIに対してコンテキストを動的に制御するための「ハンドル」と「アクセル」である。  
* **スキル**と\*\*AGENTS.md\*\*は、AIが自律的に動くための「地図」と「交通ルール」である。

特にAGENTS.md（およびそのバリエーションとしてのAGENTES.md）の登場は、AIエージェントを特定のIDEから切り離し、どのような環境でも一貫したパフォーマンスを発揮させるための重要な一歩である。開発者は、特定のツールの機能（ClaudeのCLIコマンドやCursorのタブ補完）に精通するだけでなく、これらの標準化されたプロトコルを用いて、自身のプロジェクトを「AIフレンドリー」な構造へと最適化していくことが求められる。

今後は、ツール間の壁がさらに低くなり、SKILL.mdやAGENTS.mdによって定義された能力と知識が、あらゆるAIエージェントで共有・実行可能になる「相互運用性（Interoperability）」の時代が到来すると予測される。開発組織にとっては、これらの資産を整備することが、AIによる生産性向上を最大化するための最も確実な投資となるだろう。

#### **引用文献**

1. Slash Commands in the SDK \- Claude API Docs, 2月 11, 2026にアクセス、 [https://platform.claude.com/docs/en/agent-sdk/slash-commands](https://platform.claude.com/docs/en/agent-sdk/slash-commands)  
2. Slash commands | Cursor Docs, 2月 11, 2026にアクセス、 [https://cursor.com/docs/cli/reference/slash-commands](https://cursor.com/docs/cli/reference/slash-commands)  
3. Cursor vs Claude Code: Ultimate Comparison Guide \- Builder.io, 2月 11, 2026にアクセス、 [https://www.builder.io/blog/cursor-vs-claude-code](https://www.builder.io/blog/cursor-vs-claude-code)  
4. Effective context engineering for AI agents \- Anthropic, 2月 11, 2026にアクセス、 [https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)  
5. Extend Claude with skills \- Claude Code Docs, 2月 11, 2026にアクセス、 [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)  
6. How to Create Custom Slash Commands in Claude Code \- BioErrorLog Tech Blog, 2月 11, 2026にアクセス、 [https://en.bioerrorlog.work/entry/claude-code-custom-slash-command](https://en.bioerrorlog.work/entry/claude-code-custom-slash-command)  
7. Commands | Cursor Docs, 2月 11, 2026にアクセス、 [https://cursor.com/docs/context/commands](https://cursor.com/docs/context/commands)  
8. Referencing Files and Resources in Claude Code | Developing with AI Tools | Steve Kinney, 2月 11, 2026にアクセス、 [https://stevekinney.com/courses/ai-development/referencing-files-in-claude-code](https://stevekinney.com/courses/ai-development/referencing-files-in-claude-code)  
9. @ Mentions | Cursor Docs, 2月 11, 2026にアクセス、 [https://cursor.com/docs/context/mentions](https://cursor.com/docs/context/mentions)  
10. Best practices for coding with agents \- Cursor, 2月 11, 2026にアクセス、 [https://cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)  
11. Subagents, Skills, and Image Generation \- Cursor, 2月 11, 2026にアクセス、 [https://cursor.com/changelog/2-4](https://cursor.com/changelog/2-4)  
12. Agent Skills Vs MCP Vs Prompts Vs Projects Vs Subagents :A Comparative Analysis | by Tahir | Jan, 2026, 2月 11, 2026にアクセス、 [https://medium.com/@tahirbalarabe2/agent-skills-vs-mcp-vs-prompts-vs-projects-vs-subagents-a-comparative-analysis-7a36cd85cb74](https://medium.com/@tahirbalarabe2/agent-skills-vs-mcp-vs-prompts-vs-projects-vs-subagents-a-comparative-analysis-7a36cd85cb74)  
13. The Complete Guide to Building Skills for Claude | Anthropic, 2月 11, 2026にアクセス、 [https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en)  
14. Cursor · Changelog, 2月 11, 2026にアクセス、 [https://cursor.com/changelog](https://cursor.com/changelog)  
15. Claude Code Skills & skills.sh \- Crash Course, 2月 11, 2026にアクセス、 [https://www.youtube.com/watch?v=rcRS8-7OgBo](https://www.youtube.com/watch?v=rcRS8-7OgBo)  
16. Códice de OpenAI: Una guía con 3 ejemplos prácticos \- DataCamp, 2月 11, 2026にアクセス、 [https://www.datacamp.com/es/tutorial/openai-codex](https://www.datacamp.com/es/tutorial/openai-codex)  
17. ¿Qué es AGENTS.md? \- HackerNoon, 2月 11, 2026にアクセス、 [https://hackernoon.com/lang/es/que-es-agentsmd](https://hackernoon.com/lang/es/que-es-agentsmd)  
18. AGENTS.md, 2月 11, 2026にアクセス、 [https://agents.md/](https://agents.md/)  
19. AGENTS.md — a simple, open format for guiding coding agents \- GitHub, 2月 11, 2026にアクセス、 [https://github.com/agentsmd/agents.md](https://github.com/agentsmd/agents.md)  
20. Add Support for Agent Rules Standard via Project Root AGENTS.md for Unified Natural Language Guidelines · Issue \#5966 · RooCodeInc/Roo-Code \- GitHub, 2月 11, 2026にアクセス、 [https://github.com/RooCodeInc/Roo-Code/issues/5966](https://github.com/RooCodeInc/Roo-Code/issues/5966)  
21. Consensus on using actual cursor rules \`.mdc\` vs \`./docs/\*.md\` files : r/cursor \- Reddit, 2月 11, 2026にアクセス、 [https://www.reddit.com/r/cursor/comments/1qjekug/consensus\_on\_using\_actual\_cursor\_rules\_mdc\_vs/](https://www.reddit.com/r/cursor/comments/1qjekug/consensus_on_using_actual_cursor_rules_mdc_vs/)  
22. Claude Code CLI Cheatsheet: config, commands, prompts, \+ best practices \- Shipyard.build, 2月 11, 2026にアクセス、 [https://shipyard.build/blog/claude-code-cheat-sheet/](https://shipyard.build/blog/claude-code-cheat-sheet/)  
23. Rules | Cursor Docs, 2月 11, 2026にアクセス、 [https://cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)  
24. awesome-cursor-rules-mdc/cursor-rules-reference.md at main \- GitHub, 2月 11, 2026にアクセス、 [https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/cursor-rules-reference.md](https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/cursor-rules-reference.md)