import csv
import requests
import os
from lxml import html
from concurrent.futures import ThreadPoolExecutor

def scrape_page(url):
    try:
        # Fetch the page content
        response = requests.get(url)
        response.raise_for_status()

        # Parse the page content
        tree = html.fromstring(response.content)

        # Extract data using the provided XPaths
        data = {
            "Name": ''.join(tree.xpath('//h1[@class="text-3xl font-bold"]/text()')).strip(),
            "Headline": ''.join(tree.xpath('//div[@class="text-xl"]/text()')).strip(),
            "Batch": ''.join(tree.xpath('//div[@class="flex flex-row items-center gap-[6px]"]/span/text()')).strip(),
            "Description": ''.join(tree.xpath('(//div[@class="prose max-w-full whitespace-pre-line"])[1]/text()')).strip(),
            "Activity_Status": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Status:")]/following-sibling::span/text()')).strip(),
            "Website": ''.join(tree.xpath('//a[@class="mb-2 whitespace-nowrap md:mb-0"]/@href')).strip(),
            "Founded_Date": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Founded:")]/following-sibling::span/text()')).strip(),
            "Team_Size": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Team Size:")]/following-sibling::span/text()')).strip(),
            "Location": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Location:")]/following-sibling::span/text()')).strip(),
            "Group_Partner_YC": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Group Partner:")]/following-sibling::a/@href')).strip(),
            "Group_Partner": ''.join(tree.xpath('//div[@class="flex flex-row justify-between"]/span[contains(text(),"Group Partner:")]/following-sibling::a/text()')).strip(),
            "Company_Linkedin": ''.join(tree.xpath('//a[@class="inline-block w-5 h-5 bg-contain bg-image-linkedin"]/@href')).strip(),
            "Company_Twitter": ''.join(tree.xpath('//a[@class="inline-block w-5 h-5 bg-contain bg-image-twitter"]/@href')).strip(),
            "Active_Founders": []
        }

        # ---------------------
        # Extract Tags (Major & Minor)
        # ---------------------
        tag_hrefs = tree.xpath('//div[@class="align-center flex flex-row flex-wrap gap-x-2 gap-y-2"]/a[not(@target="_blank")]/@href')
        tags = []
        for href in tag_hrefs:
            # Expecting href in the format: /companies/{major}/{minor}
            parts = href.strip('/').split('/')
            if len(parts) >= 3 and parts[0] == "companies":
                major = parts[1]
                minor = parts[2]
                tags.append(f"{major}:{minor}")
        data["Tags"] = "; ".join(tags)

        # ---------------------
        # Extract Active Founders details
        # ---------------------
        founders = tree.xpath('//div[@class="flex flex-row flex-col items-start gap-6 md:flex-row"]')
        for founder in founders:
            name = ''.join(founder.xpath('.//h3[@class="text-lg font-bold"]/text()')).strip()
            description = ''.join(founder.xpath('.//div[@class="prose max-w-full whitespace-pre-line"]/text()')).strip()
            linkedin = ''.join(founder.xpath('.//a[@class="inline-block h-5 w-5 bg-contain bg-image-linkedin"]/@href')).strip()

            data["Active_Founders"].append({
                "Name": name,
                "Description": description,
                "LinkedIn": linkedin
            })

        print(f"Scraped: {url}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"Error scraping the page: {e}")
        return None

def process_row(row):
    """
    Process a single CSV row by scraping the URL contained in the "Links" column.
    The scraped data is added to the row.
    """
    url = row.get("Links")
    row["Links"] = url  # Ensure the link is saved in the output CSV
    if url:
        try:
            scraped_data = scrape_page(url)
            if scraped_data:
                # Add scraped data to the row (skip Active_Founders for now)
                for key in scraped_data:
                    if key != "Active_Founders":
                        row[key] = scraped_data[key]

                # Fill founder columns (up to 7 founders)
                for i, founder in enumerate(scraped_data.get("Active_Founders", [])[:7], 1):
                    row[f"Founder{i}_Name"] = founder.get("Name", "")
                    row[f"Founder{i}_Description"] = founder.get("Description", "")
                    row[f"Founder{i}_LinkedIn"] = founder.get("LinkedIn", "")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return row

def process_csv(input_file, output_file):
    # Define up to 7 founder columns (columns 1-7 for each of Name, Description, LinkedIn)
    founder_columns = [
        f"Founder{i}_{attr}"
        for i in range(1, 8)
        for attr in ["Name", "Description", "LinkedIn"]
    ]

    rows = []
    # Read all rows from the input CSV
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows.append(row)
        # Prepare the fieldnames for the output CSV
        fieldnames = reader.fieldnames + [
            "Name", "Headline", "Batch", "Description", "Activity_Status", "Website",
            "Founded_Date", "Team_Size", "Location",
            "Group_Partner", "Group_Partner_YC", "Company_Linkedin",
            "Company_Twitter", "Tags"
        ] + founder_columns

    # Use a ThreadPoolExecutor to process rows in parallel.
    with ThreadPoolExecutor(max_workers=10) as executor:
        processed_rows = list(executor.map(process_row, rows))

    # Check if the output file already exists
    file_exists = os.path.exists(output_file)
    with open(output_file, mode='a', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        # If the file does not exist, write the header first
        if not file_exists:
            writer.writeheader()

        # Write each processed row to the CSV
        for row in processed_rows:
            writer.writerow(row)

if __name__ == "__main__":
    # Input and output file paths
    input_csv = "yclinks.csv"
    output_csv = "ycdet.csv"

    # Process the CSV by appending new data in parallel
    process_csv(input_csv, output_csv)
    print(f"Processed CSV saved to {output_csv}")
