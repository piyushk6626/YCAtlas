import os
import json
import chromadb
import glob
from typing import List, Dict, Any

# Define the paths
DATA_DIR = os.path.join("data","company_descriptions")  # Directory with JSON files
COLLECTION_NAME = "companies"
CHROMA_DB_PATH = "chroma_db"  # Where to store the database

# Create the ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Create or get the collection - note that we're not using an embedding function
# since we'll be using the pre-computed embeddings
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' already exists")
except:
    # Create a new collection without an embedding function
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity for the vector space
    )
    print(f"Created new collection '{COLLECTION_NAME}'")

def process_json_files(directory: str) -> List[Dict[str, Any]]:
    """Process all JSON files in the given directory."""
    processed_data = []
    
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract the company ID from filename or use the name
            company_id = os.path.basename(file_path).replace('.json', '')
            
            # Prepare the document content - what we want to have available for search results
            document_content = f"""
            Name: {data.get('name', 'N/A')}
            Headline: {data.get('headline', 'N/A')}
            Description: {data.get('description', 'N/A')}
            Batch: {data.get('batch', 'N/A')}
            Location: {data.get('location', 'N/A')}
            Founded: {data.get('founded_date', 'N/A')}
            Team Size: {data.get('team_size', 'N/A')}
            Website: {data.get('website', 'N/A')}
            Tags: {data.get('tags', 'N/A')}
            """
            
            # Add founders information if available
            if 'founders' in data and isinstance(data['founders'], list):
                founders_text = "\nFounders:\n"
                for founder in data['founders']:
                    founder_name = founder.get('name', 'N/A')
                    founder_desc = founder.get('description', 'N/A')
                    founders_text += f"- {founder_name}: {founder_desc}\n"
                document_content += founders_text
            
            # Add generated description if available
            if 'generated_description' in data:
                document_content += f"\nGenerated Description: {data['generated_description']}"
            
            # Add tags if available
            if 'tags' in data:
                document_content += f"\nTags: {data['tags']}"
                
            # Add social links if available
            if 'social_links' in data and isinstance(data['social_links'], list):
                social_links_str = ", ".join(data['social_links'])
                document_content += f"\nSocial Links: {social_links_str}"
                
            # Prepare metadata for filtering - ensure no None values and convert complex types to strings
            metadata = {
                "name": data.get('name', '') or '',
                "headline": data.get('headline', '') or '',
                "batch": data.get('batch', '') or '',
                "location": data.get('location', '') or '',
                "founded_date": float(data.get('founded_date', 0)) if data.get('founded_date') is not None else 0,
                "team_size": float(data.get('team_size', 0)) if data.get('team_size') is not None else 0,
                "tags": data.get('tags', '') or '',
                "activity_status": data.get('activity_status', '') or '',
                "description": data.get('description', '') or '',
                "generated_description": data.get('generated_description', '') or '',
                "website": data.get('website', '') or '',
                "group_partner": data.get('group_partner', '') or '',
                "group_partner_yc": data.get('group_partner_yc', '') or '',
                "links": json.dumps(data.get('links', '')) if isinstance(data.get('links'), (list, dict)) else (data.get('links', '') or ''),
                # Convert social_links to a string
                "social_links": json.dumps(data.get('social_links', [])) if isinstance(data.get('social_links'), list) else '',
                "logo_path": data.get('logo_path', '') or '',
                # Convert founders to a JSON string
                "founders": json.dumps(data.get('founders', [])) if isinstance(data.get('founders'), list) else ''
            }
            
            # Get the embedding - this should be in all your data files
            if 'embedding' in data and isinstance(data['embedding'], list):
                embedding = data['embedding']
                
                processed_data.append({
                    "id": company_id or data.get('name', '').replace(' ', '_').lower(),
                    "document": document_content,
                    "metadata": metadata,
                    "embedding": embedding
                })
                
                print(f"Processed: {data.get('name', company_id)}")
            else:
                print(f"Warning: No embedding found for {data.get('name', company_id)}. Skipping.")
                
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    return processed_data

def add_to_chroma(collection, processed_data: List[Dict[str, Any]]):
    """Add the processed data to ChromaDB."""
    batch_size = 100  # Process in batches to avoid memory issues
    
    for i in range(0, len(processed_data), batch_size):
        batch = processed_data[i:i+batch_size]
        
        # Add items with embeddings
        collection.add(
            ids=[item["id"] for item in batch],
            documents=[item["document"] for item in batch],
            metadatas=[item["metadata"] for item in batch],
            embeddings=[item["embedding"] for item in batch]
        )
        
        print(f"Added batch {i//batch_size + 1} ({len(batch)} items)")

def main():
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    
    # Process the JSON files
    processed_data = process_json_files(DATA_DIR)
    
    if processed_data:
        # Add to ChromaDB
        add_to_chroma(collection, processed_data)
        print(f"Successfully added {len(processed_data)} companies to ChromaDB")
        
        # Count items in collection to verify
        count = collection.count()
        print(f"Total items in collection: {count}")
    else:
        print("No data processed. Check if the JSON files exist in the specified directory.")

if __name__ == "__main__":
    main()