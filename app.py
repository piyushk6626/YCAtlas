from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase
import os

app = Flask(__name__)

# Set your Neo4j connection details (use environment variables or hardcode for testing)
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # A simple query: adjust it according to your data model and requirements
    query = "MATCH (n) RETURN n LIMIT 25"
    with driver.session() as session:
        result = session.run(query)
        records = []
        for record in result:
            # Convert the Neo4j node properties to a dictionary
            node = record["n"]
            records.append(dict(node))
        return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True)
