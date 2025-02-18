# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key='fc-8453af5805a8444ea032e9367d6f0bd5')

response = app.scrape_url(url='https://docs.mendable.ai', params={
	'formats': [ 'markdown' ],
})