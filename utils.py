import os
import json

# Define input and output directories
input_dir = r"D:\DEV\YC25\YC25\data\company_descriptions"
output_dir = r"D:\DEV\YC25\YC25\data\processed_descriptions"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each JSON file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        try:
            # Read JSON file
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Remove unwanted keys
            data.pop("embedding", None)
            data.pop("markdown", None)

            # Save the modified JSON to the output directory
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"Processed: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

