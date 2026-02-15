import sys
import os
import re

def format_content(content):
    # 1. バックスラッシュエスケープされたドットをアンエスケープ (\. -> .)
    content = re.sub(r'\\(\.)', r'\1', content)

    # 2. 見出しの標準化: # **Header** -> # Header
    content = re.sub(r'^(#+)\s*\*\*([^*]+)\*\*', r'\1 \2', content, flags=re.MULTILINE)
    
    # 3. 見出しの書式修正: #Header -> # Header (スペース不足)
    content = re.sub(r'^(#+)([^\s#])', r'\1 \2', content, flags=re.MULTILINE)
    
    # 4. 見出しの行頭インデント除去
    content = re.sub(r'^\s+(#+\s)', r'\1', content, flags=re.MULTILINE)
    
    # 5. 正規表現内の未エスケープスラッシュを修正 (JavaScript/TypeScript)
    # Note: Removed overly aggressive replacements that were breaking URLs.
    content = re.sub(r'/\^/', r'/^\\/', content)
    
    # 6. YAMLインデントの修正: steps配下のアクションが正しくインデントされていない
    content = re.sub(r'^(\s+steps:\s*\n)(\s*)(-\s+uses:)', r'\1\2  \3', content, flags=re.MULTILINE)
    
    # 7. 無効なJSON構文の修正: "data": の後に値がない
    content = re.sub(r'"data":\s*$', r'"data": []', content, flags=re.MULTILINE)
    
    # 8. コードブロックのフェンス追加 (TypeScript/JavaScriptが裸で書かれている場合)
    content = re.sub(r'^(TypeScript|JavaScript)\s*\n([^\n`])', r'```ts\n\2', content, flags=re.MULTILINE)

    return content

def is_multibyte(s):
    return len(s) != len(s.encode('ascii', 'ignore'))

def get_safe_filename(filename):
    name, ext = os.path.splitext(filename)
    safe_name = re.sub(r'[^a-zA-Z0-9\-_]+', '-', name).strip('-').lower()
    if not safe_name:
        safe_name = "document"
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