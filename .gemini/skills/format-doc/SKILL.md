# format-doc

This skill helps maintain consistent formatting for Markdown documentation and ensures file names are compatible with all systems by avoiding multibyte characters. It uses a coordinated approach between a Python script for low-level formatting and the LLM for context-aware structural corrections.

## Coordinated Workflow

1.  **Low-Level Formatting (Script)**:
    - Run `scripts/format_markdown.py` to handle context-independent tasks:
        - Standardize headers (e.g., `# Header` instead of `# **Header**`).
        - Remove unnecessary escapes (e.g., `1\.` to `1.`).
        - Ensure consistent spacing and basic indentation.
2.  **Structural & Context-Aware Corrections (LLM)**:
    - After running the script, the LLM reads the file to identify and fix structural issues that require context:
        - Correct the range of code blocks (especially for embedded Markdown/MDC).
        - Ensure logical consistency of heading levels across the document.
        - Resolve ambiguities where the script might have misidentified a block.
3.  **Normalize Filename (Script/LLM)**:
    - The script checks if the filename contains multibyte characters.
    - If it does, the LLM proposes a meaningful English filename.
    - Rename the file using alphanumeric characters and hyphens.

## Usage

When a user provides a file or directory:
1.  **For each file**, first execute `python3 scripts/format_markdown.py <file_path>`.
2.  **Review the output**:
    - If the script outputs `SUGGESTED_RENAME:<path>`, the LLM performs the rename using the `bash` tool (e.g., `bash(command="mv <old_path> <new_path>", description="Rename file")`).
3.  **Perform Contextual Review**: The LLM reads the formatted content and applies manual fixes (via `replace` or `write_file`) for any structural errors that the script cannot reliably handle.

## Example Triggers
- "このファイルをフォーマットして"
- "ドキュメントを整理して。ファイル名も英語にして"
- "Format this folder"
