"""
Reddit Scraper Module
Refactored from reddit_scraper_api.py for Streamlit integration
"""
import praw
from datetime import datetime
import time
import os
import re
import json
import glob


def scrape_official_user(reddit, username, limit):
    """Scrape from official user account"""
    samples = []

    try:
        user = reddit.redditor(username)
        _ = user.created_utc

        print(f"✓ Found official user: u/{username}")

        # Get ALL submissions (posts)
        print(f"  Getting posts from u/{username}...")
        for submission in user.submissions.new(limit=None):
            sample = {
                'text': f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title,
                'source': 'reddit',
                'date': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'url': f"https://reddit.com{submission.permalink}",
                'metadata': {
                    'platform_type': 'social',
                    'author': str(submission.author),
                    'engagement': submission.score,
                    'subreddit': str(submission.subreddit),
                    'num_comments': submission.num_comments,
                    'type': 'post',
                    'source_type': 'official_user'
                }
            }
            samples.append(sample)

            if len(samples) >= limit:
                break

            time.sleep(0.05)

        print(f"  Got {len(samples)} posts")

        # Get ALL comments if still need more
        if len(samples) < limit:
            print(f"  Getting comments from u/{username}...")
            for comment in user.comments.new(limit=None):
                if len(comment.body) >= 30:
                    sample = {
                        'text': comment.body,
                        'source': 'reddit',
                        'date': datetime.fromtimestamp(comment.created_utc).isoformat(),
                        'url': f"https://reddit.com{comment.permalink}",
                        'metadata': {
                            'platform_type': 'social',
                            'author': str(comment.author),
                            'engagement': comment.score,
                            'subreddit': str(comment.subreddit),
                            'type': 'comment',
                            'source_type': 'official_user'
                        }
                    }
                    samples.append(sample)

                    if len(samples) >= limit:
                        break

                    time.sleep(0.05)

            print(f"  Got {len(samples)} total (posts + comments)")

        return samples

    except Exception as e:
        print(f"Could not scrape u/{username}: {e}")
        return []


def scrape_official_subreddit(reddit, subreddit_name, limit):
    """Scrape from official subreddit"""
    samples = []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        _ = subreddit.created_utc

        print(f"✓ Found official subreddit: r/{subreddit_name}")

        print(f"  Getting posts from r/{subreddit_name}...")

        for sort_method in ['hot', 'new', 'top']:
            if len(samples) >= limit:
                break

            if sort_method == 'hot':
                posts = subreddit.hot(limit=200)
            elif sort_method == 'new':
                posts = subreddit.new(limit=200)
            else:
                posts = subreddit.top(time_filter='all', limit=200)

            for submission in posts:
                if submission.stickied:
                    continue

                text = f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title

                if len(text) < 30:
                    continue

                if any(s['url'] == f"https://reddit.com{submission.permalink}" for s in samples):
                    continue

                sample = {
                    'text': text,
                    'source': 'reddit',
                    'date': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'url': f"https://reddit.com{submission.permalink}",
                    'metadata': {
                        'platform_type': 'social',
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'engagement': submission.score,
                        'subreddit': str(submission.subreddit),
                        'num_comments': submission.num_comments,
                        'type': 'post',
                        'source_type': 'official_subreddit'
                    }
                }
                samples.append(sample)

                if len(samples) >= limit:
                    break

                time.sleep(0.05)

        print(f"  Got {len(samples)} posts from r/{subreddit_name}")
        return samples

    except Exception as e:
        print(f"Could not scrape r/{subreddit_name}: {e}")
        return []


def scrape_fallback(reddit, company, limit):
    """Aggressive fallback to get samples"""
    samples = []

    print(f"⚠️ Using fallback mode (mentions)")

    for submission in reddit.subreddit('all').search(company, limit=300, sort='relevance', time_filter='all'):
        url = f"https://reddit.com{submission.permalink}"
        if any(s['url'] == url for s in samples):
            continue

        text = f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title

        if len(text) < 30:
            continue

        sample = {
            'text': text,
            'source': 'reddit',
            'date': datetime.fromtimestamp(submission.created_utc).isoformat(),
            'url': url,
            'metadata': {
                'platform_type': 'social',
                'author': str(submission.author) if submission.author else '[deleted]',
                'engagement': submission.score,
                'subreddit': str(submission.subreddit),
                'num_comments': submission.num_comments,
                'type': 'post',
                'source_type': 'fallback'
            }
        }
        samples.append(sample)

        if len(samples) >= limit:
            break

        time.sleep(0.05)

    return samples


def scrape_reddit(company, limit=150, credentials=None):
    """
    Main function to scrape Reddit data for a company

    Args:
        company: Company name
        limit: Number of samples to collect
        credentials: Dict with reddit_client_id, reddit_client_secret, reddit_user_agent

    Returns:
        Dict with source, company, samples, etc.
    """
    try:
        print(f"\n{'='*50}")
        print(f"REDDIT SCRAPER: {company} (target: {limit} samples)")
        print(f"{'='*50}\n")

        # Get credentials
        if credentials:
            client_id = credentials.get('reddit_client_id')
            client_secret = credentials.get('reddit_client_secret')
            user_agent = credentials.get('reddit_user_agent', 'brand_voice_scraper/1.0')
        else:
            client_id = os.environ.get('REDDIT_CLIENT_ID')
            client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
            user_agent = os.environ.get('REDDIT_USER_AGENT', 'brand_voice_scraper/1.0')

        if not client_id or not client_secret:
            raise ValueError("Missing Reddit API credentials")

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        all_samples = []
        sources_used = []

        # Try official USER
        possible_usernames = [company, company.lower(), company.replace(' ', ''), f"{company}Official"]

        for username in possible_usernames:
            user_samples = scrape_official_user(reddit, username, limit)
            if user_samples:
                all_samples.extend(user_samples)
                sources_used.append(f"u/{username}")
                print(f"✓ Total so far: {len(all_samples)}")
                break

        # Try SUBREDDIT
        if len(all_samples) < limit:
            print(f"\nNeed {limit - len(all_samples)} more samples...")
            possible_subreddits = [company, company.lower(), company.replace(' ', '')]

            for sub in possible_subreddits:
                sub_samples = scrape_official_subreddit(reddit, sub, limit - len(all_samples))
                if sub_samples:
                    for sample in sub_samples:
                        if not any(s['url'] == sample['url'] for s in all_samples):
                            all_samples.append(sample)

                    sources_used.append(f"r/{sub}")
                    print(f"✓ Total so far: {len(all_samples)}")
                    break

        # Fallback
        if len(all_samples) < limit:
            print(f"\nStill need {limit - len(all_samples)} more, using fallback...")
            fallback_samples = scrape_fallback(reddit, company, limit - len(all_samples))

            for sample in fallback_samples:
                if not any(s['url'] == sample['url'] for s in all_samples):
                    all_samples.append(sample)

            sources_used.append("fallback")
            print(f"✓ Total so far: {len(all_samples)}")

        # Sort by date
        all_samples.sort(key=lambda x: x['date'], reverse=True)
        final_samples = all_samples[:limit]

        result = {
            'source': 'reddit',
            'company': company,
            'scraped_at': datetime.now().isoformat(),
            'total_samples': len(final_samples),
            'samples': final_samples,
            'sources_used': sources_used,
            'target': limit,
            'success': len(final_samples) >= limit
        }

        print(f"\n{'='*50}")
        print(f"✓ COMPLETE: {len(final_samples)}/{limit} samples")
        print(f"Sources: {', '.join(sources_used)}")
        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            'error': str(e),
            'source': 'reddit',
            'total_samples': 0,
            'samples': [],
            'success': False
        }


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


def classify_topic(title, text):
    """Classify what type of topic this is"""
    content = f"{title} {text}".lower()

    if any(word in content for word in ['why', 'how', 'what', 'when', 'where', '?']):
        return 'question'
    elif any(word in content for word in ['problem', 'issue', 'broken', 'not working', 'disappointed', 'terrible']):
        return 'complaint'
    elif any(word in content for word in ['amazing', 'love', 'excited', 'great', 'awesome', 'incredible']):
        return 'excitement'
    elif any(word in content for word in ['announce', 'release', 'launch', 'new']):
        return 'news'
    else:
        return 'discussion'


def scrape_reddit_trends(company, limit=20, credentials=None):
    """
    Scrape trending topics about a company from Reddit

    Args:
        company: Company name
        limit: Number of trending topics to find
        credentials: Dict with reddit_client_id, reddit_client_secret, reddit_user_agent

    Returns:
        Dict with trending topics
    """
    try:
        print(f"\n{'='*50}")
        print(f"REDDIT TRENDS SCRAPER: {company}")
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

        # Get credentials
        if credentials:
            client_id = credentials.get('reddit_client_id')
            client_secret = credentials.get('reddit_client_secret')
            user_agent = credentials.get('reddit_user_agent', 'brand_voice_scraper/1.0')
        else:
            client_id = os.environ.get('REDDIT_CLIENT_ID')
            client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
            user_agent = os.environ.get('REDDIT_USER_AGENT', 'brand_voice_scraper/1.0')

        if not client_id or not client_secret:
            raise ValueError("Missing Reddit API credentials")

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        trending_topics = []
        subreddits_to_check = ['technology', 'tech', 'gadgets', 'business', 'news']

        # Add company-specific subreddit if it's a well-known company
        if company.lower() in ['apple', 'google', 'microsoft', 'tesla', 'amazon']:
            subreddits_to_check.insert(0, company.lower())

        # Expand subreddit search based on main topics from brand voice
        if main_topics:
            topic_to_subreddit = {
                'game': ['gaming', 'gamedev'],
                'gaming': ['gaming', 'gamedev'],
                'game development': ['gamedev', 'Unity3D'],
                'game engine': ['gamedev', 'Unity3D'],
                '3d': ['computergraphics', 'gamedev'],
                'mobile': ['android', 'iphone'],
                'ai': ['MachineLearning', 'artificial'],
                'machine learning': ['MachineLearning'],
                'cloud': ['aws', 'cloud'],
                'software': ['programming', 'coding'],
                'electric vehicle': ['electricvehicles', 'cars'],
                'automotive': ['cars', 'electricvehicles']
            }

            for topic in main_topics:
                topic_lower = topic.lower()
                for keyword, subs in topic_to_subreddit.items():
                    if keyword in topic_lower:
                        for sub in subs:
                            if sub not in subreddits_to_check:
                                subreddits_to_check.insert(0, sub)

        print(f"Searching in: {', '.join(subreddits_to_check[:10])}" +
              (f" (+{len(subreddits_to_check)-10} more)" if len(subreddits_to_check) > 10 else "") + "\n")

        for subreddit_name in subreddits_to_check:
            if len(trending_topics) >= limit:
                break

            try:
                subreddit = reddit.subreddit(subreddit_name)
                print(f"Checking r/{subreddit_name}...")

                for post in subreddit.hot(limit=30):
                    if len(trending_topics) >= limit:
                        break

                    # Use word boundary matching to avoid matching substrings
                    # e.g., "Unity" should not match "community" or "opportunity"
                    pattern = r'\b' + re.escape(company) + r'\b'
                    title_match = re.search(pattern, post.title, re.IGNORECASE)
                    text_match = re.search(pattern, post.selftext if post.selftext else "", re.IGNORECASE)

                    is_relevant = bool(title_match or text_match)

                    # If we have main topics from brand voice, also check if post mentions any of them
                    # This helps find relevant discussions even if company name isn't mentioned
                    if not is_relevant and main_topics:
                        post_content = f"{post.title} {post.selftext if post.selftext else ''}".lower()
                        for topic in main_topics:
                            # Check if topic appears in the post
                            topic_pattern = r'\b' + re.escape(topic.lower()) + r'\b'
                            if re.search(topic_pattern, post_content):
                                is_relevant = True
                                break

                    if is_relevant:
                        topic_type = classify_topic(post.title, post.selftext)

                        trending_topics.append({
                            'text': f"{post.title}\n\n{post.selftext[:300]}..." if post.selftext else post.title,
                            'source': 'reddit_trends',
                            'date': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'url': f"https://reddit.com{post.permalink}",
                            'metadata': {
                                'platform_type': 'social',
                                'source_type': 'community_discussion',
                                'subreddit': subreddit_name,
                                'trend_type': 'hot',
                                'topic_type': topic_type,
                                'engagement': post.score,
                                'num_comments': post.num_comments
                            }
                        })

                        time.sleep(0.1)

            except Exception as e:
                print(f"  Skipping r/{subreddit_name}: {e}")
                continue

        print(f"\n✓ Found {len(trending_topics)} trending topics")
        if main_topics:
            print(f"  (Using brand voice topics for enhanced matching)")

        result = {
            'source': 'reddit_trends',
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
        return {
            'error': str(e),
            'source': 'reddit_trends',
            'total_samples': 0,
            'samples': [],
            'success': False
        }
