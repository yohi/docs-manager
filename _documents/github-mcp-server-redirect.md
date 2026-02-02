---
title: GitHub MCP Server (リダイレクト版)
description: GitHub MCP Server公式ドキュメントへ自動リダイレクト
order: 6
redirect_to: https://github.com/github/github-mcp-server/blob/main/README.md
permalink: /documents/github-mcp-server-redirect/
---

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    
    <!-- Meta Refresh リダイレクト（3秒後） -->
    <meta http-equiv="refresh" content="3;url={{ page.redirect_to }}">
    
    <!-- SEO対策：検索エンジンにリダイレクト先を伝える -->
    <link rel="canonical" href="{{ page.redirect_to }}">
    
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
            background: #f6f8fa;
        }
        .redirect-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #0366d6;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .countdown {
            font-size: 24px;
            color: #0366d6;
            font-weight: bold;
            margin: 20px 0;
        }
        .direct-link {
            margin-top: 30px;
            padding: 15px;
            background: #f1f8ff;
            border-radius: 5px;
        }
        .btn {
            display: inline-block;
            padding: 8px 16px;
            background: #0366d6;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px;
        }
        .btn:hover {
            background: #0256cc;
        }
    </style>
</head>
<body>
    <div class="redirect-box">
        <h1>🔄 リダイレクト中...</h1>
        
        <div class="spinner"></div>
        
        <p>GitHub MCP Server公式ドキュメントに移動します</p>
        
        <div class="countdown" id="countdown">3</div>
        
        <div class="direct-link">
            <p>自動リダイレクトしない場合は、以下のリンクをクリックしてください：</p>
            <a href="{{ page.redirect_to }}" class="btn" target="_blank">
                📄 GitHub MCP Server README を開く
            </a>
        </div>
        
        <p><small>
            <a href="{{ '/' | relative_url }}">← ホームに戻る</a> | 
            <a href="{{ page.redirect_to }}" target="_blank">新しいタブで開く ↗</a>
        </small></p>
    </div>

    <script>
        // JavaScript カウントダウンとリダイレクト
        let countdown = 3;
        const countdownElement = document.getElementById('countdown');
        
        const timer = setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {
                clearInterval(timer);
                countdownElement.textContent = 'リダイレクト中...';
                // 即座にリダイレクト（meta refreshのバックアップ）
                window.location.href = '{{ page.redirect_to }}';
            }
        }, 1000);
        
        // ページ読み込み完了後、さらに高速にリダイレクト（オプション）
        // window.addEventListener('load', () => {
        //     setTimeout(() => {
        //         window.location.href = '{{ page.redirect_to }}';
        //     }, 100);
        // });
    </script>
</body>
</html>
