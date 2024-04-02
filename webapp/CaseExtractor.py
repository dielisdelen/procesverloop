from selenium import webdriver
from bs4 import BeautifulSoup
import time

def scrape_case(ecli_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--no-sandbox')  # Bypass OS security model, REQUIRED on Linux if running as root
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    
    driver = webdriver.Chrome(options=options)

    # Build the URL with the case number
    url = f"https://uitspraken.rechtspraak.nl/#!/details?id={ecli_id}"

    # Navigate to the URL
    driver.get(url)
    
    # Wait for the dynamic content to load
    time.sleep(10)  # Adjust as needed

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the WebDriver
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Locate and extract the required information
    extracted_text = ""
    main_content_div = soup.find('div', class_='rs-panel rs-panel-type-1')
    if main_content_div:
        extracted_text = main_content_div.get_text(separator=' ', strip=True)
    else:
        # Fallback to extracting the entire text or handle as needed
        extracted_text = "Specific content not found."

    # Dictionary to hold the metadata
    metadata = {}
    
    # Extract metadata from the HTML structure
    detail_rows = main_content_div.find_all('div', class_='rnl-detail row')
    for row in detail_rows:
        key = row.find('label').text.strip()
        value = row.find('span', class_='rnl-details-value').get_text(strip=True)
        metadata[key] = value

    return metadata, extracted_text
