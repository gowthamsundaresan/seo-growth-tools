import re
import os
import requests
import configparser
import time
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client as SupabaseClient
from PIL import Image

# Init env
load_dotenv()

# Init OpenAI
client = OpenAI()

# Init Supabase and login
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: SupabaseClient = create_client(url, key)
data = supabase.auth.sign_in_with_password({
    "email":
    os.environ["SUPABASE_LOGIN_EMAIL"],
    "password":
    os.environ["SUPABASE_LOGIN_PASSWORD"]
})

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Setup constants from config
IMAGE_FOLDER_PATH = config['Paths']['ImageFolderPath']
BLOG_PATH = config['Paths']['BlogPath']

# Retrieve all articles to be written from Supabase Blog Queue table
articles = supabase.from_('Blog Queue').select('*').eq('is_published',
                                                       False).execute()


def escape_html_special_chars(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;').replace(
        '>', '&gt;').replace('"', '&quot;'))


def parse_chatgpt_response(text):
    # Escape special HTML characters
    text = escape_html_special_chars(text)

    # Replace @@ and !! with heading tags
    text = re.sub(r'@@(.*?)@@', r'<h1>\1</h1>', text)
    text = re.sub(r'!!(.*?)!!', r'<h2>\1</h2>', text)

    # Split the text into sections based on headings and paragraphs
    sections = re.split(r'(<h[12]>.*?</h[12]>)', text)

    # Process each section
    formatted_text = ''
    for section in sections:
        if section.startswith(('<h1>', '<h2>')):
            # Add headings directly
            formatted_text += section
        else:
            # Wrap non-heading sections in paragraph tags
            paragraphs = section.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    formatted_text += f'<p>{paragraph.strip()}</p>'

    return formatted_text


def extract_image_prompt():
    with open('image_prompt.txt', 'r') as file:
        # Read the entire file content into a single string
        return file.read().strip()


def extract_article_prompts(title, keywords, custom_instructions):
    with open('article_prompt.txt', 'r') as file:
        content = file.read()

        # Replace placeholders with actual values
        for i, keyword in enumerate(keywords, start=1):
            content = content.replace(f'{{keyword_{i}}}', keyword)
        content = content.replace('{custom_instructions}', custom_instructions)
        content = content.replace('{title}', title)

        # Split content into user_message and system_message
        sections = content.split('[system_message]')
        user_message = sections[0]
        system_message = sections[1].strip() if len(sections) > 1 else ''

    return user_message, system_message


def convert_to_hyphenated(string):
    # Remove single and double quotes
    string = string.replace("'", "").replace('"', "")

    # Convert to lowercase and replace spaces with hyphens
    return string.lower().replace(" ", "-")


def parse_ttt_file(file_path):
    categories = {}
    current_category = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Check for category line
            if line.startswith('[') and line.endswith(']'):
                current_category = line[1:-1]
                categories[current_category] = ""
            elif current_category:
                categories[current_category] += line + "\n"

    return categories


def download_image(image_url, folder_path, file_name):
    # Get the image content from the URL
    response = requests.get(image_url)

    if response.status_code == 200:
        # Define the full path with folder and file name
        file_path = f"{folder_path}/{file_name}"

        # Write the image content to a file
        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"Image successfully saved to {file_path}")

    else:
        print("Failed to download the image")


def convert_png_to_jpeg(input_path, output_path):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.save(output_path, format='JPEG', quality=85)


def growth():
    # Init
    ttt_content = parse_ttt_file('try_this_today.txt')
    total_actions = 0

    for item in articles.data:
        # Retrieve article data
        id = item['id']
        title = item['title']
        slug = item['slug']
        keyword_1 = item['keyword_1']
        keyword_2 = item['keyword_2']
        keyword_3 = item['keyword_3']
        keyword_4 = item['keyword_4']
        custom_instructions = item['custom_instructions']
        meta = item['meta']
        category = item['category']
        image_prompt = item['image_prompt']
        page_var = item['page_var']
        author = item['author']

        # Setup additional article data
        keywords = [keyword_1, keyword_2, keyword_3, keyword_4]
        date = datetime.now().strftime("%B %d, %Y")
        try_this_today = ttt_content.get(category, "Error")
        cover_image_name = f"{slug}-cover"
        category_slug = convert_to_hyphenated(category)

        print(f"Next article to write: {title}")

        # File path where article will be published and name of the .js file
        article_page_file = f'{BLOG_PATH}/{category_slug}/{slug}.js'

        # Request GPT-4 to write the article
        user_message, system_message = extract_article_prompts(
            title, keywords, custom_instructions)

        print("Requesting response from GPT-4...")
        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role":
                                                      "system",
                                                      "content":
                                                      system_message
                                                  }, {
                                                      "role":
                                                      "user",
                                                      "content":
                                                      user_message
                                                  }])
        raw_response = response.choices[0].message.content

        # Convert article to HTML
        print("Formatting response...")
        formatted_article = parse_chatgpt_response(raw_response)
        soup = BeautifulSoup(formatted_article, 'html.parser')
        formatted_article = soup.prettify()

        # Final HTML
        final_html = str(soup)

        # Plain text
        plain_text = soup.get_text()

        # Request DALL-3 to generate a cover image
        print("Requesting response from DALL-E 3...")
        additional_instructions = extract_image_prompt()
        prompt = image_prompt + ', ' + additional_instructions
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # Download and write image to the image folder defined in config.ini
        download_image(image_url, IMAGE_FOLDER_PATH, f'{cover_image_name}.png')

        # Convert and compress image
        convert_png_to_jpeg(f'{IMAGE_FOLDER_PATH}/{cover_image_name}.png',
                            f'{IMAGE_FOLDER_PATH}/{cover_image_name}.jpg')

        # Delete original .png image
        os.remove(f'{IMAGE_FOLDER_PATH}/{cover_image_name}.png')

        print(
            f"Image generated, compressed and saved to {IMAGE_FOLDER_PATH}/{cover_image_name}"
        )

        # Generate the JavaScript code for the article page component
        print("Creating page... ")
        article_page_code = f"""import React from "react";
        import BlogPageTemplate from "@/components/BlogPageTemplate";
        import Head from "next/head";

        const BlogPage{page_var} = () => {{
        return (
            <div>
                <Head>
                    <title>{title}</title>
                    <meta name="description" content="{meta}" />
                </Head>
                <BlogPageTemplate
                    content="{final_html}"
                    title="{title}"
                    meta="{meta}"
                    author="{author}"
                    category="{category}"
                    date="{date}"
                    tryThisToday="{try_this_today}"
                    coverImageName="{cover_image_name}.jpg"
                />
            </div>
        );
        }};

        export default BlogPage{page_var};
        """

        # Write the component code to the file
        with open(article_page_file, 'w') as file:
            file.write(article_page_code)

        print("New article page created: ", article_page_file)

        # Update to supabase Published Articles table
        result = supabase.table('Published Articles').insert({
            "title":
            title,
            "slug":
            slug,
            "meta":
            meta,
            "category":
            category,
            "cover_image_name":
            cover_image_name,
            "author":
            author,
            "date":
            date,
            "article_html":
            final_html,
            "article_plain_text":
            plain_text
        }).execute()
        print("Updated Published Articles table")

        # Update is_published to True
        update_table = supabase.table('Blog Queue').update({
            'is_published': True
        }).eq('id', id).execute()

        total_actions += 1

        print("Updated is_published in Blog Queue table")
        print(f"Article {title} completed!")
        print(f"Total actions this session: {total_actions}")
        print("Sleeping 60s...")
        time.sleep(60)


def main():
    """
    Main function. Performs the login and then executes the strategy.

    Returns:
    --------
        None.
    """
    # Begin strategy
    growth()


if __name__ == "__main__":
    main()