
import os
import sys
from PIL import Image

source_path = r"C:/Users/PA 208/.gemini/antigravity/brain/912f4bc3-26ed-421f-bad4-16c0a5a12ad2/uploaded_image_1765208839156.jpg"
dest_path = r"w:\sistema infra\app\static\favicon.ico"

def convert_to_ico():
    try:
        print(f"Reading image from: {source_path}")
        img = Image.open(source_path)
        
        # Save as ICO
        print(f"Saving icon to: {dest_path}")
        img.save(dest_path, format='ICO', sizes=[(32, 32)])
        print("Success!")
        
    except ImportError:
        print("PIL not installed. Performing simple copy/rename.")
        import shutil
        shutil.copy2(source_path, dest_path)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure static dir exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    convert_to_ico()
