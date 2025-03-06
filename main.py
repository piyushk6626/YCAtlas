import os
import json
import time
import pandas as pd
import asyncio
import chromadb
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
import functools

# Import modules from ScrapingScripts
from ScrapingScripts.links import scrape_links, setup_driver, Number_of_Loaded_Product, scroll_page
from ScrapingScripts.scrape import scrape_page, process_csv_to_json

# Import for AsyncWebCrawler
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# For embeddings
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System and user prompts from summerizer/prompts.py
SYSTEM_PROMPT = """
You are a helpful assistant that generates a detailed yet simple summary of a given company's information. Your writing should be clear, engaging, and in the tone of Paul Graham—direct, insightful, and slightly conversational
"""

def tag_string_to_dict(tags):
    if isinstance(tags, float) or tags is None:
        return []
    tags = tags.split(";")
    try:
        tags = [tag.split(":")[1].strip() for tag in tags if ":" in tag]
        return tags
    except IndexError:
        return []

def generate_user_prompt(markdown, name, headline, batch, description, activity_status, 
                         website, founded_date, team_size, location, group_partner, tags):
    tags_formatted = tag_string_to_dict(tags)
    output = f"""
    Name of the Company is {name}
    mission of the {name} is {headline}
    The {name} initially started as {description} Website of the Company is {website}
    it was founded in {founded_date} and is part of Y Combinator Batch {batch}
    Located in {location} it has Team of {team_size} employees
    They have {group_partner} as their Group Partner
    it is tagged as {tags_formatted}
    The Company is currently Doing following things: {markdown}
    """
    return output

# 1 & 2. Scraping YC page and getting company details
def scrape_yc_companies(batch_url, links_csv, details_json):
    """
    Scrapes YC companies from the given batch URL and saves details
    """
    print(f"Starting to scrape links from {batch_url}...")
    scrape_links(batch_url, links_csv)
    print(f"Links scraped and saved to {links_csv}")
    
    print("Processing links to get company details...")
    process_csv_to_json(links_csv, details_json)
    print(f"Company details scraped and saved to {details_json}")
    
    return details_json

# 3. Crawl company websites using crawl4ai
async def crawl_website(url):
    """Crawl a website and return its markdown content"""
    try:
        browser_config = BrowserConfig()
        run_config = CrawlerRunConfig()
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            return result.markdown_v2
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return None

async def crawl_all_websites(companies_data, max_concurrent=10):
    """Crawl all company websites in parallel"""
    semaphore = asyncio.Semaphore(max_concurrent)
    crawl_tasks = []
    
    async def crawl_with_semaphore(company):
        async with semaphore:
            website = company.get('Website')
            if website and isinstance(website, str) and website.strip():
                try:
                    markdown = await crawl_website(website)
                    if markdown:
                        company['markdown'] = markdown
                        company['crawl_status'] = True
                        print(f"Successfully crawled: {website}")
                    else:
                        company['markdown'] = None
                        company['crawl_status'] = False
                        print(f"Failed to crawl: {website}")
                except Exception as e:
                    company['markdown'] = None
                    company['crawl_status'] = False
                    print(f"Error crawling {website}: {e}")
            else:
                company['markdown'] = None
                company['crawl_status'] = False
                print(f"No valid website for company: {company.get('Name', 'Unknown')}")
            return company
    
    for company in companies_data:
        crawl_tasks.append(crawl_with_semaphore(company))
    
    return await asyncio.gather(*crawl_tasks)

# 4. Generate summaries using an LLM
def generate_company_description(company_data):
    """Generate a company description using LLM"""
    client = get_openai_client()
    
    # Extract required fields
    markdown = company_data.get('markdown', '')
    name = company_data.get('Name', '')
    headline = company_data.get('Headline', '')
    batch = company_data.get('Batch', '')
    description = company_data.get('Description', '')
    activity_status = company_data.get('Activity_Status', '')
    website = company_data.get('Website', '')
    founded_date = company_data.get('Founded_Date', '')
    team_size = company_data.get('Team_Size', '')
    location = company_data.get('Location', '')
    group_partner = company_data.get('Group_Partner', '')
    tags = company_data.get('Tags', '')
    
    if not markdown:
        print(f"No markdown content for {name}, skipping summary generation")
        return None
    
    try:
        user_prompt = generate_user_prompt(
            markdown, name, headline, batch, description, activity_status,
            website, founded_date, team_size, location, group_partner, tags
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or another model of your choice
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating description for {name}: {e}")
        return None

def generate_all_descriptions(companies_data, output_folder, num_processes=None):
    """Generate descriptions for all companies and save to JSON files"""
    os.makedirs(output_folder, exist_ok=True)
    
    if num_processes is None:
        num_processes = max(1, int(cpu_count() * 0.75))
    
    def process_company(company):
        try:
            # Skip if the company wasn't crawled successfully
            if not company.get('crawl_status', False):
                print(f"Skipping {company.get('Name', 'Unknown')}: No crawl data")
                return company
            
            # Generate description
            company['generated_description'] = generate_company_description(company)
            
            # Save as individual JSON
            if company.get('generated_description'):
                safe_name = "".join(c if c.isalnum() else "_" for c in str(company.get('Name', 'unknown')))
                batch = company.get('Batch', 'unknown')
                filename = f"{safe_name}_{batch}.json"
                file_path = os.path.join(output_folder, filename)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(company, f, ensure_ascii=False, indent=2)
                
                print(f"Saved description for {company.get('Name', 'Unknown')}")
            
            return company
        except Exception as e:
            print(f"Error processing {company.get('Name', 'Unknown')}: {e}")
            return company
    
    with ThreadPoolExecutor(max_workers=num_processes) as executor:
        processed_companies = list(executor.map(process_company, companies_data))
    
    # Save all processed companies to a single JSON file
    with open(os.path.join(output_folder, "all_companies.json"), 'w', encoding='utf-8') as f:
        json.dump(processed_companies, f, ensure_ascii=False, indent=2)
    
    return processed_companies

# 5. Generate embeddings for companies
def generate_embedding(text):
    """Generate embedding for text using OpenAI API"""
    client = get_openai_client()
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def generate_all_embeddings(companies_data, num_processes=None):
    """Generate embeddings for all companies with descriptions"""
    if num_processes is None:
        num_processes = max(1, int(cpu_count() * 0.75))
    
    def process_company_embedding(company):
        try:
            description = company.get('generated_description', '')
            if description:
                company['embedding'] = generate_embedding(description)
                print(f"Generated embedding for {company.get('Name', 'Unknown')}")
            return company
        except Exception as e:
            print(f"Error generating embedding for {company.get('Name', 'Unknown')}: {e}")
            return company
    
    with ThreadPoolExecutor(max_workers=num_processes) as executor:
        return list(tqdm(
            executor.map(process_company_embedding, companies_data),
            total=len(companies_data),
            desc="Generating embeddings"
        ))

# 6. Store in ChromaDB
def store_in_chromadb(companies_data, collection_name="yc_companies"):
    """Store company data in ChromaDB"""
    # Initialize ChromaDB client
    chroma_client = chromadb.Client()
    
    # Create or get collection
    try:
        collection = chroma_client.get_or_create_collection(name=collection_name)
        print(f"Working with ChromaDB collection: {collection_name}")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for i, company in enumerate(companies_data):
            if not company.get('embedding') or not company.get('generated_description'):
                continue
                
            company_id = f"company_{i}"
            ids.append(company_id)
            
            # Add description as document
            documents.append(company.get('generated_description', ''))
            
            # Add embedding
            embeddings.append(company.get('embedding'))
            
            # Add metadata
            metadata = {
                "name": company.get('Name', ''),
                "batch": company.get('Batch', ''),
                "website": company.get('Website', ''),
                "location": company.get('Location', ''),
                "tags": company.get('Tags', '')
            }
            metadatas.append(metadata)
        
        # Add data to collection
        if ids:
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Added {len(ids)} companies to ChromaDB")
        else:
            print("No valid companies to add to ChromaDB")
        
        return True
    except Exception as e:
        print(f"Error storing in ChromaDB: {e}")
        return False

# Main pipeline function
async def run_pipeline(batch_url, output_dir="data"):
    """Run the complete YC scraping and processing pipeline"""
    start_time = time.time()
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    links_csv = os.path.join(output_dir, "yc_links.csv")
    details_json = os.path.join(output_dir, "yc_details.json")
    descriptions_dir = os.path.join(output_dir, "company_descriptions")
    
    # Step 1 & 2: Scrape YC page for links and company details
    details_json = scrape_yc_companies(batch_url, links_csv, details_json)
    
    # Load company details
    with open(details_json, 'r', encoding='utf-8') as f:
        companies_data = json.load(f)
    
    print(f"Loaded details for {len(companies_data)} companies")
    
    # Step 3: Crawl company websites
    print("Crawling company websites...")
    companies_data = await crawl_all_websites(companies_data, max_concurrent=10)
    
    # Save intermediate results
    with open(os.path.join(output_dir, "companies_with_markdown.json"), 'w', encoding='utf-8') as f:
        json.dump(companies_data, f, ensure_ascii=False, indent=2)
    
    # Step 4: Generate descriptions
    print("Generating company descriptions...")
    companies_data = generate_all_descriptions(companies_data, descriptions_dir)
    
    # Step 5: Generate embeddings
    print("Generating embeddings...")
    companies_data = generate_all_embeddings(companies_data)
    
    # Save companies with embeddings
    with open(os.path.join(output_dir, "companies_with_embeddings.json"), 'w', encoding='utf-8') as f:
        json.dump(companies_data, f, ensure_ascii=False, indent=2)
    
    # Step 6: Store in ChromaDB
    print("Storing data in ChromaDB...")
    store_in_chromadb(companies_data)
    
    end_time = time.time()
    print(f"Complete pipeline executed in {end_time - start_time:.2f} seconds")

# Main entry point
def main():
    """Main entry point for running the YC scraper pipeline"""
    parser = argparse.ArgumentParser(description="YC Company Scraper Pipeline")
    parser.add_argument("--batch", type=str, default="X25", 
                        help="YC batch to scrape (e.g., W25, S24)")
    parser.add_argument("--output", type=str, default="data",
                        help="Output directory")
    parser.add_argument("--max-concurrent", type=int, default=10,
                        help="Maximum concurrent requests")
    
    args = parser.parse_args()
    
    # Construct batch URL
    batch_url = f"https://www.ycombinator.com/companies?batch={args.batch}"
    
    # Run the pipeline
    asyncio.run(run_pipeline(batch_url, args.output))

if __name__ == "__main__":
    import argparse
    main()