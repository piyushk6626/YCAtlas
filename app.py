import streamlit as st
import json
import os
from chromadb import search  # using your provided import

# Directory that stores the company JSON files (details)
DATA_DIR = "data/saved_companies"

# ============================================================================
# Search functions (as provided)
# ============================================================================
def search_companies(query: str, batch: str) -> list:
    """
    Search for companies based on a query string.

    Args:
        query (str): The query string to search for.
        batch (str): The batch to search for.

    Returns:
        list: A list of companies that match the query.
    """
    # Get the list of companies from the ChromaDB collection
    companies = search.search_companies(query, batch)
    # Save the search results to a JSON file
    with open("search_results.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=4, ensure_ascii=False)
    return companies

def deep_search_companies(query: str, batch: str) -> list:
    """
    Deep search for companies based on a query string.

    Args:
        query (str): The query string to search for.
        batch (str): The batch to search for.

    Returns:
        list: A list of companies that match the query.
    """
    # Get the list of companies from the ChromaDB collection using deep research.
    companies = search.deep_research(query, batch)
    # Save the search results to a JSON file
    with open("search_results.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=4, ensure_ascii=False)
    return companies

def load_search_results() -> list:
    """
    Load the search results from the JSON file.

    Returns:
        list: A list of company search results; [] if file not found.
    """
    try:
        with open("search_results.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# ============================================================================
# Helper function to format details recursively into HTML
# ============================================================================
def format_details(details, indent=0):
    """
    Recursively format company details (dict or list) into an HTML string.
    """
    html_content = ""
    spacing = "&nbsp;" * 4 * indent  # 4 non-breaking spaces per indent level
    if isinstance(details, dict):
        for key, value in details.items():
            html_content += f"{spacing}<b>{key}:</b> "
            if isinstance(value, dict) or isinstance(value, list):
                html_content += "<br>" + format_details(value, indent + 1)
            else:
                html_content += f"{value}<br>"
    elif isinstance(details, list):
        for item in details:
            html_content += format_details(item, indent)
    else:
        html_content += f"{spacing}{details}<br>"
    return html_content


# ============================================================================
# Streamlit App Layout
# ============================================================================

st.title("Company Search App")
st.write("Enter a search query and select one or more batch options to find companies.")

# INPUT: Search query text input
query = st.text_input("Search Query", placeholder="Enter your query here...")

# INPUT: Multiselect widget for batch selection (example: ["W24", "S24", "W23", "S23", "W22", "S22"])
selected_batches = st.multiselect("Select Batch", 
                                  options=["W24", "S24", "W23", "S23", "W22", "S22"],
                                  help="Select one or more batches")
# For passing to your function—which expects a string—convert to comma-separated string.
batch_str = ",".join(selected_batches) if selected_batches else ""

# Two buttons: one for standard search, one for deep research
col1, col2 = st.columns(2)
with col1:
    if st.button("Search Companies"):
        if query and batch_str:
            search_companies(query, batch_str)
            st.success("Search completed! Check the results below.")
        else:
            st.error("Please enter a search query and select at least one batch.")

with col2:
    if st.button("Deep Search Companies"):
        if query and batch_str:
            deep_search_companies(query, batch_str)
            st.success("Deep Search completed! Check the results below.")
        else:
            st.error("Please enter a search query and select at least one batch.")

# Load search results from the JSON file
results = load_search_results()

if results:
    st.subheader("Search Results")
    # Display the list of companies in a scrollable expander
    with st.expander("Companies List", expanded=True):
        # Build a mapping: { Company Name: Company ID }
        company_mapping = {}
        for company in results:
            name = company.get("metadata", {}).get("name", "Unnamed Company")
            cid = company.get("id")
            company_mapping[name] = cid
        
        # Create a select box to choose a company from the list
        selected_company_name = st.selectbox("Select a company to view details",
                                             options=list(company_mapping.keys()),
                                             help="Choose a company from the list")
        # Button to show details of the selected company.
        if st.button("Show Company Details"):
            company_id = company_mapping[selected_company_name]
            # Build file path (example: data/company_descriptions/id.json)
            detail_file = os.path.join(DATA_DIR, f"{company_id}.json")
            if os.path.exists(detail_file):
                with open(detail_file, "r", encoding="utf-8") as f:
                    company_details = json.load(f)
                st.subheader(f"Details for {selected_company_name}")

                # Format the company_details dict into HTML (this handles nested dicts/lists)
                details_html = format_details(company_details)

                # Create an HTML block with a fixed height and overflow (scrollable)
                html_container = f"""
                <div style="height:400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
                    {details_html}
                </div>
                """
                st.markdown(html_container, unsafe_allow_html=True)
            else:
                st.error(f"Company details file not found for: {selected_company_name}")
else:
    st.info("No search results to display. Please perform a search above.")
