# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()
#//img[@class="h-full w-full rounded-xl"]
def scrape_website(url):
    api_key = os.getenv('FIRECRAWL_API_KEY')

    app = FirecrawlApp(api_key=api_key)

    response = app.scrape_url(url=url, params={
        'formats': [ 'markdown' ],
    })

    if response['success']:
        return response['data']['markdown']
    else:
        return None


