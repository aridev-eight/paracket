# Madison AI Post Scheduler Setup

This guide explains how to set up automated posting for scheduled social media posts.

## Overview

The scheduler (`scheduler.py`) runs as a background process that:
- Checks for posts scheduled to be published
- Posts them to Twitter/X, Reddit, and/or Mastodon at the scheduled time
- Updates post status (posted/failed)
- Logs all activity

## Prerequisites

1. **Install posting libraries:**
```bash
cd streamlit_app
pip3 install tweepy Mastodon.py
```

2. **Get API credentials for each platform you want to use:**

### Twitter/X API
- Go to https://developer.twitter.com/en/portal/dashboard
- Create a new app (or use existing)
- Generate API Keys & Tokens:
  - API Key (Consumer Key)
  - API Secret (Consumer Secret)
  - Access Token
  - Access Token Secret
- Enable "Read and Write" permissions

### Reddit API
- Go to https://www.reddit.com/prefs/apps
- Click "Create App" or "Create Another App"
- Select "script" type
- Note your:
  - Client ID (under app name)
  - Client Secret
  - Your Reddit username & password

### Mastodon API
- Log in to your Mastodon instance
- Go to Preferences → Development → New Application
- Give it a name (e.g., "Madison AI")
- Select scopes: `read`, `write`
- Save and copy the Access Token

## Setup Options

### Option 1: Cron Job (Linux/macOS) - Recommended

Run the scheduler every 5 minutes:

```bash
# Edit your crontab
crontab -e

# Add this line (adjust path to your actual path):
*/5 * * * * cd /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app && /usr/bin/python3 scheduler.py >> logs/scheduler.log 2>&1
```

**Create logs directory:**
```bash
mkdir -p /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app/logs
```

**View logs:**
```bash
tail -f /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app/logs/scheduler.log
```

### Option 2: systemd Timer (Linux)

1. **Create service file** `/etc/systemd/system/madison-scheduler.service`:
```ini
[Unit]
Description=Madison AI Post Scheduler
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/streamlit_app
ExecStart=/usr/bin/python3 /path/to/streamlit_app/scheduler.py
StandardOutput=journal
StandardError=journal
```

2. **Create timer file** `/etc/systemd/system/madison-scheduler.timer`:
```ini
[Unit]
Description=Run Madison AI Scheduler every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=madison-scheduler.service

[Install]
WantedBy=timers.target
```

3. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable madison-scheduler.timer
sudo systemctl start madison-scheduler.timer
```

4. **Check status:**
```bash
sudo systemctl status madison-scheduler.timer
sudo journalctl -u madison-scheduler.service -f
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Madison AI Post Scheduler"
4. Trigger: Daily, repeat every 5 minutes
5. Action: Start a program
   - Program: `python`
   - Arguments: `scheduler.py`
   - Start in: `C:\path\to\streamlit_app`
6. Finish and test

### Option 4: Manual Testing

Run manually to test:
```bash
cd /Users/arundhati/Desktop/n8n-asgn-4/streamlit_app
python3 scheduler.py
```

## How It Works

1. **Every 5 minutes** (or your configured interval), the scheduler runs
2. It **loads all scheduled posts** from `data/scheduled_posts/`
3. For each post with:
   - Status = `active`
   - Scheduled time ≤ current time
4. It **attempts to post** to all enabled platforms:
   - Twitter/X (if credentials provided)
   - Reddit (if credentials provided + subreddit specified)
   - Mastodon (if credentials provided)
5. **Updates post status**:
   - `posted` - Successfully posted to at least one platform
   - `failed` - Failed to post to all platforms
6. **Saves results** including URLs of posted content

## Monitoring

### Check Scheduler Logs
```bash
# If using cron
tail -f logs/scheduler.log

# If using systemd
sudo journalctl -u madison-scheduler.service -f
```

### View Posted Content
After posting, check the scheduled post JSON file:
```json
{
  "status": "posted",
  "posted_results": {
    "platforms": {
      "twitter": {
        "success": true,
        "url": "https://twitter.com/user/status/1234567890",
        "tweet_id": "1234567890"
      },
      "reddit": {
        "success": true,
        "url": "https://reddit.com/r/technology/comments/abc123/...",
        "post_id": "abc123"
      }
    }
  }
}
```

## Troubleshooting

### Posts not being published

1. **Check scheduler is running:**
```bash
# For cron
crontab -l

# For systemd
sudo systemctl status madison-scheduler.timer
```

2. **Check logs for errors:**
```bash
tail -f logs/scheduler.log
```

3. **Verify post status in Streamlit:**
- Go to Scheduled Posts page
- Check if post is "active"
- Verify scheduled time has passed

4. **Test manually:**
```bash
python3 scheduler.py
```

### API Errors

**Twitter:**
- Ensure app has "Read and Write" permissions
- Regenerate tokens if needed
- Check rate limits (300 tweets per 3 hours)

**Reddit:**
- Verify credentials are correct
- Check username/password aren't expired
- Subreddit exists and allows posting

**Mastodon:**
- Verify instance URL is correct (include https://)
- Check access token has write permissions
- Ensure character limit not exceeded (500 chars)

### Permission Errors

```bash
# Make scheduler executable
chmod +x scheduler.py

# Ensure logs directory exists
mkdir -p logs
chmod 755 logs
```

## Best Practices

1. **Start with manual testing** before setting up automation
2. **Monitor logs** for the first few days
3. **Schedule posts at least 10 minutes in the future** to allow time for review
4. **Test with small audiences first** (e.g., test subreddits)
5. **Keep credentials secure** - use environment variables or `.streamlit/secrets.toml`
6. **Have a backup plan** for critical posts

## Security Notes

- Credentials are stored in scheduled post JSON files
- Ensure `data/scheduled_posts/` directory has proper permissions (chmod 700)
- Consider encrypting credentials at rest
- Never commit credentials to version control
- Use `.gitignore` to exclude data directory

## Uninstalling

To stop automatic posting:

**Cron:**
```bash
crontab -e
# Remove or comment out the scheduler line
```

**Systemd:**
```bash
sudo systemctl stop madison-scheduler.timer
sudo systemctl disable madison-scheduler.timer
```

**Windows:**
- Open Task Scheduler
- Find "Madison AI Post Scheduler"
- Right-click → Disable or Delete
