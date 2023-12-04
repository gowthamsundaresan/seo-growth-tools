from PIL import Image


def convert_png_to_jpeg(input_path, output_path):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.save(output_path, format='JPEG', quality=85)


def convert_to_hyphenated(string):
    # Remove single and double quotes
    string = string.replace("'", "").replace('"', "")

    # Convert to lowercase and replace spaces with hyphens
    return string.lower().replace(" ", "-")


def main():
    """
    Main function. Performs the login and then executes the strategy.

    Returns:
    --------
        None.
    """
    string = convert_to_hyphenated("Women's Health")
    print(string)


if __name__ == "__main__":
    main()