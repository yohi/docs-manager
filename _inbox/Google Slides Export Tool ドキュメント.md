これまでの議論と実装内容を体系的に整理し、**「Google Slides Export Tool」の完全な技術ドキュメント（README）** としてMarkdown形式でまとめました。

これをそのままコピーして、README.md として保存したり、チームへの共有ドキュメントとしてご利用ください。

# ---

**Google Slides Export Tool (GAS)**

Googleスライドの特定のページ、または全てのページを**高画質PNG**または**PDF**として個別に書き出し、Googleドライブに自動保存するGoogle Apps Script (GAS) ツールです。

標準機能にはない「選択したスライドのみの画像化」や「一括PDF化」を、サイドバーから直感的に実行できます。

## **🚀 特徴**

* **GUI操作:** スライド右側にサイドバーを表示し、クリックのみで操作可能。  
* **範囲指定:** 「現在選択中のスライド」または「すべてのスライド」を選択可能。  
* **フォーマット選択:**  
  * **PNG:** Google Slides APIを使用し、高解像度の画像を高速に生成。  
  * **PDF:** ベクター品質を維持したまま、1スライド＝1ファイルとして生成。  
* **安定性:** 複数のGoogleアカウントログイン時に発生する Permission Denied (Storage Error) を回避するデータ洗浄ロジックを搭載。  
* **保存先:** マイドライブ直下に日時付きフォルダを自動作成して保存（権限エラーを防止）。

## ---

**🛠 導入手順 (Installation)**

このスクリプトは、Googleスライドの「拡張機能」として動作します。以下の手順でセットアップしてください。

### **1\. スクリプトエディタを開く**

1. 対象のGoogleスライドを開きます。  
2. メニューの **\[拡張機能\]** \> **\[Apps Script\]** をクリックします。

### **2\. Google Slides API サービスの追加**

1. エディタ左側の「サービス」の横にある **\[ \+ \]** ボタンをクリックします。  
2. **Google Slides API** を選択し、\[追加\] をクリックします（識別子は Slides のままでOK）。

### **3\. マニフェストファイル (appsscript.json) の設定**

**重要:** この手順を行わないと権限エラーになります。

1. 左側メニューの **\[プロジェクトの設定\]** (歯車アイコン⚙️) をクリックします。  
2. 「全般設定」の **\[「appsscript.json」マニフェスト ファイルをエディタで表示する\]** にチェックを入れます。  
3. 左側メニューの **\[エディタ\]** (\<code\>\< \>\</code\>) に戻ります。  
4. ファイル一覧に表示された appsscript.json を開き、以下のコードで**完全に上書き**します。

JSON

{  
  "timeZone": "Asia/Tokyo",  
  "dependencies": {  
    "enabledAdvancedServices": \[{  
      "userSymbol": "Slides",  
      "serviceId": "slides",  
      "version": "v1"  
    }\]  
  },  
  "exceptionLogging": "STACKDRIVER",  
  "oauthScopes": \[  
    "https://www.googleapis.com/auth/presentations",  
    "https://www.googleapis.com/auth/drive",  
    "https://www.googleapis.com/auth/script.external\_request",  
    "https://www.googleapis.com/auth/script.container.ui"  
  \],  
  "runtimeVersion": "V8"  
}

### **4\. サーバーサイドコード (Code.gs) の実装**

1. ファイル一覧の Code.gs を開き、以下のコードで**完全に上書き**します。

JavaScript

/\*\*  
 \* @fileoverview スライド書き出しツール (Final Production Version)  
 \* 公式Slides APIによる高速化と、Blob再構築による保存エラー回避を実装した決定版。  
 \*/

// \--- UI初期化 \---  
const onOpen \= () \=\> {  
  SlidesApp.getUi()  
    .createMenu('スライド書き出し')  
    .addItem('サイドバーを表示', 'showSidebar')  
    .addToUi();  
};

const showSidebar \= () \=\> {  
  const html \= HtmlService.createHtmlOutputFromFile('Sidebar')  
    .setTitle('スライド書き出しツール')  
    .setWidth(300);  
  SlidesApp.getUi().showSidebar(html);  
};

// \--- メイン処理 \---  
const processExport \= (config) \=\> {  
  try {  
    const presentation \= SlidesApp.getActivePresentation();  
    const presentationName \= presentation.getName();  
      
    // 1\. 対象スライドの特定  
    let targetSlides \= \[\];  
    if (config.scope \=== 'SELECTED') {  
      const selection \= presentation.getSelection();  
      const pageRange \= selection.getPageRange();  
      if (\!pageRange) throw new Error('スライドが選択されていません。');  
      targetSlides \= pageRange.getPages();  
    } else {  
      targetSlides \= presentation.getSlides();  
    }  
      
    if (targetSlides.length \=== 0) throw new Error('対象が見つかりません。');

    // 2\. 保存先フォルダの作成 (マイドライブ固定で安全策)  
    const rootFolder \= DriveApp.getRootFolder();  
    const timeString \= Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyyMMdd\_HHmm');  
    const folderName \= \`Export\_${presentationName}\_${timeString}\`;  
    const outputFolder \= rootFolder.createFolder(folderName);

    // 3\. 書き出し実行  
    targetSlides.forEach((slide) \=\> {  
      const allSlides \= presentation.getSlides();  
      const pageIndex \= allSlides.findIndex(s \=\> s.getObjectId() \=== slide.getObjectId()) \+ 1;  
      const pageNumStr \= ('00' \+ pageIndex).slice(-2);  
      const fileName \= \`${presentationName}\_${pageNumStr}\`;  
      const objectId \= slide.getObjectId();

      if (config.format \=== 'PNG') {  
        exportAsPng\_(presentation.getId(), objectId, fileName, outputFolder);  
      } else {  
        exportAsPdf\_(presentation.getId(), objectId, fileName, outputFolder);  
      }  
        
      // API制限回避のための微小な待機  
      Utilities.sleep(200);  
    });

    return {  
      success: true,  
      message: \`${targetSlides.length} 枚書き出し完了。\\nフォルダ: ${folderName}\`,  
      folderUrl: outputFolder.getUrl()  
    };

  } catch (e) {  
    console.error(e);  
    return { success: false, message: \`エラー: ${e.message}\` };  
  }  
};

/\*\*  
 \* \[高速版\] 公式APIを使用してPNGを取得し、安全に保存  
 \*/  
const exportAsPng\_ \= (presentationId, pageObjectId, fileName, folder) \=\> {  
  try {  
    // 1\. 公式APIでサムネイルURLを取得 (Advanced Service)  
    const thumbnail \= Slides.Presentations.Pages.getThumbnail(presentationId, pageObjectId, {  
      'thumbnailProperties.thumbnailSize': 'LARGE'  
    });

    // 2\. 画像データの取得  
    const response \= UrlFetchApp.fetch(thumbnail.contentUrl, { muteHttpExceptions: true });  
    if (response.getResponseCode() \!== 200) throw new Error('画像取得失敗');

    // 3\. 【重要】Blobの再構築 (Storage Error回避策)  
    // 外部サーバーからのStreamを断ち切り、純粋なデータとして再定義する  
    const cleanBlob \= Utilities.newBlob(response.getContent(), 'image/png', \`${fileName}.png\`);  
      
    folder.createFile(cleanBlob);

  } catch (e) {  
    console.warn(\`PNG Export Warning (ID:${pageObjectId}): ${e.message}\`);  
    throw e;  
  }  
};

/\*\*  
 \* \[確実版\] 一時ファイル方式によるPDF保存  
 \*/  
const exportAsPdf\_ \= (presentationId, pageObjectId, fileName, folder) \=\> {  
  // 元ファイルをコピー (一時ファイル)  
  const originalFile \= DriveApp.getFileById(presentationId);  
  const tempFile \= originalFile.makeCopy(\`Temp\_${fileName}\`, folder);  
    
  try {  
    const tempDeck \= SlidesApp.openById(tempFile.getId());  
    const slides \= tempDeck.getSlides();  
      
    // 不要スライドの削除  
    for (let i \= slides.length \- 1; i \>= 0; i--) {  
      if (slides\[i\].getObjectId() \!== pageObjectId) {  
        slides\[i\].remove();  
      }  
    }  
    tempDeck.saveAndClose();  
      
    // PDF化して保存  
    const pdfBlob \= tempFile.getAs(MimeType.PDF);  
    const cleanPdf \= Utilities.newBlob(pdfBlob.getBytes(), MimeType.PDF, \`${fileName}.pdf\`);  
    folder.createFile(cleanPdf);  
      
  } finally {  
    // 確実にゴミ箱へ  
    tempFile.setTrashed(true);  
  }  
};

### **5\. フロントエンド (Sidebar.html) の作成**

1. ファイル一覧の **\[ \+ \]** \> **\[HTML\]** を選択し、ファイル名を Sidebar とします。  
2. 以下のコードを貼り付けます。

HTML

\<\!DOCTYPE **html**\>  
\<html\>  
  \<head\>  
    \<base target\="\_top"\>  
    \<link rel\="stylesheet" href\="https://ssl.gstatic.com/docs/script/css/add-ons1.css"\>  
    \<style\>  
      body { padding: 15px; font-family: 'Google Sans', Roboto, sans-serif; }  
      .section { margin-bottom: 20px; }  
      .label-title { font-weight: bold; margin-bottom: 10px; display: block; color: \#202124; }  
      .radio-group label { display: block; margin-bottom: 8px; cursor: pointer; }  
      .btn-primary { width: 100%; margin-top: 10px; background-color: \#1a73e8; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; }  
      .btn-primary:hover { background-color: \#1557b0; }  
      .btn-primary:disabled { background-color: \#ccc; cursor: not-allowed; }  
      \#status { margin-top: 15px; font-size: 13px; color: \#666; word-break: break-all; }  
      .loader { display: none; border: 3px solid \#f3f3f3; border-top: 3px solid \#1a73e8; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; margin: 10px auto; }  
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }  
      .warning { font-size: 11px; color: \#d93025; margin-top: 5px; display: none; }  
    \</style\>  
  \</head\>  
  \<body\>  
    \<div class\="section"\>  
      \<span class\="label-title"\>範囲\</span\>  
      \<div class\="radio-group"\>  
        \<label\>\<input type\="radio" name\="scope" value\="SELECTED" checked\> 選択中のスライドのみ\</label\>  
        \<label\>\<input type\="radio" name\="scope" value\="ALL"\> すべてのスライド\</label\>  
      \</div\>  
    \</div\>

    \<div class\="section"\>  
      \<span class\="label-title"\>形式\</span\>  
      \<div class\="radio-group"\>  
        \<label\>\<input type\="radio" name\="format" value\="PNG" checked onchange\="toggleWarning()"\> PNG 画像 (高速)\</label\>  
        \<label\>\<input type\="radio" name\="format" value\="PDF" onchange\="toggleWarning()"\> PDF ファイル\</label\>  
      \</div\>  
      \<div id\="pdf-warning" class\="warning"\>※PDFは処理に時間がかかります\</div\>  
    \</div\>

    \<button id\="runBtn" class\="btn-primary" onclick\="runExport()"\>書き出し開始\</button\>  
    \<div class\="loader" id\="loader"\>\</div\>  
    \<div id\="status"\>\</div\>

    \<script\>  
      function toggleWarning() {  
        const format \= document.querySelector('input\[name="format"\]:checked').value;  
        document.getElementById('pdf-warning').style.display \= (format \=== 'PDF') ? 'block' : 'none';  
      }

      function runExport() {  
        const btn \= document.getElementById('runBtn');  
        const loader \= document.getElementById('loader');  
        const status \= document.getElementById('status');  
          
        btn.disabled \= true;  
        btn.textContent \= '処理中...';  
        loader.style.display \= 'block';  
        status.textContent \= '準備中...';  
        status.style.color \= '\#666';

        const config \= {  
          scope: document.querySelector('input\[name="scope"\]:checked').value,  
          format: document.querySelector('input\[name="format"\]:checked').value  
        };

        google.script.run  
          .withSuccessHandler(res \=\> {  
            loader.style.display \= 'none';  
            btn.disabled \= false;  
            btn.textContent \= '書き出し開始';  
            if (res.success) {  
              status.innerHTML \= \`\<span style="color:green"\>✔ ${res.message}\</span\>\<br\>\<br\>\<a href="${res.folderUrl}" target="\_blank"\>フォルダを開く\</a\>\`;  
            } else {  
              status.innerHTML \= \`\<span style="color:red"\>✘ ${res.message}\</span\>\`;  
            }  
          })  
          .withFailureHandler(err \=\> {  
            loader.style.display \= 'none';  
            btn.disabled \= false;  
            btn.textContent \= '書き出し開始';  
            status.innerHTML \= \`\<span style="color:red"\>システムエラー: ${err.message}\</span\>\`;  
          })  
          .processExport(config);  
      }  
    \</script\>  
  \</body\>  
\</html\>

## ---

**🖥 使い方 (Usage)**

1. **スライドを開く:** スクリプトを導入したスライドを開きます（導入直後の場合はブラウザを一度リロードしてください）。  
2. **メニュー選択:** 上部メニューに **「スライド書き出し」** が追加されるので、**「サイドバーを表示」** をクリックします。  
3. **認証 (初回のみ):** 権限の許可を求められた場合、画面の指示に従って許可してください。  
4. **実行:** サイドバーで範囲と形式を選択し、**「書き出し開始」** をクリックします。  
5. **完了:** 処理が完了すると完了メッセージとフォルダへのリンクが表示されます。

## ---

**⚠️ トラブルシューティング**

### **Q. PERMISSION\_DENIED または Storage Error が発生する**

Google Chromeで「複数のGoogleアカウント」にログインしている場合に発生する仕様上の不具合です。

**解決策:**

* Chromeの **シークレットウィンドウ (Incognito Window)** でスライドを開き、実行してください。  
* または、Chromeのユーザープロファイルを切り替えて、単一のアカウントでブラウザを利用してください。

### **Q. PDF書き出しが遅い**

仕様です。PDF書き出しは「一時ファイルの作成→ページ削除→PDF化→削除」という工程を経るため、1枚あたり数秒かかります。大量の枚数を処理する場合は、PNG形式を推奨します。