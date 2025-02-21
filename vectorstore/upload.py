from pinecone import Pinecone
import json
import os
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def process_tags(tags):
    if tags is None:
        return []
    try:
        T= tags.split(';')
        tags=[]
        for i in T:
            if i.startswith('industry:'):
                tags.append(i.split(':')[1])
        return tags
    except Exception as e:
        logging.error(f"Error processing tags: {str(e)}")
        return []

def process_single_json(path):
    """Process a single JSON file, scrape additional data, and upload to Pinecone."""
    try:
        # Load the JSON file
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Get YC page URL
        yc_page_url = data.get('links')
        if not yc_page_url:
            logging.error(f"No YC page URL found in {path}")
            return
        
        # Fetch and parse the YC page
        response = requests.get(yc_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract company logo
        logo_img = soup.select_one('div.mb-4.flex.justify-center img')
        logo_url = logo_img['src'] if logo_img else None
        
        # Extract social links
        social_links = []
        social_div = soup.select_one('div.flex.items-center.gap-4.pt-2')
        if social_div:
            social_links = [a['href'] for a in social_div.find_all('a')]
        
        # Update the data dictionary
        data['logo'] = logo_url
        data['social_links'] = social_links
        
        # Save updated data back to the same JSON file
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Process the data and create vector
        vector = process_dict_data(data)
        if vector:
            # Upload to Pinecone
            upload_to_pinecone([vector])
            logging.info(f"Successfully processed and uploaded data from {path}")
            return vector
        else:
            logging.error(f"Failed to process data from {path}")
            return None
            
    except Exception as e:
        logging.error(f"Error processing {path}: {str(e)}")
        return None

def process_dict_data(data):
    """Process a single dictionary containing company data."""
    try:
        # Debug logging for all fields
        fields = ['description', 'links', 'name', 'headline', 'batch', 'location', 
                 'website', 'founded_date', 'tags', 'team_size', 'generated_description',
                 'logo', 'social_links']
        
        for field in fields:
            value = data.get(field, '')
            if value is None:
                value = '' if field != 'tags' and field != 'social_links' else []
                logging.warning(f"Found None {field} for company: {data.get('name', 'unknown')}")
        
        # Create metadata from relevant fields
        metadata = {
            'ycpage': str(data.get('links', '')),
            'name': str(data.get('name', '')),
            'headline': str(data.get('headline', '')),
            'description': str(data.get('description', '')),
            'batch': str(data.get('batch', '')),
            'location': str(data.get('location', '')),
            'website': str(data.get('website', '')),
            'founded_date': str(data.get('founded_date', '')),
            'tags': process_tags(data.get('tags')) or [],
            'team_size': str(data.get('team_size', '')),
            'generated_description': str(data.get('generated_description', '')),
            'logo': str(data.get('logo', '')),
            'social_links': [str(link) for link in data.get('social_links', []) if link is not None]
        }
        
        # Debug logging for founders
        founders = data.get('founders', [])
        if founders is None:
            founders = []
            logging.warning(f"Found None founders for company: {data.get('name', 'unknown')}")
            
        # Add founder information with explicit string conversion
        for i, founder in enumerate(founders, 1):
            if i > 7:  # Limit to maximum 7 founders
                break
            metadata[f'founder_{i}_name'] = str(founder.get('name', ''))
            metadata[f'founder_{i}_description'] = str(founder.get('description', ''))
            metadata[f'founder_{i}_linkedin'] = str(founder.get('linkedin', ''))
        
        # Debug logging for final metadata
        logging.debug(f"Processed metadata for {data.get('name', 'unknown')}: {metadata}")
        
        return {
            'id': str(data.get('name', '')).lower().replace(' ', '-'),
            'values': data.get('embedding', []),
            'metadata': metadata
        }
        
    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        return None

def upload_to_pinecone(vectors, index_name="ycatlas"):
    """Upload vectors to Pinecone index."""
    try:
        
        # Get index
        index = pc.Index(index_name)
        for vector in vectors:
            index.upsert(
                vectors=[vector],
                
            )   
    except Exception as e:
        logging.error(f"Failed to upload to Pinecone: {str(e)}")

def main():
    """Process all JSON files in the data/company_descriptions directory in parallel."""
    import glob
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Get all JSON files in the directory
    json_files = glob.glob('data/company_descriptions/*.json')
    
    # Process files in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tasks and store future objects
        future_to_file = {executor.submit(process_single_json, file_path): file_path 
                         for file_path in json_files}
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    logging.info(f"Successfully processed {file_path}")
                else:
                    logging.error(f"Failed to process {file_path}")
            except Exception as e:
                logging.error(f"Exception processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()