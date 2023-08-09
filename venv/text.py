import requests
from bs4 import BeautifulSoup
def scrape_charity_website(url):
    """Gets all text information from the page given by the url."""
    
    text_filename=str(input("Enter the name of the text file to save the website info :"))
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('./textfiles/'+text_filename+'.txt', 'w', encoding='utf-8') as file:
            text_content = soup.get_text()
            cleaned_content = "\n".join(line.strip() for line in text_content.splitlines() if line.strip())
            file.write(cleaned_content)
    else:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")

    return text_filename

# scrape_charity_website('https://www.nfwf.org/programs/rocky-mountain-rangelands/rocky-mountain-rangelands-program-2023-request-proposals')
# scrape_charity_website("https://nato.usmission.gov/u-s-mission-to-nato/#Grants")