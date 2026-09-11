"""Main file that calls text.py and GenerateContent.py."""

import json
import os
from urllib.parse import urlsplit, urlunsplit

import GenerateContent
import text

JSON_FILENAME = "tempContentDB.json"


def normalize_url(url):
    """Canonicalize a URL so the same page is not stored twice."""
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"Invalid URL: {url}")
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


def load_database(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def save_database(path, data):
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
        json_file.write("\n")


def find_entry_index(data, url):
    for index, entry in enumerate(data):
        existing = entry.get("url", "")
        try:
            if normalize_url(existing) == url:
                return index
        except ValueError:
            continue
    return None


if __name__ == "__main__":
    url = str(input("Please enter the URL of the charity website: ")).strip()
    normalized_url = normalize_url(url)
    existing_data = load_database(JSON_FILENAME)
    existing_index = find_entry_index(existing_data, normalized_url)

    if existing_index is not None:
        answer = input(
            "This URL is already in tempContentDB.json. Replace the existing summary? [y/N]: "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            print("Skipped. Existing summary was left unchanged.")
            raise SystemExit(0)

    text_filename = str(
        input("Enter the name of the text file to save the website info : ")
    ).strip()
    page_text = text.scrape_charity_website(url, text_filename)

    chunk_summaries = []
    for chunk in GenerateContent.text_to_chunks(page_text):
        chunk_summaries.append(GenerateContent.summarize_text(" ".join(chunk)))

    summary = " ".join(part for part in chunk_summaries if part).replace("\n", " ").strip()
    if not summary:
        raise RuntimeError("Summarization produced no content.")

    entry = {"url": normalized_url, "content": summary}
    if existing_index is not None:
        existing_data[existing_index] = entry
    else:
        existing_data.append(entry)

    save_database(JSON_FILENAME, existing_data)
    print(f"Summary for {normalized_url} saved to {JSON_FILENAME} successfully.")
    print(summary)
