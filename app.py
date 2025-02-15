import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j import GraphDatabase
import json
import tempfile
import os
import colorsys  # New import to generate dynamic colors
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

def generate_color_palette(n):
    """
    Generate a list of n distinct hex colors.
    """
    colors = []
    for i in range(n):
        hue = i / float(n)
        lightness = 0.5
        saturation = 0.95
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        rgb = tuple(int(x * 255) for x in rgb)
        colors.append('#{:02X}{:02X}{:02X}'.format(*rgb))
    return colors

def create_graph_from_neo4j(records):
    """
    Build a NetworkX graph from records returned by Neo4j.
    Each node is identified by its Neo4j id (as string) and its labels (types) are stored.
    Each relationship edge will also include its type.
    """
    G = nx.Graph()
    
    for record in records:
        # Extract nodes and relationship
        start_node = record['n']  # source node
        end_node = record['m']    # target node
        relationship = record.get('r', None)  # relationship between the nodes
        
        # Extract node properties
        start_props = dict(start_node)
        end_props = dict(end_node)
        
        # Use the actual Neo4j id as identifier (as string)
        start_id = str(start_node.id)
        end_id = str(end_node.id)
        
        # Extract node labels (i.e. types) and store them as a property
        start_labels = list(start_node.labels)
        end_labels = list(end_node.labels)
        start_props['labels'] = start_labels
        end_props['labels'] = end_labels
        
        # Add nodes to the graph
        G.add_node(start_id, **start_props)
        G.add_node(end_id, **end_props)
        
        # Process relationship properties and add the relationship type
        if relationship is not None:
            rel_props = dict(relationship)
            rel_props['type'] = relationship.type
        else:
            rel_props = {}
        
        G.add_edge(start_id, end_id, **rel_props)
    
    return G

def visualize_graph(G):
    """
    Visualize the NetworkX graph using a Pyvis network.
    
    Modifications:
    1. Each node is colored based on its type (using its first label).
    2. Each node displays its id (Neo4j id) as its label.
    3. Each edge displays its relationship type.
    """
    # Initialize Pyvis network
    net = Network(notebook=True, width="100%", height="600px")
    
    # Generate a palette of 200 colors
    color_palette = generate_color_palette(200)
    color_map = {}
    
    # Build a mapping from primary node label to a color
    for node in G.nodes(data=True):
        node_data = node[1]
        node_labels = node_data.get('labels', [])
        if node_labels:
            primary_label = node_labels[0]
        else:
            primary_label = "default"
        if primary_label not in color_map:
            color_map[primary_label] = color_palette[len(color_map) % len(color_palette)]
    
    # Add nodes to the Pyvis network
    for node in G.nodes(data=True):
        node_id = node[0]
        node_data = node[1]
        node_labels = node_data.get('labels', [])
        
        # Get the display label from the id property, fallback to Neo4j ID if not found
        display_label = node_data.get('id', node_id)
        
        if node_labels:
            primary_label = node_labels[0]
        else:
            primary_label = "default"
        node_color = color_map.get(primary_label, "#777777")
        
        # Build a tooltip from the node properties
        title = '<br>'.join([f"{k}: {v}" for k, v in node_data.items()])
        net.add_node(node_id, label=str(display_label), title=title, color=node_color)
    
    # Add edges to the Pyvis network and display the relationship type as edge label
    for edge in G.edges(data=True):
        edge_data = edge[2]
        title = '<br>'.join([f"{k}: {v}" for k, v in edge_data.items()])
        edge_label = edge_data.get("type", "")
        net.add_edge(edge[0], edge[1], title=title, label=edge_label)
    
    # Generate HTML file for visualization
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
                
                # Create a NetworkX graph from the records
                G = create_graph_from_neo4j(records)
                
                # Visualize the graph using Pyvis
                html_file = visualize_graph(G)
                
                # Display graph in Streamlit
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