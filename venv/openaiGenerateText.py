import os
from pathlib import Path

import openai
from text import scrape_charity_website


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


for directory in (Path(__file__).resolve().parent, Path(__file__).resolve().parent.parent):
    load_env_file(directory / ".env")

openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
    )

def generate_content(prompt):
    # Initialize the maximum tokens allowed by the model
    max_tokens_allowed = 4096

    # Split the prompt into chunks that fit within the model's context length
    prompt_chunks = [prompt[i:i + max_tokens_allowed] for i in range(0, len(prompt), max_tokens_allowed)]

    generated_content = ""
    for chunk in prompt_chunks:
        print(chunk)
        try:
            response = openai.Completion.create(
                engine="davinci-instruct-beta-v3",
                prompt="Generate meaningful content from this chunk: " + chunk,
                temperature=0.7,
                max_tokens=1000,  # Limit the generated tokens to the length of the chunk
            )
            generated_content += response.choices[0].text.strip()
            print(generated_content)
    # response = openai.Completion.create(
    #     engine="text-davinci-003",  # Choose the language model engine according to your needs
    #     # prompt=prompt,
    #     prompt="Generate content that can be put on a webpage from this prompt: {} \n\n: ".format(prompt),
    #     temperature=0.7,  # Controls the creativity/randomness of the generated content
    #     max_tokens=500,   # Maximum number of tokens in the generated content
    # )
            return generated_content
        except openai.error.OpenAIError as e:
            print("OpenAI API Error:", e)
            return None
# Use the content you scraped earlier as a prompt for generating more content
with open('charity_info.txt', 'r', encoding='utf-8') as file:
    existing_content = file.read()


generated_content = generate_content(existing_content)
print(generated_content)



