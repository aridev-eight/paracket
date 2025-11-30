#!/usr/bin/env python3
"""
Check Reddit post and subreddit status
"""
import praw
import os
from dotenv import load_dotenv

load_dotenv('.streamlit/secrets.toml')

client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
username = os.getenv('REDDIT_USERNAME')
password = os.getenv('REDDIT_PASSWORD')

print("Checking r/Paracket and recent posts...")
print("="*60)

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent='paracket_checker/1.0'
)

# Check subreddit
try:
    subreddit = reddit.subreddit('Paracket')
    print(f"\n✅ Subreddit: r/{subreddit.display_name}")
    print(f"   Type: {subreddit.subreddit_type}")
    print(f"   Subscribers: {subreddit.subscribers}")
    print(f"   Public: {subreddit.subreddit_type == 'public'}")

    # Spam filter settings (these require mod access and may not be available via API)
    print(f"\n📋 Subreddit Details:")
    print(f"   Submissions enabled: {subreddit.can_assign_link_flair}")
    print(f"   Over 18: {subreddit.over18}")

except Exception as e:
    print(f"❌ Could not access r/Paracket: {e}")
    exit(1)

# Check your recent submissions
print(f"\n📝 Your Recent Posts in r/Paracket:")
print("-"*60)

user = reddit.redditor(username)
found_posts = False

for submission in user.submissions.new(limit=20):
    if submission.subreddit.display_name.lower() == 'paracket':
        found_posts = True

        status_icons = {
            True: "🔴 REMOVED",
            False: "✅ VISIBLE"
        }

        is_removed = submission.removed_by_category is not None
        status = status_icons[is_removed]

        print(f"\n{status}")
        print(f"Title: {submission.title[:60]}...")
        print(f"URL: https://reddit.com{submission.permalink}")
        print(f"Score: {submission.score} | Comments: {submission.num_comments}")
        print(f"Created: {submission.created_utc}")

        if is_removed:
            print(f"Removed by: {submission.removed_by_category}")
            print("⚠️ This post was removed (spam filter, mod action, or automod)")

if not found_posts:
    print("❌ No posts found in r/Paracket from your account")
    print("\nPossible reasons:")
    print("  - Posts were deleted")
    print("  - Posts are stuck in spam filter")
    print("  - Wrong subreddit name")

# Check mod queue (if you're a mod)
print(f"\n🔍 Checking Mod Queue (if you're a moderator):")
print("-"*60)
try:
    mod_queue = list(subreddit.mod.modqueue(limit=20))
    if mod_queue:
        print(f"Found {len(mod_queue)} items in mod queue:")
        for item in mod_queue:
            print(f"  - {item.title[:50]}... (needs approval)")
    else:
        print("✅ Mod queue is empty")
except Exception as e:
    print(f"ℹ️ Cannot access mod queue: {e}")
    print("   (This is normal if you're not a moderator)")

print("\n" + "="*60)
print("\n💡 Recommendations:")
print("1. Check if your posts are in the spam filter (you need mod access)")
print("2. Go to r/Paracket → Mod Tools → Moderation → Mod Queue")
print("3. Approve any posts stuck there")
print("4. Adjust spam filter settings: Mod Tools → Settings → Content Controls")
print("5. Consider setting spam filter to 'low' for self-posts")
