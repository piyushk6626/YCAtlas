import json
import os
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool, cpu_count

def download_image(url, company_name, save_dir="data/logos"):
    """Download image from URL and save it locally."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Handle relative URLs by adding base URL
        if url.startswith('/'):
            url = f"https://www.ycombinator.com{url}"
        
        # Clean up URL by removing query parameters
        clean_url = url.split('?')[0]
        
        # Get file extension from cleaned URL or default to .png
        extension = os.path.splitext(clean_url)[1] or '.png'
        filename = f"{company_name}_logo{extension}"
        filepath = os.path.join(save_dir, filename)
        
        # Download and save image
        response = requests.get(url)  # Use original URL for download
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        return filepath
    except Exception as e:
        logging.error(f"Error downloading image from {url}: {e}")
        return None

def process_single_json(path):
    """Process a single JSON file, scrape additional data, and upload to Pinecone."""
    try:
        # Load the JSON file
        with open(path, 'r') as f:
            data = json.load(f)
        
        if data.get('logo_path'):
            logging.info(f"Logo already exists for {data.get('name')}")
            return
        
        # Get YC page URL and company name
        yc_page_url = data.get('links')
        company_name = data.get('name', '').replace(' ', '_')
        
        if not yc_page_url:
            logging.error(f"No YC page URL found in {path}")
            return
        
        # Fetch and parse the YC page
        response = requests.get(yc_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract company logo
        logo_img = soup.select_one('div.mb-4.flex.justify-center img')
        logo_url = logo_img['src'] if logo_img else None
        
        if logo_url:
            # Download and save the logo locally
            local_path = download_image(logo_url, company_name)
            if local_path:
                # Update JSON with local path
                data['logo_path'] = local_path
                with open(path, 'w') as f:
                    json.dump(data, f, indent=4)
                logging.info(f"Successfully processed {company_name}")
                
    except Exception as e:
        logging.error(f"Error processing {path}: {e}")
        return

def process_all_jsons(directory, num_workers=None):
    """Process all JSON files in the given directory in parallel."""
    if num_workers is None:
        num_workers = 15  # Leave one CPU free
    
    # Get list of all JSON files
    json_files = [
        os.path.join(directory, f) 
        for f in os.listdir(directory) 
        if f.endswith('.json')
    ]
    
    # Process files in parallel
    with Pool(num_workers) as pool:
        pool.map(process_single_json, json_files)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # # Test with a single JSON file
    # test_file = r"D:\DEV\YC25\YC25\data\company_descriptions\_AI_S24.json"
    # process_single_json(test_file)
    
    # Comment out the batch processing for now
    directory = "data/company_descriptions"
    process_all_jsons(directory)