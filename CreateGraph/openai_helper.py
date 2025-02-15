# modules/openai_helper.py 
from openai import OpenAI
import logging
import csv
import os


def generate_natural_description(text, api_key):
    logging.info("Generating natural description using OpenAI")
    
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
                Rephrase the given description in the style of Paul Graham, ensuring no details are added or removed.
                Provide context in every sentence and avoid using pronouns.
                
                # Output Format
                
                - Maintain original details, styled after Paul Graham's writings.
                """},
            {"role": "user", "content": text}
        ]
    )
    logging.info("OpenAI response received")
    output_text = completion.choices[0].message.content
    return output_text
