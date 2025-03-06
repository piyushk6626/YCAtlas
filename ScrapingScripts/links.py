import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def Number_of_Loaded_Product(page_source):        
    soup = BeautifulSoup(page_source, 'html.parser')
    product_items = soup.find_all('a', class_='_company_1pgsr_355')
    return len(product_items)

def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    numb = 0
    while numb < 5000:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Adjust the sleep time as per the loading speed of the page
        numb = Number_of_Loaded_Product(driver.page_source)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_links(url, output_file):
    driver = setup_driver()
    driver.get(url)

    # Store unique links in a set
    links_set = set()

    # Scroll and capture links
    scroll_page(driver)

    # Find all anchor tags with the specified class
    links = driver.find_elements(By.XPATH, '//a[@class="_company_i9oky_355"]')
    print(f"Found {len(links)} links on the page.")
    for link in links:
        href = link.get_attribute('href')
        if href:
            links_set.add(href)

    # Write links to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Links"])
        for href in links_set:
            writer.writerow([href])

    print(f"Scraped {len(links_set)} unique links.")
    driver.quit()

if __name__ == "__main__":
    website_url = "https://www.ycombinator.com/companies?batch=X25"  # Replace with your target website
    output_csv = "yc25.csv"
    scrape_links(website_url, output_csv) 