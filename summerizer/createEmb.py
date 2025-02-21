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

def generate_embedding(text):
    client = openai_client()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def process_json_file(file_path):
    try:
        # Read the existing JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        description = data.get('generated_description', '')
        if not description:
            print(f"No generated_description found in {file_path}")
            return
        
        # Generate embedding and add it to the JSON data
        embedding = generate_embedding(description)
        data['embedding'] = embedding
        
        # Write the updated JSON back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    directory = r"D:\DEV\YC25\YC25\data\company_descriptions"
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    
    # Process files with progress bar
    for file_path in tqdm(json_files, desc="Generating embeddings"):
        process_json_file(file_path)
    
    print("Completed generating embeddings")

if __name__ == "__main__":
    main()
