import openai
from text import scrape_charity_website

# Set your OpenAI API key
openai.api_key = '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'

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



