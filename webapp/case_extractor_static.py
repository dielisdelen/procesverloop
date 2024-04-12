from selenium import webdriver
from bs4 import BeautifulSoup
import time
import logging

# Configure logging
logging.basicConfig(filename='/var/log/scraperlogs/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_case(ecli_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')  # Bypass OS security model, REQUIRED on Linux if running as root
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-pipe')
    options.add_argument('--user-data-dir=/var/www/chrome-data')  # Custom user data directory
    options.add_argument('--disk-cache-dir=/var/www/chrome-cache')  # Custom cache directory

    # Ensure the HOME and TMPDIR are set for www-data when initializing the driver
    with webdriver.Chrome(options=options, service_args=['--verbose', '--log-path=/var/log/scraperlogs/chromedriver.log']) as driver:
        try:
            # Build and log the URL
            url = "https://uitspraken.rechtspraak.nl/#!/details?id=ECLI:NL:PHR:2005:AT3511"
            logging.info(f'Navigating to URL: {url}')
            driver.get(url)
            
            # Wait and log dynamic content loading
            time.sleep(6)
            logging.info('Waiting for page content to load')
            
            # Retrieve and log page source
            html = driver.page_source
            logging.info('Page source retrieved')
        except Exception as e:
            logging.error('Error during page navigation and data retrieval', exc_info=True)
            return {}, "Error during navigation or data retrieval."

    try:
        # Parsing the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        logging.info('HTML content parsed with BeautifulSoup')

        # Extract information
        main_content_div = soup.find('div', class_='rs-panel rs-panel-type-1')
        if main_content_div:
            extracted_text = main_content_div.get_text(separator=' ', strip=True)
            logging.info('Main content extracted successfully')
        else:
            extracted_text = "Specific content not found."
            logging.warning('Main content division not found in the page')

        # Extract metadata
        metadata = {}
        detail_rows = main_content_div.find_all('div', class_='rnl-detail row') if main_content_div else []
        for row in detail_rows:
            key = row.find('label').text.strip()
            value = row.find('span', class_='rnl-details-value').get_text(strip=True)
            metadata[key] = value
            logging.info(f'Extracted metadata - {key}: {value}')

        return metadata, extracted_text
    except Exception as e:
        logging.error('Error during HTML parsing or content extraction', exc_info=True)
        return {}, "Error during parsing."
