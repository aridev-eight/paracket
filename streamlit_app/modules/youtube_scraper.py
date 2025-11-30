"""
YouTube Scraper Module
Refactored from youtube_scraper_api.py for Streamlit integration
"""
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
import os
import time


def find_official_channel(company, youtube_api_key):
    """Try to find the company's official YouTube channel"""

    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    search_queries = [
        f"{company} official",
        company,
        f"{company} channel"
    ]

    for query in search_queries:
        try:
            search_response = youtube.search().list(
                q=query,
                part='snippet',
                type='channel',
                maxResults=5
            ).execute()

            for item in search_response.get('items', []):
                channel_id = item['id']['channelId']
                channel_title = item['snippet']['title']

                if company.lower() in channel_title.lower():
                    print(f"✓ Found potential official channel: {channel_title} ({channel_id})")
                    return channel_id, channel_title

        except Exception as e:
            print(f"Error searching for {query}: {e}")
            continue

    return None, None


def get_video_transcript(video_id):
    """Get video transcript - returns None if not available"""
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)
        text = ' '.join([snippet.text for snippet in transcript_data])
        print(f"    ✓ Got transcript ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"    ⚠ No transcript (will use title+description)")
        return None


def scrape_youtube_channel(channel_id, channel_name, limit, youtube_api_key):
    """Scrape videos from a YouTube channel"""
    samples = []
    next_page_token = None
    videos_checked = 0

    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    try:
        print(f"Scraping videos from: {channel_name}")

        # Get the channel's "uploads" playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if not channel_response.get('items'):
            print(f"Error: Channel {channel_id} not found")
            return []

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print(f"Found uploads playlist: {uploads_playlist_id}")

        while len(samples) < limit:
            request_params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': 50
            }

            if next_page_token:
                request_params['pageToken'] = next_page_token

            response = youtube.playlistItems().list(**request_params).execute()

            videos = response.get('items', [])

            if not videos:
                print("  No more videos found")
                break

            print(f"  Processing batch of {len(videos)} videos...")

            for video in videos:
                if len(samples) >= limit:
                    break

                videos_checked += 1

                video_id = video['snippet']['resourceId']['videoId']
                title = video['snippet']['title']
                description = video['snippet']['description']
                published_at = video['snippet']['publishedAt']

                print(f"  [{videos_checked}] {title[:60]}...")

                # Try to get transcript
                transcript = get_video_transcript(video_id)

                # Build sample text
                text_parts = [f"Title: {title}"]

                if description:
                    text_parts.append(f"Description: {description}")

                if transcript:
                    text_parts.append(f"Transcript: {transcript}")

                full_text = "\n\n".join(text_parts)

                if len(full_text) < 30:
                    print(f"      Skipped (no content)")
                    continue

                sample = {
                    'text': full_text,
                    'source': 'youtube',
                    'date': published_at,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'metadata': {
                        'platform_type': 'video',
                        'channel_name': channel_name,
                        'video_id': video_id,
                        'title': title,
                        'has_transcript': transcript is not None,
                        'transcript_length': len(transcript) if transcript else 0,
                        'source_type': 'official_channel'
                    }
                }

                samples.append(sample)
                print(f"      ✓ Added ({len(samples)}/{limit})")

                time.sleep(0.2)

            # Get next page token
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                print("  No more pages available")
                break

        # Count stats
        with_transcripts = sum(1 for s in samples if s['metadata']['has_transcript'])
        without_transcripts = len(samples) - with_transcripts

        print(f"\n  Checked {videos_checked} videos")
        print(f"  Collected {len(samples)} total samples:")
        print(f"    - {with_transcripts} with transcripts")
        print(f"    - {without_transcripts} without transcripts (title+description only)")

        return samples

    except Exception as e:
        print(f"Error scraping channel: {e}")
        import traceback
        traceback.print_exc()
        return samples


def find_youtube_channel(company, youtube_api_key=None):
    """
    Find YouTube channel ID for a company

    Args:
        company: Company name
        youtube_api_key: YouTube API key

    Returns:
        Dict with found, channel_id, channel_name, company
    """
    try:
        print(f"\n{'='*50}")
        print(f"FINDING YOUTUBE CHANNEL: {company}")
        print(f"{'='*50}\n")

        if not youtube_api_key:
            youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        if not youtube_api_key:
            raise ValueError("Missing YouTube API key")

        # Try to find channel
        channel_id, channel_name = find_official_channel(company, youtube_api_key)

        if channel_id:
            result = {
                'found': True,
                'channel_id': channel_id,
                'channel_name': channel_name,
                'company': company
            }
            print(f"✓ Found: {channel_name} ({channel_id})\n")
        else:
            result = {
                'found': False,
                'channel_id': None,
                'channel_name': None,
                'company': company,
                'message': f'Could not find YouTube channel for {company}'
            }
            print(f"✗ Not found\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            'error': str(e),
            'found': False
        }


def scrape_youtube(company, channel_id, limit=150, youtube_api_key=None):
    """
    Scrape YouTube channel

    Args:
        company: Company name
        channel_id: YouTube channel ID (required)
        limit: Number of samples to collect
        youtube_api_key: YouTube API key

    Returns:
        Dict with source, company, samples, etc.
    """
    try:
        print(f"\n{'='*50}")
        print(f"YOUTUBE SCRAPER: {company} (target: {limit} samples)")
        print(f"{'='*50}\n")

        if not youtube_api_key:
            youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        if not youtube_api_key:
            raise ValueError("Missing YouTube API key")

        if not channel_id:
            return {
                'error': 'channel_id is required',
                'company': company,
                'success': False
            }

        youtube = build('youtube', 'v3', developerKey=youtube_api_key)

        # Get channel name from ID
        try:
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel_id
            ).execute()

            if not channel_response.get('items'):
                return {
                    'error': f'Invalid channel_id: {channel_id}',
                    'company': company,
                    'success': False
                }

            channel_name = channel_response['items'][0]['snippet']['title']
        except Exception as e:
            return {
                'error': f'Could not verify channel_id: {str(e)}',
                'company': company,
                'success': False
            }

        print(f"Using channel: {channel_name} ({channel_id})\n")

        # Scrape videos
        samples = scrape_youtube_channel(channel_id, channel_name, limit, youtube_api_key)

        result = {
            'source': 'youtube',
            'company': company,
            'channel_name': channel_name,
            'channel_id': channel_id,
            'scraped_at': datetime.now().isoformat(),
            'total_samples': len(samples),
            'samples': samples,
            'target': limit,
            'success': len(samples) >= limit,
            'note': 'Includes videos with and without transcripts'
        }

        print(f"\n{'='*50}")
        print(f"✓ COMPLETE: {len(samples)}/{limit} samples")
        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'source': 'youtube',
            'total_samples': 0,
            'samples': [],
            'success': False
        }
