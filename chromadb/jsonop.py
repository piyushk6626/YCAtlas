import streamlit as st
import json
from serachAgent.search import search_companies, deep_research
import os

# Load JSON data from the main search results file
def load_data():
    try:
        with open('search_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        st.error(f"Error loading data: {str(e)}")
        return []

# Quick search using the search_companies function
def quick_search(query, companies):
    if not query:
        return companies
    data = search_companies(query)
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return data

# Deep search using the deep_research function
def deep_search(query, companies):
    if not query:
        return companies
    data = deep_research(query)
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return data

def show_home_page():
    st.title("YC ATLAS")
    
    # Search bar and search mode selection
    search_query = st.text_input("Search companies", "", key="search_companies_input")
    search_mode = st.radio("Select Search Type", ("Quick Search", "Deep Search"), index=0)
    
    # Load initial data
    companies = load_data()
    
    # If the Search button is pressed, execute the chosen search and clear the search bar
    if st.button("Search"):
        if search_mode == "Quick Search":
            filtered_companies = quick_search(search_query, companies)
        else:
            filtered_companies = deep_search(search_query, companies)
        # Clear the search bar text after searching
        st.session_state["search_companies_input"] = ""
    else:
        filtered_companies = companies
    
    # Display each company with its details and action buttons
    for company in filtered_companies:
        metadata = company['metadata']
        
        with st.container():
            logo_col, name_col = st.columns([1, 4])
            
            with logo_col:
                if metadata.get('name'):
                    logo_name = metadata['name'].replace(' ', '_')
                    logo_path = os.path.join("data", "logos", f"{logo_name}_logo.png")
                    if os.path.exists(logo_path):
                        try:
                            st.image(logo_path, width=150)
                        except Exception:
                            st.write("🏢")
                    else:
                        st.write("🏢")
            
            with name_col:
                # Button for navigating to company details
                if st.button(metadata['name'], key=f"company_{company['id']}", use_container_width=True):
                    st.session_state.selected_company = company
                    st.session_state.page = 'details'
                    st.experimental_user()
                
                # Custom CSS for button text styling
                st.markdown("""
                    <style>
                    .stButton button {
                        font-size: 24px;
                        font-weight: bold;
                    }
                    </style>
                    """, unsafe_allow_html=True)
            
            if metadata.get('headline'):
                st.subheader(metadata['headline'])
            
            # Layout columns for additional company info
            col1, col2 = st.columns([2, 1])
            with col1:
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.write("**Batch:**", metadata.get('batch', 'N/A'))
                with info_cols[1]:
                    st.write("**Location:**", metadata.get('location', 'N/A'))
                with info_cols[2]:
                    st.write("**Team Size:**", metadata.get('team_size', 'N/A'))
                if metadata.get('tags'):
                    st.write(" ".join(metadata['tags']))
            
            with col2:
                if metadata.get('website'):
                    st.write("🔗 [Website](" + metadata['website'] + ")")
                if metadata.get('ycpage'):
                    st.write("🏢 [YC Page](" + metadata['ycpage'] + ")")
        
            st.markdown("""---""")
            
def show_company_details(company):
    if not company:
        st.error("No company selected.")
        return
        
    metadata = company['metadata']
    
    # Company header with logo and title
    col1, col2 = st.columns([1, 3])
    with col1:
        if metadata.get('name'):
            logo_name = metadata['name'].replace(' ', '_')
            logo_path = os.path.join("data", "logos", f"{logo_name}_logo.png")
            if os.path.exists(logo_path):
                try:
                    st.image(logo_path, width=150)
                except Exception:
                    st.write("🏢")
            else:
                st.write("🏢")
    with col2:
        st.title(metadata['name'])
        if metadata.get('headline'):
            st.subheader(metadata['headline'])
    
    # Company Information section
    st.markdown("### Company Information")
    st.write("**Batch:**", metadata.get('batch', 'N/A'))
    st.write("**Location:**", metadata.get('location', 'N/A'))
    st.write("**Team Size:**", metadata.get('team_size', 'N/A'))
    st.write("**Founded:**", metadata.get('founded_date', 'N/A'))
    
    # Links section
    st.markdown("### Links")
    cols = st.columns(3)
    with cols[0]:
        if metadata.get('website'):
            st.write("🔗 [Website](" + metadata['website'] + ")")
    with cols[1]:
        if metadata.get('ycpage'):
            st.write("🏢 [YC Page](" + metadata['ycpage'] + ")")
    
    # Social links section
    if metadata.get('social_links'):
        st.markdown("### Social Links")
        for link in metadata['social_links']:
            st.write("- " + link)
    
    # Description and additional information
    st.markdown("### Description")
    st.write(metadata.get('description', 'No description available.'))
    if metadata.get('generated_description'):
        st.markdown("### Additional Information")
        st.markdown(metadata['generated_description'])
    
    # Founders information
    st.markdown("### Founders")
    for i in range(1, 3):
        founder_name = metadata.get(f'founder_{i}_name')
        founder_desc = metadata.get(f'founder_{i}_description')
        founder_linkedin = metadata.get(f'founder_{i}_linkedin')
        if founder_name:
            st.write(f"**{founder_name}**")
            if founder_desc:
                st.write(founder_desc)
            if founder_linkedin:
                st.write(f"[LinkedIn Profile]({founder_linkedin})")
    
    # Tags section
    if metadata.get('tags'):
        st.markdown("### Tags")
        st.write(", ".join(metadata['tags']))

def main():
    # Remove the default Streamlit sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for page routing and selected company
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    
    # Page routing: Home or Details page
    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'details':
        show_company_details(st.session_state.selected_company)
        if st.button("← Back to Companies"):
            st.session_state.page = 'home'
            st.experimental_user()

if __name__ == "__main__":
    main()
