# app.py
from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase
import logging
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

def get_graph_data():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        app.logger.debug(f"Connecting to Neo4j at {NEO4J_URI}")
        
        with driver.session() as session:
            # Modified query to get all relationships
            result = session.run("""
                MATCH (n)-[r]->(m)
                RETURN DISTINCT n, r, m
                UNION
                MATCH (n)
                WHERE NOT (n)--()
                RETURN n, null as r, null as m
            """)
            
            nodes = {}
            links = []
            
            for record in result:
                # Process start node
                start_node = record["n"]
                if start_node.id not in nodes:
                    nodes[start_node.id] = {
                        "id": str(start_node.id),
                        "label": list(start_node.labels),
                        "properties": dict(start_node)
                    }
                
                # Process end node and relationship if they exist
                if record["m"] is not None:
                    end_node = record["m"]
                    if end_node.id not in nodes:
                        nodes[end_node.id] = {
                            "id": str(end_node.id),
                            "label": list(end_node.labels),
                            "properties": dict(end_node)
                        }
                    
                    relationship = record["r"]
                    links.append({
                        "source": str(start_node.id),
                        "target": str(end_node.id),
                        "type": type(relationship).__name__,
                        "properties": dict(relationship)
                    })
            
            app.logger.debug(f"Found {len(nodes)} nodes and {len(links)} relationships")
            return {
                "nodes": list(nodes.values()),
                "links": links
            }
            
    except Exception as e:
        app.logger.error(f"Neo4j Error: {str(e)}")
        raise e
    finally:
        if 'driver' in locals():
            driver.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph')
def get_graph():
    try:
        data = get_graph_data()
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error in /api/graph: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)