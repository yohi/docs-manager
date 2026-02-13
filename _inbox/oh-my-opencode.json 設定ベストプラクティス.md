# Oh My OpenCode (OMO) 構成の完全ガイド：マルチエージェントAIシステムの設計と最適化

## エグゼクティブサマリー

「Oh My OpenCode」（以下、OMO）の出現は、単一のコンテキストウィンドウと線形なプロンプトチェーンに依存する従来のAIコーディングアシスタントから、階層的なマルチエージェント・オーケストレーションへのパラダイムシフトを象徴しています。OpenCode環境のプラグインとして動作するOMOは、Sisyphus（シシュポス）、Prometheus（プロメテウス）、Hephaestus（ヘパイストス）といった特化した「精神モデル」とツールセットを持つエージェント群を並列に稼働させることで、複雑なソフトウェアエンジニアリングタスクを自律的に遂行します。

本レポートは、oh-my-opencode.json（およびその拡張形式である.jsonc）の構成ベストプラクティスに関する包括的な技術分析書です。対象読者は、AI開発ワークフローの自律性、正確性、効率性を最大化しようとするシニアソフトウェアアーキテクトおよびDevOpsエンジニアです。

本構成戦略の中心となるテーゼは「汎化よりも特化」です。最適なパフォーマンスを実現するためには、各エージェントの役割に基づき、特定の推論能力、コンテキストウィンドウ効率、コストプロファイルを持つ大規模言語モデル（LLM）を精密にマッピングする必要があります。

---

## 第1章：OMOの哲学とマルチエージェント・アーキテクチャ

OMOは人間の開発者が持つ「認知の負荷分散」を模倣したシステムです。

### 1.1 「Ultrawork」と並列処理の概念
OMOの核心的な機能の一つに「Ultrawork」モードがあります。これはプロンプトに `ultrawork` または `ulw` というキーワードを含めることで発動し、エージェントが自律的にタスクを並列化し、完了するまで実行し続けるモードです。メインのオーケストレーターであるSisyphusがタスクを受け取ると、即座に複数のバックグラウンドエージェントを起動し、情報の収集と計画の立案を並行して行います。

### 1.2 コンテキストの経済学とスペシャライゼーション
AI開発においてコンテキストウィンドウは希少な資源です。OMOのベストプラクティスは、タスクの性質に応じてモデルを使い分ける「適材適所」の原則に基づいています。
* **機械的作業（検索・grep）**: 高速で安価なモデル（Grok-Code-Fast, GPT-5-Nano等）
* **高度な設計・リファクタリング**: 推論能力の高いモデル（Claude Opus, GPT-5.3-Codex等）

---

## 第2章：構成ファイルの階層構造と構文

OMOは、グローバル（ユーザーレベル）とローカル（プロジェクトレベル）のカスケード型構成システムを採用しています。

### 2.1 ファイルの優先順位と解決ロジック
設定は以下の順序で解決されます（上が高優先）：
1.  **プロジェクトレベル JSONC**: `.opencode/oh-my-opencode.jsonc`
2.  **プロジェクトレベル JSON**: `.opencode/oh-my-opencode.json`
3.  **ユーザーレベル JSONC**: `~/.config/opencode/oh-my-opencode.jsonc`（Windows: `%APPDATA%\opencode\oh-my-opencode.json`）
4.  **ユーザーレベル JSON**: `~/.config/opencode/oh-my-opencode.json`
5.  **フォールバックデフォルト**: 内部ハードコード値

### 2.2 スキーマ検証とIDEサポート
すべての構成ファイルで公式のJSONスキーマを参照することが推奨されます。

```json
{
  "$schema": "[https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/dev/assets/oh-my-opencode.schema.json](https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/dev/assets/oh-my-opencode.schema.json)",
  // ここに設定を記述...
}
```

### 2.3 JSONCの活用とコメント戦略
複雑なAI構成においては、モデル選択の理由や温度設定の意図をコメント（JSONC形式）で残すことが重要です。

```jsonc
{
  "agents": {
    "Sisyphus": {
      "model": "anthropic/claude-opus-4-6",
      // Opus 4.5では複雑な依存関係の解決に失敗したため、4.6にアップグレード。
      "temperature": 0.1
    }
  }
}
```

---

## 第3章：オーケストレーションの核心 - SisyphusとPrometheus

### 3.1 Sisyphus：エグゼクティブ機能の構成
Sisyphusは「Todo駆動」のワークフローを採用し、状態管理と検証を行います。高い推論能力と十分な「思考バジェット」の設定が不可欠です。

```json
"agents": {
  "Sisyphus": {
    "model": "anthropic/claude-opus-4-6",
    "temperature": 0.1,
    "maxTokens": 4096,
    "thinking": {
      "budget": 32768
    }
  }
}
```

### 3.2 Prometheus：プランナーの役割
`replace_plan` を有効にすることで、デフォルトのプランナーをOMO独自の再帰的計画エージェントであるPrometheusに置き換えます。

```json
"sisyphus_agent": {
  "disabled": false,
  "planner_enabled": true,
  "replace_plan": true, 
  "default_builder_enabled": false
}
```
> **注意**: `sisyphus_agent` キーは必ずトップレベルに配置してください。

### 3.3 Metis：計画コンサルタント
Metisは計画をレビューし、隠れたリスクを特定します。
```json
"agents": {
  "metis": {
    "model": "openai/gpt-5.2",
    "temperature": 0.3
  }
}
```

---

## 第4章：専門エージェントの戦略的構成

### 4.1 エージェント別推奨モデル構成表

| エージェント名 | 役割 (Role) | 推奨モデル | 温度 | 選定理由 |
| :--- | :--- | :--- | :--- | :--- |
| **Sisyphus** | オーケストレーション、統括 | anthropic/claude-opus-4-6 | 0.1 | 複雑な状態管理とメタ認知に最高の推論能力が必要。 |
| **Prometheus** | 計画立案、依存関係解析 | anthropic/claude-opus-4-6 | 0.1 | 論理的な整合性と先読み能力が必須。 |
| **Hephaestus** | 実装、深層作業 | openai/gpt-5.3-codex | 0.1 | 自律的なツール使用と長時間のコーディングに最適。 |
| **Librarian** | ドキュメント調査、検索 | google/gemini-3-flash | 0.2 | 大量テキスト処理のための巨大コンテキストと低コスト。 |
| **Oracle** | アーキテクチャ相談、デバッグ | openai/gpt-5.2 | 0.1 | 純粋な推論能力と知識ベースの広さが鍵。 |
| **Frontend** | フロントエンド実装 | google/gemini-3-pro-1.5 | 0.7 | マルチモーダル能力と画像理解に長けている。 |
| **Explore** | コードベース検索 (Grep) | xai/grok-code-fast-1 | 0.1 | 圧倒的な速度と低コストが最優先。 |

---

## 第5章：カテゴリーエンジニアリングと「マインドセット」

### 5.1 カスタムカテゴリーの定義
プロジェクトの技術スタックに合わせた「マインドセット」を定義できます。

```json
"categories": {
  "data-science": {
    "model": "anthropic/claude-sonnet-4-5",
    "temperature": 0.2,
    "prompt_append": "ループ処理よりもベクトル化演算を優先してください。Pandas/Polarsを使用してください。",
    "tools": ["read_file", "execute_python_cell"]
  }
}
```

### 5.2 プロンプトの追記（Append）と置換（Replace）
* **prompt (置換)**: システムプロンプトを完全に置き換えます。内部命令が消えるため、ツール使用ができなくなるリスクがあります。
* **prompt_append (追記)**: デフォルトの末尾に指示を追加します。最も安全で推奨される方法です。

### 5.3 言語固有の最適化戦略

| 言語 | 推奨設定 (Prompt Append) | 推奨モデル |
| :--- | :--- | :--- |
| **Python** | Strictly follow PEP 8. Use TypeHints. Prefer dataclasses over dictionaries. | gpt-5.3-codex |
| **Rust** | Follow idiomatic Rust patterns. Prioritize memory safety. Use clippy suggestions. | claude-opus-4-6 |
| **Go** | Keep it simple. Prefer standard library. Follow go fmt style. | claude-sonnet-4-5 |

---

## 第6章：ツール、スキル、MCPの統合

### 6.1 スキル管理 (Skills Management)
不要なスキルを無効化してコンテキストを節約します。

```json
"disabled_skills": [
  "playwright",
  "git-master"
]
```

### 6.2 LSP (Language Server Protocol) の構成
正確なリファクタリングのために、静的型付け言語ではLSPの統合が必須です。

```json
"lsp": {
  "typescript-language-server": {
    "command": ["typescript-language-server", "--stdio"],
    "disabled": false
  }
}
```

---

## 第7章：フックシステムと運用チューニング

### 7.1 フック管理：ノイズの抑制
シニア開発者にとってノイズとなるフックを無効化します。

```json
"disabled_hooks": [
  "startup-toast",
  "comment-checker"
]
```

### 7.2 実験的パフォーマンスフラグ
大規模リポジトリでは `aggressive_truncation` の使用を検討してください。

```json
"experimental": {
  "aggressive_truncation": true,
  "auto_resume": true,
  "preemptive_compaction_threshold": 0.85
}
```

### 7.3 コンカレンシー（並行性）の制御
APIレート制限を回避するために同時リクエスト数を制限します。

```json
"providerConcurrency": {
  "anthropic": 4,
  "openai": 10,
  "google": 20
}
```

---

## 第8章：ワークフローの統合

### 8.1 Ultraworkモード
`ultrawork` キーワードは行動抑制をバイパスし、最大並列度で実行します。無限ループを防ぐため、`staleTimeoutMs` を適切に設定してください（例：180000ms）。

### 8.2 Tmuxインテグレーション
エージェントの作業を別ペインで監視できる「司令室」UIを実現します。

```json
"tmux": {
  "enabled": true,
  "layout": "main-vertical",
  "main_pane_size": 60
}
```

---

## 第9章：トラブルシューティングとアンチパターン

1.  **Ollamaのストリーミング**: JSONパースエラーを防ぐため `stream: false` を設定してください。
2.  **幽霊ファイル**: ハルシネーションが発生する場合はLSPの設定を確認し、Exploreエージェントのモデルを強化してください。
3.  **sisyphus_agent の配置**: `agents` オブジェクトの中に入れてはいけません。必ずトップレベルに配置してください。

---

## 付録：ゴールデンスタンダード構成ファイル (oh-my-opencode.jsonc)

```jsonc
{
  "$schema": "[https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/dev/assets/oh-my-opencode.schema.json](https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/dev/assets/oh-my-opencode.schema.json)",
  "google_auth": false,
  "share": "disabled",
  "sisyphus_agent": {
    "disabled": false,
    "planner_enabled": true,
    "replace_plan": true,
    "default_builder_enabled": false
  },
  "agents": {
    "Sisyphus": {
      "model": "anthropic/claude-opus-4-6",
      "temperature": 0.1,
      "thinking": { "budget": 32768 }
    },
    "prometheus": {
      "model": "anthropic/claude-opus-4-6",
      "variant": "max"
    },
    "Hephaestus": {
      "model": "openai/gpt-5.3-codex",
      "reasoningEffort": "high"
    },
    "librarian": {
      "model": "google/gemini-3-flash",
      "temperature": 0.2
    },
    "explore": {
      "model": "xai/grok-code-fast-1",
      "temperature": 0.1
    }
  },
  "providerConcurrency": {
    "anthropic": 5,
    "openai": 10,
    "google": 20
  },
  "disabled_hooks": [
    "startup-toast",
    "comment-checker",
    "auto-update-checker"
  ],
  "experimental": {
    "aggressive_truncation": true,
    "auto_resume": true,
    "preemptive_compaction_threshold": 0.85
  }
}
```

