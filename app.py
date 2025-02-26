import streamlit as st
import json
from serachAgent.search import search_companies,deep_research
import os


# Load JSON data
def load_data():
    try:
        with open('search_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        st.error(f"Error loading data: {str(e)}")
        # Return empty list as fallback
        return []
    
def search_companie(query, companies):
    if not query:
        return companies
    
    return deep_research(query)

def main():
    # Hide streamlit sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    
    # Page routing
    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'details':
        show_company_details(st.session_state.selected_company)
        # Add a back button
        if st.button("← Back to Companies"):
            st.session_state.page = 'home'
            st.rerun()

def show_home_page():
    st.title("YC Companies Explorer")
    
    # Search bar
    search_query = st.text_input("Search companies", "")
    
    # Load data
    companies = load_data()
    
    # Filter companies based on search
    if search_query:
        filtered_companies = search_companie(search_query, companies)
    else:
        filtered_companies = companies
    
    # Display companies
    for company in filtered_companies:
        metadata = company['metadata']
        
        with st.container():
            logo_col, name_col = st.columns([1, 4])
            
            with logo_col:
                if metadata.get('name'):
                    name = metadata['name'].replace(' ', '_')
                    logo_path = os.path.join("data", "logos", f"{name}_logo.png")
                    
                    if os.path.exists(logo_path):
                        try:
                            st.image(logo_path, width=150)
                        except Exception as e:
                            st.write("🏢")
                    else:
                        st.write("🏢")
            
            with name_col:
                # Create a button that will navigate to company details
                if st.button(metadata['name'], key=f"company_{company['id']}", use_container_width=True):
                    # Store the selected company in session state
                    st.session_state.selected_company = company
                    # Change the page
                    st.session_state.page = 'details'
                    # Force a rerun to show the new page
                    st.rerun()
                
                # Add custom CSS to make the button text bigger
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
            
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create columns for company info
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.write("**Batch:**", metadata['batch'])
                with info_cols[1]:
                    st.write("**Location:**", metadata['location'])
                with info_cols[2]:
                    st.write("**Team Size:**", (metadata['team_size']))
                
                # Display tags
                if metadata.get('tags'):
                    st.write(" ".join(metadata['tags']))
            
            with col2:
                if metadata.get('website'):
                    st.write("🔗 [Website](" + metadata['website'] + ")")
                if metadata.get('ycpage'):
                    st.write("🏢 [YC Page](" + metadata['ycpage'] + ")")
        
        # Add a divider between companies
            st.markdown("""---""")
            
def show_company_details(company):
    if not company:
        st.error("No company selected.")
        return
        
    metadata = company['metadata']
    
    # Company header with logo
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if metadata.get('name'):
            name = metadata['name'].replace(' ', '_')
            logo_path = os.path.join("data", "logos", f"{name}_logo.png")
            
            if os.path.exists(logo_path):
                try:
                    st.image(logo_path, width=150)
                except Exception as e:
                    st.write("🏢")  # Show building emoji as fallback
            else:
                st.write("🏢")  # Show building emoji when logo doesn't exist
    
    with col2:
        st.title(metadata['name'])
        if metadata.get('headline'):
            st.subheader(metadata['headline'])
    
    # Company details
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
    
    # Social links
    if metadata.get('social_links'):
        st.markdown("### Social Links")
        for link in metadata['social_links']:
            st.write("- " + link)
    
    # Description
    st.markdown("### Description")
    st.write(metadata.get('description', 'No description available.'))
    
    # Generated description (if available)
    if metadata.get('generated_description'):
        st.markdown("### Additional Information")
        st.markdown(metadata['generated_description'])
    
    # Founders information
    st.markdown("### Founders")
    for i in range(1, 3):  # Support up to 2 founders
        founder_name = metadata.get(f'founder_{i}_name')
        founder_desc = metadata.get(f'founder_{i}_description')
        founder_linkedin = metadata.get(f'founder_{i}_linkedin')
        
        if founder_name:
            st.write(f"**{founder_name}**")
            if founder_desc:
                st.write(founder_desc)
            if founder_linkedin:
                st.write(f"[LinkedIn Profile]({founder_linkedin})")
    
    # Tags
    if metadata.get('tags'):
        st.markdown("### Tags")
        st.write(", ".join(metadata['tags']))

if __name__ == "__main__":
    main()