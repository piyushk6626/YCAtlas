import streamlit as st
import json
from serachAgent.search import search_companies, deep_research
import os

# Load JSON data from the main search results file
def load_data():
    try:
        with open('saved_companies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        st.error(f"Error loading data: {str(e)}")
        return []

# Search companies based on the query and update the search_results.json file
def search_companie(query, companies):
    if not query:
        return companies
    
    data = deep_research(query)
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return data

# Save the company info to a separate JSON file while checking for duplicates
def save_company_info(company):
    saved_file = 'saved_companies.json'
    try:
        if os.path.exists(saved_file):
            with open(saved_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
        else:
            saved_data = []
    except Exception as e:
        st.error(f"Error reading saved companies: {str(e)}")
        saved_data = []
    
    # Check if the company is already saved (based on its 'id')
    if any(saved_company.get('id') == company.get('id') for saved_company in saved_data):
        st.info("Company is already saved!")
    else:
        saved_data.append(company)
        try:
            with open(saved_file, 'w', encoding='utf-8') as f:
                json.dump(saved_data, f, indent=4, ensure_ascii=False)
            st.success("Company saved successfully!")
        except Exception as e:
            st.error(f"Error saving company: {str(e)}")

# New function to show saved companies
def show_saved_companies():
    st.title("Saved Companies")
    saved_file = 'saved_companies.json'
    if os.path.exists(saved_file):
        try:
            with open(saved_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
        except Exception as e:
            st.error(f"Error reading saved companies: {str(e)}")
            return
    else:
        st.info("No saved companies found.")
        return

    # Display each saved company similarly to the home page
    for company in saved_data:
        metadata = company.get('metadata', {})
        st.subheader(metadata.get('name', 'Unknown Company'))
        if metadata.get('headline'):
            st.write(metadata['headline'])
        st.markdown("---")


def main():
    # Use experimental_get_query_params to retrieve URL parameters
    query_params = st.experimental_get_query_params()
    if 'saved' in query_params and query_params['saved'] == ['true']:
        st.session_state.clear()  # Clear any preexisting state
        show_saved_companies()
        st.stop()  # Prevent further execution of the app in this tab

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
            st.experimental_rerun()

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
            st.experimental_rerun()
    
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
            st.experimental_rerun()

def show_home_page():
    st.title("YC ATLAS")
    
    # Button to open Saved Companies in a new tab
    st.markdown(
        '<a href="/?saved=true" target="_blank">'
        '<button style="background-color:#4CAF50; color:white; padding:10px 20px; '
        'border:none; border-radius:5px;">Open Saved Companies</button></a>',
        unsafe_allow_html=True
    )
    
    # Search bar
    search_query = st.text_input("Search companies", "", key="search_companies_input")

    
    # Load data
    companies = load_data()
    
    # Filter companies based on search query
    if search_query:
        filtered_companies = search_companie(search_query, companies)
        filtered_companies = load_data()  # reload updated data
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
                        except Exception as e:
                            st.write("🏢")
                    else:
                        st.write("🏢")
            
            with name_col:
                # Button for navigating to company details
                if st.button(metadata['name'], key=f"company_{company['id']}", use_container_width=True):
                    st.session_state.selected_company = company
                    st.session_state.page = 'details'
                    st.experimental_rerun()
                
                # Custom CSS for button text styling
                st.markdown("""
                    <style>
                    .stButton button {
                        font-size: 24px;
                        font-weight: bold;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                # Save button to store company info in another JSON file
                if st.button("Save", key=f"save_company_{company['id']}", use_container_width=True):
                    save_company_info(company)
            
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
                except Exception as e:
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

if __name__ == "__main__":
    main()
