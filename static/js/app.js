document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/data")
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById("data-container");
        
        if (data.length === 0) {
          container.innerHTML = "<p>No data found.</p>";
          return;
        }
        
        const list = document.createElement("ul");
        data.forEach(item => {
          const listItem = document.createElement("li");
          // Display the node properties as a JSON string
          listItem.textContent = JSON.stringify(item);
          list.appendChild(listItem);
        });
        
        container.appendChild(list);
      })
      .catch(error => {
        console.error("Error fetching data: ", error);
        document.getElementById("data-container").innerHTML = "<p>Error loading data.</p>";
      });
  });
  