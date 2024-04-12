from selenium import webdriver
import time
import logging

logging.basicConfig(filename='/var/log/scraperlogs/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')  # Bypass OS security model, REQUIRED on Linux if running as root
options.add_argument('--headless=new')  # Run Chrome in headless mode
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.add_argument("--disable-gpu")
options.add_argument('--remote-debugging-pipe')

try:
    driver = webdriver.Chrome(options=options)
    logging.info('WebDriver started successfully')
except Exception as e:
    logging.error('Failed to start WebDriver', exc_info=True)

try:
    # Build and log the URL
    url = f"https://uitspraken.rechtspraak.nl/#!/details?id=ECLI:NL:HR:2005:AT3511"
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

