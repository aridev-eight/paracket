#!/usr/bin/env python3
"""
Test Reddit API credentials
"""
import praw
import os
from dotenv import load_dotenv

# Load secrets
load_dotenv('.streamlit/secrets.toml')

client_id = os.getenv('REDDIT_CLIENT_ID', '')
client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
username = os.getenv('REDDIT_USERNAME', '')
password = os.getenv('REDDIT_PASSWORD', '')
user_agent = os.getenv('REDDIT_USER_AGENT', 'paracket_poster/1.0')

if not all([client_id, client_secret, username, password]):
    print("❌ Missing Reddit credentials in .streamlit/secrets.toml")
    print()
    print("Please add these to your secrets file:")
    print("  REDDIT_CLIENT_ID")
    print("  REDDIT_CLIENT_SECRET")
    print("  REDDIT_USERNAME")
    print("  REDDIT_PASSWORD")
    exit(1)

print("Testing Reddit API credentials...")
print()

try:
    # Create Reddit instance
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent
    )

    # Get authenticated user info
    user = reddit.user.me()

    print("✅ Reddit credentials are valid!")
    print()
    print(f"Username: u/{user.name}")
    print(f"Comment Karma: {user.comment_karma}")
    print(f"Link Karma: {user.link_karma}")
    print(f"Account Created: {user.created_utc}")
    print()
    print("You can now use Madison AI to post to Reddit!")
    print()
    print("⚠️ Note: Make sure you have posting permissions in your target subreddits")
    print("   Some subreddits have karma/age requirements")

except praw.exceptions.OAuthException as e:
    print("❌ OAuth Error!")
    print()
    print("This usually means:")
    print("  - Invalid client ID or client secret")
    print("  - Client ID/secret don't match your app")
    print()
    print("Double-check your credentials at:")
    print("  https://www.reddit.com/prefs/apps")
    print()
    print(f"Error details: {e}")

except praw.exceptions.ResponseException as e:
    print("❌ Authentication Failed!")
    print()
    print("This usually means:")
    print("  - Invalid username or password")
    print("  - Account has 2FA enabled (you may need an app password)")
    print()
    print(f"Error details: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Possible issues:")
    print("  - Invalid credentials")
    print("  - Network error")
    print("  - Reddit API is down")
    print()
    print("Check your credentials in .streamlit/secrets.toml")
