"""Generates content for a given charity website(url) using the openAI api."""
import os
import random
import time
from pathlib import Path

import openai
import spacy

CHUNK_WORD_LIMIT = 2000
MAX_RETRIES = 5
DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You summarize charity and grant-maker web pages. Write about 10 sentences with no "
    "repetition. Include the program description and the amounts of grants being offered "
    "when that information is present."
)


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

nlp = spacy.load("en_core_web_sm")
RETRYABLE_ERRORS = (
    openai.error.RateLimitError,
    openai.error.Timeout,
    openai.error.APIConnectionError,
    openai.error.APIError,
    openai.error.ServiceUnavailableError,
    openai.error.TryAgain,
)


def text_to_chunks(text):
    """Chunks the text from txt file."""
    chunkslist = [[]]
    chunk_total_words = 0

    sentences = nlp(text)

    for sentence in sentences.sents:
        chunk_total_words += len(sentence.text.split(" "))
        if chunk_total_words > CHUNK_WORD_LIMIT:
            chunkslist.append([])
            chunk_total_words = len(sentence.text.split(" "))

        chunkslist[len(chunkslist) - 1].append(sentence.text)

    return chunkslist


def summarize_text(text):
    """Generate content using the OpenAI Chat Completions API, with retries."""
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Summarize the following text in about 10 sentences with no "
                            "repetition and include the description and amounts of the "
                            f"grants being offered:\n{text}"
                        ),
                    },
                ],
                temperature=0.3,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1,
            )
            content = response["choices"][0]["message"]["content"]
            if not content or not content.strip():
                raise openai.error.APIError("Empty completion from OpenAI")
            return content.strip()
        except (openai.error.AuthenticationError, openai.error.InvalidRequestError):
            raise
        except RETRYABLE_ERRORS as exc:
            last_error = exc
            wait_seconds = _retry_wait(exc, attempt)
            print(
                f"OpenAI API error ({exc}). Retrying in {wait_seconds:.1f}s "
                f"({attempt}/{MAX_RETRIES})..."
            )
            time.sleep(wait_seconds)

    raise RuntimeError(f"OpenAI API failed after {MAX_RETRIES} attempts: {last_error}")


def _retry_wait(exc, attempt):
    headers = getattr(exc, "headers", None) or {}
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after:
        try:
            return max(float(retry_after), 1.0)
        except ValueError:
            pass
    return min((2 ** (attempt - 1)) + random.random(), 30)
