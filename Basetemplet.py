from chromadb import search
import json

# Define the directory containing the JSON files
DATA_DIR = "data/company_descriptions"


# Serach for companies based on a query
def search_companies(query: str, batch:str) -> list:
    """
    Search for companies based on a query string.

    Args:
        query (str): The query string to search for.
        batch (str): The batch to search for.

    Returns:
        list: A list of companies that match the query.
    """
    # Get the list of companies from the ChromaDB collection
    companies = search.search_companies(query,batch)
    # Save the search results to a JSON file
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=4, ensure_ascii=False)

    return companies

# Deep search for companies based on a query
def deep_search_companies(query: str , batch:str) -> list:
    """
    Deep search for companies based on a query string.

    Args:
        query (str): The query string to search for.
        batch (str): The batch to search for.

    Returns:
        list: A list of companies that match the query.
    """
    # Get the list of companies from the ChromaDB collection
    companies = search.deep_research(query,batch)
    # Save the search results to a JSON file
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=4, ensure_ascii=False)
    return companies


# Main Page for the app
#  TWO BUTTON EACH FOR SEARCH AND DEEP SEARCH
# load the data from the JSON file search_results.json
#  INPUT BOX FOR QUERY
#  INPUT FOR CHECKBOX BATCH EXAMPLE ["W24","S24","W23","S23","W22","S22"] 
#  OUTPUT RESULT IN A SCROLLEBALE LIST
Exampledata=[
    {
        "id": "SciPhi_W24",
        "score": 0.6567634344100952,
        "metadata": {
            "batch": "W24",
            "founded_date": 2023.0,
            "generated_description": "**SciPhi: Pioneering Advanced AI Retrieval**\n\nWelcome to SciPhi, a fresh face in the vibrant tech scene, founded in 2023 and already making waves as part of Y Combinator Batch W24. Situated in San Francisco and comprised of just two sharp minds, SciPhi is on a mission to redefine how we interact with data and AI through its groundbreaking retrieval system, known as R2R.\n\n### What’s the Buzz About?\n\nSciPhi emerged with a clear focus: to create the most advanced Retrieval-Augmented Generation (RAG) system on the market. This isn’t just tech jargon; R2R is designed to bridge the gap from RAG prototypes to robust production environments. By tackling challenges related to infrastructure, retrieval speed, and scalability, they aim to empower enterprises to build reliable, context-aware AI applications. \n\n### Enterprise Solutions at Your Fingertips\n\nThe team at SciPhi understands the need for effective data management in today’s AI-driven world. Their platform promises quick document ingestion—handling over 40 formats ranging from PDFs to audio files—and advanced document intelligence, which automatically uncovers hidden relationships within your data through knowledge graphs. They focus on three core features:\n\n1. **Universal Document Processing**: Process millions of documents swiftly. \n2. **Enterprise Access Control**: Secure document sharing with detailed permission settings, making collaboration seamless.\n3. **Advanced Document Intelligence**: Enrich context and automate insights extraction, turning raw data into actionable knowledge.\n\n### Why SciPhi Stands Out\n\nBacked by Dalton Caldwell as their Group Partner, and a strong emphasis on developer-friendliness, SciPhi is crafted with real-world applications in mind. Their R2R API simplifies the deployment and scaling of RAG pipelines, offering a streamlined setup that reduces traditional configuration time to mere minutes.\n\nWith a commitment to improving accuracy through their HybridRAG technology, which combines knowledge graphs and vector retrieval, SciPhi has marked impressive performance stats, like significant reductions in setup time and costs—a no-brainer for enterprises scrambling to optimize their workflows.\n\n### Join the Revolution\n\nAs they continue to make strides in AI infrastructure and document management, SciPhi invites you to transform your AI projects. Whether you're looking to accelerate your data management or capsize traditional RAG frameworks, SciPhi's tools promise to redefine your approach to AI workflows. \n\nCurious to see what SciPhi can do for your next project? Visit [SciPhi.ai](https://www.sciphi.ai) to learn more or schedule a demo and step into the future of intelligent retrieval. \n\nIn a space getting increasingly crowded with competitors, SciPhi isn't just another startup—it's a visionary outfit ready to lead us into a new era of AI-powered data management.",
            "headline": "SciPhi is building R2R, the most advanced retrieval system.",
            "links": "https://www.ycombinator.com/companies/sciphi",
            "location": "San Francisco",
            "logo_path": "data/logos\\SciPhi_logo.png",
            "name": "SciPhi",
            "social_links": "[\"https://www.linkedin.com/company/sciphi-ai/\", \"https://github.com/SciPhi-AI\"]",
            "tags": "industry:artificial-intelligence; industry:search; industry:infrastructure; industry:ai; location:san-francisco-bay-area",
            "team_size": 2.0,
            "website": "https://www.sciphi.ai"
        }
    },
    {
        "id": "Ragas_W24",
        "score": 0.6302037835121155,
        "metadata": {
            "batch": "W24",
            "founded_date": 2023.0,
            "generated_description": "**Company Overview: Ragas**\n\nFounded in 2023 and based in San Francisco, Ragas is on a mission to establish an open-source standard for evaluating large language model (LLM) applications. The founders recognized a significant issue: the current landscape of fragmented and proprietary evaluation tools is causing confusion and inefficiencies among developers. By building a unified framework, Ragas aims to create a reliable standard that the developer community can depend on.\n\n**Key Highlights:**\n\n- **Community Engagement:** The Ragas project has resonated well with the developer community, evident from its impressive traction: over 4,000 stars on GitHub, 1,300 members in its Discord community, and contributions from more than 80 external collaborators.\n  \n- **Partnerships:** Ragas has secured strategic partnerships with prominent AI companies such as Langchain, Llamaindex, Arize, and Weaviate, all working together to refine and promote this evaluation standard.\n  \n- **Growth Metrics:** The service is already processing a staggering 5 million evaluations monthly for industry giants like AWS, Microsoft, Databricks, and Moody's, with a growth rate of 70% month-over-month. This rapid expansion illustrates the demand for cohesive evaluation tools in the AI space.\n\n- **Product Offering:** Ragas provides a comprehensive testing and evaluation infrastructure for enterprises, enhancing the performance and reliability of their LLM applications. Features include automated performance metrics, synthetic evaluation data generation, and online monitoring to ensure quality in production environments.\n\n- **Team and Support:** The company is small but ambitious, consisting of just two employees, Shahul (an applied AI researcher and Kaggle GM) and Jithin James (Chief Maintainer, previously at BentoML). The team actively encourages collaboration and support through their Discord platform.\n\n- **Recognition:** Ragas has gained recognition in the industry, being the only RAG framework directly recommended by OpenAI at their Dev Day, which speaks volumes about its credibility and potential impact.\n\nIn a world where developers grapple with disparate evaluation tools, Ragas stands out as a beacon of clarity, aiming to streamline the evaluation process for LLM applications. With its vibrant community, strategic partnerships, and innovative solutions, Ragas is gearing up to shape the future of AI application evaluation.\n\nFor more information about Ragas, visit their website: [Ragas.io](https://www.ragas.io).",
            "headline": "Building the open source standard for evaluating LLM Applications",
            "links": "https://www.ycombinator.com/companies/ragas",
            "location": "San Francisco",
            "logo_path": "data/logos\\Ragas_logo.png",
            "name": "Ragas",
            "social_links": "[\"https://www.linkedin.com/company/ragas/\", \"https://twitter.com/ragas_io\", \"https://github.com/explodinggradients\"]",
            "tags": "industry:developer-tools; industry:generative-ai; industry:open-source; industry:ai; location:san-francisco-bay-area",
            "team_size": 2.0,
            "website": "https://www.ragas.io"
        }
    },
]

 
# WHEN CLICKED ON A COMPANY NAME OPEN COMAPNEY Details
#  SHOWING ALL DETAILS OF THE COMPANY
#  IT WILL GET THE RESULTS FROM JSON FILE STORED IN THE DATA_DIR WITH id.json
# Example: data/company_descriptions/id.json

Exampledata={
    "links": "https://www.ycombinator.com/companies/1stcollab",
    "name": "1stCollab",
    "headline": "Performance-Optimized Influencer Marketing",
    "batch": "W23",
    "description": "1stCollab is an AI-powered influencer marketing platform for helping brands optimize performance. We are the first platform that leverages ML to accurately predict a creator's performance and use those predictions to recruit the most relevant, best-performing creators for a brand\u2019s upcoming influencer campaigns. Our founding team collectively spent 30 years at Pinterest building up most of its Discovery systems, so are experts at finding the perfect set of creators for optimizing engagement. Let us know if we can help you run an influencer marketing campaign and see how our brands have reduced their CAC by over 70%!",
    "activity_status": "Active",
    "website": "https://1stcollab.com/",
    "founded_date": 2022.0,
    "team_size": 6.0,
    "location": "San Francisco",
    "group_partner": "Gustaf Alstromer",
    "group_partner_yc": "https://www.ycombinator.com/people/gustaf-alstromer",
    "company_linkedin": None,
    "company_twitter": None,
    "tags": "location:san-francisco-bay-area",
    "founders": [
        {
            "name": "Leon Lin, Founder & CEO",
            "description": "Currently working on 1stCollab, the best platform for brands and creators to collaborate on influencer marketing campaigns. I was previously at Pinterest for over nine years, where I watched the company grow from 100 to 3k employees. Most recently, I was Head of Discovery product there where I led our Home, Search, and Pins teams and was responsible for user engagement. Before that, I was a tech lead on the Recommendations team.",
            "linkedin": "https://www.linkedin.com/in/leonqlin/"
        },
        {
            "name": "Varun Bansal, Founder",
            "description": "Co-founder at 1stCollab, a platform for brands and creators to connect and run marketing campaigns together. Before 1stCollab, I worked at Pinterest, where I was a product manager for the homefeed recommendations team, the international growth team, and\u2014most recently\u2014the creator engagement and community teams.",
            "linkedin": "https://www.linkedin.com/in/bansalvarunb/"
        },
        {
            "name": "Andrew Liu, Founder",
            "description": "Currently working on building a network for brands and creators to connect and launch marketing campaigns. Previously, I was a Tech Lead on search and recommendations at Coupang and Pinterest.\n\nIf you're interested in search, recommendations, or creators, please reach out :)!",
            "linkedin": "https://www.linkedin.com/in/zeyu-liu/"
        }
    ],
    "status": True,
    "markdown": "raw_markdown='\\n' markdown_with_citations='\\n' references_markdown='\\n\\n## References\\n\\n' fit_markdown='' fit_html=''",
    "generated_description": "**1stCollab Overview**\n\n1stCollab is a San Francisco-based influencer marketing platform founded in 2022, and it's already making waves in the industry with its innovative approach. The company is focused on **performance-optimized influencer marketing**, harnessing the power of AI and machine learning to revolutionize how brands connect with creators.\n\nThe founding team, with a rich background of over 30 years at Pinterest, has honed their expertise in discovery systems. This deep knowledge allows them to accurately predict a creator's potential performance, ensuring that brands can recruit the most relevant and highest-performing influencers for their campaigns. The results are impressive; many of their clients have reduced Customer Acquisition Costs (CAC) by more than 70%.\n\n1stCollab is part of the prestigious Y Combinator Batch W23, which speaks volumes about its potential and the credibility it carries in the startup ecosystem. Despite being a small team of just six employees, the company is driven by a big vision, and with Gustaf Alstromer as their Group Partner, they're well-positioned to make significant strides in the influencer marketing landscape.\n\nIf you're looking to ramp up your influencer marketing campaigns, 1stCollab could be the partner you need to optimize performance and unlock new possibilities.\n\nFor more information, check out their website: [1stCollab](https://1stcollab.com/).",
    "embedding": [
        ],
    "logo": "https://bookface-images.s3.us-west-2.amazonaws.com/logos/b381115013fa733399475c569ecfc6501e378186.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAQC4NIECAEHIR6H6F%2F20250221%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250221T190937Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQDt736ZW5EfzagAz1eKRSs%2FW4TfHu28RBSFaRNkZ9h47gIhANt6WXtwkgL07bQKDKYDGFxYKx7WOO9JX0BqaYrXnKNbKu4DCNz%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMMDA2MjAxODExMDcyIgx8TqkMwTM2PLcRmr4qwgPGGtQBXv7gs7%2BXGteI1gQk%2FjkbIHwQ5hCKXJKVmVAPw3MeVLhZyp8Nf5%2FYigbwE%2BrFR7aZWKjrs7HxAE0JWit5dlINZLjZK%2BS%2FwMaCqoj%2BFDN0gw9iiAPu4Xn5c3b%2BuZe%2F5%2Flfk0EuxZAXVsZtShxXZy%2FERPQ0v%2FRZxSz5qUoaXpL1zj6VWdWVzoI7%2FPlB3bgJ2PpiF7DN%2BJeDsJPx%2FoKTo5ehP9pOeGbMNxoeegVJsCJ3zvzO3o4fcZYIf6c5iIJwM1Ot3Gg7Z3v9oLZjSRU%2FaRLL5j4n3II7DaroOCEVfPlWzTyZM7SNFZZAFSKM8vLKj1VdTr9s3How41zluf%2FOIp7sGNhG%2FjuYJoG%2FmkLFIlYP4wbGrLO69AWnenZyfi1UhAiV6N%2BlAqGnqvpOJh4vq8uNh2eRnXR%2BMVXdq9oVYkm7XFgprL5PDC4ULLyBWqA6kca4z7F4H56nkT%2FsDtT8ek2VOIRIv1Zgcz%2BeeVG7F7AHS4bdbR6eZ3ChY1iQhfPBErh4OiFQM7IqiUKw%2B1CTpvL68xcVN5gjiaDH0Jotw%2BUcW9dMSg9py8xH8qgyiWG5w3dDj9xaoA2G3NMYq6JOGKMwwIrjvQY6pAHDH54nhADhmb7YSEGxHkL3pqs%2B6aYOExStWbzLKzRb3lb2DAgGG8uU9COt8%2FqUEOtOcszTKp7yuCJwMVkfI7PDZ74h9uiRkRxjtH7%2BLlE1xrfd%2FrIq%2B%2BZr9hSFqZ9MUQ4yNHesyx2FYDbsIfCW9ntlrpmZUHCcrzpQDfufsAFcpe%2FudVT3tUqiF8WCN1Vd%2Bx%2FQ9d3i1HvBcJWV9AYAwM0W22VM%2BA%3D%3D&X-Amz-SignedHeaders=host&X-Amz-Signature=7e0b16efdc142af6cac49987e7e94705cc4686f6fb7f881b595e2a1c1e74643e",
    "social_links": [
        "https://www.linkedin.com/company/1stcollab"
    ],
    "logo_path": "data/logos\\1stCollab_logo.png"
}