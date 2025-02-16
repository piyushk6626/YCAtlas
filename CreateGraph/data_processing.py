import logging
from .openai_helper import generate_natural_description
from .llm_graph import create_graph
def create_company_description(company_name, company_headline, company_description, company_link,
                               batch, founded_date, team_size, location, group_partner, group_partner_link):
    """
    Create a natural language description of a company based on its details.

    Args:
        company_name (str): The name of the company
        company_headline (str): The headline of the company
    """
    logging.info(f"Creating company description for {company_name}")
    return (
        f"{company_name} has the headline \"{company_headline}.\" "
        f"Description of {company_name} is \"{company_description}.\" "
        f"Website: {company_link}. "
        f"It is part of the {batch} batch, founded on {founded_date} with a team of {team_size} based in {location}. "
        f"The Group Partner is {group_partner}."
    )

def create_founder_description(founder_name, founder_description, company_name):    
    """
    Create a natural language description of a founder based on their details.

    Args:
        founder_name (str): The name of the founder
        founder_description (str): The description of the founder
        company_name (str): The name of the company
    """
    logging.info(f"Creating founder description for {founder_name}")
    return (
        f"{founder_name} is the founder of {company_name}. "
        f"Bio: {founder_description}."
    )

def process_company_row(row, graph, llm_transformer, api_key):  
    """
    Process a company row and add it to the graph.

    Args:
        row (dict): The row from the CSV file
        graph (Graph): The graph to add the company to
        llm_transformer (LLMGraphTransformer): The language model transformer to use for conversion
        api_key (str): The API key for the OpenAI model

    """
    logging.info(f"Processing company row for {row.get('Name', '').strip()}")
    company_text = create_company_description(
        row.get("Name", "").strip(),
        row.get("Headline", "").strip(),
        row.get("Description", "").strip(),
        row.get("Website", "").strip(),
        row.get("Batch", "").strip(),
        row.get("Founded_Date", "").strip(),
        row.get("Team_Size", "").strip(),
        row.get("Location", "").strip(),
        row.get("Group_Partner", "").strip(),
        row.get("Group_Partner_YC", "").strip()
    )
    
    company_text_simplified = generate_natural_description(company_text, api_key)
    company_graph_documents = create_graph(company_text_simplified, llm_transformer)
    graph.add_graph_documents(company_graph_documents, baseEntityLabel=True)
    
    for i in range(1, 8):
        founder_name = row.get(f"Founder{i}_Name", "").strip()
        if founder_name:
            founder_description = row.get(f"Founder{i}_Description", "").strip()
            founder_text = create_founder_description(founder_name, founder_description, row.get("Name", "").strip())
            founder_text_simplified = generate_natural_description(founder_text, api_key)
            founder_graph_documents = create_graph(founder_text_simplified, llm_transformer)
            graph.add_graph_documents(founder_graph_documents)
