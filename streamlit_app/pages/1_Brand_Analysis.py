"""
Brand Analysis Page
Scrape data from multiple sources and analyze brand voice
Enhanced with AI-powered blog feed discovery
"""
import streamlit as st
import sys
import os
import json
from io import StringIO

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules import reddit_scraper, youtube_scraper, blog_scraper, brand_voice_analyzer, ai_blog_finder

st.set_page_config(
    page_title="Brand Analysis - Paracket",
    page_icon="📊",
    layout="wide"
)

st.title("Brand Voice Analysis")
st.markdown("### Analyze your brand voice from multiple sources")

# Check if company name is set
if not st.session_state.get('company_name'):
    st.warning("Please set a company name on the Home page first!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

company_name = st.session_state.company_name

st.success(f"**Analyzing:** {company_name}")

# Check for existing analyses
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Find existing analyses for this company
company_safe = company_name.replace(' ', '_').replace('/', '_')
existing_analyses = [f for f in os.listdir(data_dir) if f.startswith(f'brand_voice_{company_safe}_') and f.endswith('.json')]

# Show existing analyses if found
if existing_analyses and not st.session_state.get('force_new_analysis'):
    st.info(f"Found existing analysis for **{company_name}**")

    # Sort by modification time (newest first)
    existing_analyses.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)

    st.markdown("### Choose an Option:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Use Existing Analysis")
        st.markdown("Load a previously completed analysis and skip data collection.")

        # Show the most recent analysis
        most_recent = existing_analyses[0]
        try:
            with open(os.path.join(data_dir, most_recent), 'r', encoding='utf-8') as f:
                data = json.load(f)

            analyzed_at = data.get('analyzed_at', '')
            total_samples = data.get('total_samples_analyzed', 0)

            try:
                from datetime import datetime
                dt = datetime.fromisoformat(analyzed_at)
                date_str = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                date_str = analyzed_at

            st.caption(f"Most Recent: {date_str}")
            st.caption(f"Samples: {total_samples}")

            if st.button("Load Existing Analysis", type="primary", use_container_width=True):
                st.session_state.company_name = company_name
                st.session_state.brand_voice = data
                st.success(f"Loaded existing analysis for {company_name}!")
                st.info("You can now proceed to **Content Generator** to create posts!")
                st.balloons()
        except:
            st.caption("Most recent analysis found")
            if st.button("Load Existing Analysis", type="primary", use_container_width=True):
                st.session_state.force_new_analysis = False
                st.rerun()

    with col2:
        st.markdown("#### Create New Analysis")
        st.markdown("Collect fresh data and create a new brand voice analysis.")
        st.caption("This will replace the existing analysis with fresh data.")

        if st.button("Create New Analysis", use_container_width=True):
            st.session_state.force_new_analysis = True
            st.rerun()

    st.markdown("---")
    st.info("**Tip:** You can view all company analyses in the **History** page.")
    st.stop()

# Reset force_new_analysis flag after using it
if st.session_state.get('force_new_analysis'):
    st.session_state.force_new_analysis = False

# Tabs for different stages
tab1, tab2, tab3 = st.tabs(["Data Collection", "Voice Analysis", "Results"])

with tab1:
    st.header("Data Collection")
    st.markdown("Collect brand voice data from YouTube and company blogs. Reddit is optional but requires valid credentials.")

    st.info("**Note:** Brand voice analysis uses YouTube and blog content to understand your communication style. For trending topics, the Content Generator uses Hacker News (no credentials required).")

    # API Keys Section
    with st.expander("API Credentials", expanded=False):
        st.markdown("Enter your API credentials. These will be used for this session only.")

        col1, col2 = st.columns(2)

        with col1:
            reddit_client_id = st.text_input("Reddit Client ID", type="password",
                                             value=st.secrets.get("REDDIT_CLIENT_ID", "") if hasattr(st, 'secrets') else "")
            reddit_client_secret = st.text_input("Reddit Client Secret", type="password",
                                                  value=st.secrets.get("REDDIT_CLIENT_SECRET", "") if hasattr(st, 'secrets') else "")
            reddit_user_agent = st.text_input("Reddit User Agent",
                                               value=st.secrets.get("REDDIT_USER_AGENT", "brand_voice_scraper/1.0") if hasattr(st, 'secrets') else "brand_voice_scraper/1.0")

        with col2:
            youtube_api_key = st.text_input("YouTube API Key", type="password",
                                            value=st.secrets.get("YOUTUBE_API_KEY", "") if hasattr(st, 'secrets') else "")
            openai_api_key = st.text_input("OpenAI API Key", type="password",
                                           value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, 'secrets') else "")

    # Scraping Settings
    st.subheader("Scraping Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        scrape_reddit = st.checkbox("Reddit (Optional)", value=False, help="Scrape from Reddit (user, subreddit, mentions) - requires valid credentials")
        reddit_limit = st.number_input("Reddit samples", min_value=10, max_value=300, value=150, step=10)

    with col2:
        scrape_youtube = st.checkbox("YouTube", value=True, help="Scrape from YouTube channel")
        youtube_limit = st.number_input("YouTube samples", min_value=10, max_value=300, value=150, step=10)
        youtube_channel_id = st.text_input("YouTube Channel ID (optional)",
                                           value=st.session_state.get('youtube_channel_id', ''),
                                           help="Leave empty to auto-detect")

    with col3:
        scrape_blog = st.checkbox("Blog", value=True, help="Scrape from company blog (AI-powered discovery)")
        blog_limit = st.number_input("Blog samples", min_value=10, max_value=300, value=150, step=10)
        use_ai_blog_finder = st.checkbox("Use AI to find blog", value=True, 
                                         help="Let AI automatically find the company blog and RSS feed")
        
        # Only show manual blog URL if AI finder is disabled
        if not use_ai_blog_finder:
            blog_url = st.text_input("Blog URL (optional)",
                                     value=st.session_state.get('blog_url', ''),
                                     placeholder="e.g., https://blog.unity.com",
                                     help="Direct URL to the company blog")
        else:
            blog_url = None

    st.markdown("---")

    # Start Scraping Button
    if st.button("Start Data Collection", type="primary", use_container_width=True):

        # Validate credentials
        if scrape_reddit and (not reddit_client_id or not reddit_client_secret):
            st.error("Reddit credentials are required for Reddit scraping")
            st.stop()

        if scrape_youtube and not youtube_api_key:
            st.error("YouTube API key is required for YouTube scraping")
            st.stop()

        if scrape_blog and use_ai_blog_finder and not openai_api_key:
            st.error("OpenAI API key is required for AI-powered blog discovery")
            st.stop()

        if not scrape_reddit and not scrape_youtube and not scrape_blog:
            st.error("Please select at least one data source")
            st.stop()

        # Initialize results
        results = {}

        # Create progress tracking
        total_tasks = sum([scrape_reddit, scrape_youtube, scrape_blog])
        current_task = 0

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Scrape Reddit
        if scrape_reddit:
            current_task += 1
            status_text.text(f"Scraping Reddit... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)

            with st.spinner("Scraping Reddit..."):
                output_capture = StringIO()
                sys.stdout = output_capture

                reddit_result = reddit_scraper.scrape_reddit(
                    company=company_name,
                    limit=reddit_limit,
                    credentials={
                        'reddit_client_id': reddit_client_id,
                        'reddit_client_secret': reddit_client_secret,
                        'reddit_user_agent': reddit_user_agent
                    }
                )

                sys.stdout = sys.__stdout__

                if reddit_result.get('success'):
                    results['reddit'] = reddit_result
                    st.success(f"Reddit: Collected {reddit_result.get('total_samples', 0)} samples")
                    with st.expander("View Reddit scraping log"):
                        st.text(output_capture.getvalue())
                else:
                    st.error(f"Reddit scraping failed: {reddit_result.get('error')}")

        # Scrape YouTube
        if scrape_youtube:
            current_task += 1
            status_text.text(f"Scraping YouTube... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)

            # Find channel if not provided
            if not youtube_channel_id:
                with st.spinner("Finding YouTube channel..."):
                    output_capture = StringIO()
                    sys.stdout = output_capture

                    find_result = youtube_scraper.find_youtube_channel(
                        company=company_name,
                        youtube_api_key=youtube_api_key
                    )

                    sys.stdout = sys.__stdout__

                    if find_result.get('found'):
                        youtube_channel_id = find_result['channel_id']
                        st.info(f"Found channel: {find_result['channel_name']}")
                    else:
                        st.warning("Could not auto-detect YouTube channel. Please provide Channel ID manually.")

            if youtube_channel_id:
                with st.spinner("Scraping YouTube..."):
                    output_capture = StringIO()
                    sys.stdout = output_capture

                    youtube_result = youtube_scraper.scrape_youtube(
                        company=company_name,
                        channel_id=youtube_channel_id,
                        limit=youtube_limit,
                        youtube_api_key=youtube_api_key
                    )

                    sys.stdout = sys.__stdout__

                    if youtube_result.get('success'):
                        results['youtube'] = youtube_result
                        st.success(f"YouTube: Collected {youtube_result.get('total_samples', 0)} samples")
                        with st.expander("View YouTube scraping log"):
                            st.text(output_capture.getvalue())
                    else:
                        st.error(f"YouTube scraping failed: {youtube_result.get('error')}")

        # Scrape Blog with optional AI-powered feed discovery
        if scrape_blog:
            current_task += 1
            status_text.text(f"Scraping Blog... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)

            blog_url_to_use = blog_url  # Default to manual input

            # Use AI to find blog if enabled
            if use_ai_blog_finder:
                with st.spinner("🤖 Using AI to find company blog and RSS feed..."):
                    output_capture = StringIO()
                    sys.stdout = output_capture

                    ai_result = ai_blog_finder.find_blog_url_with_ai(
                        company=company_name,
                        openai_api_key=openai_api_key
                    )

                    sys.stdout = sys.__stdout__

                    # Show AI output
                    with st.expander("View AI Blog Finder log"):
                        st.text(output_capture.getvalue())

                    if ai_result.get('success'):
                        best_feed = ai_result.get('best_feed_url')
                        best_blog = ai_result.get('best_blog_url')
                        all_feeds = ai_result.get('all_working_feeds', [])
                        all_blogs = ai_result.get('all_working_blogs', [])
                        
                        st.info(f"🤖 AI Reasoning: {ai_result.get('ai_reasoning', 'N/A')}")
                        
                        if best_feed:
                            st.success(f"✓ Found RSS feed: {best_feed}")
                            blog_url_to_use = best_feed
                        elif best_blog:
                            st.info(f"✓ Found blog URL: {best_blog} (will search for RSS feed)")
                            blog_url_to_use = best_blog
                        elif all_feeds:
                            st.info(f"Found {len(all_feeds)} potential RSS feeds, trying first one")
                            blog_url_to_use = all_feeds[0]
                        elif all_blogs:
                            st.info(f"Found {len(all_blogs)} potential blog URLs, trying first one")
                            blog_url_to_use = all_blogs[0]
                        else:
                            st.warning("AI could not find working blog or RSS feed URLs")
                            blog_url_to_use = None
                    else:
                        st.warning(f"AI blog finder failed: {ai_result.get('error', 'Unknown error')}")
                        blog_url_to_use = None

            # Proceed with scraping if we have a URL
            if blog_url_to_use:
                with st.spinner(f"Scraping blog from: {blog_url_to_use}..."):
                    output_capture = StringIO()
                    sys.stdout = output_capture

                    blog_result = blog_scraper.scrape_blog(
                        company=company_name,
                        limit=blog_limit,
                        blog_url=blog_url_to_use
                    )

                    sys.stdout = sys.__stdout__

                    if blog_result.get('success'):
                        results['blog'] = blog_result
                        st.success(f"Blog: Collected {blog_result.get('total_samples', 0)} samples")
                        with st.expander("View blog scraping log"):
                            st.text(output_capture.getvalue())
                    else:
                        st.warning(f"Blog scraping: {blog_result.get('error', 'No blog found')}")
                        
                        # If we have alternative URLs from AI, suggest them
                        if use_ai_blog_finder and ai_result.get('success'):
                            all_suggestions = ai_result.get('all_working_feeds', []) + ai_result.get('all_working_blogs', [])
                            if len(all_suggestions) > 1:
                                st.info("AI found these alternative URLs you could try:")
                                for i, url in enumerate(all_suggestions[1:4], 1):  # Show up to 3 alternatives
                                    st.caption(f"{i}. {url}")
            else:
                st.warning("No blog URL available for scraping. Skipping blog collection.")

        # Save to session state
        st.session_state.scraped_data = results

        progress_bar.progress(1.0)
        status_text.text("Data collection complete!")

        # Summary
        st.markdown("---")
        st.subheader("Collection Summary")

        total_samples = sum(r.get('total_samples', 0) for r in results.values())

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Samples", total_samples)

        with col2:
            st.metric("Reddit", results.get('reddit', {}).get('total_samples', 0))

        with col3:
            st.metric("YouTube", results.get('youtube', {}).get('total_samples', 0))

        with col4:
            st.metric("Blog", results.get('blog', {}).get('total_samples', 0))

        if total_samples > 0:
            st.success("Ready for voice analysis! Go to the **Voice Analysis** tab.")
        else:
            st.error("No samples collected. Please try again with different settings.")

    # Show existing data if available
    elif st.session_state.get('scraped_data'):
        st.info("Data already collected. View summary below or collect new data.")

        results = st.session_state.scraped_data
        total_samples = sum(r.get('total_samples', 0) for r in results.values())

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Samples", total_samples)

        with col2:
            st.metric("Reddit", results.get('reddit', {}).get('total_samples', 0))

        with col3:
            st.metric("YouTube", results.get('youtube', {}).get('total_samples', 0))

        with col4:
            st.metric("Blog", results.get('blog', {}).get('total_samples', 0))

with tab2:
    st.header("Voice Analysis")
    st.markdown("Analyze the collected data to extract brand voice characteristics.")

    if not st.session_state.get('scraped_data'):
        st.warning("Please collect data first in the **Data Collection** tab.")
    else:
        results = st.session_state.scraped_data
        total_samples = sum(r.get('total_samples', 0) for r in results.values())

        st.info(f"**Data Ready:** {total_samples} samples collected from {len(results)} sources")

        # OpenAI API Key
        with st.expander("OpenAI API Key", expanded=False):
            openai_api_key = st.text_input("OpenAI API Key (required for analysis)", type="password",
                                           value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, 'secrets') else "")

        st.markdown("---")

        # Analyze Button
        if st.button("Analyze Brand Voice", type="primary", use_container_width=True):

            if not openai_api_key:
                st.error("OpenAI API key is required for voice analysis")
                st.stop()

            with st.spinner("Analyzing brand voice with GPT-4o... This may take 30-60 seconds..."):

                # Prepare training data
                training_data = []
                for source, data in results.items():
                    training_data.append(data)

                output_capture = StringIO()
                sys.stdout = output_capture

                analysis_result = brand_voice_analyzer.analyze_brand_voice_endpoint(
                    company=company_name,
                    training_data=training_data,
                    openai_api_key=openai_api_key
                )

                sys.stdout = sys.__stdout__

                if analysis_result.get('success'):
                    st.session_state.brand_voice = analysis_result
                    st.success("Brand voice analysis complete!")

                    with st.expander("View analysis log"):
                        st.text(output_capture.getvalue())

                    st.balloons()
                    st.info("View results in the **Results** tab!")
                else:
                    st.error(f"Analysis failed: {analysis_result.get('error')}")

with tab3:
    st.header("Analysis Results")

    if not st.session_state.get('brand_voice'):
        st.warning("No analysis results yet. Complete voice analysis first.")
    else:
        result = st.session_state.brand_voice
        brand_voice = result.get('brand_voice', {})

        st.success(f"**Brand Voice Profile:** {company_name}")
        st.caption(f"Analyzed: {result.get('analyzed_at', 'Unknown')} | Samples: {result.get('total_samples_analyzed', 0)}")

        # Display brand voice characteristics
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Voice Characteristics")

            # Tone
            if 'tone' in brand_voice:
                st.markdown(f"**Tone:** {brand_voice['tone']}")

            # Personality Traits
            if 'personality_traits' in brand_voice:
                st.markdown("**Personality Traits:**")
                for trait in brand_voice['personality_traits']:
                    st.markdown(f"- {trait}")

            # Formality & Vocabulary
            col_a, col_b = st.columns(2)
            with col_a:
                if 'formality_level' in brand_voice:
                    st.markdown(f"**Formality:** {brand_voice['formality_level']}")
            with col_b:
                if 'vocabulary_level' in brand_voice:
                    st.markdown(f"**Vocabulary:** {brand_voice['vocabulary_level']}")

            # Sentence Style
            if 'sentence_style' in brand_voice:
                st.markdown(f"**Sentence Style:** {brand_voice['sentence_style']}")

            # Humor Style
            if 'humor_style' in brand_voice:
                st.markdown(f"**Humor:** {brand_voice['humor_style']}")

        with col2:
            st.subheader("Quick Stats")
            st.metric("Sources Analyzed", len(result.get('sources_analyzed', [])))
            st.metric("Total Samples", result.get('total_samples_analyzed', 0))

            if 'voice_consistency' in brand_voice:
                st.metric("Voice Consistency", brand_voice['voice_consistency'])

        # Main Topics
        if 'main_topics' in brand_voice:
            st.subheader("Main Topics")
            topic_cols = st.columns(min(len(brand_voice['main_topics']), 4))
            for i, topic in enumerate(brand_voice['main_topics'][:4]):
                with topic_cols[i]:
                    st.info(topic)

        # Values
        if 'values' in brand_voice:
            st.subheader("Core Values")
            value_cols = st.columns(min(len(brand_voice['values']), 4))
            for i, value in enumerate(brand_voice['values'][:4]):
                with value_cols[i]:
                    st.success(value)

        # Common Phrases
        if 'common_phrases' in brand_voice:
            st.subheader("Common Phrases")
            for phrase in brand_voice['common_phrases']:
                st.markdown(f"- \"{phrase}\"")

        # Writing Guidelines
        if 'writing_guidelines' in brand_voice:
            st.subheader("Writing Guidelines")
            for guideline in brand_voice['writing_guidelines']:
                st.markdown(f"{guideline}")

        # Download Results
        st.markdown("---")
        st.subheader("Download Results")

        col1, col2 = st.columns(2)

        with col1:
            # Download JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="Download Full Analysis (JSON)",
                data=json_str,
                file_name=f"brand_voice_{company_name}_{result.get('analyzed_at', '')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col2:
            # Download summary as text
            summary_text = f"""Brand Voice Analysis: {company_name}
Analyzed: {result.get('analyzed_at', '')}
Total Samples: {result.get('total_samples_analyzed', 0)}

TONE: {brand_voice.get('tone', 'N/A')}

PERSONALITY TRAITS:
{chr(10).join('- ' + t for t in brand_voice.get('personality_traits', []))}

FORMALITY: {brand_voice.get('formality_level', 'N/A')}
VOCABULARY: {brand_voice.get('vocabulary_level', 'N/A')}
SENTENCE STYLE: {brand_voice.get('sentence_style', 'N/A')}

MAIN TOPICS:
{chr(10).join('- ' + t for t in brand_voice.get('main_topics', []))}

CORE VALUES:
{chr(10).join('- ' + v for v in brand_voice.get('values', []))}

WRITING GUIDELINES:
{chr(10).join('- ' + g for g in brand_voice.get('writing_guidelines', []))}
"""

            st.download_button(
                label="Download Summary (TXT)",
                data=summary_text,
                file_name=f"brand_voice_summary_{company_name}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.success("Ready to generate content! Go to the **Content Generator** page.")