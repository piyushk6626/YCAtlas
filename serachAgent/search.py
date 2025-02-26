from pinecone import Pinecone
from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
from prompts import *
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
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

def normalize_data(result):
    # If the result object has a 'matches' attribute, use it
    if hasattr(result, 'matches'):
        data = result.matches
    # Alternatively, if it's a dict with a "matches" key, use that
    elif isinstance(result, dict) and "matches" in result:
        data = result["matches"]
    else:
        data = result  # Assume result is already a list

    normalized_data = []
    for item in data:
        # Convert ScoredVectorWithNamespace to dict
        normalized_item = {
            "id": item.id,
            "score": float(item.score),  # Convert score to float for JSON serialization
            "metadata": item.metadata
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


# Set up Pinecone API
def get_index():
    """
    Load environment variables, initialize the Pinecone client, and return the index.
    """
    # Load environment variables from a .env file
    load_dotenv()

    # Retrieve Pinecone API key and host URL from environment variables
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_host = os.getenv("PINECONE_HOST_URL")

    # Initialize the Pinecone client with the API key
    pc = Pinecone(api_key=pinecone_api_key)

    # Create and return the index using the host URL
    index = pc.Index(host=pinecone_host)
    return index


def query_index(index, query_vector, number_of_results):
    # Query the index
    response = index.query_namespaces(
        vector=query_vector,
        namespaces=[""],        # Search in the default namespace
        metric="cosine",        # Use cosine similarity
        top_k=number_of_results,
        include_values=False,
        include_metadata=True,
        show_progress=False,
    )

    # Assume the response is a dict or object with a 'matches' key/attribute
    if hasattr(response, 'matches'):
        return response.matches
    elif isinstance(response, dict) and "matches" in response:
        return response["matches"]
    else:
        return response

def search_companies(query: str) -> list:
   
    """
    Find similar items based on a query string using Pinecone.

    This function takes a query string, generates vector embeddings for it,
    and queries a Pinecone index to find and return the top similar items.

    Args:
        query (str): The query string to find similar items for.

    Returns:
        list: A list of results that are most similar to the query string.
    """

    number_of_results: int = 30
    # Get the Pinecone index using a helper function
    index = get_index()

    # #update the query based on given format 
    explained_query=explain_UserQuery(query)
    #explained_query=query

    # Generate vector embeddings for the query string
    vector = create_embeddings(explained_query)

    # Query the Pinecone index with the generated embeddings
    results = query_index(index, vector, number_of_results)

    # Return the list of results
    data= normalize_data(results)
    
    return data


def explain_UserQuery(query: str) -> str :
    messages=[
            {"role": "system", "content": SystemPrompt},
            {"role": "user", "content": query}
        ]
    
    Explained_Qury=client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.9
        
    )
        
        
    
    return Explained_Qury.choices[0].message.content



def deep_Question(query: str) -> list:
    """
    Generate a list of questions based on the query.

    This function takes a query string, generates a list of questions.
    
    Args:
        query (str): The query string to find similar items for.

    Returns:
        list: A list of results that are most similar to the query string.
    """
    completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SystemPrompt_Question},
        {"role": "user", "content": query}
    ],
    response_format=QuestionGeneration,
    )

    research_paper = completion.choices[0].message.parsed    
    return research_paper.questions

def deep_research(query: str) -> list:
    Questions = deep_Question(query)
    Datafinal = []
    
    # Use ThreadPoolExecutor to parallelize the find_similar_items calls
    with ThreadPoolExecutor() as executor:
        # Map the questions to find_similar_items function in parallel
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
        
        
        
if __name__ == "__main__":
    # Output = find_similar_items("Company that Works in Ecommerce USING AI SPECIFICALLY using AI search ")
    # print(Output)
    
    # # Save output to JSON file
    # with open('search_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(Output, f, indent=4, ensure_ascii=False)
    
    # print("Results saved to search_results.json")
    
    output=deep_research("Company that Works in RAG (retrieval-augmented generation) using AI")
    
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print("Results saved to search_results.json")
    