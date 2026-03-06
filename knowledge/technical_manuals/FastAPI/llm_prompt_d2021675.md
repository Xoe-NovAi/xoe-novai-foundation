---
title: Llm Prompt
service: FastAPI
source_urls: ["/tmp/tmp2aqkafzm/repo/docs/ja/llm-prompt.md"]
scraped_at: 2026-02-17T00:28:19.478026
content_hash: d202167562350b9af009649462c9504aece71c9457b7d1e1f72c39b7a298b049
size_kb: 1.19
---

### Target language

Translate to Japanese (日本語).

Language code: ja.

### Grammar and tone

- Use polite, instructional Japanese (です/ます調).
- Keep the tone concise and technical (match existing Japanese FastAPI docs).

### Headings

- Follow the existing Japanese style: short, descriptive headings (often noun phrases), e.g. 「チェック」.
- Do not add a trailing period at the end of headings.

### Quotes

- Prefer Japanese corner brackets 「」 in normal prose when quoting a term.
- Do not change quotes inside inline code, code blocks, URLs, or file paths.

### Ellipsis

- Keep ellipsis style consistent with existing Japanese docs (commonly `...`).
- Never change `...` in code, URLs, or CLI examples.

### Preferred translations / glossary

Use the following preferred translations when they apply in documentation prose:

- request (HTTP): リクエスト
- response (HTTP): レスポンス
- path operation: path operation (do not translate)

### `///` admonitions

1) Keep the admonition keyword in English (do not translate `note`, `tip`, etc.).
2) If a title is present, prefer these canonical titles:

- `/// note | 備考`
- `/// note | 技術詳細`
- `/// tip | 豆知識`
- `/// warning | 注意`
- `/// info | 情報`
- `/// check | 確認`
- `/// danger | 警告`
