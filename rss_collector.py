import feedparser
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import html
import re
import os

INPUT_FEEDS_FILE = "feeds.csv"
OUTPUT_ARTICLES_FILE = "motorcycle_articles.csv"

def clean_summary(text):
    if pd.isna(text):
        return ""

    text = html.unescape(str(text))
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)

def contains_keyword(text, keywords):
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

        if re.search(pattern, text):
            return True

    return False

def classify_article(title, summary):
    text = f"{title} {summary}".lower()

    topics = []

    if contains_keyword(text, ["theft", "stolen", "security", "disc lock", "bike lock", "crime"]):
        topics.append("Theft & Security")

    if contains_keyword(text, ["helmet", "jacket", "boots", "gloves", "gear", "kit", "clothing"]):
        topics.append("Gear")

    if contains_keyword(text, ["review", "tested", "test ride", "road test", "first ride"]):
        topics.append("Reviews")

    if contains_keyword(text, ["motogp", "worldsbk", "superbike", "racing", "race", "qualifying", "grand prix"]):
        topics.append("Racing")

    if contains_keyword(text, ["classic", "retro", "vintage", "restoration", "1920s", "1930s", "1940s"]):
        topics.append("Classic Bikes")

    if contains_keyword(text, ["electric", "ev", "battery", "charging", "zero motorcycles", "hybrid"]):
        topics.append("Electric Motorcycles")

    if contains_keyword(text, ["touring", "adventure", "trip", "travel", "route", "road trip"]):
        topics.append("Touring & Adventure")

    if contains_keyword(text, ["licence", "license", "cbt", "law", "ulez", "tax", "mot", "regulation"]):
        topics.append("Law & Regulation")

    if contains_keyword(text, ["maintenance", "service", "servicing", "chain", "oil", "tyre", "tire"]):
        topics.append("Maintenance")

    if contains_keyword(text, ["launch", "revealed", "new model", "unveiled", "first look", "prototype"]):
        topics.append("New Bikes")

    if contains_keyword(text, ["beginner", "new rider", "learner", "125cc", "a2 licence", "a2 license"]):
        topics.append("New Riders")

    if not topics:
        topics.append("General")

    return topics

feeds = pd.read_csv(INPUT_FEEDS_FILE)

new_articles = []

for _, row in feeds.iterrows():
    source = row["source"]
    rss_url = row["rss_url"]
    category = row.get("category", "")

    print(f"Checking {source}...")

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        summary = entry.get("summary", "")
        clean_text = clean_summary(summary)
        topics = classify_article(entry.get("title", ""), clean_text)

        new_articles.append({
            "source": source,
            "category": category,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": summary,
            "clean_summary": clean_text,
            "article_topics_display": ", ".join(topics),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

new_df = pd.DataFrame(new_articles)

# Load existing articles if the file already exists
if os.path.exists(OUTPUT_ARTICLES_FILE):
    existing_df = pd.read_csv(OUTPUT_ARTICLES_FILE)

    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    combined_df = new_df

# Remove duplicates by article link
combined_df = combined_df.drop_duplicates(subset=["link"], keep="last")

# Sort newest first where possible
combined_df["published_date"] = pd.to_datetime(
    combined_df["published"],
    errors="coerce",
    utc=True
)

combined_df = combined_df.sort_values("published_date", ascending=False)

# Remove helper date column before saving
combined_df = combined_df.drop(columns=["published_date"])

combined_df.to_csv(OUTPUT_ARTICLES_FILE, index=False)

print(f"Saved {len(combined_df)} total articles to {OUTPUT_ARTICLES_FILE}")
print(f"Collected {len(new_df)} articles from RSS feeds this run")
