"""
Hacker News Scraper Module
Scrapes trending topics from Hacker News using official API
"""
import requests
from datetime import datetime
import time
import json
import glob
import os
import re


def classify_topic(title, text):
    """Classify what type of topic this is"""
    content = f"{title} {text}".lower()

    if any(word in content for word in ['show hn:', 'show:', 'launched', 'built', 'made']):
        return 'show'
    elif any(word in content for word in ['ask hn:', 'ask:', 'how', 'what', 'why', '?']):
        return 'question'
    elif any(word in content for word in ['yc', 'y combinator', 'hiring', 'jobs']):
        return 'jobs'
    elif any(word in content for word in ['release', 'version', 'announce', 'launch']):
        return 'release'
    else:
        return 'discussion'


def get_hn_item(item_id):
    """Fetch a single item from Hacker News API"""
    try:
        response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"  Error fetching item {item_id}: {e}")
        return None


def get_hn_stories(story_type='top', limit=100):
    """
    Fetch stories from Hacker News

    Args:
        story_type: 'top', 'best', 'new', or 'ask'
        limit: Number of story IDs to fetch

    Returns:
        List of story IDs
    """
    try:
        url = f"https://hacker-news.firebaseio.com/v0/{story_type}stories.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            story_ids = response.json()
            return story_ids[:limit]
        return []
    except Exception as e:
        print(f"  Error fetching {story_type} stories: {e}")
        return []


def load_brand_voice_profile(company):
    """
    Load the most recent brand voice profile for a company

    Args:
        company: Company name

    Returns:
        Brand voice profile dict or None if not found
    """
    try:
        company_safe = company.replace(' ', '_').replace('/', '_')
        # Look for brand voice profiles in the data directory
        pattern = os.path.join('streamlit_app', 'data', f'brand_voice_{company_safe}_*.json')
        profiles = glob.glob(pattern)

        if not profiles:
            # Try without streamlit_app prefix (in case we're already in that directory)
            pattern = os.path.join('data', f'brand_voice_{company_safe}_*.json')
            profiles = glob.glob(pattern)

        if profiles:
            # Get the most recent profile
            most_recent = max(profiles, key=os.path.getmtime)
            with open(most_recent, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                return profile_data.get('brand_voice', {})

        return None
    except Exception as e:
        print(f"  Could not load brand voice profile: {e}")
        return None


def scrape_hackernews_trends(company, limit=20, credentials=None):
    """
    Scrape trending topics about a company from Hacker News

    Args:
        company: Company name
        limit: Number of trending topics to find
        credentials: Not used for HN (no auth needed), kept for API compatibility

    Returns:
        Dict with trending topics
    """
    try:
        print(f"\n{'='*50}")
        print(f"HACKER NEWS TRENDS SCRAPER: {company}")
        print(f"{'='*50}\n")

        # Try to load brand voice profile for better topic matching
        brand_voice = load_brand_voice_profile(company)
        main_topics = []
        if brand_voice:
            main_topics = brand_voice.get('main_topics', [])
            if main_topics:
                print(f"✓ Loaded brand voice profile with {len(main_topics)} main topics:")
                for topic in main_topics[:5]:  # Show first 5
                    print(f"  - {topic}")
                print()
            else:
                print("⚠️ Brand voice profile found but no main topics extracted\n")
        else:
            print("ℹ️ No brand voice profile found - using company name only\n")

        trending_topics = []
        seen_urls = set()

        # Fetch stories from multiple sources for better coverage
        story_sources = [
            ('top', 200),    # Top stories (most popular)
            ('best', 100),   # Best stories (highest quality)
            ('new', 100)     # New stories (recent)
        ]

        all_story_ids = []
        for source_type, fetch_limit in story_sources:
            print(f"Fetching {source_type} stories...")
            story_ids = get_hn_stories(source_type, fetch_limit)
            all_story_ids.extend(story_ids)
            time.sleep(0.5)  # Be nice to the API

        # Remove duplicates while preserving order
        unique_story_ids = []
        seen_ids = set()
        for story_id in all_story_ids:
            if story_id not in seen_ids:
                unique_story_ids.append(story_id)
                seen_ids.add(story_id)

        print(f"\nProcessing {len(unique_story_ids)} unique stories...")
        print(f"Looking for: {company}")
        if main_topics:
            print(f"Also matching: {', '.join(main_topics[:5])}" +
                  (f" (+{len(main_topics)-5} more)" if len(main_topics) > 5 else ""))
        print()

        processed = 0
        for story_id in unique_story_ids:
            if len(trending_topics) >= limit:
                break

            # Fetch story details
            item = get_hn_item(story_id)
            if not item or item.get('type') != 'story':
                continue

            processed += 1
            if processed % 50 == 0:
                print(f"  Processed {processed} stories, found {len(trending_topics)} matches...")

            title = item.get('title', '')
            text = item.get('text', '')
            url = item.get('url', '')

            # Check if story is relevant to the company
            # Use word boundary matching to avoid matching substrings
            pattern = r'\b' + re.escape(company) + r'\b'
            title_match = re.search(pattern, title, re.IGNORECASE)
            text_match = re.search(pattern, text, re.IGNORECASE) if text else False
            url_match = re.search(pattern, url, re.IGNORECASE) if url else False

            is_relevant = bool(title_match or text_match or url_match)

            # If we have main topics from brand voice, also check if post mentions any of them
            if not is_relevant and main_topics:
                story_content = f"{title} {text}".lower()
                for topic in main_topics:
                    topic_pattern = r'\b' + re.escape(topic.lower()) + r'\b'
                    if re.search(topic_pattern, story_content):
                        is_relevant = True
                        break

            if is_relevant:
                hn_url = f"https://news.ycombinator.com/item?id={story_id}"

                # Skip if we've already seen this URL
                if hn_url in seen_urls:
                    continue
                seen_urls.add(hn_url)

                topic_type = classify_topic(title, text)
                score = item.get('score', 0)
                num_comments = item.get('descendants', 0)

                # Create sample in the same format as Reddit scraper
                sample_text = title
                if text:
                    sample_text += f"\n\n{text[:300]}..." if len(text) > 300 else f"\n\n{text}"

                trending_topics.append({
                    'text': sample_text,
                    'source': 'hackernews_trends',
                    'date': datetime.fromtimestamp(item.get('time', 0)).isoformat(),
                    'url': hn_url,
                    'metadata': {
                        'platform_type': 'social',
                        'source_type': 'tech_news',
                        'trend_type': 'hot',
                        'topic_type': topic_type,
                        'engagement': score,
                        'num_comments': num_comments,
                        'author': item.get('by', 'unknown'),
                        'external_url': url if url else None
                    }
                })

                time.sleep(0.1)  # Be nice to the API

        print(f"\n✓ Found {len(trending_topics)} trending topics")
        if main_topics:
            print(f"  (Using brand voice topics for enhanced matching)")

        result = {
            'source': 'hackernews_trends',
            'company': company,
            'scraped_at': datetime.now().isoformat(),
            'total_samples': len(trending_topics),
            'samples': trending_topics,
            'success': len(trending_topics) > 0,
            'used_brand_voice': bool(main_topics),
            'main_topics_used': main_topics if main_topics else []
        }

        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'source': 'hackernews_trends',
            'total_samples': 0,
            'samples': [],
            'success': False
        }


if __name__ == '__main__':
    # Test the scraper
    import sys

    company_name = sys.argv[1] if len(sys.argv) > 1 else "Unity"
    result = scrape_hackernews_trends(company_name, limit=10)

    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Total samples: {result['total_samples']}")

    if result['samples']:
        print("\nFirst 3 samples:")
        for i, sample in enumerate(result['samples'][:3], 1):
            print(f"\n{i}. {sample['text'][:100]}...")
            print(f"   URL: {sample['url']}")
            print(f"   Engagement: {sample['metadata']['engagement']} points, {sample['metadata']['num_comments']} comments")
