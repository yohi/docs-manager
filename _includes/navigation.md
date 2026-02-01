<!-- 共通ナビゲーション -->
<nav class="site-navigation" style="background: #f6f8fa; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
  <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
    <strong>🏠 <a href="{{ site.baseurl }}/">ホーム</a></strong>
    <span style="color: #d0d7de;">|</span>

    <div style="display: flex; flex-wrap: wrap; gap: 12px;">
      <a href="{{ site.baseurl }}/documents/anthropic-prompt-engineering/index/" style="color: #0969da; text-decoration: none;">
        🤖 Anthropic
      </a>

      <a href="{{ site.baseurl }}/documents/claude-code/index/" style="color: #0969da; text-decoration: none;">
        💻 Claude Code
      </a>

      <a href="{{ site.baseurl }}/documents/cursor/index/" style="color: #0969da; text-decoration: none;">
        🚀 Cursor
      </a>

      <a href="{{ site.baseurl }}/documents/github-mcp-index/" style="color: #0969da; text-decoration: none;">
        🔗 GitHub MCP
      </a>
    </div>

    <span style="color: #d0d7de;">|</span>

    <div style="display: flex; flex-wrap: wrap; gap: 12px;">
      <a href="{{ site.baseurl }}/documents/getting-started/" style="color: #cf222e; text-decoration: none;">
        📖 はじめに
      </a>

      <a href="{{ site.baseurl }}/documents/advanced-feature/" style="color: #cf222e; text-decoration: none;">
        ⚡ 高度な機能
      </a>
    </div>
  </div>
</nav>

<style>
.site-navigation a:hover {
  text-decoration: underline !important;
}

@media (max-width: 768px) {
  .site-navigation div {
    flex-direction: column;
    align-items: flex-start;
  }

  .site-navigation span {
    display: none;
  }
}
</style>
