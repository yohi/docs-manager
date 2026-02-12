---
title: "📥 Inbox - ドキュメント受信箱"
description: "整理中・レビュー待ちのドキュメント一覧"
layout: default
permalink: /inbox/
---

# 📥 Inbox - ドキュメント受信箱

このセクションには、整理中またはレビュー待ちのドキュメントが含まれています。

---

## 📚 ドキュメント一覧

{% assign inbox_docs = site.inbox | sort: 'title' %}
{% if inbox_docs.size > 0 %}
<div class="inbox-documents">
  {% for doc in inbox_docs %}
  <div class="document-item">
    <h3>
      <a href="{{ site.baseurl }}{{ doc.url }}">{{ doc.title | default: doc.name }}</a>
    </h3>
    {% if doc.description %}
    <p class="description">{{ doc.description }}</p>
    {% endif %}
    {% if doc.date %}
    <p class="meta">作成日: {{ doc.date | date: "%Y年%m月%d日" }}</p>
    {% endif %}
  </div>
  {% endfor %}
</div>

**総ドキュメント数**: {{ inbox_docs.size }}件

{% else %}
<p><em>現在、Inboxにドキュメントはありません。</em></p>
{% endif %}

---

## 📌 このセクションについて

### 🎯 目的
- **一時保管**: 新規作成されたドキュメントの一時的な保管場所
- **レビュー待ち**: 正式な分類・配置前のレビュー段階
- **整理中**: カテゴリ分けや構造化の作業中

### 📋 ワークフロー
1. **受信**: 新しいドキュメントはまずInboxに配置
2. **レビュー**: 内容の確認と品質チェック
3. **分類**: 適切なカテゴリへの移動
4. **公開**: メインドキュメントセクションへの統合

---

[🏠 トップページに戻る]({{ site.baseurl }}/)
