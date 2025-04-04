from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup

Asia = True
driver = webdriver.Chrome()
if Asia:
    driver.get('https://asia-en.onepiece-cardgame.com/cardlist/')
    folder_name = "Asia-Cardlists"
else:
    driver.get('https://en.onepiece-cardgame.com/cardlist/')  # Open webpage
    folder_name = "Cardlists"

# Wait until the dropdown is available
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "series")))

# Create a folder to save HTML files
os.makedirs(folder_name, exist_ok=True)

# Locate the series dropdown that lets you filter through the different sets
series_dropdown = driver.find_element(By.NAME, "series")
select = Select(series_dropdown)

# Get all available series values, excluding empty values
series_values = [option.get_attribute("value") for option in select.options if option.get_attribute("value")]

# Loop through each series value (card set, starter deck) and download the corresponding HTML
for series_value in series_values:
    if f'series_{series_value}.html' in os.listdir(folder_name):
        print(f'series_{series_value}.html already exists, skipping...')
        #continue
    else:
        print(f"Selecting series: {series_value}")

    series_dropdown = driver.find_element(By.NAME, "series")

    # Use JavaScript to select the value and trigger a change event
    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                          series_dropdown, series_value)

    # Wait for the page to update after selecting a new series
    time.sleep(2)

    #Click the "SEARCH" button after the selection is updated to load the html matching the selected filter
    search_button = driver.find_element(By.CSS_SELECTOR, '.commonBtn.submitBtn input[type="submit"]')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(search_button))
    search_button.click()

    # Wait for the results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "countCol")))  # Or any other element that indicates the page has loaded

    current_selection = driver.find_element(By.NAME, "series")
    # Get the page source and save it to a file
    html_content = driver.page_source

    file_path = os.path.join(folder_name, f'series_{series_value}.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser', multi_valued_attributes=None)
        # finds the name of the selected filter from html
        selection = soup.find('option', selected=True)
        print(f'extracting card data from: {series_value}')
    #print(f"Downloaded HTML for series: {series_value} in {folder_name}")
    print()

# Close the browser
driver.quit()
