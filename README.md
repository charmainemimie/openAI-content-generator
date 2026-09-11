# OpenAI Charity Content Generator

A Python command-line tool that turns a charity or grant-maker web page into a short, reusable summary. It scrapes the page, splits the text into chunks, asks OpenAI to highlight the program description and grant amounts, then stores the result for later use (for example SEO copy or a content database).

It was built around real grant pages (NFWF, Bob Barker Foundation, Kars4Kids, and others). Sample scraped pages live in `textfiles/`, and generated summaries are stored in `tempContentDB.json`.

## What it does

1. **Asks for a URL** — typically a grants, eligibility, or RFP page.
2. **Scrapes main page text** with Requests and Beautiful Soup (navigation, cookie banners, and other chrome are stripped). If the static HTML has almost no text, it retries with Playwright so JavaScript-rendered pages still work.
3. **Chunks the page** with spaCy so each piece stays under about 2,000 words.
4. **Summarizes each chunk** with the OpenAI Chat Completions API (`gpt-4o-mini` by default). Rate limits and transient errors are retried with backoff. The prompt asks for about 10 sentences, no repetition, including grant descriptions and amounts.
5. **Saves the combined summary** as a `{ "url", "content" }` object in `tempContentDB.json`, then prints it. The same URL is not stored twice unless you choose to replace it.

## Project layout

| Path | Role |
|------|------|
| `main.py` | Entry point: scrape → chunk → summarize → save JSON |
| `GenerateContent.py` | spaCy chunking and OpenAI summarization; loads `.env` |
| `text.py` | Scrapes a URL and writes `textfiles/<name>.txt` |
| `textfiles/` | Scraped page text and some earlier generated `.txt` outputs |
| `tempContentDB.json` | `{url, content}` summaries |
| `.env.example` | Template for secrets (safe to commit) |
| `.env` | Local secrets only — never commit this file |
| `Pipfile` | Runtime and dev dependencies (Python 3.9) |

## Requirements

- Python **3.9**
- An [OpenAI API key](https://platform.openai.com/api-keys)
- Packages listed in `Pipfile`: `openai`, `spacy`, `requests`, `beautifulsoup4`, `playwright`, `pre-commit`

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/charmainemimie/openAI-content-generator.git
cd openAI-content-generator
python -m venv venv
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 2. Install dependencies

With Pipenv:

```bash
pip install pipenv
pipenv install
python -m spacy download en_core_web_sm
playwright install chromium
```

Or with pip:

```bash
pip install openai "spacy" requests beautifulsoup4 playwright pre-commit
python -m spacy download en_core_web_sm
playwright install chromium
```

Chromium is only needed for JavaScript-heavy pages. Static HTML sites work with Requests alone.

### 3. Configure the API key

Copy the example env file and paste your key. Do not put the key in source files or commit `.env`.

```bash
copy .env.example .env
```

On macOS/Linux: `cp .env.example .env`

`.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

`GenerateContent.py` reads this file on import and sets `openai.api_key`. If the key is missing, it raises:

`OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.`

`OPENAI_MODEL` is optional. Change it if you want a different Chat Completions model.

## Usage

From the project root, with the virtual environment active:

```bash
python main.py
```

You will be prompted for:

1. **Charity website URL** — the page to scrape.
2. **Text file name** — used as `textfiles/<name>.txt` (no `.txt` suffix).

If that URL is already in `tempContentDB.json`, you are asked whether to replace the stored summary. Answering anything other than `y` / `yes` leaves the file unchanged and skips the API call.

On success, the script:

- Writes the cleaned page to `textfiles/<name>.txt`
- Adds or replaces `{ "url": "<normalized URL>", "content": "<summary>" }` in `tempContentDB.json`
- Prints the summary to the terminal

### Example

```
Please enter the URL of the charity website: https://www.bobbarkerfoundation.org/eligibility-grant-process
Enter the name of the text file to save the website info : BBF_charity_info
```

That produces `textfiles/BBF_charity_info.txt` and a row in `tempContentDB.json`.

## How summarization works

`text_to_chunks()` loads English spaCy, splits the scrape into sentences, and groups them until a chunk would exceed 2,000 words, then starts a new chunk.

`summarize_text()` sends each chunk to Chat Completions. It retries up to five times on rate limits, timeouts, and other transient API errors, honoring `Retry-After` when the API sends it.

The model is asked for:

- About 10 sentences
- No repetition
- Meaningful copy that includes **what the grants are for** and **amounts**

Settings in code: `temperature=0.3`, `max_tokens=1000`, `frequency_penalty=1`, `presence_penalty=1`.

Authentication and invalid-request errors are not retried.

## Output format

`tempContentDB.json` is a JSON array:

```json
[
  {
    "url": "https://example.org/grants",
    "content": "Generated summary..."
  }
]
```

URLs are stored in a normalized form (lowercase host, no trailing slash, no fragment) so `https://Example.org/grants/` matches an existing entry.

## Development

Python 3.9 is specified in `Pipfile`. Ruff is configured in `pyproject.toml` and wired through `.pre-commit-config.yaml`:

```bash
pip install pre-commit
pre-commit install
```
