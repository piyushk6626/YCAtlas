import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt, user_prompt


def openai_client():
    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return client

def generate_company_description(markdown,Name,Headline,Batch,Description,Activity_Status,Website,Founded_Date,Team_Size,Location,Group_Partner,Tags):
    client = openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt(markdown,Name,Headline,Batch,Description,Activity_Status,Website,Founded_Date,Team_Size,Location,Group_Partner,Tags)}
        ]
    )   
    return response.choices[0].message.content

