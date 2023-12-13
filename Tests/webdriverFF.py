from selenium import webdriver
import time

# Initialize WebDriver without any arguments to see if it defaults correctly
driver = webdriver.Firefox()

url = "https://uitspraken.rechtspraak.nl/#!/details?id=ECLI:NL:RBMNE:2023:4481"

driver.get(url)
time.sleep(5)
html = driver.page_source
print(driver.title)
print(html)
driver.quit()

