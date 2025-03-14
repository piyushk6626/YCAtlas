import chromadb
from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
import chromadb
from .prompts import *
from concurrent.futures import ThreadPoolExecutor
import chromadb

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("restaurant_process.log"),
        logging.StreamHandler()
    ]
)

def normalize_data(results):
    """
    Normalize ChromaDB results to match the expected format.
    """
    normalized_data = []
    
    # ChromaDB returns a dict with lists for ids, distances, metadatas
    for i in range(len(results['ids'][0])):
        # Convert similarity distance to score (invert distance)
        # ChromaDB returns distances where lower is better, so we convert to a 0-1 score
        score = 1.0 - results['distances'][0][i]
        
        normalized_item = {
            "id": results['ids'][0][i],
            "score": float(score),
            "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
        }
        normalized_data.append(normalized_item)

    return normalized_data


def create_embeddings(content):
    """Generate embeddings using OpenAI API."""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=content
        )
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        return None


def get_chroma_client():
    """
    Initialize and return the ChromaDB client.
    """
    load_dotenv()
    
    chroma_client = chromadb.PersistentClient(path=os.join(os.getcwd(), "chroma_db"))
    
    collection = chroma_client.get_or_create_collection(
        name="companies",  # Changed to match the uploaded collection name
        
    )
    return collection


def query_collection(collection, query_vector, number_of_results):
    """
    Query the ChromaDB collection with a vector.
    """
    # Query the collection
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=number_of_results,
        include=["distances","metadatas"]   
    )
    
    return results


def search_companies(query: str, Batch:int) -> list:
    """
    Find similar items based on a query string using ChromaDB.

    This function takes a query string, generates vector embeddings for it,
    and queries a ChromaDB collection to find and return the top similar items.

    Args:
        query (str): The query string to find similar items for.

    Returns:
        list: A list of results that are most similar to the query string.
    """
    number_of_results: int = 30
    
    # Get the ChromaDB collection
    collection = get_chroma_client()

    # Update the query based on given format 
    explained_query = explain_UserQuery(query)
    
    # Generate vector embeddings for the query string
    vector = create_embeddings(explained_query)

    # Query the ChromaDB collection with the generated embeddings
    results = query_collection(collection, vector, number_of_results)
    # Normalize and return the results
    data = normalize_data(results)
    
    return data


def explain_UserQuery(query: str) -> str:
    messages = [
        {"role": "system", "content": SystemPrompt},
        {"role": "user", "content": query}
    ]
    
    Explained_Query = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.9
    )
    
    return Explained_Query.choices[0].message.content


def deep_Question(query: str) -> list:
    """
    Generate a list of questions based on the query.

    This function takes a query string, generates a list of questions.
    
    Args:
        query (str): The query string to find similar items for.

    Returns:
        list: A list of questions derived from the query.
    """
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        reasoning_effort="low",
        messages=[
            {"role": "system", "content": SystemPrompt_Question},
            {"role": "user", "content": query}
        ],
        response_format=QuestionGeneration,
    )

    research_paper = completion.choices[0].message.parsed    
    return research_paper.questions


def deep_research(query: str,Batch:int) -> list:
    """
    Perform deep research by generating questions and searching for each.
    
    Args:
        query (str): The base query to expand on.
        
    Returns:
        list: Aggregated and scored search results.
    """
    Questions = deep_Question(query)
    Datafinal = []
    
    # Use ThreadPoolExecutor to parallelize the search_companies calls
    with ThreadPoolExecutor() as executor:
        # Map the questions to search_companies function in parallel
        results = list(executor.map(search_companies, Questions))
    
    # Process all results
    for Data in results:
        for item in Data:
            # Check if an item with the same ID exists in Datafinal
            existing_item = next((x for x in Datafinal if x['id'] == item['id']), None)
            
            if existing_item is None:
                Datafinal.append(item)
            else:
                # Add the scores for items with matching IDs
                existing_item['score'] += item['score']
    
    # Sort the list based on the score attribute
    Datafinal.sort(key=lambda x: x['score'], reverse=True)
    return Datafinal


# Function to add data to ChromaDB (not in original code but useful for setup)
def add_to_chromadb(items):
    """
    Add items to the ChromaDB collection.
    
    Args:
        items: List of items with text content and metadata
    """
    collection = get_chroma_client()
    
    ids = []
    documents = []
    metadatas = []
    
    for i, item in enumerate(items):
        ids.append(str(i))
        documents.append(item["text"])
        metadatas.append(item["metadata"])
    
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    logging.info(f"Added {len(ids)} items to ChromaDB collection")
        
        
if __name__ == "__main__":
    output = search_companies("Company that Works in RAG (retrieval-augmented generation) using AI")
    
    with open('search_results_chroma.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print("Results saved to search_results.json")