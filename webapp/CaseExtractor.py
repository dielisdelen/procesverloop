from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

def scrape_case(case_number):
    options = Options()
    options.headless = True  # Enable headless mode

    # Build the URL with the case number
    url = f"https://uitspraken.rechtspraak.nl/#!/details?id={case_number}"

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
        extracted_text = "Procesverloop section not found."

    return extracted_text
