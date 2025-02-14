import os
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from dotenv import load_dotenv
import csv

# Uncomment the below to use LangSmith. Not required.
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
# os.environ["LANGSMITH_TRACING"] = "true"


def setup_neo4j_connection():
    load_dotenv()
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    graph = Neo4jGraph(refresh_schema=False,password=NEO4J_PASSWORD, url=NEO4J_URI, username=NEO4J_USERNAME)
    return graph



def setup_openai_model():
    """
    Sets up and returns an LLMGraphTransformer using OpenAI's GPT-4o model.

    This function initializes a ChatOpenAI instance with a specific temperature and model name,
    using an API key retrieved from environment variables. It then creates an LLMGraphTransformer
    with the ability to process node properties.

    Returns:
        LLMGraphTransformer: An instance configured with the specified language model.
    """
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        )
    return llm_transformer

def create_graph(text):
    llm_transformer = setup_openai_model()    
    documents = [Document(page_content=text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    print(f"Nodes:{graph_documents[0].nodes}")
    print(f"Relationships:{graph_documents[0].relationships}")
    return graph_documents
if __name__ == "__main__":
    
    A="""
    the company Browser Use is a Open Source Web Agents company  in YC(Y combinator) W25 BATCH
    "Browser Use allows developers to create state of the art web agents with a few lines of code.

We currently stand at 89% on Web Voyager dataset, which is the best web agent you can actually use.

Fastest growing repository on Github in January 2025"
"""
    B="""the  founder of Browser Use the Open Source Web Agents company is Magnus Müller, Founder . I am a serial entrepreneur and AI researcher. I have worked as a researcher for Cambridge CARES, ETH Zurich, and in R&D for car companies. I have developed bots and web automations since I can code. 
I am now building a browser tool that enables AI to control your browser. linkdin https://www.linkedin.com/in/magnus-mueller"""
    graph_documents=create_graph(B)
    graph = setup_neo4j_connection()    
    graph.add_graph_documents(graph_documents)
    