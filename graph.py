import os
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from dotenv import load_dotenv
import csv
from openai import OpenAI

def natrual_description_genrator(text):
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
Rephrase the given description in the style of Paul Graham, ensuring no details are added or removed. Provide context in every sentence and avoid using pronouns.

# Output Format

- Maintain original details, styled after Paul Graham's writings.
            """
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    print()
    print()
    print(completion.choices[0].message.content)
    print()
    print()
    return completion.choices[0].message.content
# Uncomment the below to use LangSmith. Not required.
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
# os.environ["LANGSMITH_TRACING"] = "true"

def setup_neo4j_connection():
    load_dotenv()
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    graph = Neo4jGraph(refresh_schema=False, password=NEO4J_PASSWORD, url=NEO4J_URI, username=NEO4J_USERNAME)
    return graph

def setup_openai_model():
    """
    Sets up and returns an LLMGraphTransformer using OpenAI's GPT-4o model.
    """
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        
    )
    return llm_transformer

def create_graph(text):
    """
    Converts the given text into graph documents using the LLMGraphTransformer.
    """
    llm_transformer = setup_openai_model()    
    documents = [Document(page_content=text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    print(f"Nodes: {graph_documents[0].nodes}")
    print(f"Relationships: {graph_documents[0].relationships}")
    return graph_documents

def create_company_description(company_name, company_headline, company_description, company_link,
                               batch, founded_date, team_size, location, group_partner, group_partner_link):
    """
    Returns a factual natural language description of the company.
    """
    description = (
        f"{company_name} has the headline \"{company_headline}.\" "
        f"Description of {company_name} {company_name} is \"{company_description}.\" "
        f"Website of {company_link}. "
        f"It is part of the {batch} batch, founded on {founded_date} with a team of {team_size} based in {location}. "
        f"the Group Partner of {company_name} is {group_partner} "
    )
    return description

def create_founder_description(founder_name, founder_description, founder_linkedin, company_name):
    """
    Returns a factual natural language description of the founder.
    """
    description = (
        f"{founder_name} is the founder of {company_name}. "
        f"Bio: {founder_description}. "
        
    )
    return description
def process_company_row(row, graph):
    """
    Processes a single CSV row by:
      - Adding the company node (once).
      - Then, for each founder in that company row, creating a founder node that only references the company name.
    
    This avoids duplicating full company data for every founder.
    """
    # Extract company details
    company_name        = row.get("Name", "").strip()
    company_headline    = row.get("Headline", "").strip()
    company_description = row.get("Description", "").strip()
    company_website     = row.get("Website", "").strip()    
    batch               = row.get("Batch", "").strip()
    founded_date        = row.get("Founded_Date", "").strip()
    team_size           = row.get("Team_Size", "").strip()
    location            = row.get("Location", "").strip()
    group_partner       = row.get("Group_Partner", "").strip()
    group_partner_link  = row.get("Group_Partner_YC", "").strip()

    # Process company data only once
    company_text = create_company_description(
        company_name=company_name,
        company_headline=company_headline,
        company_description=company_description,
        company_link=company_website,
        batch=batch,
        founded_date=founded_date,
        team_size=team_size,
        location=location,
        group_partner=group_partner,
        group_partner_link=group_partner_link
    )
    company_text_simpllified=natrual_description_genrator(company_text)
    company_graph_documents = create_graph(company_text_simpllified)
    graph.add_graph_documents(company_graph_documents, baseEntityLabel=True)

    # Process each founder – include only the company name from the company data
    for i in range(1, 8):
        founder_name = row.get(f"Founder{i}_Name", "").strip()
        if founder_name:  # Only process if a founder name exists
            founder_description = row.get(f"Founder{i}_Description", "").strip()
            founder_linkedin    = row.get(f"Founder{i}_LinkedIn", "").strip()
            founder_text = create_founder_description(
                founder_name=founder_name,
                founder_description=founder_description,
                founder_linkedin=founder_linkedin,
                company_name=company_name  # Only add the company name here
            )
            founder_text_simplified=natrual_description_genrator(founder_text)
            founder_graph_documents = create_graph(founder_text_simplified)
            
            graph.add_graph_documents(founder_graph_documents)

def process_csv_file(file_path):
    """
    Reads the CSV file and processes each row to generate and add graph documents for
    companies and their founders. Each company is processed only once to avoid duplications.
    """
    graph = setup_neo4j_connection()
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            process_company_row(row, graph)

if __name__ == "__main__":
    file_path = "yc25det.csv"
    process_csv_file(file_path)
