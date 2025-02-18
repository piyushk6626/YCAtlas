import asyncio  
from crawl4ai import *

async def fetch_YC_Launch_Page(url: str) -> str:
    """
    Fetches a YC Launch page and returns its HTML content as a markdown string.

    Args:
        url (str): The URL of the YC Launch page to fetch.

    Returns:
        str: The markdown representation of the fetched page.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

if __name__ == "__main__":
    url = "https://www.ycombinator.com/launches/Mnz-inari-your-junior-ai-product-manager"
    markdown = asyncio.run(fetch_YC_Launch_Page(url)) 
    print(markdown) 