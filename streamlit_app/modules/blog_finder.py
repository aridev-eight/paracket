"""
AI-Powered Blog Finder
Uses OpenAI to intelligently find company blog URLs and RSS feeds
"""

import requests
from openai import OpenAI


def find_blog_with_ai(company, openai_api_key):
    """
    Use OpenAI to find likely blog URLs and RSS feeds for a company

    Args:
        company: Company name
        openai_api_key: OpenAI API key

    Returns:
        dict with suggested URLs to try
    """

    print(f"\n{'='*60}")
    print(f"AI Blog Finder: {company}")
    print(f"{'='*60}\n")

    client = OpenAI(api_key=openai_api_key)

    prompt = f"""Given the company name "{company}", suggest the most likely blog URLs and RSS feed URLs.

Consider:
1. Common blog subdomain patterns (blog.company.com, news.company.com)
2. Common blog paths (/blog, /news, /insights, /updates)
3. Company naming variations (with/without spaces, abbreviations)
4. Common TLDs (.com, .io, .co, .ai, .dev)
5. RSS feed patterns (/feed, /rss, /feed.xml, /atom.xml)

Return a JSON object with this structure:
{{
  "likely_blog_urls": [
    "https://blog.company.com",
    "https://company.com/blog",
    ...
  ],
  "likely_rss_feeds": [
    "https://blog.company.com/feed",
    "https://company.com/blog/feed",
    ...
  ],
  "reasoning": "Brief explanation of why these URLs are likely"
}}

Be specific to this company. If it's a well-known company, use your knowledge.
Provide 5-10 of the MOST LIKELY URLs, not every possible variation.
"""

    try:
        print("Asking AI to suggest blog URLs...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds company blog URLs and RSS feeds. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = response.choices[0].message.content

        import json
        suggestions = json.loads(result)

        print("\nAI Suggestions:")
        print(f"Reasoning: {suggestions.get('reasoning', 'N/A')}")
        print(f"\nBlog URLs to try: {len(suggestions.get('likely_blog_urls', []))}")
        for url in suggestions.get('likely_blog_urls', [])[:5]:
            print(f"  - {url}")

        print(f"\nRSS Feeds to try: {len(suggestions.get('likely_rss_feeds', []))}")
        for url in suggestions.get('likely_rss_feeds', [])[:5]:
            print(f"  - {url}")

        return {
            'success': True,
            'suggestions': suggestions
        }

    except Exception as e:
        print(f"Error using AI to find blog: {e}")
        return {
            'success': False,
            'error': str(e),
            'suggestions': {
                'likely_blog_urls': [],
                'likely_rss_feeds': []
            }
        }


def test_url_exists(url):
    """
    Quick check if a URL exists and is accessible

    Args:
        url: URL to test

    Returns:
        bool: True if URL is accessible
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Paracket/1.0)'
        }
        response = requests.head(url, timeout=5, headers=headers, allow_redirects=True)
        return response.status_code < 400
    except:
        return False


def find_working_urls(suggestions):
    """
    Test suggested URLs to find which ones actually work

    Args:
        suggestions: Dict with likely_blog_urls and likely_rss_feeds

    Returns:
        dict with working_blogs and working_feeds
    """
    print("\nTesting suggested URLs...")

    working_blogs = []
    working_feeds = []

    # Test blog URLs
    for url in suggestions.get('likely_blog_urls', []):
        print(f"Testing: {url}...", end=' ')
        if test_url_exists(url):
            print("✓ Works")
            working_blogs.append(url)
        else:
            print("✗ Not accessible")

    # Test RSS feeds
    for url in suggestions.get('likely_rss_feeds', []):
        print(f"Testing: {url}...", end=' ')
        if test_url_exists(url):
            print("✓ Works")
            working_feeds.append(url)
        else:
            print("✗ Not accessible")

    print(f"\nResults:")
    print(f"  Working blogs: {len(working_blogs)}")
    print(f"  Working feeds: {len(working_feeds)}")

    return {
        'working_blogs': working_blogs,
        'working_feeds': working_feeds
    }


def find_blog_url_with_ai(company, openai_api_key):
    """
    Complete workflow: Use AI to find blog URL, then test to find working ones

    Args:
        company: Company name
        openai_api_key: OpenAI API key

    Returns:
        dict with best_blog_url, best_feed_url, and all working URLs
    """
    # Get AI suggestions
    ai_result = find_blog_with_ai(company, openai_api_key)

    if not ai_result['success']:
        return {
            'success': False,
            'error': ai_result.get('error', 'Unknown error')
        }

    suggestions = ai_result['suggestions']

    # Test URLs to find working ones
    working = find_working_urls(suggestions)

    # Return best results
    best_blog = working['working_blogs'][0] if working['working_blogs'] else None
    best_feed = working['working_feeds'][0] if working['working_feeds'] else None

    print(f"\n{'='*60}")
    print(f"Final Results:")
    print(f"  Best blog URL: {best_blog or 'Not found'}")
    print(f"  Best feed URL: {best_feed or 'Not found'}")
    print(f"{'='*60}\n")

    return {
        'success': True,
        'best_blog_url': best_blog,
        'best_feed_url': best_feed,
        'all_working_blogs': working['working_blogs'],
        'all_working_feeds': working['working_feeds'],
        'ai_reasoning': suggestions.get('reasoning', '')
    }


if __name__ == '__main__':
    import sys
    import os

    company = sys.argv[1] if len(sys.argv) > 1 else "Unity"
    openai_key = os.getenv('OPENAI_API_KEY')

    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    print(f"Testing AI Blog Finder for: {company}")
    result = find_blog_url_with_ai(company, openai_key)

    if result['success']:
        print("\n=== Success ===")
        print(f"Best blog: {result['best_blog_url']}")
        print(f"Best feed: {result['best_feed_url']}")
        print(f"\nAll working blogs: {result['all_working_blogs']}")
        print(f"All working feeds: {result['all_working_feeds']}")
        print(f"\nAI reasoning: {result['ai_reasoning']}")
    else:
        print(f"\n=== Failed ===")
        print(f"Error: {result.get('error')}")
