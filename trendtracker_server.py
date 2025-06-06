from flask import Flask, jsonify
from flask_cors import CORS
from flask import send_from_directory

import json
import subprocess
import os

app = Flask(__name__)
CORS(app, origins=["https://bookmkttool.vercel.app"])

# Subreddit member counts of
subreddit_info = {
    "Suggestmeabook": 3200000,
    "RomanceBooks": 130000,
    "FantasyRomance": 78000,
    "AlienRomance": 45000,
    "UrbanFantasy": 97000,
    "Booksuggestions": 260000
}

@app.route('/')
def home():
    return {"status": "TrendTracker is running."}

@app.route('/tropes')
def get_tropes():
    # 🔐 Safe check if file doesn't exist
    if not os.path.exists('trendtracker_output.json'):
        return jsonify({
            "timestamp": None,
            "tropes": [],
            "insight": {
                "trope": None,
                "blurb": "TrendTracker data not yet generated. Please run the scraper."
            }
        })

    # ✅ File exists — read it normally
    file_path = os.path.join(os.path.dirname(__file__), 'trendtracker_output.json')
    with open(file_path, 'r') as f:
        data = json.load(f)

    top_trope = data['tropes'][0] if data['tropes'] else {}
    insight = {}

    if top_trope:
        subs_discussing = 3  # Placeholder
        member_sum = sum(list(subreddit_info.values())[:subs_discussing])

        insight = {
            "trope": top_trope["name"],
            "blurb": f'"{top_trope["name"].title()}" is trending across {subs_discussing} online reader groups with over {member_sum:,} book lovers. Try using this in your promo copy or book page metadata for stronger clickthroughs.'
        }

     print("\n==============================")
     print("🔁 Reddit Tropes Summary — Last 90 Days")
     for trope in data["tropes"]:
         print(f"{trope['name']} — {trope['count']}")

    
    return jsonify({
        "timestamp": data["timestamp"],
        "tropes": data["tropes"],
        "insight": insight
    })

@app.route('/trendtracker_output.json')
def serve_raw_json_file():
    return send_from_directory(directory=os.getcwd(), path='trendtracker_output.json')

# Optional: Only run push logic if inside Render
if os.getenv("RENDER"):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "RenderBot"])
        subprocess.run(["git", "config", "--global", "user.email", "render@bot.com"])
        
        # Initialize repo if needed
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"])
            subprocess.run(["git", "remote", "add", "origin", "git@github.com:ZitaCodes/trendtracker-backend.git"])
        
        subprocess.run(["git", "add", "trendtracker_output.json"])
        subprocess.run(["git", "commit", "-m", "Auto-update trendtracker_output.json"])
        subprocess.run(["git", "push", "origin", "main"])
    
    except Exception as e:
        print("❌ Git push failed:", e)

if __name__ == '__main__':
    app.run(debug=True)
