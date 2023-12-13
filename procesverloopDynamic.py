from selenium import webdriver
from bs4 import BeautifulSoup
import time

def fetch_dynamic_content(url):
    # Setup WebDriver for Firefox
    driver = webdriver.Firefox()

    # Navigate to the URL
    driver.get(url)
    
    # Wait for the dynamic content to load
    time.sleep(5)

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the WebDriver
    driver.quit()

    return html

# Define the URL
url = "https://uitspraken.rechtspraak.nl/#!/details?id=ECLI:NL:RBMNE:2023:4481"

# Call the function and retrieve HTML content
html_content = fetch_dynamic_content(url)

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Locate and extract the required information
procesverloop_div = soup.find('div', class_='section procesverloop')
if procesverloop_div:
    text_blocks = procesverloop_div.find_all('div', class_='parablock')
    for block in text_blocks:
        print(block.get_text(strip=True))
else:
    print("Procesverloop section not found.")
