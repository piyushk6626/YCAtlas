import csv
import requests
from lxml import html

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

        # Extract Active Founders details
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
        print(url)
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"Error scraping the page: {e}")
        return None

def process_csv(input_file, output_file):
    # Define up to 8 founder columns
    founder_columns = [
        f"Founder{i}_{attr}"
        for i in range(1, 8)
        for attr in ["Name", "Description", "LinkedIn"]
    ]

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + [
            "Name", "Headline", "Batch", "Description", "Activity_Status", "Website",
            "Founded_Date", "Team_Size", "Location",
            "Group_Partner", "Group_Partner_YC", "Company_Linkedin",
            "Company_Twitter"
        ] + founder_columns  # Add new columns for scraped data and founders

        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                url = row.get("Links")  # Get the URL from the "Links" column
                row["Links"] = url  # Ensure the link is saved in the output CSV
                if url:
                    try:
                        scraped_data = scrape_page(url)
                        if scraped_data:
                            # Add scraped data to the row
                            for key in scraped_data:
                                if key != "Active_Founders":
                                    row[key] = scraped_data[key]

                            # Fill founder columns
                            for i, founder in enumerate(scraped_data["Active_Founders"][:8], 1):
                                row[f"Founder{i}_Name"] = founder.get("Name", "")
                                row[f"Founder{i}_Description"] = founder.get("Description", "")
                                row[f"Founder{i}_LinkedIn"] = founder.get("LinkedIn", "")

                    except Exception as e:
                        print(f"Error scraping {url}: {e}")
                writer.writerow(row)

if __name__ == "__main__":
    # Input and output file paths
    input_csv = "yc25.csv"
    output_csv = "yc25det.csv"

    # Process the CSV
    process_csv(input_csv, output_csv)
    print(f"Processed CSV saved to {output_csv}") 