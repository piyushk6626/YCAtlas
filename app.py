import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j import GraphDatabase
import json
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Neo4j connection details from environment variables
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]

def create_graph_from_neo4j(records):
    G = nx.Graph()
    
    # Add nodes and edges from Neo4j records
    for record in records:
        # Extract node properties
        start_node = record['n']  # Assuming 'n' is the source node
        end_node = record['m']    # Assuming 'm' is the target node
        relationship = record.get('r', {})  # Assuming 'r' is the relationship
        
        # Get node properties as dictionaries
        start_props = dict(start_node)
        end_props = dict(end_node)
        
        # Use node IDs as unique identifiers
        start_id = start_props.get('name', str(start_node.id))
        end_id = end_props.get('name', str(end_node.id))
        
        # Add nodes with all their properties
        G.add_node(start_id, **start_props)
        G.add_node(end_id, **end_props)
        
        # Add edge with relationship properties
        G.add_edge(start_id, end_id, **dict(relationship))
    
    return G

def visualize_graph(G):
    # Create Pyvis network
    net = Network(notebook=True, width="100%", height="600px")
    
    # Add nodes
    for node in G.nodes(data=True):
        label = str(node[1].get('name', node[0]))
        title = '<br>'.join([f"{k}: {v}" for k, v in node[1].items()])
        net.add_node(node[0], label=label, title=title)
    
    # Add edges
    for edge in G.edges(data=True):
        title = '<br>'.join([f"{k}: {v}" for k, v in edge[2].items()])
        net.add_edge(edge[0], edge[1], title=title)
    
    # Generate HTML file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
        net.save_graph(tmpfile.name)
        return tmpfile.name

def main():
    st.title("Neo4j Graph Viewer")
    
    # Sidebar for Neo4j connection settings
    st.sidebar.header("Neo4j Connection Settings")
    uri = st.sidebar.text_input("Neo4j URI", NEO4J_URI)
    user = st.sidebar.text_input("Username", NEO4J_USER)
    password = st.sidebar.text_input("Password", type="password", value=NEO4J_PASSWORD)
    
    # Custom Cypher query input
    st.sidebar.header("Query Settings")
    cypher_query = st.sidebar.text_area(
        "Cypher Query",
        """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """
    )
    
    if st.sidebar.button("Connect and Visualize"):
        try:
            # Connect to Neo4j
            conn = Neo4jConnection(uri, user, password)
            
            with st.spinner("Fetching data from Neo4j..."):
                # Execute query
                records = conn.query(cypher_query)
                
                if not records:
                    st.warning("No data returned from the query.")
                    return
                
                # Create NetworkX graph
                G = create_graph_from_neo4j(records)
                
                # Visualize graph
                html_file = visualize_graph(G)
                
                # Display graph
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                components.html(html_data, height=600)
                
                # Display graph statistics
                st.subheader("Graph Statistics")
                st.write(f"Number of nodes: {G.number_of_nodes()}")
                st.write(f"Number of edges: {G.number_of_edges()}")
                
                # Cleanup
                os.unlink(html_file)
                conn.close()
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()