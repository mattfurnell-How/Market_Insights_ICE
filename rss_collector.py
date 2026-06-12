import feedparser
import pandas as pd
from datetime import datetime

feeds = pd.read_csv("feeds.csv")

articles = []

for _, row in feeds.iterrows():
    source = row["source"]
    rss_url = row["rss_url"]
    category = row["category"]

    print(f"Checking {source}...")

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        articles.append({
            "source": source,
            "category": category,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

df = pd.DataFrame(articles)

df = df.drop_duplicates(subset=["link"])

df.to_csv("motorcycle_articles.csv", index=False)

print(f"Saved {len(df)} articles to motorcycle_articles.csv")