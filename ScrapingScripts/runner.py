from .links import scrape_links
from .scrape import process_csv_to_json

def run_scraping_pipeline(website_url):
    """
    Runs the complete scraping pipeline:
      1. Scrapes company links from the given website URL and saves them to 'links_csv'.
      2. Processes the links CSV by scraping company details and saving the output to 'details_csv'.
    
    Args:
        website_url (str): The URL from which to scrape company links.
        links_csv (str): The file path for saving the scraped links.
        details_csv (str): The file path for saving the company details.
    """
    links_csv = "yclinks.csv"
    details_csv = "ycdet.csv"
    print("Starting link scraping...")
    scrape_links(website_url, links_csv)
    print("Link scraping completed.")

    print("Starting company details scraping...")
    process_csv_to_json(links_csv, details_csv)
    print("Company details scraping completed.")

if __name__ == "__main__":
    # Example usage:
    website_url = "https://www.ycombinator.com/companies?batch=W25"
    run_scraping_pipeline(website_url) 