from PIL import Image
import os

def add_white_background(input_folder, output_folder=None):
    """
    Add a white background to all PNG images in the specified folder.
    
    Args:
        input_folder (str): Path to the folder containing PNG files
        output_folder (str, optional): Path to save the processed images. 
                                     If None, original files will be overwritten.
    """
    # If no output folder is specified, use the input folder (overwrite originals)
    if output_folder is None:
        output_folder = input_folder
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all PNG files in the input folder
    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return
    
    # Process each PNG file
    for filename in png_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        try:
            # Open the image and convert to RGBA to ensure it has an alpha channel
            img = Image.open(input_path).convert("RGBA")
            
            # Create a white background image with the same size
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            
            # Composite the image with the white background
            composite = Image.alpha_composite(background, img)
            
            # Convert back to RGB (removing alpha channel) and save
            composite.convert("RGB").save(output_path, "PNG")
            
            print(f"Processed: {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"Completed! Processed {len(png_files)} PNG files.")

# Example usage
if __name__ == "__main__":
    # Replace with your folder path
    folder_path = "logos"
    
    # To save to a different folder (original files won't be modified):
    # output_path = "path/to/output/folder"
    # add_white_background(folder_path, output_path)
    
    # To overwrite original files:
    add_white_background(folder_path)