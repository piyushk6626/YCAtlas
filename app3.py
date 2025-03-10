import streamlit as st
import os
import json

# Define the directory containing the JSON files
DATA_DIR = "data/company_descriptions"

# Set page configuration
st.set_page_config(
    page_title="Company Search",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .company-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: white;
    }
    .company-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .company-logo {
        width: 50px;
        height: 50px;
        margin-right: 1rem;
        object-fit: contain;
    }
    .score-badge {
        background-color: #f0f2f6;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .sidebar-container {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load search results from JSON file
def load_search_results(query: str, is_deep_search: bool = False) -> list:
    """
    Load search results from the JSON file based on query.
    
    In a real implementation, this would use the actual search functionality.
    For this demo, we just load the sample data from the file.
    """
    try:
        with open("search_results_chroma.json", "r") as f:
            all_results = json.load(f)
            
        # In a real implementation, you would filter based on the query
        # For demo purposes, we're just returning all results
        return all_results
    except FileNotFoundError:
        st.error("Search results file not found.")
        return []

# Function to load company details
def load_company_details(company_id: str) -> dict:
    """Load company details from JSON file."""
    try:
        with open(os.path.join(DATA_DIR, f"{company_id}.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # For demo purposes, try to load from our example data
        try:
            with open("search_results_chroma.json", "r") as f:
                all_results = json.load(f)
                
            for company in all_results:
                if company["id"] == company_id:
                    # If found in search results, convert to the detail format
                    return {
                        "name": company["metadata"].get("name", "Unknown"),
                        "headline": company["metadata"].get("headline", ""),
                        "batch": company["metadata"].get("batch", ""),
                        "founded_date": company["metadata"].get("founded_date", None),
                        "team_size": company["metadata"].get("team_size", None),
                        "location": company["metadata"].get("location", ""),
                        "website": company["metadata"].get("website", ""),
                        "links": company["metadata"].get("links", ""),
                        "generated_description": company["metadata"].get("generated_description", ""),
                        "social_links": company["metadata"].get("social_links", "[]"),
                        "logo_path": company["metadata"].get("logo_path", "")
                    }
        except:
            pass
            
        st.error(f"Company details for {company_id} not found.")
        return None

# Function to display company card in search results
def display_company_card(company):
    with st.container():
        st.markdown(f"""
        <div class="company-card">
            <div class="company-header">
                <img src="{company['metadata'].get('logo_path', '')}" class="company-logo" onerror="this.src='https://via.placeholder.com/50'">
                <h3>{company['metadata'].get('name', 'Unknown Company')} 
                <span class="score-badge">Score: {company['score']:.2f}</span></h3>
            </div>
            <p><strong>{company['metadata'].get('headline', '')}</strong></p>
            <p>Location: {company['metadata'].get('location', 'N/A')} | Founded: {int(company['metadata'].get('founded_date', 0)) if company['metadata'].get('founded_date') else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)

# Function to display company details
def display_company_details(company_data):
    if not company_data:
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if company_data.get('logo_path'):
            st.image(company_data['logo_path'], width=150)
        else:
            st.image("https://via.placeholder.com/150", width=150)
    
    with col2:
        st.title(company_data.get('name', 'Unknown Company'))
        st.subheader(company_data.get('headline', ''))
        
        metadata_col1, metadata_col2 = st.columns(2)
        with metadata_col1:
            st.markdown(f"**Founded:** {int(company_data.get('founded_date', 0)) if company_data.get('founded_date') else 'N/A'}")
            st.markdown(f"**Location:** {company_data.get('location', 'N/A')}")
            st.markdown(f"**Team Size:** {int(company_data.get('team_size', 0)) if company_data.get('team_size') else 'N/A'}")
        
        with metadata_col2:
            st.markdown(f"**Batch:** {company_data.get('batch', 'N/A')}")
            st.markdown(f"**Website:** [{company_data.get('website', 'N/A')}]({company_data.get('website', '#')})")
            st.markdown(f"**YC Link:** [{company_data.get('links', 'N/A')}]({company_data.get('links', '#')})")
    
    st.markdown("---")
    
    # Description tab
    st.subheader("Description")
    if company_data.get('generated_description'):
        st.markdown(company_data['generated_description'])
    else:
        st.markdown(company_data.get('description', 'No description available.'))
    
    # Founders tab
    if company_data.get('founders'):
        st.subheader("Founders")
        for founder in company_data['founders']:
            with st.expander(founder.get('name', 'Unknown')):
                st.markdown(founder.get('description', 'No description available.'))
                if founder.get('linkedin'):
                    st.markdown(f"[LinkedIn Profile]({founder['linkedin']})")
    
    # Social links
    if company_data.get('social_links'):
        st.subheader("Social Links")
        social_links = company_data['social_links']
        if isinstance(social_links, str):
            try:
                social_links = json.loads(social_links.replace("'", "\""))
            except:
                social_links = []
        
        for link in social_links:
            st.markdown(f"- [{link}]({link})")

# Main app
def main():
    # Initialize session state for first-time visitors
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    
    if 'view' not in st.session_state:
        st.session_state.view = 'search'
    
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    
    # Sidebar for search
    with st.sidebar:
        st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)
        st.title("Company Search")
        
        query = st.text_input("Enter search query:", placeholder="e.g., AI, San Francisco, YC W24")
        
        col1, col2 = st.columns(2)
        with col1:
            search_btn = st.button("Search", use_container_width=True)
        with col2:
            deep_search_btn = st.button("Deep Search", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle search button clicks
    if search_btn and query:
        st.session_state.search_results = load_search_results(query, False)
        st.session_state.view = 'search'
    
    if deep_search_btn and query:
        st.session_state.search_results = load_search_results(query, True)
        st.session_state.view = 'search'
    
    # Display appropriate view
    if st.session_state.view == 'search':
        # Display search results or initial state
        if not st.session_state.search_results and not search_btn and not deep_search_btn:
            # Initial state - show instructions or example companies
            st.title("Company Search")
            st.write("Enter a search query in the sidebar and click 'Search' or 'Deep Search' to find companies.")
            
            # Load example data if available
            try:
                with open("search_results_chroma.json", "r") as f:
                    example_data = json.load(f)
                
                if example_data:
                    st.subheader("Example Companies")
                    for i, company in enumerate(example_data[:5]):  # Show only first 5 for example
                        company_container = st.container()
                        with company_container:
                            display_company_card(company)
                            if st.button("View Details", key=f"example_{i}"):
                                st.session_state.selected_company = company['id']
                                st.session_state.view = 'detail'
                                st.rerun()
            except:
                st.info("No example data available. Please perform a search.")
                
        else:
            st.title("Search Results")
            if not st.session_state.search_results:
                st.info("No companies found matching your query.")
            else:
                for i, company in enumerate(st.session_state.search_results):
                    company_container = st.container()
                    with company_container:
                        display_company_card(company)
                        if st.button("View Details", key=f"view_{i}"):
                            st.session_state.selected_company = company['id']
                            st.session_state.view = 'detail'
                            st.rerun()
    
    elif st.session_state.view == 'detail':
        # Show back button
        if st.button("← Back to Search Results"):
            st.session_state.view = 'search'
            st.rerun()
        
        # Load company details
        company_data = load_company_details(st.session_state.selected_company)
        display_company_details(company_data)

if __name__ == "__main__":
    main()