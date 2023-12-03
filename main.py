import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client as SupabaseClient

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

# Retrieve all articles to be written from Supabase Blog Queue table
articles = supabase.table('Blog Queue').select("*").execute()


def parse_chatgpt_response(text):
    # Replace @@ with <h> tags for headings
    text = re.sub(r'@@(.*?)@@', r'<h1>\1</h1>', text)

    # Replace !! with <h2> tags for subheadings
    text = re.sub(r'!!(.*?)!!', r'<h2>\1</h2>', text)

    # Split the text into paragraphs based on blank lines
    paragraphs = re.split(r'\n\s*\n', text)

    # Wrap each paragraph with <p> tags, trimming whitespace
    formatted_text = ''.join(f'<p>{paragraph.strip()}</p>'
                             for paragraph in paragraphs if paragraph.strip())

    # replace " with &quot;
    formatted_text = formatted_text.replace('"', '&quot;')

    return formatted_text


def read_messages():
    with open('prompts.txt', 'r') as file:
        lines = file.readlines()

    user_message = []
    system_message = []
    current_section = None

    for line in lines:
        if '[user_message]' in line:
            current_section = 'user'
            continue
        elif '[system_message]' in line:
            current_section = 'system'
            continue

        if current_section == 'user':
            user_message.append(line.strip())
        elif current_section == 'system':
            system_message.append(line.strip())

    return '\n'.join(user_message), '\n'.join(system_message)


def parse_ttt_file(file_path):
    categories = {}
    current_category = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Check for category line
            if line.startswith('[') and line.endswith(']'):
                current_category = line[1:-1]  # Remove the square brackets
                categories[current_category] = ""
            elif current_category:
                categories[current_category] += line + "\n"

    return categories


def generate_image_name(category):
    print("")


def growth():
    # Init
    ttt_content = parse_ttt_file('try_this_today.txt')

    for item in articles.data:
        # Retrieve article data
        title = item['title']
        meta = item['meta']
        category = item['category']
        slug = item['slug']
        page_var = item['page_var']
        author = item['author']
        date = datetime.now().strftime("%B %d, %Y")
        try_this_today = ttt_content.get(category, "Error")
        cover_image_name = f"{slug}-cover"

        print(f"Next article to write: {title}")

        # Define the file path and name
        article_page_file = f'../joyroots-v1-homepage/pages/blog/{slug}.js'

        # Request GPT-4 to write the article
        user_message, system_message = read_messages()
        system_message = ""
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

        print("plain_text: ")
        print(plain_text)

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
                    content="{final_html}",
                    title="{title}",
                    meta="{meta}",
                    author="{author}",
                    category="{category}",
                    date="{date}"
                    tryThisToday="{try_this_today}"
                    coverImageName="{cover_image_name}"
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

        # Delete row from Supabase Blog Queue table
        delete_response = supabase.table('countries').delete().eq(
            'title', title).execute()
        print("Deleted entry from Blog Queue table")
        print(f"Article {title} completed")


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