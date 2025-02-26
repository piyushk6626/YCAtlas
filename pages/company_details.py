import streamlit as st
import os

def show_company_details():
    # Get company data from query parameters
    company = st.session_state.get('selected_company')
    
    if not company:
        st.write("No company selected")
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
                    st.write("🏢")
            else:
                st.write("🏢")
    
    with col2:
        st.title(metadata['name'])
        if metadata.get('headline'):
            st.subheader(metadata['headline'])
    
    # Rest of the company details display code...
    # (Copy the rest of the original show_company_details function here)

if __name__ == "__main__":
    show_company_details() 