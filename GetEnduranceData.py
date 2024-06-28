import requests
import sys
from bs4 import BeautifulSoup


# Step 1: Make a request to the website
carnum = input("Enter car number")

if not carnum.isnumeric():
    print("Enter a valid number")
    sys.exit()

url = f"https://results.fsaeonline.com/MyResults.aspx?carnum={carnum}&tab=notices"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Step 2: Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example: Extract the title of the webpage
    title = soup.title.string
    print(f"Title: {title}")
    
    # Example: Extract all paragraphs
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        print(p.text)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
