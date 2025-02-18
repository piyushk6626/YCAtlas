import pandas as pd

def merge_csv_files(ycdet_path, yc25_path, output_path):
    """
    Merge two CSV files based on Links column and add Post_Link from YC25Launch to ycdet
    
    Parameters:
    ycdet_path (str): Path to the ycdet CSV file
    yc25_path (str): Path to the YC25Launch CSV file
    output_path (str): Path where the merged CSV will be saved
    """
    # Read the CSV files
    ycdet_df = pd.read_csv(ycdet_path)
    yc25_df = pd.read_csv(yc25_path)
    
    # Create new Post_Link column in ycdet_df with empty strings
    ycdet_df['Post_Link'] = ''
    
    # Iterate through ycdet rows
    for index, row in ycdet_df.iterrows():
        # Look for matching Links in YC25Launch
        match = yc25_df[yc25_df['Links'] == row['Links']]
        
        # If match found, add Post_Link value
        if not match.empty:
            ycdet_df.at[index, 'Post_Link'] = match.iloc[0]['Post_Link']
    
    # Save the updated dataframe to a new CSV file
    ycdet_df.to_csv(output_path, index=False)
    print(f"Merged file saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    # Replace these paths with your actual file paths
    ycdet_path = "ycdet.csv"
    yc25_path = "YC25Launch.csv"
    output_path = "ycdet_merged.csv"
    
    merge_csv_files(ycdet_path, yc25_path, output_path)