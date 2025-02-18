# PARENT ELEMENT //div[@class="post row align-center"]
# COMANEY LINK //div[@class="post row align-center"]/a
# POST LINK //div[@class="post row align-center"]/div[@class="post-text col"]/a[@class="post-title"]
import time
import csv
from selenium import webdriver
from bs4 import BeautifulSoup

# Initialize WebDriver globally
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

def number_of_loaded_products(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    product_items = soup.find_all('div', class_='post row align-center')
    return len(product_items)

def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    numb = 0
    while numb < 5000:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Adjust as needed
        numb = number_of_loaded_products(driver.page_source)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_data(url):
    driver.get(url)
    time.sleep(5)
    scroll_page(driver)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = soup.find_all('div', class_='post row align-center')
    
    data = []
    for post in posts:
        company_link = post.find('a')['href'] if post.find('a') else None
        post_link_tag = post.find('div', class_='post-text col').find('a', class_='post-title') if post.find('div', class_='post-text col') else None
        post_link = post_link_tag['href'] if post_link_tag else None
        
        if company_link and not company_link.startswith("https"):
            company_link = "https://www.ycombinator.com" + company_link
        if post_link and not post_link.startswith("https"):
            post_link = "https://www.ycombinator.com" + post_link
        
        data.append([company_link, post_link])
    
    with open('YC25Launch.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Optionally, ensure the header is written only once
        writer.writerow(["Link", "Post_Link"])
        writer.writerows(data)
    
    print(f"Data saved to YC25Launch.csv for URL: {url}")

if __name__ == "__main__":
    scrape_data("https://www.ycombinator.com/launches?batch=W2023")
    
    driver.quit()  # Quit once after all scraping is done