# 🚀 Deployment Checklist for Streamlit Cloud

## Pre-Deployment Checklist

- [ ] App runs successfully locally (`streamlit run app.py`)
- [ ] All features tested and working
- [ ] API keys are in `.streamlit/secrets.toml` (not `.env`)
- [ ] `.gitignore` includes `.streamlit/secrets.toml`
- [ ] README.md is complete and helpful

## Step 1: Prepare GitHub Repository

### Create New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `madison-ai-streamlit` (or your choice)
3. Description: "AI-powered brand voice marketing automation system"
4. Select "Public" (required for free Streamlit Cloud)
5. Do NOT initialize with README (we have one)
6. Click "Create repository"

### Push Code to GitHub

```bash
cd streamlit_app

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Madison AI Streamlit app"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/madison-ai-streamlit.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Streamlit Cloud

### Sign Up / Sign In

1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Authorize Streamlit Cloud to access your repositories

### Create New App

1. Click "New app" button
2. Fill in the deployment form:
   - **Repository**: Select your `madison-ai-streamlit` repo
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `madison-ai-yourname`)

### Add Secrets

1. Click "Advanced settings"
2. In the "Secrets" section, paste your API keys:

```toml
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "brand_voice_scraper/1.0"
YOUTUBE_API_KEY = "your_youtube_api_key"
OPENAI_API_KEY = "your_openai_api_key"
MASTODON_INSTANCE = "https://mastodon.social"
MASTODON_ACCESS_TOKEN = "your_mastodon_access_token"
```

**IMPORTANT**: Replace these placeholders with your actual API keys. Keep them secure!

3. Click "Deploy"

### Wait for Deployment

- Initial deployment takes 2-5 minutes
- Watch the deployment logs for any errors
- Once complete, your app will be live!

## Step 3: Test Deployed App

1. Visit your app URL: `https://your-app-name.streamlit.app`
2. Test the complete workflow:
   - Enter a company name
   - Run data collection
   - Analyze brand voice
   - Generate content
3. Verify all features work as expected

## Step 4: Add to Your Portfolio

### For Your Assignment Submission

**Live Demo URL:**
```
https://your-app-name.streamlit.app
```

**GitHub Repository:**
```
https://github.com/YOUR_USERNAME/madison-ai-streamlit
```

### Portfolio Integration

Add to your portfolio website:

```html
<div class="project">
  <h3>Madison AI - Brand Voice Marketing System</h3>
  <p>AI-powered tool that analyzes brand voice and generates authentic social media content</p>
  <ul>
    <li>Scrapes data from Reddit, YouTube, and blogs</li>
    <li>GPT-4o powered brand voice analysis</li>
    <li>Multi-platform content generation</li>
  </ul>
  <a href="https://your-app-name.streamlit.app">Live Demo</a>
  <a href="https://github.com/YOUR_USERNAME/madison-ai-streamlit">View Code</a>
</div>
```

### Create Case Study

Use this outline for your case study (Assignment Part 2):

**Title:** "Madison AI: Automated Brand Voice Marketing System"

**Problem:**
- Companies struggle to maintain consistent brand voice
- Manual content creation is time-consuming
- Hard to keep up with trends

**Solution:**
- Multi-source brand voice analysis
- AI-powered content generation
- Trend monitoring and opportunity identification

**Technical Implementation:**
- Python backend with Reddit, YouTube, Blog scrapers
- GPT-4o for voice analysis and content generation
- Streamlit for user-friendly interface
- Deployed on Streamlit Cloud

**Results:**
- Reduces content creation time from hours to minutes
- Maintains brand voice consistency across platforms
- Trend-aware content generation

**Screenshots:**
- Home page
- Brand analysis results
- Generated content examples

**Demo:**
- 2-minute video walkthrough OR
- Detailed demo script

## Troubleshooting Deployment

### Build Failed

**Check requirements.txt:**
- Ensure all packages have version numbers
- No local-only packages

**Check file paths:**
- All imports use relative paths
- No hardcoded absolute paths

### App Crashes on Startup

**Check secrets:**
- Verify all API keys are in Streamlit Cloud secrets
- Format matches `.toml` syntax

**Check logs:**
- Click "Manage app" → "Logs"
- Look for Python errors

### API Errors in Deployed App

**Verify secrets:**
- Go to Streamlit Cloud → Your App → Settings → Secrets
- Make sure all keys are present and correct

**Check quotas:**
- Reddit API: Usually no issues
- YouTube API: 10,000 units/day
- OpenAI API: Check your billing

## Post-Deployment Checklist

- [ ] App is live and accessible
- [ ] All features work in production
- [ ] API keys are secure (in Streamlit secrets, not in code)
- [ ] GitHub repository is public
- [ ] README.md is visible on GitHub
- [ ] Live URL added to portfolio
- [ ] Screenshots captured for case study
- [ ] Demo video recorded OR demo script written

## 🎉 You're Done!

Your Madison AI tool is now:
- ✅ Live on the internet
- ✅ Accessible to anyone via URL
- ✅ Ready for your portfolio
- ✅ Ready for assignment submission

**Share your live URL:**
```
https://your-app-name.streamlit.app
```

Good luck with your assignment! 🚀
