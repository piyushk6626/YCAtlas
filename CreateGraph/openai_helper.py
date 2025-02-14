# modules/openai_helper.py 
from openai import OpenAI
import logging
import csv
import os

def log_openai_interaction(input_text, output_text, filename='openai_log.csv'):
    """
    Appends a row with the input text and output text to a CSV file.
    If the file doesn't exist, it writes the header first.
    """
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
         fieldnames = ['input', 'output']
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
         if not file_exists:
             writer.writeheader()
         writer.writerow({'input': input_text, 'output': output_text})

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
    # Log both the input and the output into one CSV file.
    log_openai_interaction(text, output_text)
    return output_text
