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

def basic_scrape():
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    logging.info('Basic Scrape successfully')
    driver.quit()

basic_scrape()

logging.info('Before Try Setup completed')

driver = None
try:
    driver = webdriver.Chrome(options=options)
    logging.info('WebDriver started successfully')

    # Build and log the URL
    url = f"https://www.google.com"
    logging.info(f'Navigating to URL: {url}')
    driver.get(url)
        
    # Wait and log dynamic content loading
    time.sleep(6)
    logging.info('Waiting for page content to load')
        
    # Retrieve and log page source
    html = driver.page_source
    logging.info('Page source retrieved')
except Exception as e:
    logging.error('Error during WebDriver operation', exc_info=True)

finally:
    if driver:
        driver.quit()
        logging.info('WebDriver closed')
