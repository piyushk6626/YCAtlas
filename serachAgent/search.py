from pinecone import Pinecone
from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv


def normalize_restaurant_data(result):
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

def find_similar_items(query: str) -> list:
   
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
    data= normalize_restaurant_data(results)
    # dicto={
    #     "type": "restaurant",
    #     "data": data
    # }
    return data

SystemPrompt="""Write a concise description to help the user find a company based on their query. Ensure the description incorporates the following points:

- **Mission of the company**: Clearly articulate the company's mission.
- **Tech Stack of the company**: Highlight the technologies the company utilizes.

Your writing should be clear, engaging, and in the tone of Paul Graham—direct, insightful, and slightly conversational.

# Steps

1. Analyze the user's query to understand their needs.
2. Identify the key aspects of the company's mission and tech stack.
3. Write a clear, concise, and engaging description that reflects these aspects.
4. Ensure the tone is direct, insightful, and conversational, resembling Paul Graham's style.

# Output Format

- A short paragraph comprising 100-150 words.
- Ensure the language is clear and easy to understand.
- Use a tone that is direct, insightful, and slightly conversational.

# Examples

**Input**: User is looking for a company that has a strong mission related to sustainability and uses innovative technology.

**Output Example**: "a company passionately driven to make the world sustainable by integrating cutting-edge technology into everyday life. Their mission is simple yet powerful: to reduce carbon footprints globally. Leveraging a multi-faceted tech stack that includes AI-driven solutions and IoT devices, they are continuously innovating to create more sustainable practices. It's all about impact here—transforming our planet for the better, one tech solution at a time."

(Note: The output should be tailored according to the specific company's mission and tech stack, ensuring it reflects the tone and style specified above.)"""

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
    
    
    
    

if __name__ == "__main__":
    Output = find_similar_items("Company that works on RAG(Retrieval Augmented Generation)")
    print(Output)
    
    # Save output to JSON file
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(Output, f, indent=4, ensure_ascii=False)
    
    print("Results saved to search_results.json")