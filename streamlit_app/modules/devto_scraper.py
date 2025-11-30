"""
Dev.to Scraper
Scrapes trending articles from Dev.to
"""

import requests
import re
from datetime import datetime, timedelta

def scrape_devto_trends(company, limit=20, credentials=None):
    """
    Scrape trending articles from Dev.to related to a company

    Args:
        company: Company name to search for
        limit: Maximum number of trends to return
        credentials: Optional dict with brand_voice for topic matching

    Returns:
        dict with success status, trends list, and metadata
    """

    print(f"\n=== Dev.to Trends Scraper ===")
    print(f"Company: {company}")
    print(f"Limit: {limit}")

    trends = []
    api_base = "https://dev.to/api"

    try:
        # Strategy 1: Search for company name
        print(f"Searching Dev.to for articles about '{company}'...")

        # Dev.to search endpoint
        search_url = f"{api_base}/articles"

        # Search parameters - get recent popular articles
        params = {
            'per_page': 50,
            'top': 7  # Articles from last week
        }

        response = requests.get(search_url, params=params, timeout=10)

        if response.status_code == 200:
            articles = response.json()

            # Filter for company mentions
            company_lower = company.lower()
            company_pattern = r'\b' + re.escape(company_lower) + r'\b'

            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                tags = article.get('tag_list', [])
                body_markdown = article.get('body_markdown', '')

                # Check if company is mentioned in title, description, or tags
                combined_text = f"{title} {description} {' '.join(tags)}".lower()

                if re.search(company_pattern, combined_text):
                    trends.append({
                        'title': title,
                        'description': description,
                        'url': article.get('url', ''),
                        'published_at': article.get('published_at', ''),
                        'reactions': article.get('public_reactions_count', 0),
                        'comments': article.get('comments_count', 0),
                        'reading_time': article.get('reading_time_minutes', 0),
                        'tags': tags,
                        'author': article.get('user', {}).get('name', 'Unknown'),
                        'source': 'devto'
                    })

            print(f"Found {len(trends)} articles directly mentioning '{company}'")

        # Strategy 2: Search by tags if we have brand voice data
        if len(trends) < 5 and credentials and 'brand_voice' in credentials:
            brand_voice = credentials['brand_voice']
            main_topics = brand_voice.get('main_topics', [])

            if main_topics:
                print(f"Searching by brand topics: {main_topics[:3]}")

                # Try searching by tags
                for topic in main_topics[:3]:
                    # Clean topic to make it tag-friendly
                    tag = topic.lower().replace(' ', '').replace('-', '')

                    tag_url = f"{api_base}/articles"
                    tag_params = {
                        'tag': tag,
                        'per_page': 10,
                        'top': 7
                    }

                    try:
                        tag_response = requests.get(tag_url, params=tag_params, timeout=10)
                        if tag_response.status_code == 200:
                            tag_articles = tag_response.json()

                            for article in tag_articles[:3]:  # Top 3 per topic
                                # Avoid duplicates
                                if not any(t.get('url') == article.get('url') for t in trends):
                                    trends.append({
                                        'title': article.get('title', ''),
                                        'description': article.get('description', ''),
                                        'url': article.get('url', ''),
                                        'published_at': article.get('published_at', ''),
                                        'reactions': article.get('public_reactions_count', 0),
                                        'comments': article.get('comments_count', 0),
                                        'reading_time': article.get('reading_time_minutes', 0),
                                        'tags': article.get('tag_list', []),
                                        'author': article.get('user', {}).get('name', 'Unknown'),
                                        'source': 'devto',
                                        'matched_topic': topic
                                    })
                    except Exception as e:
                        print(f"Error searching tag '{tag}': {e}")
                        continue

                    if len(trends) >= limit:
                        break

        # Strategy 3: Get latest popular articles in relevant tags
        if len(trends) < 3:
            print("Fetching latest popular tech articles...")

            # Common tech tags
            tech_tags = ['ai', 'machinelearning', 'programming', 'webdev', 'technology', 'startup']

            for tag in tech_tags[:2]:  # Try first 2 tags
                try:
                    tag_url = f"{api_base}/articles"
                    tag_params = {
                        'tag': tag,
                        'per_page': 5,
                        'top': 1  # Today's top
                    }

                    tag_response = requests.get(tag_url, params=tag_params, timeout=10)
                    if tag_response.status_code == 200:
                        tag_articles = tag_response.json()

                        for article in tag_articles[:2]:
                            if not any(t.get('url') == article.get('url') for t in trends):
                                trends.append({
                                    'title': article.get('title', ''),
                                    'description': article.get('description', ''),
                                    'url': article.get('url', ''),
                                    'published_at': article.get('published_at', ''),
                                    'reactions': article.get('public_reactions_count', 0),
                                    'comments': article.get('comments_count', 0),
                                    'reading_time': article.get('reading_time_minutes', 0),
                                    'tags': article.get('tag_list', []),
                                    'author': article.get('user', {}).get('name', 'Unknown'),
                                    'source': 'devto',
                                    'note': 'General tech trend'
                                })

                except Exception as e:
                    print(f"Error fetching tag '{tag}': {e}")
                    continue

        # Limit results
        trends = trends[:limit]

        print(f"\nTotal unique trends found: {len(trends)}")

        return {
            'success': True,
            'trends': trends,
            'total_found': len(trends),
            'company': company,
            'scraped_at': datetime.now().isoformat(),
            'source': 'devto'
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Dev.to data: {e}")
        return {
            'success': False,
            'error': str(e),
            'trends': [],
            'total_found': 0
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'success': False,
            'error': str(e),
            'trends': [],
            'total_found': 0
        }


if __name__ == '__main__':
    # Test the scraper
    import sys

    company = sys.argv[1] if len(sys.argv) > 1 else "Unity"

    print(f"Testing Dev.to scraper for: {company}")
    result = scrape_devto_trends(company, limit=10)

    print(f"\n=== Results ===")
    print(f"Success: {result['success']}")
    print(f"Total found: {result['total_found']}")

    if result['trends']:
        print(f"\nTrends:")
        for i, trend in enumerate(result['trends'][:5], 1):
            print(f"\n{i}. {trend.get('title', 'N/A')}")
            print(f"   Description: {trend.get('description', 'N/A')[:100]}...")
            print(f"   Reactions: {trend.get('reactions', 0)} | Comments: {trend.get('comments', 0)}")
            print(f"   Tags: {', '.join(trend.get('tags', []))}")
            print(f"   URL: {trend.get('url', 'N/A')}")
