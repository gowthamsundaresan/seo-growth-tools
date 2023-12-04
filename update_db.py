import json
import os
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv

# Init env
load_dotenv()

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


def upload_articles_to_supabase(file_path='article_updates.json'):
    # Read the JSON file
    with open(file_path, 'r') as file:
        articles = json.load(file)

    # Insert articles into Supabase
    for article in articles:
        result = supabase.table('Published Articles').insert(article).execute()
        print(f"Updated Published Articles table for {article['title']}")

    # Clear the file after successful upload
    open(file_path, 'w').close()
    print(f"All articles updated")


# Run the function
upload_articles_to_supabase()