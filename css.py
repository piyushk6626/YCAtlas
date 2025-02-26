A="""
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
"""
