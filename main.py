"""Main file that calls text.py and GenerateContent.py."""

import text
import GenerateContent
import os
import json

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # get text from site
    url = str(input("Please enter the URL of the charity website: "))

    # url = "https://www.bobbarkerfoundation.org/eligibility-grant-process"
    text_filename = text.scrape_charity_website(url)

    # generating content

    with open("./textfiles/"+text_filename+".txt", "r", encoding="utf-8") as file:
        one_large_text = file.read()

    chunks = GenerateContent.text_to_chunks(one_large_text)

    chunk_summaries = []

    for chunk in chunks:
        chunk_summary = GenerateContent.summarize_text(" ".join(chunk))
        chunk_summaries.append(chunk_summary)

    summary = " ".join(chunk_summaries)
    summary = summary.replace("\n", "")

    # # save summary in text file
    # with open('GG253_generated_content.txt', 'w', encoding='utf-8') as file:
    #     file.write(summary)

    # save generated content to json file
    json_filename = "tempContentDB.json"
    if os.path.exists(json_filename):
        with open(json_filename, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Create a dictionary entry for the URL and its corresponding summary
    entry = {"url": url, "content": summary}

    # Add the new entry to the existing data list
    existing_data.append(entry)

    # Write the updated data to the JSON file
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(existing_data, ensure_ascii=False, indent=4))

    print(f"Summary for {url} saved to {json_filename} successfully.")

    print(summary)
