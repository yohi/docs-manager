# AIエージェントガイドライン（Docs-Managerリポジトリ）

このファイルは、このリポジトリで作業するAIエージェント（あなた）のためのガイドラインです。
Jekyllプロジェクトとしての技術的制約と、以下の開発フローを遵守してください。

## 1. プロジェクト概要
- **目的**: 開発者向けドキュメントハブ (AI, Cursor, GitHub MCPなどの知見集約)
- **技術スタック**: Jekyll (Static Site Generator) + GitHub Pages
- **主要言語**: Markdown (Docs), HTML/Liquid (Templates), Python (Utility Scripts), Ruby (Build)

---

## 2. 環境構築とビルド (Build & Environment)

### 前提条件
- Ruby >= 3.3
- Python 3.x (ユーティリティ用)
- Bundler

### コマンドリファレンス
```bash
# 依存関係のインストール
bundle install

# ローカルサーバー起動 (http://localhost:4000/docs-manager/)
bundle exec jekyll serve

# HTML構造チェック (ビルド後に実行)
bundle exec jekyll build
bundle exec htmlproofer ./_site --disable-external-links

# リンク切れチェック (デプロイ済みサイトに対して実行)
python3 check_404.py
```

---

## 3. 開発フロー (Development Workflow)

このプロジェクトでは、標準的なGitベースのワークフローを採用しています。

### A. ブランチ戦略
タスクの性質に応じて、以下のどちらかを選択してください。

| タイプ | ブランチ名 | 戦略 |
| :--- | :--- | :--- |
| **単発タスク** | `task/{id}` | 機能追加、バグ修正など独立したタスク。 |
| **大規模機能** | `feature/{name}` | 複数の変更を含む大きな機能開発。 |

### B. エージェントの行動指針
1.  **ブランチ作成**: 作業開始時に必ず新しいブランチを作成してください。
2.  **Pull Request**: 実装が完了し、検証が通ったらPRを作成してください。
3.  **言語**: すべてのドキュメント、コミットメッセージ、PRの説明は **日本語** で記述してください。

---

## 4. コードスタイル (Code Style)

### Markdown (Documentation)
`_documents/` ディレクトリ配下に配置します。

- **Frontmatter (必須)**:
  ```yaml
  ---
  layout: default
  title: "記事のタイトル"
  description: "記事の概要（検索結果・SEO用）"
  order: 10 # 並び順
  permalink: /documents/category-name/article-slug/
  ---
  ```
- **本文**:
  - 見出しは `#` (H1) ではなく `##` (H2) から開始することを推奨（タイトルがH1になるため）。
  - コードブロックには必ず言語を指定する (例: \`\`\`python)。
  - 画像は `assets/images/` に配置し、相対パスで参照。

### Liquid / HTML (Templates)
`_layouts/` および `_includes/` 配下。

- **インデント**: 2スペース
- **変数**: `page.title` や `site.baseurl` などのJekyll標準変数を使用。
- **SEO**: `<head>` 内で `{% seo %}` タグが正しく動作することを妨げない。
- **リダイレクト**: クライアントサイドリダイレクトが必要な場合は `_includes/redirect_handler.html` を活用。

### Python Scripts
ルートディレクトリのユーティリティスクリプト (`.py`)。

- **仕様**:
  - 依存ライブラリ: `requests`, `beautifulsoup4` (標準的なスクレイピング構成)
  - 型ヒント: 可能な限り付与するが、厳密な型チェックパイプラインは現状なし。
  - エラー処理: ネットワークリクエストには必ず `try-except` を含める。

### Ruby / Gemfile
- **バージョン**: `ruby '>= 3.3'` を厳守。
- **グループ**: `development`, `test` グループを適切に使用し、本番環境 (GitHub Pages) に不要なgemを含めない。

---

## 5. ディレクトリ構造ルール (Directory Structure)

- **`_documents/`**:
  - ドキュメント記事の本体。
  - サブディレクトリによるカテゴリ分けを推奨 (例: `_documents/cursor/`).
  - `_config.yml` の `collections` 設定により、出力パスが決まる。
- **`_layouts/`**:
  - `default.html`: 基本レイアウト。
- **`assets/`**:
  - 静的ファイル置き場。CSS, JS, Images。
- **`check_404.py` / `fix_links.py`**:
  - メンテナンス用スクリプト。これらを変更する場合は慎重に行うこと。

---

## 6. 禁止事項 (Anti-Patterns)

1.  **`_config.yml` の無断変更**:
    - 特に `url`, `baseurl`, `collections` の設定変更はサイト全体に影響するため、ユーザーの明示的な指示がない限り変更しない。
2.  **Frontmatterの削除**:
    - 既存記事を編集する際、Frontmatterを削除または破壊しないこと。ビルドエラーの原因になります。
3.  **英語でのコミット**:
    - 特段の指示がない限り、コミットメッセージは日本語で統一する。

---

## 7. テスト・検証手順

タスク完了とみなす前に、以下の検証を行ってください。

1.  **ビルド確認**: `bundle exec jekyll build` がエラーなく通ること。
2.  **HTML検証**: 新規ページを追加した場合、`htmlproofer` でリンク切れやタグの閉じ忘れがないか確認する。
3.  **ローカルプレビュー**: UI変更を伴う場合は、ローカルサーバーで表示崩れがないか確認する（スクリーンショット撮影ツール等が利用可能な場合）。
