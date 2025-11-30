#!/usr/bin/env python3
"""
Test Mastodon API credentials
"""
from mastodon import Mastodon
import os
from dotenv import load_dotenv

# Load secrets
load_dotenv('.streamlit/secrets.toml')

instance = os.getenv('MASTODON_INSTANCE', 'https://mastodon.social')
access_token = os.getenv('MASTODON_ACCESS_TOKEN', '')

if not access_token:
    print("❌ No MASTODON_ACCESS_TOKEN found in .streamlit/secrets.toml")
    print("Please add your Mastodon access token to the secrets file.")
    exit(1)

print("Testing Mastodon API credentials...")
print(f"Instance: {instance}")
print()

try:
    # Create Mastodon client
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=instance
    )

    # Get account info to verify credentials
    account = mastodon.account_verify_credentials()

    print("✅ Mastodon credentials are valid!")
    print()
    print(f"Account: @{account['username']}")
    print(f"Display Name: {account['display_name']}")
    print(f"Followers: {account['followers_count']}")
    print(f"Following: {account['following_count']}")
    print(f"Posts: {account['statuses_count']}")
    print()
    print("You can now use Madison AI to post to Mastodon!")
    print()
    print("To post a test message, you can use:")
    print("  status = mastodon.status_post('Hello from Madison AI! 🤖')")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Possible issues:")
    print("  - Invalid access token")
    print("  - Wrong instance URL")
    print("  - Token doesn't have write permissions")
    print()
    print("Please check your credentials and try again.")
