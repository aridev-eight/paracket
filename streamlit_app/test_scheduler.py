#!/usr/bin/env python3
"""
Test the Madison AI Scheduler
Creates a test scheduled post and runs the scheduler to verify it works
"""
import os
import json
from datetime import datetime, timedelta


def create_test_post():
    """Create a test scheduled post for 1 minute in the future"""
    print("Creating test scheduled post...")

    # Create scheduled post 1 minute in the future
    scheduled_time = datetime.now() + timedelta(minutes=1)

    test_post = {
        'id': 'TEST_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
        'company': 'Test Company',
        'scheduled_time': scheduled_time.isoformat(),
        'created_at': datetime.now().isoformat(),
        'status': 'active',
        'master_message': 'This is a test post from Madison AI scheduler.',
        'theme': 'Scheduler Test',
        'platforms': {
            'twitter': {
                'content': 'Test tweet from Madison AI 🤖 #test',
                'enabled': True
            }
        },
        'credentials': {
            # Note: These are fake credentials for testing
            # Real credentials would be needed for actual posting
        }
    }

    # Save test post
    posts_dir = os.path.join('data', 'scheduled_posts')
    os.makedirs(posts_dir, exist_ok=True)

    file_path = os.path.join(posts_dir, f"scheduled_{test_post['id']}.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_post, f, indent=2)

    print(f"✓ Test post created: {file_path}")
    print(f"  Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Post ID: {test_post['id']}")
    print()
    print("⚠️ Note: This post won't actually be posted without valid API credentials")
    print("   It will test the scheduler logic only")
    print()
    print("To test the scheduler:")
    print("  1. Wait until after the scheduled time")
    print("  2. Run: python3 scheduler.py")
    print("  3. Check that the post status changes to 'failed' (due to missing credentials)")
    print()

    return test_post


if __name__ == '__main__':
    print("="*60)
    print("Madison AI Scheduler Test")
    print("="*60)
    print()

    test_post = create_test_post()

    print("Test post created successfully!")
    print()
    print("Next steps:")
    print("  • Go to the Scheduled Posts page in the Streamlit app to view it")
    print("  • Wait 1 minute, then run 'python3 scheduler.py' to test posting")
    print("  • Check the Scheduled Posts page to see the status update")
    print()
