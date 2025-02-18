# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('FIRECRAWL_API_KEY')

app = FirecrawlApp(api_key=api_key)

response = app.scrape_url(url='https://docs.mendable.ai', params={
	'formats': [ 'markdown' ],
})

response={
    "success": True,
    "data": {
      "markdown": "# Markdown Content",
      "metadata": {
        "title": "Mendable | AI for CX and Sales",
        "description": "AI for CX and Sales",
        "language": None,
        "sourceURL": "https://www.mendable.ai/"
      }
    }
  }