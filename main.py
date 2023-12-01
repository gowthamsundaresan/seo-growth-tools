import re
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
from datetime import datetime

# Init env
load_dotenv()

# Init OpenAI and prompts
client = OpenAI()

# Init article data
title = "Ashwagandha vs Tongkat Ali: Unveiling the Power of Natural Supplements"
meta = "Ashwagandha and Tongkat Ali are exceptional natural supplements that offer a myriad of health benefits. The choice between the two largely depends on individual health goals. Be it improving mental clarity with Ashwagandha, or enhancing bodily strength and endurance with Tongkat Ali, one is investing in health and wellness."
category = "Comparing Supplements"
slug = "comparing-supplements/ashwagandha-vs-tongkat-ali-unveiling-the-power-of-natural-supplements"
mini_slug = "AshwagandhaVsTongkatAli"
author = "Ashley Olsen"
date = datetime.now().strftime("%B %d, %Y")
try_this_today = "Try this today: Here are more ideas to help you reduce stress: \nSpend some time in the great outdoors. \nTry to get enough sleep. \nMove your body by participating in enjoyable activities. \nSpend time with loved ones. \nSet boundaries to protect and prioritize your physical and mental health."
cover_image_name = "ashwagandha-vs-tongkat-ali.png"

# Define the file path and name
article_page_file = f'../joyroots-v1-homepage/pages/blog/{slug}.js'


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


def growth():
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
                                                  "role": "user",
                                                  "content": user_message
                                              }])
    raw_response = response.choices[0].message.content

    print("Formatting response...")
    formatted_article = parse_chatgpt_response(raw_response)
    soup = BeautifulSoup(formatted_article, 'html.parser')
    formatted_article = soup.prettify()
    final_html = str(soup)

    print("formatted_article: ")
    print(formatted_article)

    print("final_html: ")
    print(final_html)

    print("Creating page... ")
    # Generate the JavaScript code for the article page component
    article_page_code = f"""import React from "react";
    import BlogPageTemplate from "@/components/BlogPageTemplate";
    import Head from "next/head";

    const BlogPage{mini_slug} = () => {{
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

    export default BlogPage{mini_slug};
    """

    # Write the component code to the file
    with open(article_page_file, 'w') as file:
        file.write(article_page_code)

    print("New article page created:", article_page_file)

    # Update to supabase Published table

    # Delete row from supabase Queued table


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