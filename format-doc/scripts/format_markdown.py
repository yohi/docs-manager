import sys
import os
import re

def format_content(content):
    # 見出しの後のバックスラッシュ付きピリオドなどを修正 (\. -> .)
    content = re.sub(r'(\d+)\.', r'\1.', content)
    # 見出しの前後などの余分な太字を整理（必要に応じて）
    # (ここではユーザーの要望に合わせて最低限の整形を行う)
    return content

def is_multibyte(s):
    return len(s) != len(s.encode('ascii', 'ignore'))

def get_safe_filename(filename):
    # シンプルな変換例: 日本語を削除し、ハイフンで繋ぐ
    # 実際にはLLMが適切な名前を考える方が良いが、スクリプトでは安全な文字のみ残す
    name, ext = os.path.splitext(filename)
    safe_name = re.sub(r'[^a-zA-Z0-9\-_]+', '-', name).strip('-').lower()
    return safe_name + ext

def main():
    if len(sys.argv) < 2:
        print("Usage: python format_markdown.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a file.")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    formatted = format_content(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted)

    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)

    if is_multibyte(base_name):
        new_base = get_safe_filename(base_name)
        new_path = os.path.join(dir_name, new_base)
        # スクリプト内でのリネームは慎重に行うため、標準出力で通知する
        print(f"SUGGESTED_RENAME:{new_path}")
    
    print("SUCCESS: File formatted.")

if __name__ == "__main__":
    main()
