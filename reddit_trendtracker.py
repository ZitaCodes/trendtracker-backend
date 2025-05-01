import praw
from collections import Counter
import re
import os
import subprocess
from dotenv import load_dotenv
import json
from datetime import datetime
import pytz

local_time = datetime.now(pytz.timezone("US/Eastern")).isoformat()

# Direct credentials — skip .env
reddit = praw.Reddit(
    client_id="2G5r4uUl4r_D_AezICfEUg",
    client_secret="GoHNq_IOzimnp34GKCBk-iZrBpvSVA",
    user_agent="TrendTrackerBot/0.1"
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
    "timestamp": local_time,
    "source": "Reddit",
    "tropes": [{"name": k, "count": v} for k, v in results.most_common()]
}

print("🕒 TrendTracker Local Time:", local_time, flush=True)


# Save file
with open("trendtracker_output.json", "w") as f:
    json.dump(trend_data, f, indent=2)

print("✅ TrendTracker data written to trendtracker_output.json")

# Local Git commit (optional - no push)
print("🔁 Starting auto-commit and push to GitHub...")

try:
    # Set identity scoped to this repo only
    subprocess.run(["git", "config", "user.name", "RenderBot"])
    subprocess.run(["git", "config", "user.email", "render@cloutbooks.com"])

    # Set remote URL to SSH for pushing
    subprocess.run(["git", "remote", "set-url", "origin", "git@github.com:ZitaCodes/trendtracker-backend.git"])

    # Stage and commit file
    subprocess.run(["git", "add", "trendtracker_output.json"])
    subprocess.run(["git", "commit", "-m", "✅ Auto-update trendtracker output via Render"])

    # Push with error capture
    push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

    if push_result.returncode == 0:
        print("🚀 Git push succeeded.")
    else:
        print("❌ Git push failed.")
        print("STDERR:", push_result.stderr)

except Exception as e:
    print("💥 Git error:", e)
