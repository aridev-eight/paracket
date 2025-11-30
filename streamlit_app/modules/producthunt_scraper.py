"""
Product Hunt Scraper
Scrapes trending topics from Product Hunt
"""

import requests
import re
from datetime import datetime, timedelta

def scrape_producthunt_trends(company, limit=20, credentials=None):
    """
    Scrape trending topics about a company from Product Hunt

    Args:
        company: Company name to search for
        limit: Maximum number of trends to return
        credentials: Optional dict with 'product_hunt_token' for authenticated requests

    Returns:
        dict with success status, trends list, and metadata
    """

    print(f"\n=== Product Hunt Trends Scraper ===")
    print(f"Company: {company}")
    print(f"Limit: {limit}")

    trends = []

    # Product Hunt GraphQL API endpoint
    api_url = "https://api.producthunt.com/v2/api/graphql"

    # Set up headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'paracket/1.0'
    }

    # Add auth token if provided
    if credentials and 'product_hunt_token' in credentials:
        headers['Authorization'] = f"Bearer {credentials['product_hunt_token']}"
        print("Using authenticated API access")
    else:
        print("Using public API access (limited to featured posts)")

    try:
        # If we have auth, we can search for posts
        if credentials and 'product_hunt_token' in credentials:
            # GraphQL query to search for posts
            query = """
            query($search_query: String!) {
              posts(order: VOTES, first: 50, postedAfter: "2024-01-01", search: $search_query) {
                edges {
                  node {
                    id
                    name
                    tagline
                    description
                    votesCount
                    commentsCount
                    createdAt
                    url
                    topics {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
            """

            variables = {
                "search_query": company
            }

            response = requests.post(
                api_url,
                json={'query': query, 'variables': variables},
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('posts', {}).get('edges', [])

                for post_edge in posts[:limit]:
                    post = post_edge.get('node', {})

                    topics_list = []
                    for topic_edge in post.get('topics', {}).get('edges', []):
                        topic_name = topic_edge.get('node', {}).get('name')
                        if topic_name:
                            topics_list.append(topic_name)

                    trends.append({
                        'title': post.get('name', ''),
                        'description': post.get('tagline', ''),
                        'full_description': post.get('description', ''),
                        'url': post.get('url', ''),
                        'votes': post.get('votesCount', 0),
                        'comments': post.get('commentsCount', 0),
                        'created_at': post.get('createdAt', ''),
                        'topics': topics_list,
                        'source': 'producthunt'
                    })

                print(f"Found {len(trends)} matching posts via authenticated search")

        else:
            # Without auth, scrape the public "today" page
            # Get today's featured posts
            today = datetime.now().strftime('%Y-%m-%d')
            public_url = f"https://www.producthunt.com/posts"

            print(f"Fetching public featured posts...")

            response = requests.get(
                public_url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; paracket/1.0)'},
                timeout=10
            )

            if response.status_code == 200:
                # Use simple text parsing to extract product information
                content = response.text

                # Look for product data in the page
                # This is a simplified approach - Product Hunt's public page structure
                # Pattern to find product mentions
                pattern = r'<a[^>]*data-test="post-name"[^>]*>([^<]+)</a>'
                products = re.findall(pattern, content)

                # Check if any products are relevant to the company
                company_lower = company.lower()
                company_pattern = r'\b' + re.escape(company_lower) + r'\b'

                for product_name in products[:30]:  # Check top 30 products
                    if re.search(company_pattern, product_name.lower()):
                        trends.append({
                            'title': product_name,
                            'description': 'Featured on Product Hunt',
                            'url': f'https://www.producthunt.com/search?q={company.replace(" ", "+")}',
                            'source': 'producthunt',
                            'votes': 0,
                            'comments': 0
                        })

                print(f"Found {len(trends)} matching products from public feed")

        # If we have brand voice data in credentials, try topic-based matching
        if len(trends) < 5 and credentials and 'brand_voice' in credentials:
            brand_voice = credentials['brand_voice']
            main_topics = brand_voice.get('main_topics', [])

            if main_topics:
                print(f"Trying topic-based search with brand topics: {main_topics[:3]}")

                # Try searching for main topics
                for topic in main_topics[:3]:  # Try top 3 topics
                    if credentials and 'product_hunt_token' in credentials:
                        # Use GraphQL search for topic
                        query = """
                        query($search_query: String!) {
                          posts(order: VOTES, first: 10, postedAfter: "2024-01-01", search: $search_query) {
                            edges {
                              node {
                                id
                                name
                                tagline
                                votesCount
                                url
                              }
                            }
                          }
                        }
                        """

                        variables = {"search_query": topic}

                        response = requests.post(
                            api_url,
                            json={'query': query, 'variables': variables},
                            headers=headers,
                            timeout=10
                        )

                        if response.status_code == 200:
                            data = response.json()
                            posts = data.get('data', {}).get('posts', {}).get('edges', [])

                            for post_edge in posts[:3]:  # Take top 3 per topic
                                post = post_edge.get('node', {})
                                trends.append({
                                    'title': post.get('name', ''),
                                    'description': post.get('tagline', ''),
                                    'url': post.get('url', ''),
                                    'votes': post.get('votesCount', 0),
                                    'source': 'producthunt',
                                    'matched_topic': topic
                                })

                    if len(trends) >= limit:
                        break

        # Remove duplicates
        seen_titles = set()
        unique_trends = []
        for trend in trends:
            title = trend.get('title', '').lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_trends.append(trend)

        trends = unique_trends[:limit]

        print(f"\nTotal unique trends found: {len(trends)}")

        return {
            'success': True,
            'trends': trends,
            'total_found': len(trends),
            'company': company,
            'scraped_at': datetime.now().isoformat(),
            'source': 'producthunt'
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Product Hunt data: {e}")
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

    company = sys.argv[1] if len(sys.argv) > 1 else "OpenAI"

    print(f"Testing Product Hunt scraper for: {company}")
    result = scrape_producthunt_trends(company, limit=10)

    print(f"\n=== Results ===")
    print(f"Success: {result['success']}")
    print(f"Total found: {result['total_found']}")

    if result['trends']:
        print(f"\nTrends:")
        for i, trend in enumerate(result['trends'][:5], 1):
            print(f"\n{i}. {trend.get('title', 'N/A')}")
            print(f"   Description: {trend.get('description', 'N/A')}")
            print(f"   Votes: {trend.get('votes', 0)}")
            print(f"   URL: {trend.get('url', 'N/A')}")
