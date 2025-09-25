# 🚀 GitHub Pages デプロイメント チェックリスト

## 📋 事前確認項目

### ✅ **必須ファイル確認**
- [ ] `_config.yml` - Collections設定が統一されている
- [ ] `404.html` - カスタム404ページが存在
- [ ] `_includes/redirect_handler.html` - リダイレクト機能が実装
- [ ] `Gemfile` - 必要なプラグインが含まれている
- [ ] `robots.txt` - SEO設定が適切
- [ ] `.github/workflows/link-validation.yml` - CI/CD設定

### 📁 **ディレクトリ構造確認**
- [ ] `_documents/_anthropic-prompt-engineering/index.md` 存在
- [ ] `_documents/_cursor/index.md` 存在
- [ ] `_documents/_claude-code/index.md` 存在
- [ ] すべてのサブディレクトリに適切なindex.mdが配置

### 🔗 **リンク形式確認**
- [ ] メインナビゲーションが `{{ site.baseurl }}/documents/*/index/` 形式
- [ ] 相対パスリンクが絶対パスに変更済み
- [ ] `.html` 拡張子が除去済み

---

## 🚀 **デプロイメント手順**

### **Step 1: ローカルテスト**
```bash
# Jekyll ビルドテスト
bundle install
bundle exec jekyll build --verbose

# リンク検証
bundle exec htmlproofer _site --internal-domains="localhost"
```

### **Step 2: GitHub リポジトリへプッシュ**
```bash
git add .
git commit -m "🔧 Fix 404 errors: Collections config, redirects, and link validation"
git push origin master
```

### **Step 3: GitHub Pages 設定確認**
1. リポジトリ設定 → Pages
2. Source: Deploy from a branch
3. Branch: master / (root)
4. GitHub Pages サイトの有効化確認

### **Step 4: デプロイ完了確認**
- [ ] GitHub Actions ワークフローが成功
- [ ] GitHub Pages サイトが公開済み
- [ ] SSL証明書が適用済み

---

## 🧪 **デプロイ後テスト**

### **主要テストページ**
1. **トップページ**: <https://y_ohi.github.io/docs-manager/>
2. **テストページ**: <https://y_ohi.github.io/docs-manager/test-links.html>
3. **404ページ**: <https://y_ohi.github.io/docs-manager/nonexistent-page/>

### **✅ 機能テスト項目**

#### **1. メインナビゲーション**
- [ ] [Anthropic プロンプトエンジニアリング](https://y_ohi.github.io/docs-manager/documents/_anthropic-prompt-engineering/index/)
- [ ] [Cursor Documentation](https://y_ohi.github.io/docs-manager/documents/_cursor/index/)
- [ ] [Claude Code Documentation](https://y_ohi.github.io/docs-manager/documents/_claude-code/index/)
- [ ] [GitHub MCP Server](https://y_ohi.github.io/docs-manager/documents/github-mcp-index/)

#### **2. リダイレクト機能**
- [ ] <https://y_ohi.github.io/docs-manager/documents/_anthropic-prompt-engineering/> → /index/
- [ ] <https://y_ohi.github.io/docs-manager/documents/_cursor/> → /index/
- [ ] .html拡張子付きURL → 拡張子なしURL

#### **3. 404エラーハンドリング**
- [ ] 存在しないページで適切な404ページ表示
- [ ] 自動リダイレクト機能の動作
- [ ] ナビゲーションリンクの提供

#### **4. SEO・パフォーマンス**
- [ ] sitemap.xml が生成されている
- [ ] robots.txt が適切に配置
- [ ] メタデータが正しく設定

### **📊 期待結果**
- 404エラー率: **95%削減** (5件 → ≤1件)
- ページロード時間: **2秒以内**
- リダイレクト成功率: **100%**
- SEO スコア: **90点以上**

---

## 🚨 **トラブルシューティング**

### **よくある問題と解決策**

#### **❌ GitHub Pages ビルドエラー**
```yaml
# _config.yml の確認
safe: true
plugins:
  - jekyll-sitemap  # GitHub Pages で許可されているプラグインのみ
```

#### **❌ リンクが404エラー**
1. `_config.yml` のpermalink設定確認
2. ファイルパスの大文字小文字確認
3. `_includes/redirect_handler.html` の動作確認

#### **❌ リダイレクトが動作しない**
1. JavaScript が有効か確認
2. `redirect_handler.html` がincludeされているか確認
3. ブラウザキャッシュをクリア

#### **❌ sitemap.xml が生成されない**
1. `jekyll-sitemap` プラグインの有効化確認
2. `_config.yml` のサイトマップ設定確認

---

## 📈 **監視・メンテナンス**

### **定期確認項目**
- [ ] **週次**: GitHub Actions リンク検証結果
- [ ] **月次**: Google Search Console での404エラー確認
- [ ] **四半期**: サイト全体のパフォーマンス評価

### **アラート設定**
- GitHub Actions ワークフロー失敗時の通知
- 404エラー急増時のアラート
- サイトダウン時の監視

---

## ✅ **完了確認**

全ての項目をテストし、以下を確認してください：

- [ ] **機能性**: すべてのリンクが正常動作
- [ ] **パフォーマンス**: ページロード時間が適切
- [ ] **SEO**: 検索エンジン最適化が有効
- [ ] **ユーザビリティ**: 404エラー時の適切な案内
- [ ] **保守性**: CI/CDによる自動検証

---

**🎯 成功基準**: GitHub Pages サイトの404エラーが根本解決され、安定したナビゲーション体験を提供できること

**📅 最終更新**: {{ site.time | date: "%Y年%m月%d日" }}
