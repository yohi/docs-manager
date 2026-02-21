# OpenCode環境における自律的Git操作のためのアーキテクチャ分析と構成戦略

## エグゼクティブサマリー

2026年現在、ソフトウェア開発におけるAgentic Developer Environments (ADEs) の進化は目覚ましく、特に oh-my-opencode のような高度なオーケストレーション層の導入により、LLM（大規模言語モデル）とローカル開発環境の統合は新たなフェーズに突入している。しかし、この自律性の向上は、セキュリティと利便性の間の不可避な摩擦を生み出している。本レポートでは、ユーザーが提起したカスタムコマンド /git-pr-flow 実行時における Git コマンドの権限承認（Ask）によるボトルネック現象に対し、提供された設定ファイル群（opencode.txt）および最新の技術文書に基づく包括的な技術分析を提供する。

分析の結果、根本的な原因は OpenCode ランタイムにおける「権限継承モデル」と「エージェントの役割分担」の不一致にあることが特定された。具体的には、/git-pr-flow コマンドが、デフォルトで制限的な権限を持つ指揮官エージェント sisyphus のコンテキストで実行されている一方で、Git 操作に必要な特権は専門家エージェント git-specialist にのみ付与されているという構造的な乖離が存在する。本稿では、opencode.jsonc、oh-my-opencode.base.jsonc、および patterns/*.jsonc の階層的な構成優先順位を解明し、セキュリティ境界を維持しつつ、バージョン管理タスクにおける「Human-on-the-loop（人間が監視するループ）」型の自律性を実現するための具体的なアーキテクチャ改修案を提示する。

---

## 1. エージェンティック開発環境における権限アーキテクチャの現状

### 1.1 2026年におけるOpenCodeのセキュリティモデル

OpenCode ランタイム（v1.1.64以降）におけるセキュリティモデルは、単純なオン・オフのスイッチではなく、ツールタイプ、コマンドパターン、および実行エージェントのアイデンティティに基づく多層的な評価ロジックを採用している。このモデルは、AI エージェントが開発者のローカル環境（ファイルシステム、シェル、ネットワーク）に対して持つ「破壊的能力」を制御するために不可欠な防波堤である。

oh-my-opencode のようなプラグインエコシステムは、この基本レイヤーの上に「専門化された役割（Specialized Roles）」という概念を導入している。これは、すべての権限を単一のエージェントに与えるのではなく、タスクごとに適切な権限セットを持つエージェント（例：sisyphus, git-specialist, librarian）を切り替えて使用する「最小特権の原則（Principle of Least Privilege）」に基づく設計思想である。

#### 権限評価の3段階プロセス

エージェントが bash ツールを通じてシェルコマンドを実行しようとする際、システムは以下の順序で厳格な評価を行う：

1. **ツールレベルのゲート（Tool-Level Gate）**:
   現在アクティブなエージェントに対して、bash ツール自体が有効化されているかを確認する。例えば、oracle（相談役）のような読み取り専用エージェントでは、この時点で拒否される設定が一般的である。
2. **パターンマッチング（Pattern Matching）**:
   有効化されている場合、実行しようとしているコマンド文字列（引数を含む）が、設定ファイルで定義された「許可リスト（Allow List）」または「拒否リスト（Deny List）」のパターンと照合される。このマッチングにはグロブ形式のワイルドカード（例：git *, npm run *）が使用される。
3. **アクション解決（Action Resolution）**:
   マッチングの結果、以下の3つの状態のいずれかに解決される：
   * **ALLOW**: ユーザーの介入なしに即座にコマンドを実行する。ログには記録されるが、ワークフローは中断しない。
   * **ASK**: 実行を一時停止し、TUI（Terminal User Interface）上に確認プロンプトを表示する。これは、意図しない副作用を防ぐための「フェイルセーフ」なデフォルト状態である。
   * **DENY**: 即座に実行をブロックし、エージェントに対して権限エラーを返す。エージェントはこれを受けて代替手段を模索するか、タスクの不能を報告する。

### 1.2 構成ファイルの階層と優先順位（Configuration Precedence）

ユーザーが直面している「非効率な状況」を解決するためには、競合するルールが存在する場合にどの設定ファイルが優先されるかという「構成の優先順位」を正確に理解する必要がある。提供されたドキュメントおよび AGENTS.md の記述に基づくと、以下の階層構造が明らかになる。

| 優先順位 | 構成ソース | 説明 |
| :--- | :--- | :--- |
| **1 (最高)** | **エージェント/コマンドコンテキスト** | カスタムコマンド（.mdファイル）のフロントマターや、ランタイムで動的に生成されるエージェントオーバーライド設定。 |
| **2** | **プロジェクト構成** | プロジェクトルートにある .opencode/oh-my-opencode.json または opencode.json。これはグローバル設定を上書きする。 |
| **3** | **グローバルパターン/プロファイル** | プロファイルスイッチャーによって注入されるアクティブなパターンファイル（例：patterns/pattern-5.jsonc）。 |
| **4** | **グローバルベース構成** | ~/.config/opencode/opencode.jsonc および oh-my-opencode.base.jsonc。 |
| **5 (最低)** | **システムデフォルト** | OpenCode バイナリにハードコードされたデフォルト設定（通常、bash はすべて ask）。 |

現状の問題は、git-specialist エージェントには pattern-5.jsonc（レベル3）で適切な許可が与えられているにもかかわらず、/git-pr-flow コマンドが sisyphus エージェント（レベル1で指定）として実行されている点にある。sisyphus はパターンファイル内で明示的な権限ブロックを持たないため、より下位の（より制限的な）グローバル設定（レベル4）またはシステムデフォルト（レベル5）を継承してしまっているのである。

### 1.3 "Ask" メカニズムによるボトルネックの発生機序

「Ask」状態は本来、ユーザーの安全を確保するための重要な機能である。しかし、Git のような高頻度かつ定型的な操作においては、これが深刻なワークフローの阻害要因となる。

ユーザーの環境における /git-pr-flow コマンドは、一連の Git 操作を連続して実行するように設計されている。権限が ask に設定されている場合、以下のようなインタラクションが強制されることになり、自動化の恩恵が完全に失われる：

1. git branch --show-current → **Prompt: 実行しますか？ (y/n)**
2. git checkout -b feature/update-dependency → **Prompt: 実行しますか？ (y/n)**
3. git status → **Prompt: 実行しますか？ (y/n)**
4. git add packages/core/utils.ts → **Prompt: 実行しますか？ (y/n)**
5. git commit -m "fix:..." → **Prompt: 実行しますか？ (y/n)**

この「承認疲れ（Approval Fatigue）」は、ユーザーが最終的にセキュリティ設定をすべて無効化（YOLOモード）する原因となりやすく、長期的にはセキュリティリスクを高める結果となる。したがって、特定の信頼できるコンテキスト（この場合は /git-pr-flow）においてのみ、安全な操作を許可する「サージカル（外科的）」な権限設定が求められる。

---

## 2. ユーザー環境の診断的分析

提供されたファイル群 opencode.txt の内容を詳細に分析し、なぜ現状の構成が期待通りに動作していないのか、その技術的根拠を特定する。

### 2.1 コマンド定義の分析：/opencode/commands/git-pr-flow.md

カスタムコマンドの定義ファイルは、この問題の震源地である。以下のフロントマター記述に注目する。

```markdown
---
description: 状況に応じてfeatureブランチ作成/選択、関連ファイルのコミット、PR作成（未存在時のみ）を行うスマートフロー
agent: sisyphus
model: google/antigravity-gemini-3-pro
---
```

**分析結果:**

* **Agent指定**: agent: sisyphus と明示的に指定されている。これは、このコマンドが実行される際、ランタイムが sisyphus エージェントのプロファイルと権限セットをロードすることを意味する。
* **モデル指定**: model: google/antigravity-gemini-3-pro が指定されている。
* **不一致**: コマンドの目的は Git 操作であるが、使用されるエージェントは「指揮官（Orchestrator）」である sisyphus であり、Git 操作に特化した権限を持つ git-specialist ではない。

### 2.2 パターン構成の分析：patterns/pattern-5.jsonc

次に、現在のアクティブな設定と思われる pattern-5.jsonc におけるエージェント定義を比較分析する。

#### A. git-specialist エージェントの定義

```json
"git-specialist": {
  "description": "Git operations specialist",
  "model": "google/antigravity-gemini-3-flash",
  "permission": {
    "bash": {
      "git push --force": "deny",  // 明示的な拒否
      "git push -f": "deny",       // 明示的な拒否
      "git clean *": "ask",        // 危険な操作は確認
      "git add .": "ask",          // 全追加は確認
      "git *": "allow",            // その他のGit操作は許可
      "*": "deny"                  // それ以外は拒否
    },
    "edit": "deny",
    "webfetch": "deny"
  }
}
```

このエージェント定義は理想的である。「安全な Git 操作」は許可され、危険な操作は確認または拒否されるよう細かく制御されている。

#### B. sisyphus エージェントの定義

```json
"sisyphus": {
  "model": "google/antigravity-gemini-3-pro",
  "variant": "high",
  "temperature": 0.2
  // ここに permission ブロックが存在しない
}
```

**分析結果:** sisyphus エージェントには、permission オブジェクトが定義されていない。OpenCode の仕様上、エージェントレベルで権限が定義されていない場合、そのエージェントはベース設定ファイル（opencode.jsonc）のグローバル権限設定を継承する。

### 2.3 グローバル設定の分析：opencode.jsonc

最後に、権限の継承元となる opencode.jsonc を確認する。

```json
"permission": {
  "bash": {
    "*": "ask", // デフォルトは確認（ASK）
    "git *": "allow", // 一見すると許可されているように見えるが...

    // -----------------------------------------------------------
    // ▼ 制限・禁止リスト（下の行ほど優先＝上書きされます）
    // -----------------------------------------------------------

    // 【Gitの特例制限】
    "git push*": "ask",   // ここでASKに上書きされている
    "git commit*": "ask", // ここでASKに上書きされている
    "git rebase*": "ask",
    "git merge*": "ask"
  }
}
```

**決定的原因:** opencode.jsonc において、git push* と git commit* が明示的に "ask" に設定されている。OpenCode の権限評価は、JSONオブジェクト内の記述順序に基づいて後勝ちで適用されるため、前段の "git *": "allow" は、より具体的な "git commit*": "ask" によって上書きされている。

結果として、sisyphus エージェントはこのグローバル設定を継承し、コミットやプッシュのたびにユーザー確認を求める挙動となっている。

---

## 3. アプローチ方法の調査と解決策

この問題を解決するための3つの戦略を提示する。

### 戦略A：パターンファイルにおけるSisyphus権限の昇格（推奨・即効性あり）

最も確実で副作用の少ない方法は、現在使用しているパターンファイル内の sisyphus エージェント定義に、Git 操作を許可する permission ブロックを追加することである。

#### 具体的な修正手順

対象ファイル：`/opencode/patterns/pattern-5.jsonc`

```json
"sisyphus": {
  "model": "google/antigravity-gemini-3-pro",
  "variant": "high",
  "temperature": 0.2,
  "permission": {
    "bash": {
      "git push --force": "deny",
      "git push -f": "deny",
      "git clean *": "ask",
      "git reset --hard": "ask",
      "git add *": "allow",
      "git commit*": "allow",
      "git push origin HEAD": "allow",
      "git push": "allow",
      "git checkout*": "allow",
      "git branch*": "allow",
      "git status": "allow",
      "gh pr *": "allow",
      "*": "ask" 
    }
  }
},
```

---

### 戦略B：コマンド定義におけるエージェントの変更（アーキテクチャ的正解）

Git 操作は git-specialist の領分であり、指揮官である sisyphus が直接行うべきではないという考え方に基づく修正である。

#### 具体的な修正手順

対象ファイル：`/opencode/commands/git-pr-flow.md`

**修正案1（実行エージェントの変更）:**
フロントマターの `agent: sisyphus` を `agent: git-specialist` に変更する。

**修正案2（プロンプト内での委譲指示）:**
本文を修正し、実際のコマンド実行を `task(subagent_type="git-specialist", ...)` を通じて委譲するように指示する。

---

### 戦略C：グローバル設定の緩和（広範な適用）

すべてのエージェントで Git 操作の確認を省略したい場合、グローバル設定自体の制限を緩和する。

#### 具体的な修正手順

対象ファイル：`/opencode/opencode.jsonc`

```json
// "git push*": "ask",
// "git commit*": "ask",
"git push*": "allow",
"git commit*": "allow",
```

---

## 4. 推奨される構成とアクションアイテム

**戦略A（パターンファイルでの権限昇格）** を最優先の解決策として推奨する。

### 手順 1: パターンファイルの編集
`/opencode/patterns/pattern-5.jsonc` の sisyphus 定義内に上述の permission ブロックを挿入する。

### 手順 2: プロファイルの再適用
設定を反映させるためにプロファイルスイッチャーを実行する。

```bash
./opencode/switch-opencode-pattern.sh
# メニューから該当のパターン番号を選択
```

### 手順 3: コマンド定義の微調整（オプション）
`/opencode/commands/git-pr-flow.md` の末尾に「あなたは権限を持っており、自律的に実行してください」という指示を追加する。

---

## 5. 第二次・第三次オーダーの洞察と将来展望

### 5.1 権限システムの「粒度」と「認知負荷」のトレードオフ
今回の事象は、セキュリティの「粒度」と開発者の「認知負荷」のトレードオフを浮き彫りにしている。2026年のトレンドとして、静的な許可から、特定のコマンド実行中のみ一時的に権限を昇格させる「コンテキスト単位の許可（Context-based Permission）」への移行が見られる。

### 5.2 「YOLOモード」のリスクと構成ドリフト
利便性のためにすべての確認を無効化する「YOLOモード」は、エージェントが自身の設定を書き換えてしまう「構成ドリフト」を引き起こす可能性がある。エージェント単位のオーバーライドは、このリスクを最小限に抑える中間解である。

### 5.3 役割分担の再考：Sisyphusの過負荷
長期的には、指揮官 sisyphus が計画を立て、軽量な git-specialist が実行するというフローに移行することが、コストとパフォーマンスの両面で最適解となるだろう。

---

## 結論

/git-pr-flow におけるボトルネックは、sisyphus がグローバルの厳しい制限を継承していることに起因する。解決策は、パターンファイル内での明示的な権限付与である。

```json
// patterns/pattern-5.jsonc 内の sisyphus 定義
"permission": {
  "bash": {
    "git push --force": "deny",
    "git commit*": "allow",
    "git push origin HEAD": "allow",
    "git add *": "allow",
    "*": "ask"
  }
}
```

---

### 参考文献
* OpenCode Documentation: Permissions
* oh-my-opencode Configuration Guide
* GitHub Issue #7407: Scoped Permission Overrides
