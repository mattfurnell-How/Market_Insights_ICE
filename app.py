import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import html
import re

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

def topics_from_display(value):
    if pd.isna(value) or str(value).strip() == "":
        return ["General"]

    return [topic.strip() for topic in str(value).split(",") if topic.strip()]

# Page setup
st.set_page_config(
    page_title="TheBikeInsurer Market Insight Tool",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
        color: #1f2933;
    }

    h1, h2, h3 {
        color: #003b5c;
        font-family: Roboto, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #003b5c;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 6px solid #86d93f;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        color: #003b5c !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }

    .article-card {
        background-color: white;
        padding: 22px;
        margin-bottom: 18px;
        border-radius: 10px;
        border-top: 5px solid #86d93f;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }

    .article-card a {
        color: #003b5c;
        text-decoration: none;
    }

    .article-card a:hover {
        color: #86d93f;
        text-decoration: underline;
    }

    .article-meta {
        color: #5f6b7a;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .badge {
        display: inline-block;
        background-color: #86d93f;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 13px;
        margin-right: 8px;
        margin-bottom: 6px;
    }

    .stTextInput label,
    .stTextInput p,
    .stTextInput div {
        color: #003b5c !important;
        font-weight: 700;
    }

    .stTextInput input {
        background-color: white !important;
        border: 2px solid #003b5c !important;
        border-radius: 8px !important;
        color: #003b5c !important;
        padding: 10px !important;
    }

    .stTextInput input:focus {
        border: 2px solid #86d93f !important;
        box-shadow: 0 0 0 1px #86d93f !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        color: #003b5c !important;
    }

</style>
""", unsafe_allow_html=True)

st.title("TheBikeInsurer Market & Topic Insight Tool")

# Load data
df = pd.read_csv("motorcycle_articles.csv")

# Convert published date into usable datetime format
df["published_date"] = pd.to_datetime(df["published"], errors="coerce", utc=True)

# Use pre-cleaned summaries if rss_collector.py has created them.
# Otherwise fall back to cleaning in the app.
if "clean_summary" not in df.columns:
    df["clean_summary"] = df["summary"].apply(clean_summary)
else:
    df["clean_summary"] = df["clean_summary"].fillna("")

# Use pre-created article topics if rss_collector.py has created them.
# Otherwise fall back to classifying in the app.
if "article_topics_display" in df.columns:
    df["article_topics_display"] = df["article_topics_display"].fillna("General")
    df["article_topics"] = df["article_topics_display"].apply(topics_from_display)
else:
    df["article_topics"] = df.apply(
        lambda row: classify_article(
            row.get("title", ""),
            row.get("clean_summary", "")
        ),
        axis=1
    )

    df["article_topics_display"] = df["article_topics"].apply(lambda topics: ", ".join(topics))

# Sidebar filters
st.sidebar.header("Filters")

recency_filter = st.sidebar.selectbox(
    "Article Recency",
    [
        "All articles",
        "Last 7 days",
        "Last 30 days",
        "Last 90 days",
        "This year"
    ]
)

source_filter = st.sidebar.multiselect(
    "Select Sources",
    options=sorted(df["source"].dropna().unique())
)

all_topics = sorted(set(topic for topics in df["article_topics"] for topic in topics))

article_topic_filter = st.sidebar.multiselect(
    "Select Article Topics",
    options=all_topics
)

hide_racing = st.sidebar.checkbox(
    "Hide Racing articles by default",
    value=True
)

excluded_racing_sources = [
    "MotoGP News",
    "BikeSport News",
    "Superbike News"
]

search = st.text_input("Search topics, titles or summaries")

# Apply filters
filtered_df = df.copy()

now = pd.Timestamp.now(tz="UTC")

if recency_filter == "Last 7 days":
    filtered_df = filtered_df[
        filtered_df["published_date"] >= now - pd.Timedelta(days=7)
    ]

elif recency_filter == "Last 30 days":
    filtered_df = filtered_df[
        filtered_df["published_date"] >= now - pd.Timedelta(days=30)
    ]

elif recency_filter == "Last 90 days":
    filtered_df = filtered_df[
        filtered_df["published_date"] >= now - pd.Timedelta(days=90)
    ]

elif recency_filter == "This year":
    filtered_df = filtered_df[
        filtered_df["published_date"].dt.year == now.year
    ]

if source_filter:
    filtered_df = filtered_df[
        filtered_df["source"].isin(source_filter)
    ]

if article_topic_filter:
    filtered_df = filtered_df[
        filtered_df["article_topics"].apply(
            lambda topics: any(topic in topics for topic in article_topic_filter)
        )
    ]

if hide_racing and not article_topic_filter:

    # Remove racing-tagged articles
    filtered_df = filtered_df[
        ~filtered_df["article_topics"].apply(
            lambda topics: "Racing" in topics
        )
    ]

    # Remove racing-heavy sources
    filtered_df = filtered_df[
        ~filtered_df["source"].isin(excluded_racing_sources)
    ]

if search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(search, case=False, na=False)
        |
        filtered_df["clean_summary"].str.contains(search, case=False, na=False)
        |
        filtered_df["article_topics_display"].str.contains(search, case=False, na=False)
    ]

filtered_df = filtered_df.sort_values("published_date", ascending=False)

# Metrics
st.subheader("Dashboard Overview")

col1, col2, col3 = st.columns(3)

visible_topics = set(topic for topics in filtered_df["article_topics"] for topic in topics)

col1.metric("Total Articles", len(filtered_df))
col2.metric("Sources", filtered_df["source"].nunique())
col3.metric("Article Topics", len(visible_topics))

# Display articles
st.subheader("Articles")

if filtered_df.empty:
    st.warning("No articles found for the selected filters.")

for _, row in filtered_df.iterrows():

    summary = row["clean_summary"]
    topic_badges = " ".join([f'<span class="badge">{topic}</span>' for topic in row["article_topics"]])

    st.markdown(f"""
    <div class="article-card">
        <h3><a href="{row['link']}" target="_blank">{row['title']}</a></h3>
        <div class="article-meta">
            <span class="badge">{row['source']}</span>
            {topic_badges}
            <br><br>
            <strong>Published:</strong> {row['published']}
        </div>
        <p>{summary[:400] + "..." if summary else ""}</p>
    </div>
    """, unsafe_allow_html=True)
