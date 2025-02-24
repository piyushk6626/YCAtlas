import streamlit as st
import json
from serachAgent.search import find_similar_items
import os

# Add custom CSS for styling
st.markdown("""
    <style>
        /* Main background color */
        .stApp {
            background-color: #F5F5EE;
            color: black;
        }
        
        /* Accent color for buttons and interactive elements */
        .stButton>button {
            background-color: #F26522;
            color: white;
        }
        
        /* Style for company name buttons */
        .stButton>button:hover {
            background-color: #d55416;
            color: white;
        }
        
        /* Accent color for links */
        a {
            color: #F26522 !important;
        }
        
        /* Container styling */
        .stMarkdown {
            background-color: #F5F5EE;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            color: black;
        }

        /* Ensure all text elements are black */
        p, h1, h2, h3, h4, h5, h6, span, div {
            color: black !important;
        }

        /* Style the search input */
        .stTextInput input {
            background-color: white;
            color: black;
            border: 1px solid #ddd;
        }

        /* Style all other Streamlit components */
        .stSelectbox, 
        .stMultiSelect,
        .stSlider,
        .stDateInput,
        .stTimeInput,
        .stNumberInput,
        .stTextArea,
        .stRadio,
        .stCheckbox,
        .stMetric,
        .stDataFrame {
            background-color: #F5F5EE !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load JSON data
def load_data():
    try:
        with open('search_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        st.error(f"Error loading data: {str(e)}")
        # Return empty list as fallback
        return []
    
    

def search_companies(query,companies):
    if not query:
        return companies
    
    return find_similar_items(query)

def main():
    st.title("YC Companies Explorer")
    
    # Ensure the logos directory exists
    
    # Search bar
    search_query = st.text_input("Search companies", "")
    
    # Load data
    companies = load_data()
    
    # Filter companies based on search
    filtered_companies = companies
    
    # Display companies
    for company in filtered_companies:
        metadata = company['metadata']
        
        # Create a card-like container for each company
        with st.container():
            # Create columns for logo and company name
            logo_col, name_col = st.columns([1, 4])
            
            with logo_col:
                if metadata.get('name') :
                    name = metadata['name'].replace(' ', '_')
                    logo_path = os.path.join("data", "logos", f"{name}_logo.png")
                    
                    if os.path.exists(logo_path):
                        try:
                            st.image(logo_path, width=150)
                        except Exception as e:
                            st.write("🏢")  # Show building emoji as fallback
                    else:
                        st.write("🏢")  # Show building emoji when logo doesn't exist
            
            with name_col:
                # Make the company name clickable
                if st.button(metadata['name'], key=f"btn_{company['id']}", use_container_width=True):
                    show_company_details(company)
                    return  # Exit main to show only company details
                # Add subtitle styling to make it look prominent
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
                    st.write("**Team Size:**", str(int(float(metadata['team_size']))))
                
                # Display tags
                if metadata.get('tags'):
                    st.write(" ".join(metadata['tags']))
            
            with col2:
                if metadata.get('website'):
                    st.write("🔗 [Website](" + metadata['website'] + ")")
                if metadata.get('ycpage'):
                    st.write("🏢 [YC Page](" + metadata['ycpage'] + ")")
                

def show_company_details(company):
    # Add a back button
    if st.button("← Back to Companies"):
        st.rerun()
    
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
    
