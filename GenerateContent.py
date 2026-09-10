"""Generates content for a given charity website(url) using the openAI api."""
import os
from pathlib import Path

import openai
import spacy
# from spacy.lang.en import English
# from text import scrape_charity_website


def load_env_file(path):
    """Load KEY=VALUE pairs from a local .env file without committing secrets."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


load_env_file(Path(__file__).resolve().parent / ".env")
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
    )

# spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")
def text_to_chunks(text):
    """Chunks the text from txt file."""
    chunkslist = [[]]
    chunk_total_words = 0

    sentences = nlp(text)

    for sentence in sentences.sents:
        chunk_total_words += len(sentence.text.split(" "))
        num_of_words = 2000
        if chunk_total_words > num_of_words:
            chunkslist.append([])
            chunk_total_words = len(sentence.text.split(" "))

        chunkslist[len(chunkslist) - 1].append(sentence.text)

    return chunkslist
def summarize_text(text):
    """Generate content using OpenAI API."""
    prompt = (
        f"Summarize the following text in about 10 sentences with no repetition and give meaningful content including "
        f"the description and"
        f"amounts of the grants being offered:\n{text}")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.3,
            max_tokens=1000,  # approximately 600-800 words generated
            top_p=1,
            frequency_penalty=1,
            presence_penalty=1,
        )

        return response["choices"][0]["text"]

    except openai.error.OpenAIError as e:
        print("OpenAI API Error:", e)
        return None

# with open('charity_info.txt2', 'r', encoding='utf-8') as file:
#     one_large_text = file.read()
#
# chunks = text_to_chunks(one_large_text)
#
# chunk_summaries = []
#
# for chunk in chunks:
#     chunk_summary = summarize_text(" ".join(chunk))
#     chunk_summaries.append(chunk_summary)
#
# summary = " ".join(chunk_summaries)
# with open('generated_content.txt', 'w', encoding='utf-8') as file:
#     file.write(summary)
# print(summary)
