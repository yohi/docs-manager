---
title: GitHub MCP Server (即座リダイレクト版)
description: GitHub MCP Server公式ドキュメントへ即座にリダイレクト
order: 7
redirect_to: https://github.com/github/github-mcp-server/blob/main/README.md
---

<script>
// 即座にリダイレクト（ページ読み込み開始と同時）
window.location.replace('{{ page.redirect_to }}');
</script>

<!-- JavaScriptが無効な環境用のフォールバック -->
<noscript>
    <meta http-equiv="refresh" content="0;url={{ page.redirect_to }}">
</noscript>

<!-- フォールバック表示（通常は表示されない） -->
<div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
    <h2>🔄 リダイレクト中...</h2>
    <p>自動でリダイレクトされない場合は、<a href="{{ page.redirect_to }}">こちらをクリック</a>してください。</p>
</div>
