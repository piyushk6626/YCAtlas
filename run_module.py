from CreateGraph import process_csv_file
from ScrapingScripts.runner import run_scraping_pipeline


def Link_to_graph(website_url):
    run_scraping_pipeline(website_url)
    csv_file_path = "ycdet.csv"
    process_csv_file(csv_file_path) 


if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file_path = "ycdet.csv"
    
    # Call the function from your module
    process_csv_file(csv_file_path) 
    website_url = "https://www.ycombinator.com/companies?batch=W25"
    Link_to_graph(website_url)