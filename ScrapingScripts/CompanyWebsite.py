# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio  
from crawl4ai import *


#//img[@class="h-full w-full rounded-xl"]
def scrape_website(url,api_key):
    """
    Scrape a website and return its content as markdown.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The markdown content of the website, or None if the scrape fails.
    """
    

    app = FirecrawlApp(api_key=api_key)

    response = app.scrape_url(url=url, params={
        'formats': [ 'markdown' ],
    })

    if response['success']:
        return response['data']['markdown']
    else:
        return None


async def fetch_YC_Launch_Page(url: str) -> str:
    """
    Fetches a YC Launch page and returns its HTML content as a markdown string.

    Args:
        url (str): The URL of the YC Launch page to fetch.

    Returns:
        str: The markdown representation of the fetched page.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

def fetch_company_logo(url):
    """
    Opens the given URL and uses BeautifulSoup to find the image with the classes:
    h-full, w-full, and rounded-xl. Returns the src attribute of that image.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the <img> element with all required classes.
        img = soup.find("img", class_=lambda c: c and 
                        all(cls in c.split() for cls in ["h-full", "w-full", "rounded-xl"]))
        if img and img.has_attr("src"):
            return img["src"]
        return ""
    except Exception as e:
        print(f"Error in fetch_company_logo for {url}: {e}")
        return ""

def process_row(row, api_key):
    """
    Processes a single CSV row. Only if Activity_Status is 'Active', it will:
      - Compute 'mark down' by calling the appropriate function.
      - Scrape the company logo and store it.
    Otherwise, the new columns remain empty.
    """
    # Only process active rows (case-insensitive check).
    if row.get("Activity_Status", "").strip().lower() == "active":
        # Ensure 'markdown' is initialized.
        if "markdown" not in row:
            row["markdown"] = ""
            
        post_link = row.get("Post_Link", "").strip()
        website = row.get("Website", "").strip()
        Links = row.get("Link", "").strip()
        Batch = row.get("Batch", "").strip()
        
        # Add website content to markdown if available.
        if website:
            result = scrape_website(website, api_key)
            if result:
                row["markdown"] += result

        # If post_link exists and Batch matches, fetch the YC Launch page markdown.
        if post_link and (Batch in ["W25", "F24", "W24", "S24"]):
            row["markdown"] = asyncio.run(fetch_YC_Launch_Page(post_link))
        
        # Fetch the company logo from the given link.
        row["companylogo"] = fetch_company_logo(Links)
    
        return row
    else:
        return None

def main():
    input_csv = "ycdet_merged.csv"
    output_csv = "output.csv"
    rows = []

    # Read the CSV file.
    with open(input_csv, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows.append(row)
    load_dotenv()
    # Process rows in parallel using ThreadPoolExecutor.
    processed_rows = []
    FIRECRAWL_API_KEY1=os.getenv('FIRECRAWL_API_KEY1')
    FIRECRAWL_API_KEY2=os.getenv('FIRECRAWL_API_KEY2')
    FIRECRAWL_API_KEY3=os.getenv('FIRECRAWL_API_KEY3')
    FIRECRAWL_API_KEY4=os.getenv('FIRECRAWL_API_KEY4')
    FIRECRAWL_API_KEY5=os.getenv('FIRECRAWL_API_KEY5')
    FIRECRAWL_API_KEY6=os.getenv('FIRECRAWL_API_KEY6')
    FIRECRAWL_API_KEY7=os.getenv('FIRECRAWL_API_KEY7')
    FIRECRAWL_API_KEY8=os.getenv('FIRECRAWL_API_KEY8')
    FIRECRAWL_API_KEY9=os.getenv('FIRECRAWL_API_KEY9')
    FIRECRAWL_API_KEY10=os.getenv('FIRECRAWL_API_KEY10')
    api_keys=[FIRECRAWL_API_KEY1,FIRECRAWL_API_KEY2,FIRECRAWL_API_KEY3,FIRECRAWL_API_KEY4,FIRECRAWL_API_KEY5,FIRECRAWL_API_KEY6,FIRECRAWL_API_KEY7,FIRECRAWL_API_KEY8,FIRECRAWL_API_KEY9,FIRECRAWL_API_KEY10]

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit each row for processing, cycling through API keys
        futures = {executor.submit(process_row, row, api_keys[i % len(api_keys)]): row 
                  for i, row in enumerate(rows)}
        for future in as_completed(futures):
            processed_row = future.result()
            if processed_row:
                processed_rows.append(processed_row)

    # Determine fieldnames for the output CSV. This includes the new columns.
    if processed_rows:
        fieldnames = list(processed_rows[0].keys())
        if "markdown" not in fieldnames:
            fieldnames.append("markdown")
        if "companylogo" not in fieldnames:
            fieldnames.append("companylogo")

        # Write the updated rows to the output CSV.
        with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in processed_rows:
                writer.writerow(row)
    else:
        print("No rows found in the input CSV.")

if __name__ == "__main__":
    main()

