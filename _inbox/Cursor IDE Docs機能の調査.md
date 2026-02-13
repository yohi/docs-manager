# **Cursor IDEにおける「Docs機能」の包括的技術仕様および運用分析レポート**

## **1\. 序論：AIネイティブ開発環境におけるコンテキスト管理の進化**

現代のソフトウェアエンジニアリングにおいて、開発者が扱うべき情報の総量は指数関数的に増大している。フレームワークの更新頻度は加速し、ライブラリのAPIは数ヶ月単位で非推奨となり、新しいベストプラクティスが次々と提唱される現状において、個人のエンジニアがすべての仕様を脳内に保持することは不可能に近い。これまでの統合開発環境（IDE）は、静的解析によるコード補完や定義へのジャンプといった機能で開発者を支援してきたが、これらはあくまで「既存のコードベース」や「インストール済みの型定義」という閉じた世界の中での支援に留まっていた。

AIネイティブエディタとして登場したCursor IDEは、大規模言語モデル（LLM）を開発プロセスの中心に据えることで、この限界を突破しようとしている。しかし、LLMには「知識のカットオフ（学習データの期限）」と「ハルシネーション（もっともらしい嘘）」という二つの大きな課題が存在する。特に、急速に進化するWeb技術や、特定の企業内でのみ通用するプロプライエタリな仕様に関しては、汎用的なLLMは無力であるか、あるいは自信満々に誤った情報を提示するリスクがある。

ここで重要となるのが、RAG（Retrieval-Augmented Generation：検索拡張生成）技術のIDEへの統合である。Cursorの「Docs（ドキュメンテーション）」機能は、単なるWebブラウザの代替機能ではない。それは、外部の膨大な技術知識をベクトル化し、開発者の意図（Intent）に合わせて動的にコンテキストウィンドウへと注入する、高度なナレッジマネジメントシステムである。本レポートでは、このCursor IDEの中核機能であるDocs機能について、そのアーキテクチャ、詳細な仕様、インデックス化のメカニズム、運用上の課題、そして「llms.txt」に代表される次世代のドキュメント標準との関わりについて、徹底的な調査と分析を行う。

## **2\. アーキテクチャと基盤技術**

CursorのDocs機能がどのように機能しているかを理解するためには、その背後にある技術的アーキテクチャを解剖する必要がある。このシステムは、情報の収集（Ingestion）、処理（Processing）、保存（Storage）、そして検索（Retrieval）という4つのフェーズで構成されている。

### **2.1 情報収集とクローリングのメカニズム**

Docs機能の入り口となるのは、ユーザーによるURLの指定である。Cursorの設定画面やチャットコマンドを通じて外部ドキュメントのURLが追加されると、Cursorのバックエンドシステム（クローラー）が稼働を開始する 1。

このクローラーは、指定されたエントリーポイント（Entrypoint）を起点として、同一ドメイン内、あるいは指定されたプレフィックス（Prefix）配下のリンクを再帰的に辿る仕様となっている 2。一般的な検索エンジンのクローラーとは異なり、Cursorのクローラーは「コード生成のためのコンテキスト収集」に特化している。これは、マーケティング的な文言よりも、コードブロック、APIシグネチャ、設定パラメータの記述を優先的に抽出する必要があることを意味する。

しかし、現代のWebサイトの多くはシングルページアプリケーション（SPA）として構築されており、JavaScriptの実行（Hydration）なしにはコンテンツが表示されない。調査によると、CursorのクローラーはこのJavaScript実行能力に一定の制限があるか、あるいはタイムアウトの設定が厳格であるため、動的に生成されるドキュメントサイト（例えばUnreal Engineのドキュメントや一部のReactベースのドキュメントサイト）において、インデックス化に失敗するケースが多発している 3。この現象はユーザーインターフェース上で「Red Dot（赤い点）」として視覚化され、開発者に混乱をもたらす要因となっている 5。

### **2.2 セマンティック・チャンキングとベクトル化**

収集されたHTMLやMarkdownコンテンツは、そのまま保存されるわけではない。LLMのコンテキストウィンドウは有限であり（例えばClaude 3.5 SonnetやGPT-4oであっても数万〜数十万トークン）、無関係な情報を大量に流し込むことはコストの増大と推論精度の低下を招く。そのため、Cursorは収集したドキュメントを「チャンク（Chunk）」と呼ばれる意味的な単位に分割する 6。

| 処理フェーズ | 技術的詳細 | 目的 |
| :---- | :---- | :---- |
| **Parsing** | HTMLタグの除去、不要なナビゲーションやフッターの削除。 | ノイズの低減とトークン密度の向上。 |
| **Chunking** | 関数、クラス、見出し（H2, H3）単位でのテキスト分割。 | 文脈の維持と検索粒度の最適化。 |
| **Embedding** | OpenAIのtext-embedding-3-smallや独自の埋め込みモデルによるベクトル化。 | 自然言語クエリとの類似度計算を可能にする。 |

このチャンキングプロセスにおいて、Cursorは「コードの構造」を理解するロジックを組み込んでいるとされる 6。単に文字数で区切るのではなく、クラス定義やメソッドのブロックが分断されないように配慮することで、検索時に「部分的なコード」ではなく「機能するコードスニペット」をLLMに提供できるよう設計されている。

### **2.3 インデックスの保存と共有モデル**

ベクトル化されたデータ（Embeddings）は、Cursorが管理するクラウドインフラストラクチャ上のベクトルデータベースに格納される。ここで特筆すべき仕様は、インデックスの「共有（De-duplication）」メカニズムである 3。

調査により判明した仕様として、あるユーザーが特定のURL（例：https://docs.python.org/3/）のインデックス化をリクエストした場合、そのインデックスデータはキャッシュされ、他のユーザーが同じURLをリクエストした際には再クロールを行わず、既存のインデックスを再利用する仕組みが存在する可能性がある。これにより、ポピュラーなライブラリのドキュメントについては、ユーザーが「Indexing...」の待ち時間を短縮できるメリットがある一方、ドキュメントが更新された際の反映ラグ（Staleness）が発生するリスクも孕んでいる。

また、インデックスデータはクラウドに保存されるが、コードベース自体のインデックス（ローカルのファイル群）については、Merkle Tree（ハッシュ木）を用いて差分のみを同期し、セキュリティとパフォーマンスを両立させるアーキテクチャが採用されている 6。

### **2.4 検索と拡張生成（Retrieval Strategy）**

開発者がチャットで@Docsメンションを使用したり、Agentモードでタスクを依頼したりすると、システムはユーザーの入力（クエリ）をベクトル化し、データベース内のドキュメントチャンクとのコサイン類似度計算を行う 6。

ここで重要なのは、Cursorが単純なベクトル検索だけでなく、ハイブリッドな検索戦略を採用している点である。コード内のキーワード（特定の関数名やクラス名）の一致を重視するキーワード検索と、概念的な質問（「認証の実装方法は？」など）に対応するセマンティック検索を組み合わせることで、開発者の意図に合致したドキュメントを抽出する。抽出されたドキュメントの断片は、システムプロンプトの一部としてLLMに注入され、回答生成の根拠として利用される。これにより、LLMは学習していない最新のライブラリであっても、正確なコードを生成することが可能となる。

## **3\. 機能仕様とユーザーインターフェースの詳細**

CursorのDocs機能は、単なる設定項目ではなく、開発ワークフロー全体に統合されたインターフェースを持っている。ここでは、UIの変遷と現在の仕様について詳述する。

### **3.1 @Docs シンボルとコンテキスト操作**

Cursorにおけるドキュメント参照の基本操作は、@（アットマーク）キーによるメンション機能である。チャットウィンドウ（Cmd+L / Ctrl+L）やインライン編集（Cmd+K / Ctrl+K）において@Docsと入力することで、登録済みのドキュメントリストが呼び出される 2。

UIの進化と現状（Ver 0.40以降）:  
かつてはチャット入力欄の上部にコンテキストトレイが存在し、そこに参照ファイルが表示されていたが、最近のアップデート（Cursor 2.0以降）により、入力欄内部に「ピル（Pill）」と呼ばれる楕円形のチップとしてインライン表示される形式に変更された 2。これにより、テキストとコンテキストが一体化し、コピー＆ペースト時の挙動も改善されている。  
ドキュメントの自動検知:  
ユーザーが明示的に@Docsを指定しない場合でも、CursorのAgent機能はユーザーのクエリ内容を解析し、必要に応じて登録済みのドキュメントやWeb検索（@Web相当の機能）を自律的に利用する能力を持っている 2。例えば、「Drizzle ORMでのスキーマ定義はどうやるの？」と聞いた場合、Drizzleのドキュメントが登録されていれば、Agentはそれを自動的に参照して回答する。

### **3.2 ドキュメント管理インターフェース**

ドキュメントの追加、削除、管理は Cursor Settings \> Features \> Docs パネルに集約されている 2。

| 操作項目 | 仕様詳細 |
| :---- | :---- |
| **Add new doc** | URL入力モーダルが開く。URLを入力後、ドキュメント名（エイリアス）を設定する。 |
| **Prefix / Entrypoint** | クロールの範囲と開始点を指定する重要な設定項目。デフォルトでは入力したURLがそのまま両方に適用されるが、手動で調整が可能。 |
| **Indexing Status** | 各ドキュメントの横にインジケータ（緑、青、赤の点）と、インデックス済みのページ数が表示される。 |
| **Delete** | ゴミ箱アイコンで削除可能。ただし、UI上のバグとして、削除後もリストに残ったり、同名の再登録がブロックされる現象が報告されている 9。 |
| **Share with team** | このスイッチをオンにすると、同じチームIDに属する他のメンバーのCursor環境にも、そのドキュメント設定が自動的に同期される 1。 |

### **3.3 プリセットドキュメントとカスタムドキュメント**

Cursorには、主要な言語やフレームワーク（React, Vue, Node.js, Python, AWS SDKなど）のドキュメントがあらかじめインデックス化され、プリセットとして提供されている 10。これらはユーザーがURLを登録せずとも、@React や @AWS といった形で即座に呼び出すことができる。

一方、カスタムドキュメント機能こそがDocs機能の真価である。社内独自のフレームワークや、マイナーなライブラリ、あるいはリリースされたばかりのベータ版ドキュメントなどを独自に追加することで、汎用LLMでは対応できないニッチな領域の開発支援を実現する。

## **4\. インデックス化における技術的課題とトラブルシューティング**

Docs機能は強力であるが、Webの多様性ゆえに「インデックス化の失敗」は頻繁に発生する問題である。ここでは、その原因と対策を技術的な観点から分析する。

### **4.1 「Red Dot（赤い点）」の分類学**

ユーザーフォーラムで最も頻繁に報告される「赤い点」は、インデックス処理の異常終了を示唆している 5。このエラーには詳細なログが表示されないことが多く、ユーザーを困惑させる要因となっているが、背景には以下のような技術的要因が存在する。

1. SPA（シングルページアプリケーション）の壁:  
   ReactやVueで構築され、クライアントサイドでのJavaScript実行（Hydration）によって初めてDOMが生成されるサイトにおいて、Cursorのクローラーがコンテンツを取得できないケースである。クローラーが受け取るのは \<div id="app"\>\</div\> だけの空のHTMLであり、結果としてインデックスページ数が「0」または「1」となり、失敗扱いとなる 4。  
2. WAFとアンチスクレイピング:  
   CloudflareなどのWAF（Web Application Firewall）や、サイト独自のBot対策により、CursorのUser-Agentからのアクセスが403 Forbiddenで拒否される場合がある。特にUnreal Engineのドキュメントや、一部の商用ライブラリのサイトでこの傾向が強い 3。  
3. リソース制限とタイムアウト:  
   Swiftの公式ドキュメントのように、ページ数が数万に及ぶ巨大なドキュメントサイトの場合、クローラーの処理時間制限（タイムアウト）や、メモリ制限に抵触し、処理が中断されることがある 3。フォーラムでは「sheer amount of data（膨大なデータ量）」が原因で実用性が低下するとの指摘もある。  
4. 動的URLとセッション:  
   URLにセッションIDが含まれていたり、ログイン後のクッキーを必要とするページは、パブリックなクローラーではアクセスできない 13。

### **4.2 robots.txt とクローラーの倫理**

Cursorのクローラーが robots.txt を遵守しているかどうかについては、明確な公式ドキュメントは存在しないが、一般的なWebクローラーの挙動として User-agent: \* のDisallow設定に影響を受けている可能性が高い 14。特定のディレクトリ（例えば /api/ や /private/）が robots.txt でブロックされている場合、Docs機能でもその部分のインデックス化は行われない。

### **4.3 プライベートドキュメントへのアクセス**

企業利用において最大の障壁となるのが、認証（Authentication）が必要なドキュメントの取り扱いである。Confluence、Notion、GitHub Enterprise上のWikiなど、ログインを要するページは、URLを指定するだけの現状のDocs機能ではインデックス化できない 13。

これに対する回避策として、以下の手法がコミュニティで確立されている。

* **Markdownエクスポート**: 社内ドキュメントをMarkdown形式でエクスポートし、プロジェクトリポジトリ内の docs/ ディレクトリに配置する。これにより、Cursorはそれを「コードベースの一部」としてローカルでインデックス化し、参照可能にする 17。  
* **Gistの利用**: 機密性が許容される範囲であれば、MarkdownをGitHub Gist（Secret Gist）にアップロードし、そのRaw URLをDocs機能に登録する手法がある 18。  
* **MCP（Model Context Protocol）**: 後述するが、認証付きAPI経由でドキュメントを取得するMCPサーバーを構築することが、最も本質的な解決策となりつつある。

## **5\. llms.txt：AIのための新しいドキュメント標準**

CursorのDocs機能を取り巻く環境において、現在最も重要なパラダイムシフトが「llms.txt」の登場である。これは、従来の「人間用」のWebサイト構造から脱却し、「AIエージェント用」の情報提供ルートを確立しようとする動きである。

### **5.1 llms.txt とは何か**

llms.txt は、Webサイトのルートディレクトリに配置されるテキストファイルであり、robots.txt に着想を得ているが、その目的は「拒否」ではなく「誘導」にある 15。

* **llms.txt**: AIに対して、サイトの概要、主要なリンク、そしてドキュメント全体の構造を簡潔に伝えるナビゲーションファイル。  
* **llms-full.txt**: サイト内の全ドキュメントコンテンツ（あるいは主要な部分）を、単一のMarkdownファイルに結合したもの。

### **5.2 Cursorと llms.txt の親和性**

Cursorはこの標準規格を強力に推進しており、実際にCursor自身の公式サイトでも https://cursor.com/llms.txt を提供している 21。

ユーザーにとってのメリットは計り知れない。従来のクローラーがSPAのレンダリングや複雑なリンク構造に躓いて「Indexing Failed」を起こしていた問題に対し、llms-full.txt のURLをDocs機能に登録するだけで、クレンジング済み・構造化済みの完璧なコンテキストを一発で取り込むことができる 22。

これは、SvelteやBunといった先進的なフレームワークのコミュニティでも採用が進んでおり、ライブラリ作者にとっては「Cursorユーザーに使ってもらいやすくする」ためのSEO（Search Engine Optimization）ならぬ「AIO（AI Optimization）」施策として定着しつつある 24。また、Context7 のようなサービスが登場し、llms.txt を提供していないライブラリのために、サードパーティとして llms.txt を生成・ホスティングするエコシステムも形成されている 23。

## **6\. 実践的ユースケースと運用ワークフロー**

CursorのDocs機能を単なる「検索窓」として使うのはもったいない。リサーチ資料 1 に示されたエージェント活用例に基づき、開発現場での具体的な運用フローを詳述する。

### **6.1 新規プロジェクトの立ち上げとREADME生成**

新しいプロジェクトを開始する際、Docs機能はスカッフォールディング（骨組み作成）の質を劇的に向上させる。

* **シナリオ**: まだコードが空の状態から、使用予定のライブラリ（例えば Hono と Drizzle ORM）のドキュメントをDocsに登録する。  
* **アクション**: Agentに対し「@Hono と @Drizzle のベストプラクティスに基づき、ディレクトリ構成と初期セットアップを行い、その設計思想を含めた README.md を生成して」と指示する。  
* **効果**: 汎用的な知識ではなく、ライブラリの最新バージョンに準拠した構成案と、具体的で実行可能なセットアップ手順書が自動生成される 1。

### **6.2 オンボーディングガイドの作成**

チームに新しいメンバーが加わった際のコスト削減にも寄与する。

* **アクション**: Agentに対し「このリポジトリのコードを解析し、新入社員向けの ONBOARDING.md を作成して。環境構築、テストの実行方法、最初のプルリクエストの出し方、そしてコードからは読み取れない注意点（Gotchas）を含めて」と指示する。  
* **効果**: ドキュメントと実際のコードの乖離がない、生きたオンボーディング資料が生成される 1。

### **6.3 設計ドキュメント（Design Doc）の逆生成**

既存のコードベースはあるが、ドキュメントが存在しない、あるいは陳腐化している場合。

* **アクション**: 「決済処理モジュール（src/payment）のコードを解析し、そのアーキテクチャ、主要な決定事項、コンポーネント間の相互作用を図解（Mermaid記法）付きで設計ドキュメントとして出力して」と指示する。  
* **効果**: ブラックボックス化していたシステムの仕様が可視化され、リファクタリングや機能追加の足がかりとなる 1。

### **6.4 コンプライアンスドキュメントの作成**

監査やセキュリティチェックへの対応。

* **アクション**: 「ユーザーデータの取り扱いに関するコンプライアンスドキュメントを作成して。どのファイルで個人情報を収集し、どこに保存し、どのように暗号化しているか、コードの具体的な箇所（ファイルパスと行数）を参照しながら記述して」と指示する。  
* **効果**: ポリシー文書と実実装の整合性を証明する、監査証跡レベルのドキュメントが作成される 1。

### **6.5 古いドキュメントの検出（Stale Documentation Check）**

* **アクション**: 「docs/ フォルダ内のドキュメントと、現在の実装（src/）を比較し、記述が古くなっている箇所、欠落している箇所をリストアップして。修正の優先度順に並べて」と指示する。  
* **効果**: ドキュメントのメンテナンスを自動化し、情報の鮮度を保つことができる 1。

## **7\. Docs機能とルールの統合によるガバナンス**

Cursorには「Rules for AI」という、AIの挙動を制御する機能がある 25。Docs機能とRules機能を組み合わせることで、チーム全体のコード品質を統制することが可能になる。

### **7.1 プロジェクトルールの設定**

.cursor/rules ディレクトリにMarkdownファイル（.mdc）を配置し、特定のファイルの編集時に参照すべきドキュメントを強制する 25。

## **例：frontend-rules.mdc**

## **description: フロントエンドの実装ルール globs: src/components/\*\*/\*.tsx**

# **フロントエンド実装ルール**

UIコンポーネントを実装する際は、必ず @Docs Shadcn/UI を参照し、そのスタイルガイドとアクセシビリティ基準に準拠すること。  
直接CSSを書くのではなく、Tailwindのユーティリティクラスを使用すること。  
このように設定することで、開発者が明示的にドキュメントを参照しなくても、AIは自動的に指定されたドキュメントのコンテキストを読み込み、ルールに従ったコードを提案するようになる。これは、経験の浅いメンバーがシニアエンジニアと同じ品質のコードを書くための強力な支援となる。

## **8\. セキュリティとエンタープライズ対応**

企業での導入において、Docs機能が扱うデータのセキュリティは最重要課題である。

### **8.1 プライバシーモードとデータ保持**

Cursorは「プライバシーモード（Privacy Mode）」を提供しており、これを有効にすると、ユーザーのコードや入力されたプロンプト、インデックス化されたドキュメントデータは、Cursorのサーバーに保存されず（Zero Retention）、AIモデルの学習にも使用されないことが保証される 7。

* **インデックスの扱い**: プライバシーモード下でも、RAGを実行するためには一時的にデータをサーバーに送信し、ベクトル化処理を行う必要がある。ただし、このデータは処理完了後に破棄され、長期保存されない仕様となっている。  
* **パスの難読化**: ファイルパスなどのメタデータは暗号化・難読化されて送信されるため、ディレクトリ構造などの情報漏洩リスクも最小化されている 7。

### **8.2 チーム管理とアクセス制御**

エンタープライズプランでは、SSO（シングルサインオン）やSCIMによるユーザー管理が可能であり、「Allowed Team IDs」機能によって、会社のデバイスから個人のCursorアカウントへのログインを禁止するなどの制御ができる 27。

Docs機能に関しても、チーム共有されたドキュメントセットを管理者が一元管理し、不適切なドキュメントの追加を防ぐ、あるいは必須のドキュメント（社内規定など）を全員に強制的に適用するといったガバナンス機能の拡充が期待されている。

## **9\. 競合ツールとの比較評価**

Docs機能において、Cursorは他のAIコーディングツールと比較してどのような位置付けにあるか。

| 機能 | Cursor | GitHub Copilot | Windsurf |
| :---- | :---- | :---- | :---- |
| **外部Docsの追加** | **任意URLを無制限に追加可能**。カスタム性が極めて高い。 | 主にプリセットのドキュメントや学習データに依存。任意のURL追加は限定的。 | 任意のURL追加に対応しており、Cursorに近い機能性を持つ。 |
| **インデックス精度** | RAGに特化した高度なチャンキング。SPAには弱いが llms.txt 対応でカバー。 | 学習データの量で勝負する傾向。最新情報の即応性ではRAGに劣る場合がある。 | 深いコンテキスト理解（Cascade）を売りにしているが、Docs機能のUXはCursorが先行。 |
| **ローカル連携** | @Codebase による強力なローカル検索。 | ワークスペースのコンテキスト理解は進んでいるが、RAGとしての透明性はCursorが高い。 | ファイルシステムとの統合が深く、Agentの自律性が高い。 |

Cursorの最大の強みは、\*\*「ユーザーがコンテキストをコントロールできる自由度の高さ」\*\*にある。開発者はAIに何を知ってほしいかをURL単位で細かく指定でき、それが結果としてAIの回答精度に直結する体験を得られる。

## **10\. 結論と将来展望**

Cursor IDEのDocs機能は、開発者が「検索」という行為に費やしていた時間を劇的に削減し、コーディングという創造的な作業に集中させるための核心的な技術である。

本調査により、以下の点が明らかになった。

1. **RAGの民主化**: 高度なRAGシステムを、URLを貼り付けるだけという極めてシンプルなUIで万人に提供している。  
2. **インデックスの課題**: 現代のWeb技術（SPA）との相性問題は依然として残るが、llms.txt という新しい標準への移行が解決の鍵となっている。  
3. **運用によるカバー**: 「Red Dot」問題や認証の壁に対しては、Markdown化やGist利用といった運用ノウハウ（Workarounds）が必要である。  
4. **エージェント化**: Docs機能は、単なる辞書引きツールから、READMEや設計書を生成する自律型エージェントの「頭脳」へと進化している。

今後、MCP（Model Context Protocol）の普及により、CursorがConfluenceやGoogle Drive、Slackといった外部ツールと直接かつ安全に接続できるようになれば、Docs機能は「Webドキュメント」の枠を超え、企業の全ナレッジを統合する「開発コックピット」へと進化するだろう。開発者は、このツールを使いこなすことで、自身の記憶力や検索能力の限界を超えたパフォーマンスを発揮することが可能になる。それはまさに、AI時代の新しいエンジニアリングの形である。

# **11\. 参考文献・情報源一覧**

本レポートの作成にあたり、以下の調査資料（Snippet）を参照した。

* **機能概要とユースケース**: 1  
* **技術仕様・アーキテクチャ**: 6  
* **インデックス・トラブルシューティング**: 3  
* **セキュリティ・エンタープライズ**: 7  
* **llms.txt・新標準**: 14  
* **ルール・設定**: 25  
* **UI/UX変更・Changelog**: 46

#### **引用文献**

1. Generating Documentation with Cursor | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/for/documentation](https://cursor.com/for/documentation)  
2. @ Mentions | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/context/mentions](https://cursor.com/docs/context/mentions)  
3. Custom Doc Indexing \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/custom-doc-indexing/44584](https://forum.cursor.com/t/custom-doc-indexing/44584)  
4. Adding Docs, Indexing keeping fails after a bit \- \#4 by deanrie \- Bug Reports \- Cursor, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/adding-docs-indexing-keeping-fails-after-a-bit/40670/4](https://forum.cursor.com/t/adding-docs-indexing-keeping-fails-after-a-bit/40670/4)  
5. What does this red dot mean in custom docs? \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/what-does-this-red-dot-mean-in-custom-docs/7138](https://forum.cursor.com/t/what-does-this-red-dot-mean-in-custom-docs/7138)  
6. Semantic Search | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/context/semantic-search](https://cursor.com/docs/context/semantic-search)  
7. Security \- Cursor, 1月 21, 2026にアクセス、 [https://cursor.com/security](https://cursor.com/security)  
8. DOCS should be automatically detected\! \- Discussions \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/docs-should-be-automatically-detected/51791](https://forum.cursor.com/t/docs-should-be-automatically-detected/51791)  
9. Removing Docs doesn't remove the option to add them \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/removing-docs-doesnt-remove-the-option-to-add-them/54019](https://forum.cursor.com/t/removing-docs-doesnt-remove-the-option-to-add-them/54019)  
10. Boosting Your Dev Workflow with Cursor Docs | by Julien Landuré ..., 1月 21, 2026にアクセス、 [https://medium.com/@jlandure/boosting-your-dev-workflow-with-cursor-docs-e4bcfd1c9efe](https://medium.com/@jlandure/boosting-your-dev-workflow-with-cursor-docs-e4bcfd1c9efe)  
11. Managing a Database \- pgEdge Documentation, 1月 21, 2026にアクセス、 [https://docs.pgedge.com/cloud/database/manage\_db/](https://docs.pgedge.com/cloud/database/manage_db/)  
12. What is the Red error icon when use inline edit context? \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/what-is-the-red-error-icon-when-use-inline-edit-context/138297](https://forum.cursor.com/t/what-is-the-red-error-icon-when-use-inline-edit-context/138297)  
13. Best practices for private documentation indexing? \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/best-practices-for-private-documentation-indexing/26709](https://forum.cursor.com/t/best-practices-for-private-documentation-indexing/26709)  
14. How Google Interprets the robots.txt Specification | Google Crawling Infrastructure, 1月 21, 2026にアクセス、 [https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)  
15. llms.txt vs robots.txt \- Medium, 1月 21, 2026にアクセス、 [https://medium.com/@speaktoharisudhan/llm-txt-vs-robots-txt-bb22c9739434](https://medium.com/@speaktoharisudhan/llm-txt-vs-robots-txt-bb22c9739434)  
16. Best practices for private documentation indexing? \- \#3 by tomkulzer \- Discussions \- Cursor, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/best-practices-for-private-documentation-indexing/26709/3](https://forum.cursor.com/t/best-practices-for-private-documentation-indexing/26709/3)  
17. Documentation of Local Files \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/documentation-of-local-files/1189](https://forum.cursor.com/t/documentation-of-local-files/1189)  
18. Tutorial: Adding full repo context, pdfs and other docs \- Guides \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/tutorial-adding-full-repo-context-pdfs-and-other-docs/33925](https://forum.cursor.com/t/tutorial-adding-full-repo-context-pdfs-and-other-docs/33925)  
19. LLMs.txt Explained | TDS Archive \- Medium, 1月 21, 2026にアクセス、 [https://medium.com/data-science/llms-txt-explained-414d5121bcb3](https://medium.com/data-science/llms-txt-explained-414d5121bcb3)  
20. LLMs.txt Explained | TDS Archive \- Medium, 1月 21, 2026にアクセス、 [https://medium.com/data-science/llms-txt-414d5121bcb3](https://medium.com/data-science/llms-txt-414d5121bcb3)  
21. llms.txt \- Cursor, 1月 21, 2026にアクセス、 [https://cursor.com/llms.txt](https://cursor.com/llms.txt)  
22. Cursor not support llms.txt standard \- Bug Reports, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/cursor-not-support-llms-txt-standard/108980](https://forum.cursor.com/t/cursor-not-support-llms-txt-standard/108980)  
23. Introducing Context7: Up-to-Date Docs for LLMs and AI Code Editors | Upstash Blog, 1月 21, 2026にアクセス、 [https://upstash.com/blog/context7-llmtxt-cursor](https://upstash.com/blog/context7-llmtxt-cursor)  
24. add llms.txt to docs · Issue \#17017 · oven-sh/bun \- GitHub, 1月 21, 2026にアクセス、 [https://github.com/oven-sh/bun/issues/17017](https://github.com/oven-sh/bun/issues/17017)  
25. Rules | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)  
26. Demo Privacy \- Cursor AI \- KodeKloud Notes, 1月 21, 2026にアクセス、 [https://notes.kodekloud.com/docs/Cursor-AI/Understanding-and-Customizing-Cursor/Demo-Privacy](https://notes.kodekloud.com/docs/Cursor-AI/Understanding-and-Customizing-Cursor/Demo-Privacy)  
27. Identity and Access Management | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/enterprise/identity-and-access-management](https://cursor.com/docs/enterprise/identity-and-access-management)  
28. Modes | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/agent/modes](https://cursor.com/docs/agent/modes)  
29. Quickstart | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/get-started/quickstart](https://cursor.com/docs/get-started/quickstart)  
30. Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs](https://cursor.com/docs)  
31. 次世代のエディター Cursor(カーソル) を使いこなす(2024年更新 ..., 1月 21, 2026にアクセス、 [https://qiita.com/kota33/items/20a884cbd969cf1ce087](https://qiita.com/kota33/items/20a884cbd969cf1ce087)  
32. Cursorの機能5：Docs｜サクッと始めるAIコードエディタ【Cursor / VS Code / ChatGPT】 \- Zenn, 1月 21, 2026にアクセス、 [https://zenn.dev/umi\_mori/books/ai-code-editor-cursor/viewer/how\_to\_use\_docs](https://zenn.dev/umi_mori/books/ai-code-editor-cursor/viewer/how_to_use_docs)  
33. Commands | Cursor Docs, 1月 21, 2026にアクセス、 [https://cursor.com/docs/context/commands](https://cursor.com/docs/context/commands)  
34. Indexing documentation \- Discussions \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/indexing-documentation/107805](https://forum.cursor.com/t/indexing-documentation/107805)  
35. Adding Docs, Indexing keeping fails after a bit \- Bug Reports \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/adding-docs-indexing-keeping-fails-after-a-bit/40670](https://forum.cursor.com/t/adding-docs-indexing-keeping-fails-after-a-bit/40670)  
36. Teams Platform Documentation: Indexing Failed Status in Cursor Settings \#2644 \- GitHub, 1月 21, 2026にアクセス、 [https://github.com/getcursor/cursor/issues/2644](https://github.com/getcursor/cursor/issues/2644)  
37. Documentation indexing problems \- Bug Reports \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/documentation-indexing-problems/20860](https://forum.cursor.com/t/documentation-indexing-problems/20860)  
38. What's the little red arrow / green rectangle / blue rectangle in VS Code in the narrow space between the line numbers and the code? \- Stack Overflow, 1月 21, 2026にアクセス、 [https://stackoverflow.com/questions/31235330/whats-the-little-red-arrow-green-rectangle-blue-rectangle-in-vs-code-in-the](https://stackoverflow.com/questions/31235330/whats-the-little-red-arrow-green-rectangle-blue-rectangle-in-vs-code-in-the)  
39. Custom Doc Indexing \- Page 2 \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/custom-doc-indexing/44584?page=2](https://forum.cursor.com/t/custom-doc-indexing/44584?page=2)  
40. Button to Index project and reindex it is gone \- Bug Reports \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/button-to-index-project-and-reindex-it-is-gone/39074](https://forum.cursor.com/t/button-to-index-project-and-reindex-it-is-gone/39074)  
41. About Querying Documents in a Collection \- Oracle Help Center, 1月 21, 2026にアクセス、 [https://docs.oracle.com/en/database/oracle/sql-developer-web/sdwad/querying-documents.html](https://docs.oracle.com/en/database/oracle/sql-developer-web/sdwad/querying-documents.html)  
42. 1.1 Buttons \- Racket Documentation, 1月 21, 2026にアクセス、 [https://docs.racket-lang.org/drracket/buttons.html](https://docs.racket-lang.org/drracket/buttons.html)  
43. What does a colored dot in the Explorer View in VS Code mean? \- Stack Overflow, 1月 21, 2026にアクセス、 [https://stackoverflow.com/questions/76030027/what-does-a-colored-dot-in-the-explorer-view-in-vs-code-mean](https://stackoverflow.com/questions/76030027/what-does-a-colored-dot-in-the-explorer-view-in-vs-code-mean)  
44. Text formats are best understood by LLMs \- Discussions \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/text-formats-are-best-understood-by-llms/51176](https://forum.cursor.com/t/text-formats-are-best-understood-by-llms/51176)  
45. LLMs-full.txt \- Allow AI editors like Cursor to better consume the the doc · Issue \#10549 · godotengine/godot-docs \- GitHub, 1月 21, 2026にアクセス、 [https://github.com/godotengine/godot-docs/issues/10549](https://github.com/godotengine/godot-docs/issues/10549)  
46. Changelog \- Cursor, 1月 21, 2026にアクセス、 [https://cursor.com/changelog](https://cursor.com/changelog)  
47. Mastering Cursor IDE: 10 Best Practices (Building a Daily Task Manager App) | by Roberto Infante | Medium, 1月 21, 2026にアクセス、 [https://medium.com/@roberto.g.infante/mastering-cursor-ide-10-best-practices-building-a-daily-task-manager-app-0b26524411c1](https://medium.com/@roberto.g.infante/mastering-cursor-ide-10-best-practices-building-a-daily-task-manager-app-0b26524411c1)  
48. Maximizing Your Cursor Use: Advanced Prompting, Cursor Rules, and Tooling Integration, 1月 21, 2026にアクセス、 [https://extremelysunnyyk.medium.com/maximizing-your-cursor-use-advanced-prompting-cursor-rules-and-tooling-integration-496181fa919c](https://extremelysunnyyk.medium.com/maximizing-your-cursor-use-advanced-prompting-cursor-rules-and-tooling-integration-496181fa919c)  
49. How do I get the LLMs to do what I want? \- Discussions \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/how-do-i-get-the-llms-to-do-what-i-want/148486](https://forum.cursor.com/t/how-do-i-get-the-llms-to-do-what-i-want/148486)  
50. Changelog · Cursor, 1月 21, 2026にアクセス、 [https://cursor.com/changelog/page/2](https://cursor.com/changelog/page/2)  
51. \[Megathread\] Cursor layout and UI feedback, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/megathread-cursor-layout-and-ui-feedback/146790](https://forum.cursor.com/t/megathread-cursor-layout-and-ui-feedback/146790)  
52. A visual editor for the Cursor Browser, 1月 21, 2026にアクセス、 [https://cursor.com/blog/browser-visual-editor](https://cursor.com/blog/browser-visual-editor)  
53. Getting tired of the UI changes : r/cursor \- Reddit, 1月 21, 2026にアクセス、 [https://www.reddit.com/r/cursor/comments/1pmwmp2/getting\_tired\_of\_the\_ui\_changes/](https://www.reddit.com/r/cursor/comments/1pmwmp2/getting_tired_of_the_ui_changes/)  
54. Reindex All Docs Button \- Feature Requests \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/reindex-all-docs-button/125027](https://forum.cursor.com/t/reindex-all-docs-button/125027)  
55. Way to remove added docs? \- Help \- Cursor \- Community Forum, 1月 21, 2026にアクセス、 [https://forum.cursor.com/t/way-to-remove-added-docs/187](https://forum.cursor.com/t/way-to-remove-added-docs/187)