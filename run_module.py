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
    website_url = "https://www.ycombinator.com/companies?batch=S05&batch=W06&batch=S06&batch=W07&batch=S07&batch=W08&batch=S08&batch=W09&batch=S09&batch=W10&batch=S10&batch=W11&batch=S11&batch=W12&batch=S12&batch=W13&batch=S13"
    run_scraping_pipeline(website_url)
    # A=["W25","F24","S24","W24","S23","W23","S22","W22","S21","W21","S20","W20","S19","W19","S18","W18","S17","W17","IK12","S16","W16","S15","W15","S14","W14","S13","W13","S12","W12","S11","W11","S10","W10","S09","W09","S08","W08","S07","W07","S06","W06","S05"]
    # #https://www.ycombinator.com/companies?batch=S05&batch=W06&batch=S06&batch=W07&batch=S07&batch=W08&batch=S08&batch=W09&batch=S09&batch=W10&batch=S10&batch=W11&batch=S11&batch=W12&batch=S12&batch=W13&batch=S13
    # for i in A:
    #     website_url = "https://www.ycombinator.com/companies?batch="+i
    #     run_scraping_pipeline(website_url)
    