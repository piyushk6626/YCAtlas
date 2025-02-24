import streamlit as st
import json
from serachAgent.search import find_similar_items
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
    
    # Search bar
    search_query = st.text_input("Search companies", "")
    
    # Load data
    companies = load_data()
    
    # Filter companies based on search
    filtered_companies = search_companies(search_query, companies)
    
    # Display companies
    for company in filtered_companies:
        metadata = company['metadata']
        
        # Create a card-like container for each company
        with st.container():
            # Make the company name clickable
            if st.button(metadata['name'], key=f"btn_{company['id']}", use_container_width=True):
                show_company_details(company)
                return  # Exit main to show only company details
            
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Description:**", metadata['description'])
                st.write("**Batch:**", metadata['batch'])
                st.write("**Location:**", metadata['location'])
                st.write("**Team Size:**", metadata['team_size'])
                
                # Display tags
                if metadata.get('tags'):
                    st.write("**Tags:**", ", ".join(metadata['tags']))
            
            with col2:
                if metadata.get('website'):
                    st.write("🔗 [Website](" + metadata['website'] + ")")
            
            # Add a separator between companies
            st.markdown("---")

def show_company_details(company):
    # Add a back button
    if st.button("← Back to Companies"):
        st.rerun()
    
    metadata = company['metadata']
    
    # Company header with logo
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if metadata.get('logo'):
            st.image(metadata['logo'], width=150)
    
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