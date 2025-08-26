# こんにちは、GitHub Pages！

これは私の新しいウェブサイトです。

- GitHubリポジトリから直接公開されています。
- Markdownで簡単にページを作成できます。

# ドキュメント一覧

このサイトの公式ドキュメントです。

## コンテンツ
<ul>
  {% for doc in site.documents %}
    <li>
      <a href="{{ doc.url | relative_url }}">{{ doc.title | default: doc.name }}</a>
      {% if doc.description %}
        <p>{{ doc.description }}</p>
      {% endif %}
    </li>
  {% endfor %}
</ul>

{% if site.documents.size == 0 %}
<p><em>ドキュメントがまだありません。_documentsフォルダにMarkdownファイルを追加してください。</em></p>
{% endif %}
