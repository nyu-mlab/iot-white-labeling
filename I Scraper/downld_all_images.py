import os
import requests
import json

json_file_path = 'output.json'
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

output_folder = './downloaded_images'
os.makedirs(output_folder, exist_ok=True)

def download_image(image_link, output_path):
    try:
        response = requests.get(image_link, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as image_file:
            for chunk in response.iter_content(chunk_size=8192):
                image_file.write(chunk)
        print(f"Downloaded: {output_path}")
    except Exception as e:
        print(f"Error downloading {image_link}: {e}")

for key, value in data.items():
    image_link = value.get('image_link')
    if image_link:
        image_name = f"{key}.jpg"  
        output_path = os.path.join(output_folder, image_name)
        print("Fetching image ", key, "out of", len(data.items()))
        download_image(image_link, output_path)
