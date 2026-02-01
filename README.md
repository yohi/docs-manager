# Development Documentation Hub

https://yohi.github.io/docs-manager/

プロフェッショナル開発者のための包括的ドキュメントサイト。
AI活用、プロンプトエンジニアリング、Cursor IDE、GitHub統合など、現代的な開発ワークフローに必要な情報を体系的にまとめています。

## 🎯 特徴

*   **AI ファースト**: Claude 4、GPT活用のベストプラクティスを網羅
*   **モダンIDE統合**: Cursor、Claude Codeの完全ガイド
*   **GitHub自動化**: MCP (Model Context Protocol) サーバーの実装と活用
*   **高速・軽量**: Jekyll + GitHub Pages による静的サイト生成

## 📚 ドキュメントカテゴリ

*   **AI・プロンプトエンジニアリング**: `_documents/_anthropic-prompt-engineering/`
    *   Claude 4の活用、思考の連鎖、構造化プロンプトなど
*   **Cursor IDE**: `_documents/_cursor/`
    *   インストール、エージェント機能、CLI活用、設定ガイド
*   **Claude Code**: `_documents/_claude-code/`
    *   IDE統合、開発効率化テクニック
*   **GitHub MCP**: `_documents/github-mcp-*/`
    *   GitHub統合、サーバー実装、プラグイン開発

## 🚀 開発とデプロイ

### 必要要件

*   Ruby: 3.3以上
*   Bundler

### ローカルでの実行

1.  依存関係のインストール:
    ```bash
    bundle install
    ```

2.  ビルドとサーブ:
    ```bash
    bundle exec jekyll serve
    ```

### デプロイ

GitHub Pagesを使用しています。`master`ブランチへのプッシュで自動的にデプロイされます。
詳細は [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) を参照してください。

## 📂 ディレクトリ構造

```
docs-manager/
├── _config.yml         # Jekyll設定
├── _documents/         # ドキュメント本体（カテゴリ別）
│   ├── _anthropic-prompt-engineering/
│   ├── _cursor/
│   └── ...
├── _includes/          # 共通部品
│   └── redirect_handler.html # クライアントサイドリダイレクト
├── _layouts/           # ページレイアウト
├── .github/
│   └── workflows/      # CI/CD設定
├── assets/             # 静的リソース
└── index.md            # トップページ
```
