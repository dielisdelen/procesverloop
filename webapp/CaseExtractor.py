from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

def scrape_case(ecli_id):
    options = Options()
    options.headless = True  # Enable headless mode

    # Build the URL with the case number
    url = f"https://uitspraken.rechtspraak.nl/#!/details?id={ecli_id}"

    # Initialize WebDriver for Firefox (make sure it's installed in your environment)
    driver = webdriver.Firefox(options=options)

    # Navigate to the URL
    driver.get(url)
    
    # Wait for the dynamic content to load
    time.sleep(5)  # Adjust as needed

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the WebDriver
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Locate and extract the required information
    extracted_text = ""
    procesverloop_div = soup.find('div', class_='section procesverloop')
    if procesverloop_div:
        text_blocks = procesverloop_div.find_all('div', class_='parablock')
        extracted_texts = [block.get_text(strip=True) for block in text_blocks]
        extracted_text = ' '.join(extracted_texts)
    else:
        # If the primary div is not found, try the secondary div
        secondary_div = soup.find('div', class_='rs-panel rs-panel-type-1')
        if secondary_div:
            extracted_text = secondary_div.get_text(separator=' ', strip=True)
        else:
            # Fallback to extracting the entire text or handle as needed
            extracted_text = "Specific content not found."

    return extracted_text
