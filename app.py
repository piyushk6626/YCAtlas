from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv()

# Set your Neo4j connection details (use environment variables or hardcode for testing)
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Query to fetch nodes and relationships
    query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25"
    nodes = {}
    edges = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            n = record["n"]
            m = record["m"]
            r = record["r"]
            # Add nodes (use the internal Neo4j id as unique key)
            if n.id not in nodes:
                nodes[n.id] = {
                    "id": n.id,
                    "labels": list(n.labels),
                    "properties": dict(n)
                }
            if m.id not in nodes:
                nodes[m.id] = {
                    "id": m.id,
                    "labels": list(m.labels),
                    "properties": dict(m)
                }
            # Add the relationship as an edge
            edges.append({
                "id": r.id,
                "source": r.start_node.id,
                "target": r.end_node.id,
                "type": r.type,
                "properties": dict(r)
            })
    return jsonify({"nodes": list(nodes.values()), "edges": edges})

if __name__ == '__main__':
    app.run(debug=True)