import praw
from datetime import datetime, timedelta
from collections import Counter
import re
import os
from dotenv import load_dotenv
import json

# Load Reddit credentials
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Config
subreddits = [
    "Suggestmeabook", "RomanceBooks", "FantasyRomance",
    "AlienRomance", "UrbanFantasy", "Booksuggestions"
]

# List of tropes to track
tropes_list = [
    "grumpy/sunshine", "fated mates", "forced proximity", "enemies to lovers",
    "friends to lovers", "slow burn", "alpha male", "possessive hero",
    "soulmates", "second chance", "touch her and die", "found family",
    "why choose", "age gap", "forbidden love", "dark romance",
    "billionaire", "arranged marriage", "fake relationship", "secret baby"
]

# Normalize variations
tropes_lookup = {t.lower(): t for t in tropes_list}
results = Counter()

def clean_text(text):
    return re.sub(r'[^\w\s/]', '', text.lower())

# Pull from last 90 days
cutoff = datetime.utcnow() - timedelta(days=90)

# Scrape subreddit posts
for sub in subreddits:
    print(f"🔍 Scanning r/{sub}...")

    for submission in reddit.subreddit(sub).search("flair:Recommendation", sort="new", time_filter="all", limit=200):
        if datetime.utcfromtimestamp(submission.created_utc) < cutoff:
            continue
        body = clean_text(submission.title + " " + submission.selftext)
        for trope in tropes_lookup:
            if trope in body:
                results[tropes_lookup[trope]] += 1

    # Scrape recent comments too
    for comment in reddit.subreddit(sub).comments(limit=300):
        if datetime.utcfromtimestamp(comment.created_utc) < cutoff:
            continue
        body = clean_text(comment.body)
        for trope in tropes_lookup:
            if trope in body:
                results[tropes_lookup[trope]] += 1

# Output as JSON
trend_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "source": "Reddit",
    "tropes": [{"name": k, "count": v} for k, v in results.most_common()]
}

# Save file
with open("trendtracker_output.json", "w") as f:
    json.dump(trend_data, f, indent=2)

print("✅ TrendTracker data written to trendtracker_output.json")
