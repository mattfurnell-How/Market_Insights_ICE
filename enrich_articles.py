import os
import json
import time
import pandas as pd
from openai import OpenAI

INPUT_FILE = "motorcycle_articles.csv"
OUTPUT_FILE = "motorcycle_articles_enriched.csv"

client = OpenAI(api_key=os.environ.get("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"))

def enrich_article(title, summary, source, category):
    prompt = f"""
You are helping a UK motorcycle insurance brand find newsletter topic ideas.

Analyse this motorcycle-related article and return ONLY valid JSON.

Article:
Title: {title}
Source: {source}
Category: {category}
Summary: {summary}

Return this JSON structure:
{{
  "topic": "",
  "rider_type": "",
  "newsletter_angle": "",
  "relevance_score": 0,
  "why_it_matters": ""
}}

Rules:
- topic should be short, e.g. Theft, Touring, New Bikes, Safety, Gear, Racing, Electric Motorcycles, Licensing, Weather, Maintenance
- rider_type should be short, e.g. Commuter, New Rider, Enthusiast, Tourer, Sports Rider, Adventure Rider
- newsletter_angle should be a practical newsletter idea for motorcycle riders
- relevance_score should be an integer from 1 to 10
- why_it_matters should explain why this could interest motorcycle insurance customers
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    text = response.output_text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "topic": "Unknown",
            "rider_type": "General Rider",
            "newsletter_angle": "Review this article manually for newsletter inspiration.",
            "relevance_score": 5,
            "why_it_matters": "The AI response could not be parsed cleanly."
        }

def main():
    df = pd.read_csv(INPUT_FILE)

    enriched_rows = []

    for index, row in df.iterrows():
        print(f"Enriching {index + 1}/{len(df)}: {row.get('title', '')}")

        result = enrich_article(
            title=row.get("title", ""),
            summary=row.get("summary", ""),
            source=row.get("source", ""),
            category=row.get("category", "")
        )

        enriched_row = row.to_dict()
        enriched_row["topic"] = result.get("topic", "")
        enriched_row["rider_type"] = result.get("rider_type", "")
        enriched_row["newsletter_angle"] = result.get("newsletter_angle", "")
        enriched_row["relevance_score"] = result.get("relevance_score", "")
        enriched_row["why_it_matters"] = result.get("why_it_matters", "")

        enriched_rows.append(enriched_row)

        time.sleep(0.5)

    enriched_df = pd.DataFrame(enriched_rows)
    enriched_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Done. Saved enriched file to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()