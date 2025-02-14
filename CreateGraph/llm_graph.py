
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import logging
import csv
import os

def log_graph_interaction(input_text, graph_output, filename='graph_log.csv'):
    """
    Appends a row with the graph input text and its corresponding output to a CSV file.
    If the file doesn't exist, it writes the header first.
    """
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
         fieldnames = ['input', 'output']
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
         if not file_exists:
             writer.writeheader()
         writer.writerow({'input': input_text, 'output': graph_output})

def setup_openai_model(api_key):
    logging.info("Setting up OpenAI LLMGraphTransformer")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=api_key)
    return LLMGraphTransformer(llm=llm)

def create_graph(text, llm_transformer):
    logging.info("Converting text to graph document")
    documents = [Document(page_content=text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    
    # Convert graph output to a single string for CSV logging.
    # Adjust this if your Document objects contain more complex data.
    print(graph_documents)
    graph_output_str = str(graph_documents)
    
    # Log both the input text and the graph output.
    log_graph_interaction(text, graph_output_str)
    
    return graph_documents
