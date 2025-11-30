#!/usr/bin/env python3
"""
Test Twitter/X API credentials
"""
import tweepy
import os
from dotenv import load_dotenv

# Load secrets
load_dotenv('.streamlit/secrets.toml')

api_key = os.getenv('TWITTER_API_KEY', '')
api_secret = os.getenv('TWITTER_API_SECRET', '')
access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
access_secret = os.getenv('TWITTER_ACCESS_SECRET', '')

if not all([api_key, api_secret, access_token, access_secret]):
    print("❌ Missing Twitter credentials in .streamlit/secrets.toml")
    print()
    print("Please add these to your secrets file:")
    print("  TWITTER_API_KEY")
    print("  TWITTER_API_SECRET")
    print("  TWITTER_ACCESS_TOKEN")
    print("  TWITTER_ACCESS_SECRET")
    exit(1)

print("Testing Twitter/X API credentials...")
print()

try:
    # Create Twitter API client using OAuth 1.0a
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )

    # Get authenticated user info to verify credentials
    me = client.get_me(user_fields=['public_metrics', 'description'])

    if me.data:
        user = me.data
        metrics = user.public_metrics

        print("✅ Twitter credentials are valid!")
        print()
        print(f"Account: @{user.username}")
        print(f"Name: {user.name}")
        print(f"Followers: {metrics.get('followers_count', 0)}")
        print(f"Following: {metrics.get('following_count', 0)}")
        print(f"Tweets: {metrics.get('tweet_count', 0)}")
        print()
        print("You can now use Madison AI to post to Twitter/X!")
        print()
        print("⚠️ Note: Make sure your app has 'Read and Write' permissions")
        print("   Check at: https://developer.twitter.com/en/portal/dashboard")
    else:
        print("❌ Could not retrieve user info")
        print("This might mean your credentials are invalid or permissions are wrong")

except tweepy.errors.Forbidden as e:
    print("❌ Access Forbidden!")
    print()
    print("This usually means:")
    print("  1. Your app doesn't have 'Read and Write' permissions")
    print("  2. Go to https://developer.twitter.com/en/portal/dashboard")
    print("  3. Click your app → Settings → Edit App permissions")
    print("  4. Change to 'Read and Write'")
    print("  5. Regenerate your Access Tokens")
    print()
    print(f"Error details: {e}")

except tweepy.errors.Unauthorized as e:
    print("❌ Unauthorized!")
    print()
    print("This usually means:")
    print("  - Invalid API keys or access tokens")
    print("  - Tokens don't match the API keys")
    print()
    print("Double-check your credentials in .streamlit/secrets.toml")
    print()
    print(f"Error details: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Possible issues:")
    print("  - Invalid credentials")
    print("  - Network error")
    print("  - Twitter API is down")
