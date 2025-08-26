---
title: GitHub MCP Server
description: GitHub MCP Serverの公式ドキュメント（動的読み込み）
order: 3
external_url: https://raw.githubusercontent.com/github/github-mcp-server/refs/heads/main/README.md
---

<div id="external-content-loading">
  <p>📄 外部コンテンツを読み込み中...</p>
</div>

<div id="external-content" style="display: none;"></div>

<div id="external-content-error" style="display: none;">
  <p>❌ コンテンツの読み込みに失敗しました。</p>
  <p><a href="{{ page.external_url }}" target="_blank">元のファイルを直接表示 ↗</a></p>
</div>

<script>
// 外部Markdownコンテンツを動的に読み込む
async function loadExternalContent() {
  const loadingDiv = document.getElementById('external-content-loading');
  const contentDiv = document.getElementById('external-content');
  const errorDiv = document.getElementById('external-content-error');
  
  try {
    // CORSプロキシを使用して外部コンテンツを取得
    const proxyUrl = 'https://api.allorigins.win/raw?url=';
    const targetUrl = '{{ page.external_url }}';
    const response = await fetch(proxyUrl + encodeURIComponent(targetUrl));
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const markdownContent = await response.text();
    
    // 簡単なMarkdown → HTMLの変換（基本的なもののみ）
    let htmlContent = markdownContent
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(?!<[hul])/gm, '<p>')
      .replace(/$(?![hul>])/gm, '</p>');
    
    // 更新日時を追加
    const updateTime = new Date().toLocaleString('ja-JP');
    htmlContent = `
      <div style="background: #f6f8fa; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <small>🔄 最終更新: ${updateTime} | 
        <a href="${targetUrl}" target="_blank">元のファイル ↗</a></small>
      </div>
      ${htmlContent}
    `;
    
    loadingDiv.style.display = 'none';
    contentDiv.innerHTML = htmlContent;
    contentDiv.style.display = 'block';
    
  } catch (error) {
    console.error('Error loading external content:', error);
    loadingDiv.style.display = 'none';
    errorDiv.style.display = 'block';
  }
}

// ページ読み込み後に実行
document.addEventListener('DOMContentLoaded', loadExternalContent);
</script>

---

**注意**: このページは外部のMarkdownファイルを動的に読み込んで表示しています。最新の内容を確認するには、ページを再読み込みしてください。
