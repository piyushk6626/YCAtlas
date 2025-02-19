import pandas as pd
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# Provided async crawl function
async def crawl_website(url):
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig()     # Default crawl run configuration
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
        return result.markdown_v2

async def process_dataframe(df, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = []
    indices = []

    async def sem_task(idx, url):
        async with semaphore:
            return idx, await crawl_website(url)
    
    # Loop over the DataFrame rows
    for idx, row in df.iterrows():
        print(row.get('Name', ''))
        if not row['status'] and str(row.get('Activity_Status', '')).strip().lower() == "active":
            if str(row.get('Batch', '')).strip() != "W25" and str(row.get('Batch', '')).strip() != "F24" and str(row.get('Batch', '')).strip() != "W24" and str(row.get('Batch', '')).strip() != "S24":
                website = row.get('Website', '')
                url = None
                
                if pd.notnull(website) and str(website).strip():
                    url = str(website).strip()

                if url:
                    tasks.append(sem_task(idx, url))
                else:
                    print(f"No valid URL found for row index {idx}.")

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update DataFrame with results.
    for res in results:
        idx, result = res if not isinstance(res, Exception) else (None, res)
        if idx is None:
            print(f"Error processing a task: {result}")
        else:
            df.at[idx, 'markdown'] = result
            df.at[idx, 'status'] = True
            print(f"Processed row {idx} successfully.")

    return df

def main():
    input_csv = 'input.csv'
    output_csv = 'output.csv'
    df = pd.read_csv(input_csv)
    
    if 'status' not in df.columns:
        df['status'] = False
    if 'markdown' not in df.columns:
        df['markdown'] = None

    # Set max_concurrent to control how many tasks run at once.
    df = asyncio.run(process_dataframe(df, max_concurrent=20))
    
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV has been saved to {output_csv}.")

if __name__ == "__main__":
    main()
