---
title: "OpenCode設定の決定版ガイド：opencode.jsonおよびopencode.jsoncにおけるベストプラクティスとアーキテクチャ戦略"
date: 2026-02-13
layout: default
---

# OpenCode設定の決定版ガイド：opencode.jsonおよびopencode.jsoncにおけるベストプラクティスとアーキテクチャ戦略

## エグゼクティブサマリー

AI支援型開発ツールの急速な進化により、自律的なコード生成、リファクタリング、そして複雑な問題解決能力を持つ「エージェント」が実用段階に到達しました。その中でも、OpenCodeは独自の構成システムを通じた比類なきカスタマイズ性を提供するオープンソースの代替ソリューションとして、独自の地位を確立しています。このシステムの中心にあるのが、opencode.json（またはopencode.jsonc）ファイルです。この宣言型マニフェストは、モデルの選択からツールの権限管理、マルチエージェントオーケストレーション、そしてプラグイン統合に至るまで、システムのあらゆる挙動を制御します。

本レポートでは、OpenCodeの設定に関する技術的な詳細を網羅的に分析します。設定読み込みの階層構造、大規模モノレポにおけるセキュリティとパフォーマンスのベストプラクティス、および専門化されたエージェントを定義するための高度な戦略について論じます。opencode.jsonスキーマを完全に掌握することで、エンジニアリングチームはOpenCodeを単なるコーディングアシスタントから、組織固有のアーキテクチャ基準とワークフロー要件に適合した、特注の開発プラットフォームへと変貌させることが可能となります。

---

## 1. 設定アーキテクチャと哲学

OpenCodeの設定システムは、柔軟性と継承を核として設計されています。グローバル設定やコマンドライン引数のみに依存する硬直的なツールとは異なり、OpenCodeは組織レベル、ユーザーレベル、そしてプロジェクトレベルでのきめ細やかな制御を可能にするカスケード型の設定戦略を採用しています。

### 1.1 JSON対JSONC：コメント機能の戦略的価値

OpenCodeは標準的な.jsonファイルをサポートしていますが、業界のベストプラクティスとしては.jsonc（JSON with Comments）拡張子の利用が強く推奨されます。複雑なAIエージェントの設定ファイルには、なぜ特定のパラメータが選択されたのかという「意図」を説明するドキュメントが不可欠です。

**JSONCを採用すべき技術的根拠：**

* **インラインドキュメンテーション**：CI/CD環境において特定のMCP（Model Context Protocol）サーバーを無効化する理由や、特定のモデルバリアントを選択した背景など、アーキテクチャ上の決定事項を設定ファイル内に直接記述できます。
* **一時的なトグル機能**：実験的なエージェント定義やツール設定を削除することなく、コメントアウトするだけで一時的に無効化できます。
* **スキーマバリデーションと型安全性**：VS Code、Cursor、Zedなどの現代的なエディタは、`$schema`キーが存在する場合、.jsoncファイルに対してもスキーマバリデーションを適用します。

### 1.2 コンフィギュレーション・カスケード（優先順位ロジック）

OpenCodeは複数のソースから設定を読み込み、それらを最終的なランタイム設定へとマージします。優先順位は低いものから高いものへと以下の順序で適用されます。

| 優先順位 | 設定ソース | パス/場所 | 役割と特徴 |
| :--- | :--- | :--- | :--- |
| 1 | リモート設定 | .well-known/opencode | **組織的基盤**：組織全体のデフォルト設定。許可されたモデルプロバイダーや必須のセキュリティスキャンツールなど。 |
| 2 | グローバル設定 | ~/.config/opencode/opencode.json | **ユーザーの好み**：テーマ、キーバインディング、個人的なAPIキーなど。 |
| 3 | 環境変数オーバーライド | OPENCODE_CONFIG | **動的注入**：CIパイプラインやコンテナ環境において一時的な設定ファイルを指し示すために使用。 |
| 4 | プロジェクト設定 | プロジェクトルートの opencode.json(c) | **リポジトリのルール**：エージェント定義、リンター設定、アーキテクチャ上の制約。最も頻繁に編集される。 |
| 5 | ディレクトリベースのオーバーライド | .opencode/ | **モジュール化**：設定を複数のファイルに分散させ、管理性を向上させる。 |
| 6 | インラインランタイム設定 | OPENCODE_CONFIG_CONTENT | **即時オーバーライド**：CLIやスクリプトを介して一時的に上書きする際に使用。 |

**競合解決戦略（Deep Merge vs. Replacement）：**
キーが競合する場合、高い優先順位のソースが上書きします。ただし、ネストされたオブジェクト（mcpサーバーやエージェント定義）に対しては**ディープマージ（深層結合）**が行われます。一方、配列（pluginsリストなど）に関しては完全に置換される可能性があるため注意が必要です。

### 1.3 スキーマバリデーションによる品質保証

設定ファイルの冒頭でスキーマを宣言することで、エディタの支援機能を最大限に活用できます。

```json
{
  "$schema": "[https://opencode.ai/config.json](https://opencode.ai/config.json)",
  //... configuration
}
```

---

## 2. コア接続性とモデルエンジニアリング

### 2.1 プロバイダー設定と認証管理

OpenCodeは、OpenAI、Anthropic、Google Vertex、Amazon Bedrock、Ollamaを含む75以上のプロバイダーをサポートしています。

```json
"provider": {
  "openai": {
    "options": {
      "baseURL": "[https://gateway.mycorp.internal/v1](https://gateway.mycorp.internal/v1)",
      "headers": {
        "Helicone-Auth": "Bearer sk-..."
      }
    }
  },
  "amazon-bedrock": {
    "options": {
      "region": "us-east-1",
      "profile": "bedrock-admin",
      "endpoint": "[https://bedrock-runtime.us-east-1.vpce-xyz.amazonaws.com](https://bedrock-runtime.us-east-1.vpce-xyz.amazonaws.com)"
    }
  }
}
```

### 2.2 戦略的なモデル選択：プライマリとスモールモデル

`model`キーでデフォルトエンジンを、`small_model`キーで補助的なタスクのコストとレイテンシを最適化します。

| 設定キー | 推奨モデル例 | 用途と役割 |
| :--- | :--- | :--- |
| **model** (プライマリ) | anthropic/claude-3-5-sonnet, openai/gpt-4o | **複雑な推論**：実装、リファクタリング、アーキテクチャ設計、デバッグ。 |
| **small_model** (補助) | google/gemini-2.5-flash, anthropic/claude-3-haiku | **管理・要約**：セッションタイトルの生成、履歴の要約、単純な分類。 |

### 2.3 モデルバリアントと推論努力（Reasoning Effort）

「バリアント（Variant）」を使用することで、思考の深さを調整するプロファイルを作成できます。

```json
"provider": {
  "openai": {
    "variants": {
      "architect": {
        "model": "gpt-4o",
        "reasoning_effort": "high"
      },
      "scripter": {
        "model": "gpt-4o-mini",
        "reasoning_effort": "low"
      }
    }
  }
}
```
ユーザーは `Ctrl+T` を使用して、これらのバリアントをセッション中に動的に切り替えることが可能です。

---

## 3. エージェントオーケストレーション：「エージェンティック」な設定

### 3.1 opencode.jsonでのエージェント定義

各エージェントは独立した設定オブジェクトを持ち、アクティブ時にデフォルト設定を上書きします。

**事例：「厳格なレビュアー（Strict Reviewer）」**

```json
"agent": {
  "code-reviewer": {
    "description": "セキュリティ、パフォーマンス、およびスタイル準拠のためにコードをレビューします。",
    "mode": "subagent",
    "model": "anthropic/claude-3-opus-20240229",
    "prompt": "{file:.opencode/prompts/reviewer.md}",
    "tools": {
      "write": false,
      "edit": false,
      "bash": false,
      "read": true,
      "glob": true
    }
  }
}
```

### 3.2 Markdownによるモジュール式エージェント定義

`.opencode/agents/` ディレクトリ内に Markdown ファイルとして定義することも推奨されます。Frontmatter で設定を記述し、本文をプロンプトとします。

### 3.3 AGENTS.md標準とコンテキスト管理

`AGENTS.md` はプロジェクトの「AIのためのREADME」として機能し、ディレクトリの目的やコーディング規約を記述します。OpenCode はこれを自動的にコンテキストウィンドウに注入します。

---

## 4. ツールとセキュリティ：権限モデル

### 4.1 粒度の高い権限状態

* **allow (許可)**：ユーザーの確認なしに実行。
* **ask (確認)**：実行前に承認を求める（デフォルト）。
* **deny (拒否)**：実行を厳格に禁止。

### 4.2 シェル（bashツール）のセキュア化

```json
"permission": {
  "bash": {
    "allow": ["ls -la", "git status", "npm run test"],
    "ask": ["npm install *", "git commit *"],
    "deny": ["rm -rf *", "curl * | bash", "aws *"]
  }
}
```

---

## 5. モノレポおよび大規模アーキテクチャ戦略

### 5.1 AGENTS.mdの「Search Up」戦略

OpenCodeは、現在のディレクトリからGitルートに向かって `AGENTS.md` を探索します。
* ルート：共通ルール（コミット規約など）
* `packages/backend/`：バックエンド固有ルール
* `packages/frontend/`：フロントエンド固有ルール

これにより、LLMの焦点を絞りトークンを節約できます。

---

## 6. 高度なカスタマイズ：プラグインとフック

### 6.1 oh-my-opencodeによる統合

```json
"plugin": [
  "oh-my-opencode",
  "opencode-ignore",
  "opencode-beads"
]
```

### 6.2 カスタムフックの活用

| フック名 | 実行タイミング | ユースケース |
| :--- | :--- | :--- |
| **PreToolUse** | ツール実行前 | 入力の検証、危険な引数のブロック。 |
| **PostToolUse** | ツール実行後 | 出力の加工、エラーに対する自動修正提案。 |
| **UserPromptSubmit** | プロンプト送信時 | 入力内容に基づくエージェントの動的ルーティング。 |

---

## 7. トラブルシューティングとメンテナンス

* **JSON構文エラー**：.jsonファイルでのコメント使用に注意（.jsoncを使用すること）。
* **優先順位の誤解**：プロジェクトレベルの設定がグローバルを上書きしていないか確認。
* **無限ループ**：`auto_mode` 実行時は適切な `steps` 制限を設定すること。

---

## 8. 結論

opencode.json 設定ファイルは、OpenCode エージェントのコントロールプレーンです。設定をコードとして扱い（Configuration as Code）、バージョン管理された opencode.jsonc、モジュール化された AGENTS.md、そして厳格な権限境界を使用することで、チームは安全で専門化された AI ワークフォースを持続的にスケールさせることが可能となります。


