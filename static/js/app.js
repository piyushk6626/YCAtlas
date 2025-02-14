document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/data")
      .then(response => response.json())
      .then(data => {
        // Build the elements array for Cytoscape:
        const elements = [];
  
        // Process nodes: Convert Neo4j nodes to Cytoscape nodes
        data.nodes.forEach(node => {
          elements.push({
            data: {
              id: node.id.toString(),               // Ensure the id is a string
              label: node.labels.join(', '),         // Concatenate labels for display
              ...node.properties                     // Spread any additional properties
            }
          });
        });
  
        // Process edges: Convert Neo4j relationships to Cytoscape edges
        data.edges.forEach(edge => {
          elements.push({
            data: {
              id: "edge-" + edge.id,
              source: edge.source.toString(),
              target: edge.target.toString(),
              label: edge.type,
              ...edge.properties
            }
          });
        });
  
        // Initialize Cytoscape with the constructed elements
        const cy = cytoscape({
          container: document.getElementById('cy'),
          elements: elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'background-color': '#0074D9',
                'color': '#fff',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': '40px',
                'height': '40px'
              }
            },
            {
              selector: 'edge',
              style: {
                'label': 'data(label)',
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
              }
            }
          ],
          layout: {
            name: 'cose', // A force-directed layout; try others if desired
            padding: 10
          }
        });
      })
      .catch(error => {
        console.error("Error fetching graph data:", error);
        document.getElementById("cy").innerHTML = "<p>Error loading graph data.</p>";
      });
  });
  