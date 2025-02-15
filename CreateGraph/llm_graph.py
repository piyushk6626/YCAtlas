from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import logging


def setup_openai_model(api_key):
    """
    Set up an OpenAI language model for graph transformation.

    Args:
        api_key (str): The API key for the OpenAI model
    """
    logging.info("Setting up OpenAI LLMGraphTransformer")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=api_key)
    return LLMGraphTransformer(llm=llm)

def create_graph(text, llm_transformer):
    """
    Convert input text into graph documents using a language model transformer.

    Args:
        text (str): The input text to be converted into graph format
        llm_transformer (LLMGraphTransformer): The language model transformer to use for conversion

    Returns:
        list[Document]: A list of graph documents containing the extracted relationships
    """
    
    logging.info("Converting text to graph document")
    documents = [Document(page_content=text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    
    # Convert graph output to a single string for CSV logging.
    # Adjust this if your Document objects contain more complex data.
    print(graph_documents)
    
    return graph_documents
