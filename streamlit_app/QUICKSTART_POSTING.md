# Quick Start: Automated Posting

## ✅ What's Been Set Up

Your Madison AI app now has **complete automated posting** capabilities!

### New Files Created:
1. **`modules/social_poster.py`** - Posts to Twitter, Reddit, Mastodon
2. **`scheduler.py`** - Background scheduler script
3. **`test_scheduler.py`** - Test script to verify setup
4. **`pages/4_📅_Scheduled_Posts.py`** - Manage scheduled posts
5. **`SCHEDULER_SETUP.md`** - Detailed setup instructions

### New Libraries Installed:
- `tweepy` - Twitter/X API client
- `Mastodon.py` - Mastodon API client
- `praw` - Reddit API client (already installed)

## 🚀 Quick Start (3 Steps)

### Step 1: Test the Scheduler (No API Keys Needed)

```bash
cd /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app

# Create a test post
python3 test_scheduler.py

# Wait 1 minute, then run scheduler
python3 scheduler.py
```

This tests the scheduler logic without actually posting.

### Step 2: Set Up Social Media API Credentials

Get API credentials from:
- **Twitter:** https://developer.twitter.com/en/portal/dashboard
- **Reddit:** https://www.reddit.com/prefs/apps
- **Mastodon:** Your instance → Preferences → Development

Add them to `.streamlit/secrets.toml`:

```toml
# Twitter/X
TWITTER_API_KEY = "your_api_key"
TWITTER_API_SECRET = "your_api_secret"
TWITTER_ACCESS_TOKEN = "your_access_token"
TWITTER_ACCESS_SECRET = "your_access_secret"

# Reddit
REDDIT_CLIENT_ID = "your_client_id"
REDDIT_CLIENT_SECRET = "your_client_secret"
REDDIT_USERNAME = "your_username"
REDDIT_PASSWORD = "your_password"

# Mastodon
MASTODON_INSTANCE = "https://mastodon.social"
MASTODON_ACCESS_TOKEN = "your_access_token"
```

### Step 3: Set Up Automation (Choose One)

**Option A: Cron (Recommended for Mac/Linux)**

```bash
# Edit crontab
crontab -e

# Add this line (posts are checked every 5 minutes):
*/5 * * * * cd /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app && /usr/bin/python3 scheduler.py >> logs/scheduler.log 2>&1

# Create logs directory
mkdir -p logs
```

**Option B: Run Manually When Needed**

```bash
python3 scheduler.py
```

## 📝 How to Use

### 1. Create Content in Streamlit App

1. **Brand Analysis** → Analyze brand voice
2. **Trending Topics** → Find topics
3. **Generate Post Ideas** → Get 3-5 ideas
4. **Select & Edit** → Pick one, edit the master message
5. **Adapt to Platforms** → Generate Twitter/Reddit/Mastodon versions
6. **Finalize & Schedule** → Set date/time, select platforms

### 2. Monitor in Scheduled Posts Page

- View all scheduled posts
- Edit schedules or content
- Activate/deactivate posts
- See posting results

### 3. Scheduler Does the Rest

Every 5 minutes (or your interval):
- Checks for posts due to publish
- Posts to selected platforms
- Updates status (posted/failed)
- Logs results

## 📊 Workflow Example

```
9:00 AM - Create post, schedule for 2:00 PM
2:00 PM - Scheduler runs, posts to platforms
2:01 PM - Status updated to "posted"
```

View results in **Scheduled Posts** page:
- ✅ Posted to Twitter: https://twitter.com/...
- ✅ Posted to Reddit: https://reddit.com/r/...
- ✅ Posted to Mastodon: https://mastodon.social/@.../...

## 🔍 Monitoring

**View scheduler logs:**
```bash
tail -f logs/scheduler.log
```

**Check post status:**
- Go to Scheduled Posts page in Streamlit app
- Green 🟢 = active
- Green ✅ = successfully posted
- Red 🔴 = failed or past due

## 🛠️ Troubleshooting

**Posts not publishing?**
1. Check scheduler is running: `crontab -l`
2. Check logs: `tail -f logs/scheduler.log`
3. Test manually: `python3 scheduler.py`
4. Verify post is "active" in Scheduled Posts page

**API errors?**
- Twitter: Check "Read and Write" permissions
- Reddit: Verify username/password
- Mastodon: Check instance URL and token

## 📚 More Info

- **Full setup guide:** See `SCHEDULER_SETUP.md`
- **API documentation:**
  - Twitter: https://developer.twitter.com/en/docs/twitter-api
  - Reddit: https://www.reddit.com/dev/api
  - Mastodon: https://docs.joinmastodon.org/client/intro/

## 🎉 You're All Set!

Your Madison AI app can now:
✅ Analyze brand voice
✅ Find trending topics
✅ Generate AI posts
✅ Edit and refine content
✅ Schedule for future posting
✅ Automatically post to Twitter, Reddit, Mastodon
✅ Track and manage all scheduled posts

Happy posting! 🚀
