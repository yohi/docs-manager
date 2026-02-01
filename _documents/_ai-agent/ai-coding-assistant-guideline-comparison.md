

# **現代AIコーディングアシスタントにおけるガイドライン設定の比較分析**

## **エグゼクティブサマリー**

AIコーディングツールが開発ワークフローに不可欠な要素となる中で、その真価は単なるコード生成能力だけでなく、プロジェクト固有の文脈や規約を理解し、それに準拠する能力にかかっています。本レポートでは、主要な5つのAIコーディングアシスタント（VSCode/Copilot、Cursor、ClaudeCode、Codex、Gemini CLI）における、コーディング規約などのガイドラインを設定するための永続的なコンテキスト管理手法を徹底的に比較分析します。

分析の結果、業界全体として、バージョン管理下に置かれるファイルベースの設定（リポジトリ内の.mdファイル）がデファクトスタンダードとして収斂しつつあることが明らかになりました。これは、AIへの指示をコードと同様に扱い、チーム全体で共有・レビューするという思想の現れです。一方で、各ツールの設定思想には明確な違いが存在します。VSCodeの柔軟な階層型システム、Cursorのエンタープライズ向け強制力のあるガバナンスモデル、ClaudeCodeの開発者体験を重視したエレガントなメモリ階層、そしてGemini CLIのターミナル中心の動的なコンテキスト管理は、それぞれ異なるターゲット市場と戦略的ビジョンを反映しています。これらの差異は、組織がAIツールを選定する上で、単なる機能比較以上に重要な判断基準となります。

---

## **第I部：設定パラダイムの深掘り**

### **第1章：はじめに \- 指示可能なAIの必要性**

初期のAIコーディングアシスタントは、対話のたびに記憶を失う「健忘症」の問題を抱えていました。開発者は、コーディング規約、アーキテクチャパターン、利用ライブラリといった文脈を、対話のたびに繰り返し説明する必要がありました 1。この非効率性は、AIを単なる便利なツールから真の協力的なパートナーへと昇華させる上での大きな障壁でした。

この課題を解決するために、AIへの指示方法は、チャットウィンドウ内でのその場限りのプロンプトエンジニアリングから、構造化され、永続的で、共有可能な設定ファイルへと進化しました。本レポートでは、この「永続的なコンテキスト」という概念を軸に、5つの主要ツールを以下の基準で分析します：設定方法、適用範囲（スコープ）、永続性、チームでの共有方法、そして規約の強制力。

### **第2章：VSCode (GitHub Copilot) — 柔軟な多層エコシステム**

VSCodeに統合されたGitHub Copilotは、単一のシンプルな設定ファイルから始まり、AIの能力拡張に合わせて多層的で詳細な設定体系へと進化してきました。これは、Copilotが単なるコード補完機能から、複雑なワークフローをこなすプラットフォームへと成熟したことを示しています。

#### **2.1. 基礎：.github/copilot-instructions.md**

Copilotにカスタム指示を与える最も基本的かつ主要な方法は、ワークスペースのルートに.github/copilot-instructions.mdというMarkdownファイルを配置することです 2。このファイルに記述された内容は、ワークスペース内のすべてのCopilot Chatリクエストに自動的に適用されます 5。

このアプローチの強みは、そのシンプルさと発見可能性にあります。.githubディレクトリは、GitHubにおけるコミュニティ向けの標準的な規約ファイルを置く場所であり、開発者にとって自然な選択です 6。ファイルには、プロジェクトの概要、使用されている技術スタック、そして具体的なコーディング規約（例：変数名はcamelCase、文字列はシングルクォートを使用するなど）を記述することが推奨されています 5。これにより、このファイルはAIをプロジェクトに「オンボーディング」するための包括的なドキュメントとして機能します。

#### **2.2. 詳細な制御：.instructions.mdとapplyToによるスコープ設定**

単一の包括的な指示ファイルだけでなく、より詳細な制御も可能です。VSCodeは、複数の.instructions.mdファイルの使用をサポートしており、特定のファイルタイプやタスクにのみ指示を適用できます 2。

これを実現するのが、ファイル冒頭のメタデータに記述するapplyToプロパティです。ここにはglobパターン（例："\*\*/\*.ts"）を指定し、特定のファイル群にのみ指示を適用させることができます 2。これは、複数の言語やフレームワークが混在するモノレポ構成のプロジェクトで特に強力です。

指示ファイルは2種類に大別されます：

* **ワークスペース指示ファイル**：.github/instructionsフォルダに保存され、そのワークスペース内でのみ有効です 2。  
* **ユーザー指示ファイル**：VS Codeのプロファイル内に保存され、すべてのプロジェクトで横断的に利用できます。個人の好みを設定するのに適しており、Settings Sync機能でデバイス間の同期も可能です 2。

#### **2.3. エージェント中心アプローチの台頭：AGENTS.mdの役割**

AGENTS.mdは、Copilotだけでなく、ワークスペース内で利用される「すべてのAIエージェント」に対する共通の指示ファイルとして構想されています 2。これは、MicrosoftがVSCodeを単なるCopilotのホストではなく、複数のAIエージェントが共存するプラットフォームとして捉えていることを示唆しています。さらに、ネストされたAGENTS.mdファイルをサポートする実験的な設定（chat.useNestedAgentsMdFiles）もあり、これによりディレクトリ単位でのより詳細な指示が可能になります 2。

#### **2.4. 特殊タスク：settings.jsonによる設定**

コミットメッセージの自動生成（github.copilot.chat.commitMessageGeneration.instructions）やコードレビューといった特定のタスクの振る舞いは、VS Codeのsettings.jsonファイルで直接カスタマイズできます 2。これにより、一般的なコーディングの文脈はMarkdownファイルに、ツール固有の振る舞いの調整はJSON設定ファイルに、という関心の分離が図られています。

#### **2.5. チームでの共有とワークフロー**

チームで指示を共有する主要なメカニズムは、Gitによるバージョン管理です。.githubディレクトリをリポジトリにコミットすることで、チームメンバー全員が同じAIコンテキストを継承し、AIへの指示をコードとして扱うことができます 2。また、Copilot Chatの/generate instructionsコマンドを使えば、プロジェクトを分析して初期のcopilot-instructions.mdファイルを自動生成することも可能です 2。

### **第3章：Cursor IDE — エンタープライズ級のガバナンスモデル**

Cursor IDEは、開発者個人の生産性向上だけでなく、組織全体のコード品質と一貫性を担保するための、強力なガバナンス機能を備えています。その中核をなすのが、階層化されたルールシステムです。

#### **3.1. コアシステム：プロジェクトルール (.cursor/rules/\*.mdc)**

Cursorのルールシステムは、.cursor/rulesディレクトリ内に個別の.mdc（メタデータ付きMarkdown）ファイルとしてルールを保存します 9。これにより、ルールはモジュール化され、バージョン管理の対象となります。

ルールの適用方法は、メタデータによって4種類に分類されます。これにより、コンテキストウィンドウのトークン使用量を最適化しつつ、必要な情報を的確にAIに提供できます 9。

* **Always**: 常に適用される。  
* **Auto Attached**: globsで指定されたファイルパターンに一致するファイルがコンテキストに含まれる場合に自動で適用される。  
* **Agent Requested**: descriptionを基に、AIエージェントが必要と判断した場合に適用される。  
* **Manual**: @ruleNameのように、ユーザーがチャットで明示的に呼び出した場合にのみ適用される。

#### **3.2. 最大の差別化要因：チームルールと中央集権的な強制**

Cursorを他のツールと一線を画すのが**チームルール**機能です 10。これはリポジトリ内ではなく、管理者が中央のWebダッシュボードから設定するルールです。

最も重要な点は、\*\*Enforce this rule（このルールを強制する）\*\*というオプションです 10。これを有効にすると、ルールは全チームメンバーにプッシュされ、個人が設定で無効にすることはできません。これにより、コーディング規約は単なる「推奨」から「必須のコンプライアンス」へと昇格します。この機能は、開発者の利便性向上というよりも、組織的な標準、セキュリティ、コンプライアンスを大規模に確保することを目的としており、Cursorがエンタープライズ市場を強く意識していることを示しています。Gitによるルール共有では開発者がローカルでルールを無効化できてしまいますが、この強制機能はその抜け道を塞ぎます。これは、金融や医療など、規制の厳しい業界にとって不可欠な要件に応えるものです。

#### **3.3. パーソナライズと簡素化：ユーザールールとAGENTS.md**

個人設定として、UIからプレーンテキストでグローバルな設定を行える**ユーザールール**も存在します 9。また、Cursorは業界標準となりつつあるAGENTS.mdもサポートしており、複雑なメタデータなしでシンプルな指示を定義する代替手段として利用できます 10。

#### **3.4. ルールの優先順位とワークフロー**

ルールの適用には厳格な優先順位が存在します：**チームルール → プロジェクトルール → ユーザールール** 10。これにより、組織全体のポリシーが常にプロジェクトや個人の設定を上書きすることが保証されます。また、/Generate Cursor Rulesコマンドを使えば、成功した対話の内容を再利用可能なルールとして保存でき、強力なフィードバックループを形成します 9。

### **第4章：ClaudeCode — エレガントな「メモリ」階層**

ClaudeCodeは、「メモリ」という概念を中心に、非常に洗練されたコンテキスト管理システムを構築しています。このアプローチは、開発者の思考プロセスを巧みに模倣しており、優れた開発者体験（DevEx）を提供します。

#### **4.1. 「メモリ」パラダイム**

ClaudeCodeのコンテキスト管理は、CLAUDE.mdという名前のMarkdownファイル群によって行われます。これらが永続的な階層型メモリシステムとして機能します 1。

#### **4.2. 3層のコンテキストアーキテクチャ**

ClaudeCodeのメモリシステムは、開発者の頭の中にある3つの異なるレベルのルール（チームの規約、個人の好み、一時的な設定）をファイルシステム上に再現しています。この設計思想は、ツールの挙動をユーザーの既存のメンタルモデルに合わせることで、認知的な負荷を軽減します。

* **プロジェクトメモリ (./CLAUDE.md)**: チームで共有される「脳」であり、バージョン管理されます。アーキテクチャの決定事項やチーム共通のコーディング規約をここに記述します 1。  
* **ユーザーメモリ (\~/.claude/CLAUDE.md)**: すべてのプロジェクトに適用される、グローバルな個人設定です。コミットメッセージのスタイルやリンターの好みなどを保存します 1。  
* **ローカルプロジェクトメモリ (./CLAUDE.local.md)**: プロジェクト固有の個人設定で、.gitignoreされます。ローカルのAPIキーやデバッグフラグなど、一時的な設定に最適です。（注：この機能は、ユーザーファイルからのインポートを推奨する形で非推奨となっています 13）

#### **4.3. インテリジェントなコンテキスト読み込み**

Claudeは、カレントディレクトリから親ディレクトリに向かって再帰的にCLAUDE.mdファイルを検索し、見つかったすべてのファイルを読み込みます 1。これにより、より具体的な（下層の）指示が一般的な（上層の）指示を上書きする階層構造が実現されます。

さらに、@path/to/fileという構文によるファイルのインポート機能をサポートしています 1。これは、メインのCLAUDE.mdを簡潔に保ちつつ、詳細な仕様（テストガイドラインなど）をモジュール化して管理するための重要な機能であり、トークン消費の抑制にも貢献します。

#### **4.4. ワークフローと管理**

対話型インターフェースからメモリを直接操作できるコマンドが用意されています。

* /init: コードベースを分析し、プロジェクトの初期CLAUDE.mdを自動生成します 1。  
* \#: プロンプトの先頭に付けることで、その内容をメモリファイルに素早く追記できます 1。  
* /memory: メモリファイルを直接エディタで開きます 13。

### **第5章：OpenAI Codex — 基礎となるAPIファーストアプローチ**

OpenAI Codexは、特定のIDEに統合されたツールではなく、AIコーディング機能の基礎となるAPIです。そのため、ファイルベースの設定システムは提供されておらず、すべてのガイドライン指示はAPI呼び出し時のプロンプトエンジニアリングによって行われます。

#### **5.1. ファイルではなく、すべてがプロンプト**

Codex API自体はステートレスであり、永続的な設定ファイルを持ちません 14。ガイドラインの指示は、APIリクエストの一部として送信されるプロンプトによって行われます。

#### **5.2. systemメッセージとinstructionsパラメータ**

APIを通じてコーディング規約を渡す方法は、使用するAPIによって異なります。

* **Chat Completions API**: messages配列の中にrole: "system"（またはrole: "developer"）を持つオブジェクトとして指示を含めます 15。  
* **Responses API**: より新しいこのAPIでは、instructionsという専用のパラメータが用意されており、ここに記述された指示はメインの入力よりも優先されます 17。

効果的な指示を行うために、\<code\_editing\_rules\>のようなXMLタグを用いてプロンプトを構造化するテクニックが推奨されています 18。

#### **5.3. 永続性の責務**

Codex APIは対話間の状態を保持しないため、これらの指示を管理・保存し、API呼び出しのたびに注入する責務は、すべてAPIを呼び出す側のアプリケーションにあります 14。これは、VSCodeやCursorのようなツールが内部的に行っている処理を、開発者が自ら実装することを意味します。このトレードオフにより、最大限の柔軟性が得られます。例えば、ルールをMarkdownファイルではなく、データベースやConfluenceから動的に取得するようなカスタムシステムを構築することが可能です。

#### **5.4. プロンプトベースのガイドラインにおけるベストプラクティス**

OpenAIは、効果的なプロンプトを作成するためのベストプラクティスをいくつか提示しています。具体的には、指示を明確かつ具体的にすること、 few-shot（少数例示）で手本を示すこと、望ましい出力形式を明示すること、そして指示をプロンプトの冒頭に配置することなどが挙げられます 19。

### **第6章：Gemini CLI — ターミナルネイティブな階層モデル**

Gemini CLIは、ターミナルでの開発体験を重視したAIエージェントであり、その設定思想もコマンドラインワークフローに深く根差しています。

#### **6.1. GEMINI.mdコンテキストファイル**

永続的な指示を与える主要なメカニズムはGEMINI.mdファイルです 20。このファイルの読み込みは階層的であり、ClaudeCodeと同様に、グローバル（\~/.gemini/GEMINI.md）、プロジェクト（カレントディレクトリから親へ検索）、サブディレクトリの各スコープからコンテキストを結合します 21。

#### **6.2. 設定のためのツールチェーン**

Gemini CLIの際立った特徴は、設定ワークフローをサポートする豊富なコマンド群です。これにより、設定は単に編集する静的なファイルではなく、対話セッションの中で動的に管理・調査できる対象となります。

* /init: プロジェクトを分析し、GEMINI.mdの雛形を自動生成します 21。  
* /memory show: 読み込まれたすべてのGEMINI.mdファイルから結合された最終的なコンテキストを表示します。これにより、どのルールが有効になっているかを正確に把握でき、デバッグが容易になります 20。  
* /memory refresh: セッションを再起動することなく、コンテキストファイルを再読み込みします 21。

#### **6.3. 高度な設定：settings.jsonとGitHub連携**

より低レベルな設定（MCPサーバーの定義や認証方法など）は、\~/.gemini/settings.jsonで行います 20。また、GitHubでのコードレビューに特化した設定として、.gemini/styleguide.mdや.gemini/config.yamlといったファイルが使用される場合もあり、特定の統合機能に対して専用の設定パスが用意されていることがわかります 25。

---

## **第II部：統合的考察と戦略的提言**

### **第7章：比較分析**

ここまでの詳細な分析を基に、5つのツールを横断的に比較し、そのアーキテクチャ思想と市場における位置付けを明らかにします。

#### **7.1. 機能比較マトリクス**

以下の表は、各ツールのガイドライン設定機能を主要な側面から要約したものです。これにより、各ツールの特性と違いが一目でわかります。

| 機能 | VSCode (Copilot) | Cursor IDE | ClaudeCode | OpenAI Codex (API) | Gemini CLI |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **主要な設定方法** | ファイルベース | ファイルベース & UIダッシュボード | ファイルベース | APIベース（プロンプトエンジニアリング） | ファイルベース |
| **主要なファイル名** | .github/copilot-instructions.md, \*.instructions.md, AGENTS.md | .cursor/rules/\*.mdc, AGENTS.md | CLAUDE.md, CLAUDE.local.md | N/A | GEMINI.md, .gemini/styleguide.md |
| **フォーマット** | Markdown | MDC（YAMLメタデータ付きMarkdown）、プレーンテキスト | Markdown | JSON（APIコール用） | Markdown |
| **スコープのレベル** | ユーザー、ワークスペース、ファイル固有 | ユーザー、プロジェクト、チーム（グローバル） | ユーザー、プロジェクト、ローカルプロジェクト | アプリケーションが定義 | グローバル、プロジェクト、サブディレクトリ |
| **チームでの共有** | バージョン管理（Git） | バージョン管理 & 中央ダッシュボード | バージョン管理（Git） | カスタム実装 | バージョン管理（Git） |
| **強制力** | なし（規約ベース） | **あり**（管理者によるチームルールの強制） | なし（規約ベース） | アプリケーションが定義 | なし（規約ベース） |
| **主要な差別化要因** | 最も普及したIDEに統合された、柔軟で多層的なシステム。 | **エンタープライズチーム向けの中央集権的で強制力のあるガバナンス。** | 開発者のメンタルモデルを反映したエレガントな階層構造。 | カスタムツール開発者向けの最大限の柔軟性。 | コンテキストを管理するための強力なCLIツール群（/init, /memory show）。 |

#### **7.2. アーキテクチャ思想：コントロールのスペクトラム**

各ツールの設定アプローチは、開発者の自律性と組織の統制という二つの軸の間で、異なる思想を反映しています。

* **開発者中心・協調型 (VSCode, Claude, Gemini)**: これらのツールは、ガイドラインをコードベースの一部として扱います。Gitを通じて共有され、プルリクエストで議論され、チームの規律に依存します。これは、開発者に権限を与えるボトムアップ型の協調モデルです。  
* **エンタープライズガバナンス・コンプライアンス型 (Cursor)**: このツールは、トップダウンの統制レイヤーを導入します。セキュリティ、法務、または一貫性の理由から標準を強制する必要がある組織向けに設計されています。  
* **基礎となるツールキット型 (Codex)**: これは「Bring Your Own Architecture（自前のアーキテクチャを持ち込む）」モデルであり、永続化レイヤー全体を自ら構築する意欲のある開発者に対して、究極のパワーを提供します。

#### **7.3. 必然的な標準規格：AGENTS.md**

VSCode、Cursor、Geminiといった複数の競合ツールが、すべてAGENTS.mdのサポートを追加しているという事実は注目に値します 10。これは、市場が相互運用性を求めていることの現れです。開発者が複数の特化したAIエージェントを使い分けるようになると、ツールごとに設定ファイルを維持する手間は耐え難いものになります。AGENTS.mdは、AIエージェントにおける.editorconfigやDockerfileのような、シンプルで普遍的な標準規格となる可能性を秘めています。これは、AIエコシステムが成熟し、ツールが独自の構成フォーマットではなく、独自の機能（Cursorの強制力など）で競争しなければならない段階に入ったことを示唆しています。

### **第8章：導入に向けた戦略的提言**

#### **8.1. 組織に最適な設定モデルの選択**

* **大企業および規制産業向け**: **Cursor IDE**を推奨します。中央管理ダッシュボードと強制力のあるチームルールは、大規模な組織でコンプライアンスとセキュリティを確保するために不可欠です 10。  
* **オープンソースプロジェクトおよび協調型チーム向け**: **VSCode (Copilot)** または **Gemini CLI**を推奨します。バージョン管理されたファイル（.github/、GEMINI.md）への依存は、透明性の高いコミュニティ主導の開発ワークフローに完全に適合します 2。  
* **開発者体験を最優先するチーム向け**: **ClaudeCode**を推奨します。その直感的な3層のメモリシステムは、卓越した設計であり、開発者の認知的な負荷を軽減します 1。  
* **カスタム開発者プラットフォームを構築する企業向け**: **OpenAI Codex API**を推奨します。独自のツールチェーンにAIを深く統合し、永続化レイヤーを構築するエンジニアリングリソースがある場合、これが唯一の選択肢です 14。

#### **8.2. 効果的なガイドラインファイルを作成するためのベストプラクティス**

* **具体的かつ実行可能に**: 「良いコードを書く」ではなく、「関数型コンポーネントを使用する」のように、具体的で行動可能な指示を記述します 9。  
* **具体例を提供する (Few-Shot)**: 優れたコンポーネントやコミットメッセージがどのようなものか、AIに具体的に示します 6。  
* **見出しで構造化する**: Markdownの見出しを使い、ルールをトピックごと（例：\#\# 命名規則、\#\# テスト戦略）に整理します 5。  
* **簡潔に保つ**: これらのファイルは貴重なコンテキストウィンドウのトークンを消費することを念頭に置き、簡潔に記述し、古いルールは定期的に削除します 6。  
* **自動生成と反復**: /init (Gemini/Claude) や /Generate Cursor Rules といったコマンドで雛形を作成し、AIのパフォーマンスに基づいてルールを継続的に改善します 9。

## **結論**

AIに効果的に指示を与え、永続的なコンテキストを提供する能力は、目新しいAIツールとプロフェッショナルグレードの開発パートナーとを分ける主要な要因です。本レポートで明らかになったように、ツール選定における重要なトレードオフは、柔軟性と統制、開発者の自律性とエンタープライズガバナンスの間に存在します。

今後は、AGENTS.mdのような標準規格の重要性がさらに高まるでしょう。これにより、AIは単なるツールではなく、プロジェクトの文脈を完全に理解し、「オンボーディング」されたチームの一員として、人間との協調作業を新たなレベルへと引き上げることが期待されます。

#### **引用文献**

1. Claude Code's Memory: Working with AI in Large Codebases | by ..., 10月 25, 2025にアクセス、 [https://medium.com/@tl\_99311/claude-codes-memory-working-with-ai-in-large-codebases-a948f66c2d7e](https://medium.com/@tl_99311/claude-codes-memory-working-with-ai-in-large-codebases-a948f66c2d7e)  
2. Use custom instructions in VS Code \- Visual Studio Code, 10月 25, 2025にアクセス、 [https://code.visualstudio.com/docs/copilot/customization/custom-instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)  
3. Get started with GitHub Copilot in VS Code, 10月 25, 2025にアクセス、 [https://code.visualstudio.com/docs/copilot/getting-started](https://code.visualstudio.com/docs/copilot/getting-started)  
4. GitHub Copilotにカスタムインストラクションで最新技術や独自ルールを教え込む \- Zenn, 10月 25, 2025にアクセス、 [https://zenn.dev/microsoft/articles/github-copilot-custom-instructions](https://zenn.dev/microsoft/articles/github-copilot-custom-instructions)  
5. Context is all you need: Better AI results with custom instructions \- Visual Studio Code, 10月 25, 2025にアクセス、 [https://code.visualstudio.com/blogs/2025/03/26/custom-instructions](https://code.visualstudio.com/blogs/2025/03/26/custom-instructions)  
6. 5 tips for writing better custom instructions for Copilot \- The GitHub Blog, 10月 25, 2025にアクセス、 [https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/)  
7. Customize chat responses \- Visual Studio (Windows) | Microsoft Learn, 10月 25, 2025にアクセス、 [https://learn.microsoft.com/en-us/visualstudio/ide/copilot-chat-context?view=vs-2022](https://learn.microsoft.com/en-us/visualstudio/ide/copilot-chat-context?view=vs-2022)  
8. GitHub Copilot Custom Chat Modesで独自エージェントを作成 \- JBS Tech Blog, 10月 25, 2025にアクセス、 [https://blog.jbs.co.jp/entry/2025/09/17/145028](https://blog.jbs.co.jp/entry/2025/09/17/145028)  
9. Awesome Cursor Rules You Can Setup for Your Cursor AI IDE Now \- Apidog, 10月 25, 2025にアクセス、 [https://apidog.com/blog/awesome-cursor-rules/](https://apidog.com/blog/awesome-cursor-rules/)  
10. Rules | Cursor Docs, 10月 25, 2025にアクセス、 [https://cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)  
11. ルール \- Cursor, 10月 25, 2025にアクセス、 [https://docs.cursor.com/ja/context/rules](https://docs.cursor.com/ja/context/rules)  
12. Claude Code: Part 2 \- CLAUDE.md Configuration Files \- Luiz Tanure, 10月 25, 2025にアクセス、 [https://www.letanure.dev/blog/2025-07-31--claude-code-part-2-claude-md-configuration](https://www.letanure.dev/blog/2025-07-31--claude-code-part-2-claude-md-configuration)  
13. Manage Claude's memory, 10月 25, 2025にアクセス、 [https://docs.claude.com/en/docs/claude-code/memory](https://docs.claude.com/en/docs/claude-code/memory)  
14. How to get Codex to produce the code you want\! | Prompt Engineering, 10月 25, 2025にアクセス、 [https://microsoft.github.io/prompt-engineering/](https://microsoft.github.io/prompt-engineering/)  
15. OpenAI API Coding in Python Cheatsheet \- Codecademy, 10月 25, 2025にアクセス、 [https://www.codecademy.com/learn/open-ai-api-coding-with-python/modules/open-ai-api-coding-in-python/cheatsheet](https://www.codecademy.com/learn/open-ai-api-coding-with-python/modules/open-ai-api-coding-in-python/cheatsheet)  
16. Work with chat completion models \- Azure OpenAI in Azure AI Foundry Models | Microsoft Learn, 10月 25, 2025にアクセス、 [https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/chatgpt](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/chatgpt)  
17. Text generation \- OpenAI API, 10月 25, 2025にアクセス、 [https://platform.openai.com/docs/guides/text](https://platform.openai.com/docs/guides/text)  
18. GPT-5 prompting guide | OpenAI Cookbook, 10月 25, 2025にアクセス、 [https://cookbook.openai.com/examples/gpt-5/gpt-5\_prompting\_guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)  
19. Best practices for prompt engineering with the OpenAI API, 10月 25, 2025にアクセス、 [https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api)  
20. Hands-on with Gemini CLI \- Google Codelabs, 10月 25, 2025にアクセス、 [https://codelabs.developers.google.com/gemini-cli-hands-on](https://codelabs.developers.google.com/gemini-cli-hands-on)  
21. Google Gemini CLI Cheatsheet \- Philschmid, 10月 25, 2025にアクセス、 [https://www.philschmid.de/gemini-cli-cheatsheet](https://www.philschmid.de/gemini-cli-cheatsheet)  
22. Gemini CLI with GEMINI.md \- sample, example and best practices., 10月 25, 2025にアクセス、 [https://blog.saif71.com/gemini-cli-and-gemini/](https://blog.saif71.com/gemini-cli-and-gemini/)  
23. Use the Gemini Code Assist agent mode \- Google for Developers, 10月 25, 2025にアクセス、 [https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer](https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer)  
24. This Week in Gemini CLI. 3 features you NEED to be aware of that ..., 10月 25, 2025にアクセス、 [https://medium.com/google-cloud/hot-new-features-of-the-week-in-gemini-cli-d7cda5cb9833](https://medium.com/google-cloud/hot-new-features-of-the-week-in-gemini-cli-d7cda5cb9833)  
25. Customize Gemini Code Assist behavior in GitHub \- Google for Developers, 10月 25, 2025にアクセス、 [https://developers.google.com/gemini-code-assist/docs/customize-gemini-behavior-github](https://developers.google.com/gemini-code-assist/docs/customize-gemini-behavior-github)  
26. Improve your AI code output with AGENTS.md (+ my best tips) \- Builder.io, 10月 25, 2025にアクセス、 [https://www.builder.io/blog/agents-md](https://www.builder.io/blog/agents-md)  
27. AGENTS.md, 10月 25, 2025にアクセス、 [https://agents.md/](https://agents.md/)
