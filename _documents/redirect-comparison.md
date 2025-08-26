---
title: リダイレクト方法の比較
description: 外部URLへのリダイレクト実装方法の比較とデモ
order: 9
---

# 🔄 リダイレクト方法の比較

このページでは、GitHub Pagesで外部URLにリダイレクトする様々な方法を比較できます。

## 📋 実装方法一覧

### 1. Meta Refresh + JavaScript（推奨）
- **ファイル**: [github-mcp-server-redirect.md](github-mcp-server-redirect/)
- **特徴**: カウントダウン表示、SEO対応、フォールバック完備
- **対応**: 全ブラウザ、JavaScript無効環境にも対応
- **速度**: 3秒後リダイレクト（カスタマイズ可能）

### 2. 即座リダイレクト
- **ファイル**: [github-mcp-server-instant.md](github-mcp-server-instant/)
- **特徴**: 読み込み開始と同時にリダイレクト
- **対応**: JavaScript必須、noscriptフォールバック有り
- **速度**: 即座（<100ms）

### 3. Jekyll Plugin（標準）
- **ファイル**: [github-mcp-server-plugin.md](github-mcp-server-plugin/)
- **特徴**: Jekyll標準機能、HTTP 301リダイレクト
- **対応**: GitHub Pages完全対応
- **速度**: サーバーレベルで即座

## 🎯 推奨される使用場面

| 方法 | 使用場面 | メリット | デメリット |
|------|----------|----------|------------|
| **Meta Refresh版** | 一般的な用途 | ユーザビリティ高、説明可能 | 若干の遅延 |
| **即座リダイレクト版** | 透明なリダイレクト | 最高速度 | JavaScript依存 |
| **Plugin版** | SEO重視 | HTTP標準準拠 | 設定が必要 |

## 🔗 外部URLリンク集

すべての版で以下のURLにリダイレクトします：

**リダイレクト先**: [GitHub MCP Server README](https://github.com/github/github-mcp-server/blob/main/README.md)

## 🧪 テスト方法

1. 各リンクをクリックしてリダイレクトをテスト
2. ブラウザの開発者ツールでNetworkタブを確認
3. JavaScriptを無効にしてフォールバック動作を確認

---

**注意**: リダイレクトページは新しいタブで開くことをお勧めします。
