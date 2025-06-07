import praw
from collections import Counter
import re
import os
import json
from datetime import datetime, timedelta
import pytz

# Set local time
local_time = datetime.now(pytz.timezone("US/Eastern")).isoformat()

# Initialize Reddit
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Subreddits to scan
subreddits = [
    "Suggestmeabook", "RomanceBooks", "FantasyRomance",
    "AlienRomance", "UrbanFantasy", "Booksuggestions"
]

# Expanded trope list
tropes_list = [
    "grumpy/sunshine", "fated mates", "forced proximity", "enemies to lovers",
    "friends to lovers", "slow burn", "alpha male", "possessive hero",
    "soulmates", "second chance", "touch her and die", "found family",
    "why choose", "age gap", "forbidden love", "dark romance", "shifter", 
    "werewolves", "dragons", "unicorns", "fae", "hidden treasure", "ancient secrets",
    "high action", "action", "secret identity", "demons",
    "billionaire", "arranged marriage", "fake relationship", "secret baby"
]

# Normalize
tropes_lookup = {t.lower(): t for t in tropes_list}
results = Counter()

# Clean text
def clean_text(text):
    return re.sub(r'[^\w\s/]', '', text.lower())

# Scrape cutoff (90 days)
cutoff = datetime.utcnow() - timedelta(days=90)

# Begin scan
for sub in subreddits:
    print(f"🔍 Scanning r/{sub}...")

    for submission in reddit.subreddit(sub).search("flair:Recommendation", sort="new", time_filter="all", limit=200):
        if datetime.utcfromtimestamp(submission.created_utc) < cutoff:
            continue
        body = clean_text(submission.title + " " + submission.selftext)
        for trope in tropes_lookup:
            if trope in body:
                results[tropes_lookup[trope]] += 1

    for comment in reddit.subreddit(sub).comments(limit=300):
        if datetime.utcfromtimestamp(comment.created_utc) < cutoff:
            continue
        body = clean_text(comment.body)
        for trope in tropes_lookup:
            if trope in body:
                results[tropes_lookup[trope]] += 1

# Final data
trend_data = {
    "timestamp": local_time,
    "source": "Reddit",
    "tropes": [{"name": k, "count": v} for k, v in results.most_common()]
}

# Save file
with open("trendtracker_output.json", "w") as f:
    json.dump(trend_data, f, indent=2)

print("\n✅ TrendTracker data written to trendtracker_output.json")

# Log output to console for copy/paste
print("\n🔁 Reddit Tropes Summary — Last 90 Days")
for trope in trend_data["tropes"]:
    print(f"{trope['name']} — {trope['count']}")

# Print full JSON block for copy
print("\n🧾 Full JSON for GitHub:")
print(json.dumps(trend_data, indent=2))
