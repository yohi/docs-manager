---
name: format-doc
description: Format Markdown files for readability and ensure filenames use only alphanumeric characters. Use when handling new documents in the Inbox or organizing project documentation.
---

# format-doc

This skill helps maintain consistent formatting for Markdown documentation and ensures file names are compatible with all systems by avoiding multibyte characters.

## Workflow

1. **Format Content**: Read the specified Markdown file and apply formatting rules:
    - Standardize headers (e.g., ensure `# Header` instead of `# **Header**`).
    - Remove unnecessary escapes (e.g., change `1\.` to `1.`).
    - Ensure consistent spacing around headers and lists.
2. **Normalize Filename**: Check if the filename contains multibyte characters (Japanese, etc.).
    - If it does, propose a new English filename that reflects the content.
    - Rename the file using half-width alphanumeric characters and hyphens.

## Usage

When a user provides a file or directory:
- For each file, run `scripts/format_markdown.py`.
- If the script outputs `SUGGESTED_RENAME:<path>`, perform the rename using `run_shell_command`.
- If a directory is provided, repeat the process for all `.md` files within it.

## Example Triggers
- "このファイルをフォーマットして"
- "ドキュメントを整理して。ファイル名も英語にして"
- "Format this folder"