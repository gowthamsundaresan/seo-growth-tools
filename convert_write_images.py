import os
import configparser
from PIL import Image

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Retrive path to write the final image into
IMAGE_FOLDER_PATH = config['Paths']['ImageFolderPath']


def convert_png_to_jpeg(input_path, output_path):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.save(output_path, format='JPEG', quality=85)


def process_images_in_folder(folder_path):
    # Iterate over each .png and convert it
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(IMAGE_FOLDER_PATH,
                                       os.path.splitext(filename)[0] + '.jpg')

            convert_png_to_jpeg(input_path, output_path)

            # Delete the original PNG image
            os.remove(input_path)


# Example usage
process_images_in_folder('images')