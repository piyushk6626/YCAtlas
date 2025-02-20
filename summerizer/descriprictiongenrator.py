import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt, user_prompt
import pandas as pd
from tqdm import tqdm
import json
from multiprocessing import Pool, cpu_count
import functools


def openai_client():    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client


def generate_company_description(markdown,Name,Headline,Batch,Description,Activity_Status,Website,Founded_Date,Team_Size,Location,Group_Partner,Tags):
    client = openai_client()
    max_retries = 10
    base_delay = 5  # base delay in seconds
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt(markdown,Name,Headline,Batch,Description,Activity_Status,Website,Founded_Date,Team_Size,Location,Group_Partner,Tags)}
                ]
            )
            # If successful, proceed with the rest of the function
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Completion tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")
            
            # Read current totals from file
            try:
                with open('token_usage_totals.json', 'r') as totals_file:
                    totals = json.load(totals_file)
            except FileNotFoundError:
                totals = {
                    'companies_processed': 0,
                    'total_prompt_tokens': 0,
                    'total_completion_tokens': 0,
                    'total_tokens': 0
                }
            
            # Update totals
            totals['companies_processed'] += 1
            totals['total_prompt_tokens'] += response.usage.prompt_tokens
            totals['total_completion_tokens'] += response.usage.completion_tokens
            totals['total_tokens'] += response.usage.total_tokens
            
            # Save updated totals
            with open('token_usage_totals.json', 'w') as totals_file:
                json.dump(totals, totals_file, indent=2)
            
            # Log individual usage with running totals
            with open('token_usage.log', 'a') as log_file:
                log_file.write(f"Company: {Name}, Batch: {Batch}\n")
                log_file.write(f"Prompt tokens: {response.usage.prompt_tokens}\n")
                log_file.write(f"Completion tokens: {response.usage.completion_tokens}\n")
                log_file.write(f"Total tokens: {response.usage.total_tokens}\n")
                log_file.write(f"Running Totals:\n")
                log_file.write(f"Companies processed: {totals['companies_processed']}\n")
                log_file.write(f"Total prompt tokens: {totals['total_prompt_tokens']}\n")
                log_file.write(f"Total completion tokens: {totals['total_completion_tokens']}\n")
                log_file.write(f"Total tokens overall: {totals['total_tokens']}\n")
                log_file.write("-" * 50 + "\n")
            
            return response.choices[0].message.content
            
        except Exception as e:
            if 'rate_limit_exceeded' in str(e):
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit reached. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(delay)
                    continue
            # If it's not a rate limit error or we've exhausted retries, raise the exception
            raise e

def process_company(row, output_folder):
    try:
        # Create filename
        safe_name = "".join(c if c.isalnum() else "_" for c in str(row['Name']))
        filename = f"{safe_name}_{row['Batch']}.json"
        file_path = os.path.join(output_folder, filename)
        
        # Skip if file already exists
        if os.path.exists(file_path):
            print(f"Skipping {row['Name']}: JSON file already exists")
            return
            
        # Generate description
        description = generate_company_description(
            row['markdown'],
            row['Name'],
            row['Headline'],
            row['Batch'],
            row['Description'],
            row['Activity_Status'],
            row['Website'],
            row['Founded_Date'],
            row['Team_Size'],
            row['Location'],
            row['Group_Partner'],
            row['Tags']
        )
        
        # Helper function to clean NaN values
        def clean_value(val):
            if pd.isna(val):
                return None
            return val
        
        # Create JSON data structure with all available fields
        company_data = {
            "links": clean_value(row['Links']),
            "name": clean_value(row['Name']),
            "headline": clean_value(row['Headline']),
            "batch": clean_value(row['Batch']),
            "description": clean_value(row['Description']),
            "activity_status": clean_value(row['Activity_Status']),
            "website": clean_value(row['Website']),
            "founded_date": clean_value(row['Founded_Date']),
            "team_size": clean_value(row['Team_Size']),
            "location": clean_value(row['Location']),
            "group_partner": clean_value(row['Group_Partner']),
            "group_partner_yc": clean_value(row['Group_Partner_YC']),
            "company_linkedin": clean_value(row['Company_Linkedin']),
            "company_twitter": clean_value(row['Company_Twitter']),
            "tags": clean_value(row['Tags']),
            "founders": [
                {
                    "name": clean_value(row['Founder1_Name']),
                    "description": clean_value(row['Founder1_Description']),
                    "linkedin": clean_value(row['Founder1_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder2_Name']),
                    "description": clean_value(row['Founder2_Description']),
                    "linkedin": clean_value(row['Founder2_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder3_Name']),
                    "description": clean_value(row['Founder3_Description']),
                    "linkedin": clean_value(row['Founder3_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder4_Name']),
                    "description": clean_value(row['Founder4_Description']),
                    "linkedin": clean_value(row['Founder4_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder5_Name']),
                    "description": clean_value(row['Founder5_Description']),
                    "linkedin": clean_value(row['Founder5_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder6_Name']),
                    "description": clean_value(row['Founder6_Description']),
                    "linkedin": clean_value(row['Founder6_LinkedIn'])
                },
                {
                    "name": clean_value(row['Founder7_Name']),
                    "description": clean_value(row['Founder7_Description']),
                    "linkedin": clean_value(row['Founder7_LinkedIn'])
                }
            ],
            "status": clean_value(row['status']),
            "markdown": clean_value(row['markdown']),
            "generated_description": description
        }
        
        # Remove None values from founders list
        company_data['founders'] = [
            founder for founder in company_data['founders'] 
            if founder['name'] is not None
        ]
        
        # Save to JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(company_data, f, ensure_ascii=False, indent=2)
        import time
        time.sleep(0.2)
            
    except Exception as e:
        print(f"Error processing {row['Name']}: {e}")

def process_companies_csv(input_path, output_folder):
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Determine number of processes (use 75% of available CPUs)
    num_processes = max(1, int(cpu_count() * 0.75))
    
    # Create a partial function with fixed output_folder
    process_company_partial = functools.partial(process_company, output_folder=output_folder)
    
    # Create a process pool and map the work
    with Pool(processes=num_processes) as pool:
        # Convert DataFrame rows to dictionaries for multiprocessing
        rows = df.to_dict('records')
        # Process companies in parallel with progress bar
        list(tqdm(pool.imap(process_company_partial, rows), total=len(rows), desc="Generating descriptions"))

if __name__ == "__main__":
    input_file = "data/Archive/filtered_output.csv"
    output_folder = "data/company_descriptions"
    process_companies_csv(input_file, output_folder)

