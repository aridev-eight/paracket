#!/usr/bin/env python3
"""
Paracket Post Scheduler
Checks for scheduled posts and publishes them at the scheduled time
Run this script periodically (e.g., every 5 minutes) via cron or GitHub Actions
"""
import os
import sys
import json
import glob
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(__file__))

from modules.social_poster import post_to_platforms


def load_scheduled_posts():
    """Load all scheduled posts from the data directory"""
    # Try both possible paths
    patterns = [
        os.path.join('streamlit_app', 'data', 'scheduled_posts', 'scheduled_*.json'),
        os.path.join('data', 'scheduled_posts', 'scheduled_*.json')
    ]

    post_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            post_files = files
            break

    scheduled_posts = []
    for file_path in post_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = json.load(f)
                post['file_path'] = file_path
                scheduled_posts.append(post)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return scheduled_posts


def check_and_post():
    """Check for posts due to be published and post them"""
    print(f"\n{'='*60}")
    print(f"Paracket Scheduler - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    scheduled_posts = load_scheduled_posts()

    if not scheduled_posts:
        print("No scheduled posts found.")
        return

    print(f"Found {len(scheduled_posts)} total scheduled post(s)")

    now = datetime.now()
    posts_to_publish = []

    # Find posts that should be published
    for post in scheduled_posts:
        status = post.get('status', 'active')
        scheduled_time = datetime.fromisoformat(post['scheduled_time'])

        # Only process active posts that are due
        if status == 'active' and scheduled_time <= now:
            posts_to_publish.append(post)

    if not posts_to_publish:
        print("No posts due for publishing at this time.")
        return

    print(f"\n{len(posts_to_publish)} post(s) ready to publish:\n")

    # Publish each post
    for post in posts_to_publish:
        post_id = post['id']
        company = post.get('company', 'Unknown')
        theme = post.get('theme', 'Untitled')
        scheduled_time = datetime.fromisoformat(post['scheduled_time'])

        print(f"{'='*60}")
        print(f"Publishing: {company} - {theme}")
        print(f"Post ID: {post_id}")
        print(f"Scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Attempt to post to all platforms
        try:
            results = post_to_platforms(post)

            # Update post status based on results
            if results['success']:
                post['status'] = 'posted'
                post['posted_results'] = results
                print(f"\n✓ Successfully posted to at least one platform")
            else:
                post['status'] = 'failed'
                post['failed_results'] = results
                print(f"\n✗ Failed to post to all platforms")

            # Save updated post
            with open(post['file_path'], 'w', encoding='utf-8') as f:
                json.dump(post, f, indent=2)

        except Exception as e:
            print(f"\n✗ Error publishing post: {e}")

            # Mark as failed
            post['status'] = 'failed'
            post['error'] = str(e)

            with open(post['file_path'], 'w', encoding='utf-8') as f:
                json.dump(post, f, indent=2)

        print()

    print(f"{'='*60}")
    print(f"Scheduler run complete")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    try:
        check_and_post()
    except KeyboardInterrupt:
        print("\nScheduler interrupted by user")
    except Exception as e:
        print(f"\nScheduler error: {e}")
        import traceback
        traceback.print_exc()
