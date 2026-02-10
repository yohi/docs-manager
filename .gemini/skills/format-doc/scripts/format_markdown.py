import sys
import os
import re

def format_content(content):
    # 1. 見出しの後のバックスラッシュ付きピリオドなどを修正 (\. -> .)
    content = re.sub(r'(\d+)\.', r'\1.', content)

    # 2. 見出しの標準化: # **Header** -> # Header
    # 文中の太字と区別するため、行頭の見出し記号の直後にある太字を対象にする
    content = re.sub(r'^(#+)\s*\*\*([^*]+)\*\*', r'\1 \2', content, flags=re.MULTILINE)

    # 3. リスト項目の前後の余分な空白などを整理 (低レイヤーの整形)
    # (将来的に共通の低レイヤー処理をここに追加していく)

    return content

def is_multibyte(s):
    return len(s) != len(s.encode('ascii', 'ignore'))

def get_safe_filename(filename):
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
        print(f"SUGGESTED_RENAME:{new_path}")
    
    print("SUCCESS: File formatted.")

if __name__ == "__main__":
    main()