# 🎯 Madison AI - Automated Brand Voice Marketing System

An AI-powered marketing automation system that analyzes brand voice from multiple sources and generates authentic social media content.

## 🌟 Features

- **Multi-Source Brand Voice Analysis**: Scrapes and analyzes content from Reddit, YouTube, and company blogs
- **GPT-4o Powered**: Uses advanced AI to understand tone, personality, and writing style
- **Trend Monitoring**: Tracks trending topics on Reddit to identify content opportunities
- **Multi-Platform Content Generation**: Creates platform-optimized posts for Twitter/X, Reddit, and Mastodon
- **Authentic Voice Matching**: Generates content that maintains brand consistency across all platforms

## 📋 Prerequisites

Before you begin, you'll need:

1. **Python 3.8+** installed on your system
2. **API Keys** for:
   - Reddit API (client ID and secret)
   - YouTube Data API v3
   - OpenAI API (GPT-4o access)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd streamlit_app

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the secrets template and add your API keys:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your credentials:

```toml
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "brand_voice_scraper/1.0"

YOUTUBE_API_KEY = "your_youtube_api_key"

OPENAI_API_KEY = "your_openai_api_key"
```

### 3. Run Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔑 Getting API Keys

### Reddit API

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the required fields
5. Copy the client ID (under the app name) and client secret

### YouTube Data API

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Go to Credentials → Create Credentials → API Key
5. Copy the API key

### OpenAI API

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (you won't be able to see it again!)
4. Ensure you have access to GPT-4o model

## ☁️ Deploy to Streamlit Cloud (FREE)

### Step 1: Prepare Your Repository

1. Create a GitHub account if you don't have one
2. Create a new repository
3. Push the `streamlit_app` directory to your repository:

```bash
cd streamlit_app
git init
git add .
git commit -m "Initial commit: Madison AI Streamlit app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch (main), and main file (`app.py`)
5. Click "Advanced settings"
6. Add your API keys in the "Secrets" section:

```toml
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "brand_voice_scraper/1.0"
YOUTUBE_API_KEY = "your_youtube_api_key"
OPENAI_API_KEY = "your_openai_api_key"
```

7. Click "Deploy"
8. Wait 2-3 minutes for deployment
9. Your app will be live at `https://YOUR_APP_NAME.streamlit.app`

## 📁 Project Structure

```
streamlit_app/
├── app.py                          # Main entry point (Home page)
├── pages/
│   ├── 1_📊_Brand_Analysis.py      # Brand voice analysis page
│   ├── 2_✨_Content_Generator.py   # Content generation page
│   └── 3_📁_History.py             # View past analyses
├── modules/
│   ├── reddit_scraper.py           # Reddit scraping logic
│   ├── youtube_scraper.py          # YouTube scraping logic
│   ├── blog_scraper.py             # Blog scraping logic
│   └── brand_voice_analyzer.py     # GPT-4o analysis & generation
├── data/                           # Saved brand voice profiles (gitignored)
├── .streamlit/
│   └── secrets.toml.template       # API keys template
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🎯 How to Use

### 1. Home Page
- Enter company name, YouTube channel ID (optional), and domain (optional)
- Save settings and navigate to Brand Analysis

### 2. Brand Analysis
- **Data Collection Tab**:
  - Select data sources (Reddit, YouTube, Blog)
  - Click "Start Data Collection"
  - Wait for scraping to complete
- **Voice Analysis Tab**:
  - Click "Analyze Brand Voice"
  - Wait for GPT-4o to analyze the data
- **Results Tab**:
  - View comprehensive brand voice profile
  - Download results as JSON or TXT

### 3. Content Generator
- **Trending Topics Tab**:
  - Click "Find Trending Topics"
  - Select a trending topic
- **Generate Content Tab**:
  - Choose platforms (Twitter, Mastodon, Reddit)
  - Click "Generate Content"
  - Review, download, or copy generated posts

### 4. History
- View all past brand voice analyses
- Load previous analyses
- Download or delete old profiles

## 🛠️ Troubleshooting

### "Missing API credentials" error
- Make sure you've created `.streamlit/secrets.toml`
- Verify all required API keys are present
- Check that there are no extra quotes or spaces

### Reddit scraping fails
- Verify your Reddit credentials are correct
- Ensure your Reddit app type is "script"
- Check that you're not rate-limited

### YouTube scraping fails
- Verify the YouTube API is enabled in your Google Cloud project
- Check that your API key has permission to use YouTube Data API v3
- Ensure you haven't exceeded your daily quota

### OpenAI analysis fails
- Verify your OpenAI API key is valid
- Ensure you have access to GPT-4o model
- Check that you have sufficient API credits

## 💡 Tips for Best Results

1. **Company Selection**: Works best with companies that have:
   - Active Reddit presence (official accounts or subreddits)
   - YouTube channel with videos
   - Company blog with RSS feed

2. **Sample Size**: Collect at least 100-150 samples per source for accurate analysis

3. **Trending Topics**: Use non-controversial, relevant topics for better content generation

4. **Content Review**: Always review generated content before posting to ensure accuracy

## 📊 Cost Estimate

**Free Tiers:**
- Streamlit Cloud: Free hosting
- Reddit API: Free
- YouTube Data API: 10,000 quota units/day (free)

**Paid Services:**
- OpenAI API: ~$0.01-0.05 per analysis + generation
  - Brand Voice Analysis: ~$0.02 (uses GPT-4o)
  - Content Generation: ~$0.01 per platform

**Typical Usage:**
- One complete workflow (scrape + analyze + generate for 3 platforms): ~$0.04-0.08

## 🔐 Security Notes

- **Never commit `.streamlit/secrets.toml` to version control**
- Add `.streamlit/secrets.toml` to your `.gitignore`
- Rotate API keys if accidentally exposed
- Use environment-specific secrets for production

## 📝 License

This project was created as part of INFO7375 Assignment 9 at Northeastern University.

## 🤝 Contributing

This is an educational project. Feel free to fork and modify for your own learning purposes.

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review API provider documentation
3. Check Streamlit Community forums

---

Built with ❤️ using Streamlit, OpenAI GPT-4o, and modern web scraping tools.
