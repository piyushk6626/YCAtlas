# modules/neo4j_helper.py
from langchain_neo4j import Neo4jGraph
import logging

def setup_neo4j_connection(config):
    logging.info("Setting up Neo4j connection")
    return Neo4jGraph(
        refresh_schema=False,
        password=config["NEO4J_PASSWORD"],
        url=config["NEO4J_URI"],
        username=config["NEO4J_USERNAME"]
    )
