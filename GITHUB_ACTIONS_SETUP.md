# GitHub Actions Scheduler Setup for Paracket

## How It Works

```
┌──────────────────┐
│  Streamlit App   │ ← User creates scheduled posts
│  (Cloud hosted)  │
└────────┬─────────┘
         │ saves to
         ▼
┌──────────────────┐
│  GitHub Repo     │ ← Stores scheduled posts as JSON files
│ data/scheduled_  │
│     posts/       │
└────────┬─────────┘
         │ runs every 5 min
         ▼
┌──────────────────┐
│ GitHub Actions   │ ← Checks for posts that are due
│   (Scheduler)    │
└────────┬─────────┘
         │ posts to
         ▼
┌──────────────────┐
│ Social  Media    │ ← Twitter, Reddit, Mastodon
│   Platforms      │
└────────┬─────────┘
         │ updates status
         ▼
┌──────────────────┐
│  GitHub Repo     │ ← Status updated (posted/failed)
│  (committed)     │
└────────┬─────────┘
         │ reflected in
         ▼
┌──────────────────┐
│  Streamlit App   │ ← User sees updated status
│   (refreshed)    │
└──────────────────┘
```

## Setup Steps

### 1. Push Your Code to GitHub

```bash
cd /Users/arundhati/Desktop/n8n-asgn-4
git init
git add .
git commit -m "Initial commit - Paracket application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/paracket.git
git push -u origin main
```

### 2. Add GitHub Secrets

Go to your GitHub repository:
- Click **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**

Add these secrets one by one:

#### Twitter/X API (required for Twitter posting)
- `TWITTER_API_KEY` - Your Twitter API key
- `TWITTER_API_SECRET` - Your Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Your Twitter access token
- `TWITTER_ACCESS_SECRET` - Your Twitter access token secret

#### Reddit API (required for Reddit posting)
- `REDDIT_CLIENT_ID` - Your Reddit client ID
- `REDDIT_CLIENT_SECRET` - Your Reddit client secret
- `REDDIT_USERNAME` - Your Reddit username
- `REDDIT_PASSWORD` - Your Reddit password

#### Mastodon API (required for Mastodon posting)
- `MASTODON_INSTANCE` - Your Mastodon instance URL (e.g., https://mastodon.social)
- `MASTODON_ACCESS_TOKEN` - Your Mastodon access token

### 3. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see "Paracket Social Media Scheduler" workflow
4. If GitHub Actions are disabled, click "I understand my workflows, go ahead and enable them"

### 4. Test the Workflow

#### Manual Trigger (Recommended for first test):
1. Go to **Actions** tab
2. Click "Paracket Social Media Scheduler"
3. Click "Run workflow" dropdown
4. Click the green "Run workflow" button

This will run immediately so you can see if everything works.

#### Wait for Automatic Run:
The workflow runs every 5 minutes automatically.

### 5. Monitor Workflow Runs

1. Go to **Actions** tab
2. Click on any workflow run to see details
3. Click on the "post-scheduled-content" job
4. Expand each step to see logs

### 6. Commit Scheduled Posts

**Important:** For the scheduler to work, scheduled post files must be in the repo.

After creating a scheduled post in Streamlit:

```bash
cd /Users/arundhati/Desktop/n8n-asgn-4
git add streamlit_app/data/scheduled_posts/
git commit -m "Add scheduled post"
git push
```

Or set up automatic syncing (see below).

## Integration with Streamlit Cloud

### Workflow:

1. **Deploy Streamlit app to Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Connect your GitHub repo
   - Deploy the app

2. **Create posts in Streamlit UI**
   - User fills out form
   - Saves to `data/scheduled_posts/scheduled_TIMESTAMP.json`

3. **Commit posts to GitHub**
   - Either manually: `git add . && git commit && git push`
   - Or: Use Streamlit's git integration (if available)
   - Or: Download and commit locally

4. **GitHub Actions runs every 5 minutes**
   - Reads files from `streamlit_app/data/scheduled_posts/`
   - Posts any that are due
   - Updates JSON files with status
   - Commits changes back

5. **Streamlit app shows updated status**
   - Next time user opens "Scheduled Posts" page
   - Reads updated JSON files from repo
   - Shows "posted" or "failed" status

## File Sync Options

### Option A: Manual Commit (Simplest)

After creating posts in Streamlit, commit manually:

```bash
git pull  # Get any updates
git add streamlit_app/data/scheduled_posts/
git commit -m "Add new scheduled posts"
git push
```

### Option B: Automatic Sync Script

Create a script that runs periodically to sync:

```bash
#!/bin/bash
# sync-posts.sh
cd /path/to/repo
git pull
# Your scheduled posts are created here
git add streamlit_app/data/scheduled_posts/
if ! git diff --staged --quiet; then
  git commit -m "Sync scheduled posts [automated]"
  git push
fi
```

### Option C: Use Streamlit File Upload

Add a feature to download scheduled posts as JSON, then upload them back when needed.

## Troubleshooting

### Workflow fails with "No scheduled posts found"
- Make sure `data/scheduled_posts/` directory exists in repo
- Make sure JSON files are committed to GitHub
- Check workflow logs to see which path it's checking

### "Invalid credentials" error
- Double-check your GitHub Secrets
- Make sure secret names match exactly (case-sensitive)
- Ensure credentials are valid for each platform

### Posts not getting updated in Streamlit
- Streamlit Cloud caches the repo
- May need to restart the app or wait for cache to refresh
- Try redeploying the Streamlit app

### Workflow doesn't run automatically
- Check if GitHub Actions is enabled for your repo
- Cron jobs in GitHub Actions can have up to 10-minute delays
- Free tier has usage limits (2,000 minutes/month)

## Limitations

- **5-minute minimum interval**: GitHub Actions cron cannot run more frequently
- **2,000 free minutes/month**: Should be plenty for a 5-minute cron (8,640 runs/month)
- **File-based storage**: Posts are stored as files, not in a database
- **Eventual consistency**: Small delay between posting and status update in Streamlit

## Alternative: Database Approach

For a more robust solution:

1. Use a database (Supabase, MongoDB Atlas - both have free tiers)
2. Streamlit app writes scheduled posts to database
3. GitHub Actions reads from database
4. Updates status in database
5. Streamlit app reads from database

This eliminates the need to commit files, but adds complexity.

## Cost

**GitHub Actions**: Free for public repos, 2,000 minutes/month for private repos
**Streamlit Cloud**: Free tier available
**Total**: $0 for this setup!

## Questions?

Check the GitHub Actions logs for detailed information about what's happening during each run.
