import csv
import requests
import os
import json
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io

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

        # --------------------
        # Extract Social Links
        # --------------------
        social_links=[]
        Socail_Media = tree.xpath('//div[@class="flex items-center gap-4 pt-2"]/a')
        for social in Socail_Media:
            social_media = ''.join(social.xpath('.//@href')).strip()
            social_links.append(social_media)
            if "linkedin" in social_media:
                data["Company_Linkedin"] = social_media
            elif "twitter" in social_media:
                data["Company_Twitter"] = social_media
        
        data['social_links']=social_links
        
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

        # ---------------------
        # Extract Logo URL, download and process the image
        # ---------------------
        logo_url = ''.join(tree.xpath('//img[@class="h-full w-full rounded-xl"]/@src')).strip()
        if logo_url:
            try:
                response_logo = requests.get(logo_url)
                response_logo.raise_for_status()
                img_bytes = io.BytesIO(response_logo.content)
                img = Image.open(img_bytes)

                # Add a white background if the image has transparency.
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert("RGB")

                # Prepare the logos directory.
                logos_dir = os.path.join("data", "logos")
                if not os.path.exists(logos_dir):
                    os.makedirs(logos_dir)

                # Use company name as the filename with spaces replaced by underscores.
                company_name = data.get("Name", "default_company").replace(" ", "_")
                logo_filename = f"{company_name}.png"
                logo_path = os.path.join(logos_dir, logo_filename)

                # Save the processed image.
                img.save(logo_path)
                data["logo_path"] = logo_path
            except Exception as e:
                print(f"Error processing logo from {logo_url}: {e}")
                data["logo_path"] = ""
        else:
            data["logo_path"] = ""

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
    row["Links"] = url  # Ensure the link is saved in the output JSON
    if url:
        try:
            scraped_data = scrape_page(url)
            if scraped_data:
                # Add scraped data to the row (skip Active_Founders for now)
                for key in scraped_data:
                    if key != "Active_Founders":
                        row[key] = scraped_data[key]

                # Add the list of active founders to the row
                row["Active_Founders"] = scraped_data.get("Active_Founders", [])
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return row

def process_csv_to_json(input_file, output_file):
    rows = []
    # Read all rows from the input CSV
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows.append(row)

    # Use a ThreadPoolExecutor to process rows in parallel.
    with ThreadPoolExecutor(max_workers=10) as executor:
        processed_rows = list(executor.map(process_row, rows))

    # Save the processed rows as a JSON file.
    with open(output_file, mode='w', encoding='utf-8') as outfile:
        json.dump(processed_rows, outfile, indent=4)

if __name__ == "__main__":
    # Input and output file paths
    input_csv = "yclinks.csv"
    output_json = "ycdet.json"

    # Process the CSV and save the data to JSON in parallel.
    process_csv_to_json(input_csv, output_json)
    print(f"Processed data saved to {output_json}")
