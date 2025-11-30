# 🚀 Quick Start Guide

## Test the App Locally (5 minutes)

### 1. Install Dependencies

```bash
cd streamlit_app
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### 3. Test the Workflow

**Home Page:**
- Enter a company name (try "Unity", "Apple", or "Notion")
- (Optional) Add YouTube channel ID if you know it
- (Optional) Add domain (e.g., "unity.com")
- Click "Save & Continue to Analysis"

**Brand Analysis Page:**
1. Go to "Data Collection" tab
2. Keep all three sources checked (Reddit, YouTube, Blog)
3. Click "Start Data Collection" (takes 2-5 minutes)
4. Go to "Voice Analysis" tab
5. Click "Analyze Brand Voice" (takes 30-60 seconds)
6. Go to "Results" tab to see the analysis

**Content Generator Page:**
1. Go to "Trending Topics" tab
2. Click "Find Trending Topics"
3. Go to "Generate Content" tab
4. Select a trending topic
5. Choose platforms
6. Click "Generate Content"
7. Review and download the generated posts

## 🐛 Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`, make sure you're in the right directory:

```bash
cd streamlit_app
pip install -r requirements.txt
```

### API Key Errors

Your API keys are already configured in `.streamlit/secrets.toml` from your existing `.env` file.

If you need to update them:
1. Edit `.streamlit/secrets.toml`
2. Update the relevant API keys
3. Restart the Streamlit app

### No Module Named 'modules'

Make sure you're running the app from the `streamlit_app` directory:

```bash
cd streamlit_app
streamlit run app.py
```

## 📊 Expected Results

**Data Collection:**
- Reddit: 100-150 samples
- YouTube: 50-150 samples (depends on channel activity)
- Blog: 10-100 samples (depends on blog activity)

**Voice Analysis:**
- Generates a comprehensive profile with:
  - Tone, personality traits, formality level
  - Vocabulary level, sentence style
  - Main topics, core values
  - Common phrases, writing guidelines

**Content Generation:**
- Creates platform-specific posts:
  - Twitter: ~200-280 characters
  - Mastodon: ~300-500 characters
  - Reddit: Title + 2-4 paragraph body

## ⚡ Quick Tips

1. **First Test**: Try "Unity" - they have good Reddit, YouTube, and blog presence
2. **Faster Testing**: Reduce sample limits to 50 for quicker scraping
3. **Best Results**: Use companies with active social media presence
4. **Save Time**: Analysis results are saved in the History page

## 🚀 Next Steps

Once you've tested locally and it works:

1. Review the full README.md for deployment instructions
2. Push to GitHub
3. Deploy to Streamlit Cloud (free!)
4. Add the live URL to your portfolio

## 🎯 Demo for Assignment

For your assignment demo, you can:

1. **Option A - Video Recording**:
   - Screen record the entire workflow
   - Show: Home → Data Collection → Analysis → Content Generation
   - Duration: 2-3 minutes (can skip waiting times in editing)

2. **Option B - Live Demo Script**:
   - Prepare a company with pre-collected data
   - Show the analysis results
   - Generate content live
   - Duration: 2 minutes

Need help? Check the full README.md for detailed troubleshooting!
