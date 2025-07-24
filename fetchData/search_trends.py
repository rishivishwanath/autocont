import requests
from datetime import datetime, timedelta, timezone
from newspaper import Article
from supabase import create_client, Client
from utils import get_env_var

url=get_env_var("SUPABASE_URL")
key=get_env_var("SUPABASE_KEY")

supabase:Client=create_client(url, key)

NEWSAPI_KEY = get_env_var("NEWS_API_KEY")
API_URL = "https://newsapi.org/v2/everything"

KEYWORDS = [
    "cybercrime", "conspiracy", "unsolved mystery", "cult",
    "espionage", "paranormal", "forbidden", "secret society", "ritual",
    "black market", "scandal", "hidden truth", "classified", "covert operation",
    "did you know", "bizarre", "unbelievable", "shocking", "unexplained"
]

def fetch_full_articles(api_key, keywords):
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=7)

    for keyword in keywords:
        print(f"\nFetching articles for keyword: {keyword}")
        params = {
            "q": keyword,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 2,
            "apiKey": api_key
        }

        response = requests.get(API_URL, params=params)
        data = response.json()
        if data.get("status") == "ok" and data.get("articles"):
            for article_meta in data["articles"]:
                url = article_meta.get("url")
                if url:
                    try:
                        article = Article(url)
                        article.download()
                        article.parse()
                        print(f"URL: {url}\n")
                        # Check if the URL already exists
                        existing = supabase.table("storeart").select("num").eq("url", url).execute()

                        if not existing.data:
                            # Only insert if the URL doesn't already exist
                            response = supabase.table("storeart").insert({"url": url,"category":keyword}).execute()
                        else:
                            print("URL already exists. Skipping insert.")

                    except Exception as e:
                        print(f"Failed to fetch full article from {url}: {e}")
        else:
            print(f"No articles found for keyword: {keyword}")

if __name__ == "__main__":
    try:
        fetch_full_articles(NEWSAPI_KEY, KEYWORDS)
        response=(supabase.table("storeart").select("*").execute())
        print(response.data)
    except Exception as e:
        print(f"Error: {e}")