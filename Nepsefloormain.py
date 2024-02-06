from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

url = 'https://www.nepalstock.com.np/floor-sheet'

chrome_options = Options()
# Create a WebDriver instance
driver = webdriver.Chrome(options=chrome_options)

# Load the page
driver.get(url)

# Wait for a few seconds to allow dynamic content to load (you might need to adjust this)
driver.implicitly_wait(1000)

# Get the page source after JavaScript execution
page_source = driver.page_source

# Close the browser
driver.quit()

# Use BeautifulSoup to parse the page source
soup = BeautifulSoup(page_source, 'html.parser')

# Print all text content
print(soup)