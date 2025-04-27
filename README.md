# Reverse Engineering StackExchange Dataset Processor

This project processes and prepares Reverse Engineering StackExchange data for LLM training.

It includes scraping questions, scraping each question's full details, converting the content into Markdown format, and assembling a final structured dataset.

---

## 📂 Project Structure

```
reverseengineering/
├── reverseengineering_html/         # (Optional) Raw scraped HTML files
├── reverseengineering_markdown/     # Cleaned JSONs (content and text converted to Markdown)
├── reverseengineering_text/         # (Optional) Pure text versions
├── stackexchange_scraper.py          # Scrapes list of questions
├── stackexchange_question_scraper.py # Scrapes full question content into separate JSON files
├── markdown_and_assemble.py          # Converts and assembles all cleaned JSONs into final dataset
├── stackexchange_questions.json      # Output of question list scraper
├── reverseengineering_markdown.json  # Final merged dataset for LLM feeding
└── README.md
```

---

## ⚙️ Script Descriptions

| Script | Purpose |
|:---|:---|
| `stackexchange_scraper.py` | Scrapes a **list of questions** from Reverse Engineering StackExchange and outputs to `stackexchange_questions.json`. |
| `stackexchange_question_scraper.py` | Scrapes **full individual question content** (with raw HTML inside) into **separate JSON files** under the `reverseengineering/` folder (for debugging purposes). |
| `markdown_and_assemble.py` | **Converts** all `"content"` and `"text"` fields from **raw HTML to Markdown**, then **assembles** all questions into a single file `reverseengineering_markdown.json` for **feeding to LLMs**. |

---

## 🚀 Workflow

### Step 1: Scrape Question List

```bash
python stackexchange_scraper.py
```
- Outputs: `stackexchange_questions.json`

### Step 2: Scrape Each Full Question

```bash
python stackexchange_question_scraper.py
```
- Outputs: Individual JSON files in `reverseengineering/` (one file per question).

### Step 3: Convert and Assemble

```bash
python markdown_and_assemble.py
```
- Outputs: `reverseengineering_markdown.json`
- All `content` and `text` fields are cleaned into **Markdown format**.
- Ready for **LLM fine-tuning** or **embedding generation**.

---

## 📦 Final Output

The final dataset `reverseengineering_markdown.json` is structured as:

```json
{
  "data": {
    "dataset": [
      { ... question 1 ... },
      { ... question 2 ... },
      ...
    ]
  }
}
```

Each question contains:
- Title
- Link
- Content (Markdown format)
- Comments (cleaned text)
- Answers (content + comments cleaned)
- Metadata (user, votes, views, etc.)

✅ Ready for large language models!

---

