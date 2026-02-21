---
title: "📥 Inbox - ドキュメント受信箱"
description: "整理中・レビュー待ちのドキュメント一覧"
layout: default
permalink: /inbox/
---

# 📥 Inbox - ドキュメント受信箱

このセクションには、整理中またはレビュー待ちのドキュメントが含まれています。ディレクトリ構成の変更（カテゴリ分け）に対応しました。

---

## 📚 ドキュメント一覧 (カテゴリ別)

{% assign inbox_docs = site.inbox | sort: 'path' %}
{% assign grouped_docs = inbox_docs | group_by_exp: "item", "item.path | split: '/' | slice: 1 | first" %}

{% if inbox_docs.size > 0 %}
<div class="inbox-categories">
  {% for group in grouped_docs %}
    {% assign category_name = group.name %}
    {% if category_name contains ".md" %}
      {% assign category_display = "未分類 / その他" %}
    {% else %}
      {% assign category_display = category_name | replace: "-", " " | capitalize %}
    {% endif %}

    <section class="category-group" style="margin-bottom: 2rem; border-left: 4px solid #eee; padding-left: 1rem;">
      <h2 style="color: #2c3e50;">📁 {{ category_display }}</h2>
      <div class="inbox-documents" style="display: grid; gap: 1rem; margin-top: 1rem;">
        {% assign sorted_items = group.items | sort: 'title' %}
        {% for doc in sorted_items %}
        <div class="document-item" style="background: #f9f9f9; padding: 1rem; border-radius: 8px;">
          <h3 style="margin-top: 0;">
            <a href="{{ site.baseurl }}{{ doc.url }}">{{ doc.title | default: doc.name }}</a>
          </h3>
          {% if doc.description %}
          <p class="description" style="margin-bottom: 0.5rem; color: #666;">{{ doc.description }}</p>
          {% endif %}
          <p class="meta" style="font-size: 0.85rem; color: #999; margin-bottom: 0;">
            パス: <code>{{ doc.path | replace: "_inbox/", "" }}</code>
            {% if doc.date %} | 作成日: {{ doc.date | date: "%Y年%m月%d日" }}{% endif %}
          </p>
        </div>
        {% endfor %}
      </div>
    </section>
  {% endfor %}
</div>

<br>
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
