# seo-growth-tools

## Description

This project automates the process of creating, formatting, and publishing articles to a blog. It integrates OpenAI's GPT-4 for content generation, Supabase for data management, and DALL-E 3 for image creation, offering both automated and manual modes for image processing.

Use ChatGPT to populate the Blog Queue Table for SEO-focussed titles, custom instructions, 4 target keywords, meta description, prompt for the cover images, etc. and then use the script to automatically generate and publish all article one by one. It takes about 45 seconds to generate and entire article.

This workflow assumes that you don't use a CMS and automates the entire process for a blog built directly on a Next.js. In case you use a CMS, change up the way the article data and generated images are sent for publishing.

## Features

- **Content Generation**: Utilizes OpenAI's GPT-4 for article generation.
- **Image Creation**: Uses DALL-E 3 for automated image generation, with support for manual mode.
- **Data Management**: Employs Supabase for handling blog queue data and tracking published articles.
- **HTML Formatting**: Converts raw text into HTML to automatically create a .js page for web publishing.
- **Image Processing**: Includes functionality for downloading, converting, compressing and managing images.

## Prerequisites

- Python 3.x
- Supabase account
- OpenAI API keys
- DALL-E 3 access
- Required Python libraries: `requests`, `configparser`, `PIL`, `bs4`, `dotenv`, `openai`, `supabase`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gowthamsundaresan/seo-growth-tools
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Supabase Configuration

### Blog Queue Table

- **id**: bigint, auto-generated unique identifier.
- **created_at**: timestamp, automatically set to the current time.
- **title**: text, title of the article (optional).
- **slug**: text, URL-friendly version of the title.
- **keyword_1** to **keyword_4**: text, primary and secondary keywords for SEO.
- **custom_instructions**: text, special instructions for content generation.
- **meta**: text, meta description of the article for SEO.
- **category**: text, category of the article.
- **image_prompt**: text, instructions for image generation.
- **page_var**: text, a variable for the article's web page.
- **author**: text, author of the article.
- **is_published**: boolean, indicates if the article is published, default is false.

### Published Articles Table

- **id**: bigint, auto-generated unique identifier.
- **title**: text, title of the article.
- **meta**: text, meta description of the article.
- **category**: text, category of the article.
- **cover_image_name**: text, name of the cover image file.
- **slug**: text, URL-friendly version of the title.
- **author**: text, author of the article.
- **date**: text, publication date of the article.
- **article_html**: text, HTML content of the article.
- **article_plain_text**: text, plain text version of the article.
- **created_at**: timestamp, automatically set when the article is published.
- **category_slug**: text, URL-friendly version of the category name.
- **live_link**: text, live URL where the article is accessible.

## Configuration Folder

The configuration folder contains essential files for customizing the article generation process:

- **config.ini**: Defines paths and automation settings.
- **image_prompt.txt**: Contains prompts for image generation.
- **article_prompt.txt**: Template for generating article content with placeholders for title and keywords.
- **try_this_today.txt**: Categorized suggestions to be displayed as engaging content for readers.

## Setup

1. Set up a `.env` file with Supabase credentials and your OpenAI API key.
2. Modify `config.ini` in the `configuration` directory for paths and automation settings.

## Usage

Run the script using Python:

```bash
python main.py
```

The `manual/article_updates.json` file gets updated with every article that's created. Once you've published your site and your articles are live, update Supabase with the data of these published articles:

```bash
python update_db.py
```

### Choosing Manual vs. Auto Image Generation Mode

- **Auto Generation Mode**: Set `AutoImageGen` to `true` in `config.ini` for automated image creation. Uses DALL-E-3 which can get expensive.
- **Manual Generation Mode**: Set `AutoImageGen` to `false` if you want to manually generate/add your own images. With this setting, `images_to_generate.txt` gets populated with the prompts and filenames for each cover image that you need to create. Manually generate the images, rename them and place the .png files in `images`, then use `convert_write_images.py` to convert them to .jpg and write place them in your website's public images folder.

```bash
python convert_write_images.py
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/AmazingFeature`).
3. Commit changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.
