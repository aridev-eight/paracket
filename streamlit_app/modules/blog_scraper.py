"""
Blog Scraper Module
Refactored from blog_scraper_api.py for Streamlit integration
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


def find_blog_feeds(company, blog_url=None):
    """Try to find RSS/blog feeds for a company"""
    potential_feeds = []

    if blog_url:
        # If blog URL is provided, use it as the base
        # Remove trailing slashes
        blog_url = blog_url.rstrip('/')

        # Extract base domain from blog URL
        import urllib.parse
        parsed = urllib.parse.urlparse(blog_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        # Use the provided blog URL as primary base
        base_urls = [
            blog_url,
            base_domain
        ]
    else:
        # Fallback to guessing from company name
        domain_guess = company.lower().replace(' ', '').replace(',', '').replace('.', '')
        base_urls = [
            f"https://www.{domain_guess}.com",
            f"https://{domain_guess}.com",
            f"https://blog.{domain_guess}.com",
            f"https://news.{domain_guess}.com",
            f"https://www.{domain_guess}.io",
            f"https://{domain_guess}.io"
        ]

    feed_paths = [
        '/feed',
        '/rss',
        '/blog/feed',
        '/blog/rss',
        '/feeds/posts/default',
        '/atom.xml',
        '/feed.xml',
        '/rss.xml',
        '/blog/feed.xml',
        '/news/feed',
        '/blog',
        '/news',
        '/articles',
        ''  # Try the blog URL itself as a feed
    ]

    for base in base_urls:
        for path in feed_paths:
            if path:
                potential_feeds.append(f"{base}{path}")
            else:
                potential_feeds.append(base)  # Try base URL as-is

    return potential_feeds


def validate_feed(feed_url):
    """Check if a feed URL is valid and return parsed feed"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BlogScraper/1.0)'
        }

        response = requests.get(feed_url, timeout=10, headers=headers)

        if response.status_code == 200:
            feed = feedparser.parse(response.content)

            if feed.entries and len(feed.entries) > 0:
                print(f"  ✓ Valid feed: {feed_url} ({len(feed.entries)} entries)")
                return feed
            else:
                return None
        else:
            return None

    except Exception as e:
        return None


def scrape_blog_article(url):
    """Scrape full text content from a blog article URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BlogScraper/1.0)'
        }

        response = requests.get(url, timeout=10, headers=headers)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script, style, nav, footer elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Try common article content selectors
        content_selectors = [
            'article',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.blog-post-content',
            '.content',
            'main',
            '#content',
            '.post-body'
        ]

        content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator='\n', strip=True)
                if len(content) > 200:
                    break

        # Fallback: get all paragraphs
        if not content or len(content) < 200:
            paragraphs = soup.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])

        # Clean up excessive whitespace
        if content:
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r' {2,}', ' ', content)

        return content

    except Exception as e:
        print(f"    Error scraping {url}: {e}")
        return None


def scrape_blog_from_feed(feed, limit):
    """Extract blog posts from a parsed RSS feed"""
    samples = []

    for entry in feed.entries[:limit]:
        try:
            # Get basic info from feed
            title = entry.get('title', 'Untitled')
            link = entry.get('link', '')

            # Get published date
            published = entry.get('published', entry.get('updated', ''))
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                date = datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                date = datetime.now().isoformat()

            # Get summary/description from feed
            summary = entry.get('summary', entry.get('description', ''))

            # Clean HTML from summary
            if summary:
                summary_soup = BeautifulSoup(summary, 'html.parser')
                summary = summary_soup.get_text(strip=True)

            print(f"  [{len(samples) + 1}] {title[:60]}...")

            # Try to get full article content
            full_content = scrape_blog_article(link)

            if full_content and len(full_content) > 300:
                text = f"Title: {title}\n\nContent: {full_content}"
                print(f"      ✓ Got full article ({len(full_content)} chars)")
            elif summary and len(summary) > 100:
                text = f"Title: {title}\n\nSummary: {summary}"
                print(f"      ⚠ Using summary only ({len(summary)} chars)")
            else:
                text = f"Title: {title}"
                print(f"      ⚠ Title only")

            # Only add if we have meaningful content
            if len(text) > 50:
                sample = {
                    'text': text,
                    'source': 'blog',
                    'date': date,
                    'url': link,
                    'metadata': {
                        'platform_type': 'blog',
                        'title': title,
                        'has_full_content': full_content is not None,
                        'content_length': len(text),
                        'source_type': 'company_blog'
                    }
                }

                samples.append(sample)
                print(f"      ✓ Added ({len(samples)}/{limit})")

            if len(samples) >= limit:
                break

            time.sleep(0.5)

        except Exception as e:
            print(f"    Error processing entry: {e}")
            continue

    return samples


def scrape_blog(company, limit=150, blog_url=None):
    """
    Main function to scrape blog posts from a company blog

    Args:
        company: Company name
        limit: Number of samples to collect
        blog_url: Optional blog URL (will attempt to find RSS feed from this URL)

    Returns:
        Dict with source, company, samples, etc.
    """
    try:
        print(f"\n{'='*50}")
        print(f"BLOG SCRAPER: {company} (target: {limit} samples)")
        if blog_url:
            print(f"Blog URL: {blog_url}")
        print(f"{'='*50}\n")

        samples = []
        feed_url = None

        # Try to find RSS feed
        if blog_url:
            print(f"Searching for RSS feed from provided blog URL: {blog_url}")
        else:
            print("No blog URL provided, trying to guess from company name...")

        potential_feeds = find_blog_feeds(company, blog_url)

        for url in potential_feeds:
            feed = validate_feed(url)

            if feed:
                feed_url = url
                print(f"\n✓ Found feed: {feed_url}\n")
                samples = scrape_blog_from_feed(feed, limit)
                break

        # If no feed found
        if not feed_url:
            print("\n⚠️ No RSS feed found\n")
            error_msg = "Could not find RSS feed"
            if blog_url:
                error_msg += f" at {blog_url}"
            else:
                error_msg += f" for {company}"

            return {
                'error': error_msg,
                'source': 'blog',
                'company': company,
                'total_samples': 0,
                'samples': [],
                'success': False
            }

        # Sort by date
        samples.sort(key=lambda x: x['date'], reverse=True)
        final_samples = samples[:limit]

        result = {
            'source': 'blog',
            'company': company,
            'scraped_at': datetime.now().isoformat(),
            'total_samples': len(final_samples),
            'samples': final_samples,
            'feed_url': feed_url,
            'blog_url': blog_url,
            'target': limit,
            'success': len(final_samples) > 0
        }

        print(f"\n{'='*50}")
        print(f"✓ COMPLETE: {len(final_samples)}/{limit} samples")
        print(f"Feed: {feed_url}")
        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'source': 'blog',
            'total_samples': 0,
            'samples': [],
            'success': False
        }
