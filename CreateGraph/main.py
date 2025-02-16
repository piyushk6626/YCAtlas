# main.py
import csv
import logging
from .config import load_env_vars, setup_logging
from .neo4j_helper import setup_neo4j_connection
from .llm_graph import setup_openai_model
from .data_processing import process_company_row

def process_csv_file(file_path):
    """
    Process a CSV file and add its contents to a Neo4j graph.

    Args:
        file_path (str): The path to the CSV file to process
    """
    logger = setup_logging()
    config = load_env_vars()
    graph = setup_neo4j_connection(config)
    llm_transformer = setup_openai_model(config["OPENAI_API_KEY"])
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            process_company_row(row, graph, llm_transformer, config["OPENAI_API_KEY"])
    
    logging.info("CSV processing completed")

if __name__ == "__main__":
    """
    Entry point for the script.
    """
    process_csv_file("yc25det.csv")
