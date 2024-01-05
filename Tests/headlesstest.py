from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
driver.get("http://www.google.com")
print(driver.title)  # Should print the title of the page without opening a window
driver.quit()
