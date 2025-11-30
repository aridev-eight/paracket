"""
Content Generator Page
Generate social media posts based on brand voice and trending topics
"""
import streamlit as st
import sys
import os
from io import StringIO
import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules import hackernews_scraper, producthunt_scraper, devto_scraper, brand_voice_analyzer

st.set_page_config(
    page_title="Content Generator - Paracket",
    page_icon="✨",
    layout="wide"
)

st.title("Content Generator")
st.markdown("### Generate authentic social media posts based on your brand voice")

# Check if brand voice exists
if not st.session_state.get('brand_voice'):
    st.warning("Please complete brand voice analysis first!")
    if st.button("Go to Brand Analysis"):
        st.switch_page("pages/1_Brand_Analysis.py")
    st.stop()

company_name = st.session_state.company_name
brand_voice_result = st.session_state.brand_voice
brand_voice = brand_voice_result.get('brand_voice', {})

st.success(f"**Generating content for:** {company_name}")

# Tabs
tab1, tab2 = st.tabs(["Trending Topics", "Generate Content"])

with tab1:
    st.header("Find Trending Topics")
    st.markdown("Discover what people are talking about on **Hacker News**, **Product Hunt**, and **Dev.to** related to your brand.")
    st.info("All sources require no API credentials - the system will automatically search all platforms and combine the results!")

    col1, col2 = st.columns([3, 1])
    with col1:
        trends_limit = st.slider("Number of trends to find (per source)", min_value=5, max_value=30, value=15, step=5)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        min_trends = st.number_input("Minimum required", min_value=3, max_value=20, value=5,
                                     help="Minimum total trends needed from all sources")

    if st.button("Find Trending Topics", type="primary", use_container_width=True):

        all_trends = []
        source_counts = {}

        # Search Hacker News
        with st.spinner("Searching Hacker News..."):
            output_capture_hn = StringIO()
            sys.stdout = output_capture_hn

            hn_result = hackernews_scraper.scrape_hackernews_trends(
                company=company_name,
                limit=trends_limit,
                credentials={'brand_voice': brand_voice}
            )

            sys.stdout = sys.__stdout__

            if hn_result.get('success') and hn_result.get('samples'):
                all_trends.extend(hn_result.get('samples', []))
                source_counts['Hacker News'] = len(hn_result.get('samples', []))
                st.success(f"Hacker News: Found {source_counts['Hacker News']} trends")
            else:
                source_counts['Hacker News'] = 0
                st.warning("Hacker News: No trends found")

        # Search Product Hunt
        with st.spinner("Searching Product Hunt..."):
            output_capture_ph = StringIO()
            sys.stdout = output_capture_ph

            ph_result = producthunt_scraper.scrape_producthunt_trends(
                company=company_name,
                limit=trends_limit,
                credentials={'brand_voice': brand_voice}
            )

            sys.stdout = sys.__stdout__

            if ph_result.get('success') and ph_result.get('trends'):
                # Convert Product Hunt format to match Hacker News format
                for trend in ph_result.get('trends', []):
                    all_trends.append({
                        'text': f"{trend.get('title', '')}: {trend.get('description', '')}",
                        'url': trend.get('url', ''),
                        'source': 'producthunt',
                        'metadata': {
                            'author': 'Product Hunt',
                            'engagement': trend.get('votes', 0),
                            'num_comments': trend.get('comments', 0),
                            'topic_type': 'product',
                            'external_url': trend.get('url', ''),
                            'topics': trend.get('topics', [])
                        }
                    })
                source_counts['Product Hunt'] = len(ph_result.get('trends', []))
                st.success(f"Product Hunt: Found {source_counts['Product Hunt']} trends")
            else:
                source_counts['Product Hunt'] = 0
                st.warning("Product Hunt: No trends found")

        # Search Dev.to
        with st.spinner("Searching Dev.to..."):
            output_capture_devto = StringIO()
            sys.stdout = output_capture_devto

            devto_result = devto_scraper.scrape_devto_trends(
                company=company_name,
                limit=trends_limit,
                credentials={'brand_voice': brand_voice}
            )

            sys.stdout = sys.__stdout__

            if devto_result.get('success') and devto_result.get('trends'):
                # Convert Dev.to format to match Hacker News format
                for trend in devto_result.get('trends', []):
                    all_trends.append({
                        'text': f"{trend.get('title', '')}: {trend.get('description', '')}",
                        'url': trend.get('url', ''),
                        'source': 'devto',
                        'metadata': {
                            'author': trend.get('author', 'Dev.to'),
                            'engagement': trend.get('reactions', 0),
                            'num_comments': trend.get('comments', 0),
                            'topic_type': 'article',
                            'external_url': trend.get('url', ''),
                            'tags': trend.get('tags', []),
                            'reading_time': trend.get('reading_time', 0)
                        }
                    })
                source_counts['Dev.to'] = len(devto_result.get('trends', []))
                st.success(f"Dev.to: Found {source_counts['Dev.to']} trends")
            else:
                source_counts['Dev.to'] = 0
                st.warning("Dev.to: No trends found")

        # Combine results
        total_found = len(all_trends)

        if total_found >= min_trends:
            # Create combined result in same format as hackernews_scraper
            combined_result = {
                'success': True,
                'samples': all_trends,
                'total_samples': total_found,
                'company': company_name,
                'sources': source_counts,
                'scraped_at': datetime.datetime.now().isoformat()
            }

            st.session_state.trending_topics = combined_result
            st.success(f"Total: Found {total_found} trending topics from {len([k for k, v in source_counts.items() if v > 0])} sources")

            # Show source breakdown
            with st.expander("Source Breakdown"):
                for source, count in source_counts.items():
                    st.metric(source, count)

            # Show logs
            with st.expander("View search logs"):
                st.markdown("**Hacker News Log:**")
                st.text(output_capture_hn.getvalue())
                st.markdown("**Product Hunt Log:**")
                st.text(output_capture_ph.getvalue())
                st.markdown("**Dev.to Log:**")
                st.text(output_capture_devto.getvalue())
        else:
            st.error(f"Only found {total_found} trends (minimum {min_trends} required). Try:")
            st.markdown("- Increasing the trends limit")
            st.markdown("- Lowering the minimum required")
            st.markdown("- Checking back later for new trending topics")

            if total_found > 0:
                st.info(f"Found trends breakdown: {source_counts}")

    # Display trending topics
    if st.session_state.get('trending_topics'):
        st.markdown("---")
        st.subheader("Trending Topics")

        trends = st.session_state.trending_topics
        samples = trends.get('samples', [])

        # Show source breakdown if available
        if trends.get('sources'):
            source_counts = trends.get('sources', {})
            st.caption(f"Combined results from {len([k for k, v in source_counts.items() if v > 0])} sources: " +
                      " | ".join([f"{k}: {v}" for k, v in source_counts.items() if v > 0]))

        if samples:
            for i, topic in enumerate(samples[:10], 1):
                # Determine source icon
                source = topic.get('source', 'hackernews')
                if source == 'hackernews':
                    source_icon = "🔥"
                    source_name = "Hacker News"
                elif source == 'producthunt':
                    source_icon = "🚀"
                    source_name = "Product Hunt"
                elif source == 'devto':
                    source_icon = "📝"
                    source_name = "Dev.to"
                else:
                    source_icon = "💬"
                    source_name = "Unknown"

                with st.expander(f"{source_icon} #{i} - {topic.get('text', '')[:100]}..."):
                    st.caption(f"Source: **{source_name}**")
                    st.markdown(f"**Full Text:**\n\n{topic.get('text', '')}")
                    st.caption(f"Author: {topic.get('metadata', {}).get('author', 'unknown')}")
                    st.caption(f"Engagement: {topic.get('metadata', {}).get('engagement', 0)} points | {topic.get('metadata', {}).get('num_comments', 0)} comments")
                    st.caption(f"Topic Type: {topic.get('metadata', {}).get('topic_type', 'discussion')}")

                    # Link text based on source
                    if source == 'producthunt':
                        st.markdown(f"[View on Product Hunt]({topic.get('url', '#')})")
                    elif source == 'devto':
                        st.markdown(f"[View on Dev.to]({topic.get('url', '#')})")
                        if topic.get('metadata', {}).get('reading_time'):
                            st.caption(f"Reading time: {topic.get('metadata', {}).get('reading_time')} min")
                    else:
                        st.markdown(f"[View on Hacker News]({topic.get('url', '#')})")

                    if topic.get('metadata', {}).get('external_url') and source == 'hackernews':
                        st.markdown(f"[External Article]({topic.get('metadata', {}).get('external_url')})")

                    # Show Product Hunt topics if available
                    if topic.get('metadata', {}).get('topics'):
                        st.caption(f"Topics: {', '.join(topic.get('metadata', {}).get('topics', []))}")

                    # Show Dev.to tags if available
                    if topic.get('metadata', {}).get('tags'):
                        st.caption(f"Tags: {', '.join(topic.get('metadata', {}).get('tags', []))}")
        else:
            st.info("No trending topics found. Try different settings or check back later.")

with tab2:
    st.header("Generate Social Media Posts")
    st.markdown("Create platform-optimized content that matches your brand voice.")

    # OpenAI API Key
    with st.expander("OpenAI API Key", expanded=False):
        openai_api_key = st.text_input("OpenAI API Key", type="password",
                                       value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, 'secrets') else "")

    # Check if we have trending topics
    if not st.session_state.get('trending_topics'):
        st.warning("Please find trending topics first in the **Trending Topics** tab")
        st.stop()

    trends = st.session_state.trending_topics
    samples = trends.get('samples', [])

    if not samples:
        st.warning("No trending topics available. Please search for trends first.")
        st.stop()

    # Step 1: Generate Post Ideas
    st.markdown("---")
    st.subheader("Step 1: Generate Post Ideas")
    st.markdown(f"AI will analyze all {len(samples)} trending topics and create ready-to-use post drafts.")

    st.warning("**Safety Note:** AI-generated posts provide commentary and insights on trending topics. Always review to ensure accuracy and verify that no fake announcements or features are mentioned.")

    col1, col2 = st.columns([3, 1])
    with col1:
        num_ideas = st.slider("Number of post ideas to generate", min_value=3, max_value=7, value=3)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("Generate Post Ideas", type="primary", use_container_width=True):
            if not openai_api_key:
                st.error("OpenAI API key is required. Please expand the OpenAI API Key section above.")
                st.stop()

            with st.spinner(f"Analyzing {len(samples)} trending topics and generating {num_ideas} post ideas..."):
                output_capture = StringIO()
                sys.stdout = output_capture

                post_ideas_result = brand_voice_analyzer.generate_post_ideas(
                    company=company_name,
                    brand_voice=brand_voice,
                    trending_topics=samples,
                    num_ideas=num_ideas,
                    openai_api_key=openai_api_key
                )

                sys.stdout = sys.__stdout__

                if post_ideas_result.get('success'):
                    st.session_state.post_ideas = post_ideas_result
                    st.success(f"Generated {len(post_ideas_result.get('post_ideas', {}).get('post_ideas', []))} post ideas!")

                    with st.expander("View generation log"):
                        st.text(output_capture.getvalue())
                else:
                    st.error(f"Failed to generate post ideas: {post_ideas_result.get('error')}")

    # Display generated post ideas
    if st.session_state.get('post_ideas'):
        st.markdown("---")
        st.subheader("Generated Post Ideas")
        st.markdown("Select the post idea you like best, or regenerate for more options.")

        post_ideas_data = st.session_state.post_ideas
        post_ideas = post_ideas_data.get('post_ideas', {}).get('post_ideas', [])

        if post_ideas:
            # Display each post idea as a card
            for i, idea in enumerate(post_ideas):
                with st.expander(f"Post Idea #{i+1}: {idea.get('theme', 'Untitled')}", expanded=(i == 0)):
                    st.markdown(f"**Theme:** {idea.get('theme', 'N/A')}")
                    st.markdown(f"**Rationale:** {idea.get('rationale', 'N/A')}")
                    st.markdown(f"**Estimated Engagement:** {idea.get('estimated_engagement', 'N/A').upper()}")

                    topic_ids = idea.get('topic_ids', [])
                    if topic_ids:
                        st.caption(f"Addresses trending topics: #{', #'.join(map(str, topic_ids))}")

                    st.markdown("**Post Content:**")
                    st.info(idea.get('content', ''))

                    if st.button(f"Select This Post", key=f"select_post_{i}", use_container_width=True):
                        st.session_state.selected_post_idea = idea
                        st.session_state.master_message = idea.get('content', '')
                        st.success("Post selected! Scroll down to edit the master message.")
                        st.rerun()

    # Step 2: Edit Master Message
    if st.session_state.get('master_message'):
        st.markdown("---")
        st.subheader("Step 2: Edit Master Message")
        st.markdown("Review and edit your selected post. This will be adapted to different platforms.")

        selected_idea = st.session_state.get('selected_post_idea', {})
        if selected_idea:
            st.caption(f"**Theme:** {selected_idea.get('theme', 'N/A')}")

        master_message = st.text_area(
            "Master Message",
            value=st.session_state.master_message,
            height=200,
            help="Edit this content as needed. This is your master message that will be adapted for each platform.",
            key="master_msg_editor"
        )

        # Update session state when edited
        if master_message != st.session_state.master_message:
            st.session_state.master_message = master_message

        st.caption(f"Character count: {len(master_message)}")

        # Step 3: Platform Selection and Adaptation
        st.markdown("---")
        st.subheader("Step 3: Adapt to Platforms")

        col1, col2, col3 = st.columns(3)
        with col1:
            adapt_twitter = st.checkbox("Twitter/X", value=True, key="adapt_twitter")
        with col2:
            adapt_mastodon = st.checkbox("Mastodon", value=True, key="adapt_mastodon")
        with col3:
            adapt_reddit = st.checkbox("Reddit", value=True, key="adapt_reddit")

        if st.button("Adapt to Selected Platforms", type="primary", use_container_width=True):
            if not openai_api_key:
                st.error("OpenAI API key is required")
                st.stop()

            if not adapt_twitter and not adapt_mastodon and not adapt_reddit:
                st.error("Please select at least one platform")
                st.stop()

            platforms = []
            if adapt_twitter:
                platforms.append('twitter')
            if adapt_mastodon:
                platforms.append('mastodon')
            if adapt_reddit:
                platforms.append('reddit')

            with st.spinner(f"Adapting master message to {len(platforms)} platform(s)..."):
                output_capture = StringIO()
                sys.stdout = output_capture

                adaptation_result = brand_voice_analyzer.adapt_master_to_platforms(
                    company=company_name,
                    brand_voice=brand_voice,
                    master_message=master_message,
                    platforms=platforms,
                    openai_api_key=openai_api_key
                )

                sys.stdout = sys.__stdout__

                if adaptation_result.get('success'):
                    st.session_state.platform_adaptations = adaptation_result
                    st.success(f"Adapted to {len(platforms)} platform(s)!")

                    with st.expander("View adaptation log"):
                        st.text(output_capture.getvalue())
                else:
                    st.error(f"Failed to adapt: {adaptation_result.get('error')}")

    # Display platform adaptations
    if st.session_state.get('platform_adaptations'):
        st.markdown("---")
        st.header("Platform-Specific Content")
        st.markdown("Your content has been adapted for each platform. **Edit as needed** and regenerate if you want a different version!")

        st.info("**Before posting:** Verify that the content is accurate, appropriate, and contains no fake announcements or unverified claims.")

        adaptations = st.session_state.platform_adaptations.get('adaptations', {})

        # Initialize edited content in session state if not exists
        if 'edited_content' not in st.session_state:
            st.session_state.edited_content = {}

        # Twitter
        if 'twitter' in adaptations:
            st.subheader("Twitter/X")

            # Initialize with original content if not edited yet
            if 'twitter' not in st.session_state.edited_content:
                st.session_state.edited_content['twitter'] = adaptations['twitter']['content']

            twitter_content = st.text_area(
                "Edit Twitter/X post:",
                value=st.session_state.edited_content['twitter'],
                height=120,
                key="twitter_editor",
                help="Edit this post as needed. Max 280 characters."
            )

            # Update edited content
            st.session_state.edited_content['twitter'] = twitter_content

            char_count = len(twitter_content)
            max_chars = adaptations['twitter']['max_length']
            color = "●" if char_count <= max_chars else "●"
            st.caption(f"{color} Character count: {char_count}/{max_chars}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "Download",
                    twitter_content,
                    file_name=f"twitter_{company_name}.txt",
                    use_container_width=True
                )
            with col2:
                if st.button("Copy", key="copy_twitter", use_container_width=True):
                    st.toast("Copied to clipboard!")
            with col3:
                if st.button("Regenerate", key="regen_twitter", use_container_width=True):
                    if not openai_api_key:
                        st.error("OpenAI API key required")
                    else:
                        with st.spinner("Regenerating Twitter post..."):
                            output_capture = StringIO()
                            sys.stdout = output_capture

                            regen_result = brand_voice_analyzer.adapt_master_to_platforms(
                                company=company_name,
                                brand_voice=brand_voice,
                                master_message=st.session_state.master_message,
                                platforms=['twitter'],
                                openai_api_key=openai_api_key
                            )

                            sys.stdout = sys.__stdout__

                            if regen_result.get('success'):
                                new_content = regen_result['adaptations']['twitter']['content']
                                st.session_state.edited_content['twitter'] = new_content
                                adaptations['twitter']['content'] = new_content
                                st.success("Regenerated!")
                                st.rerun()

        # Mastodon
        if 'mastodon' in adaptations:
            st.subheader("Mastodon")

            # Initialize with original content if not edited yet
            if 'mastodon' not in st.session_state.edited_content:
                st.session_state.edited_content['mastodon'] = adaptations['mastodon']['content']

            mastodon_content = st.text_area(
                "Edit Mastodon post:",
                value=st.session_state.edited_content['mastodon'],
                height=150,
                key="mastodon_editor",
                help="Edit this post as needed. Max 500 characters."
            )

            # Update edited content
            st.session_state.edited_content['mastodon'] = mastodon_content

            char_count = len(mastodon_content)
            max_chars = adaptations['mastodon']['max_length']
            color = "●" if char_count <= max_chars else "●"
            st.caption(f"{color} Character count: {char_count}/{max_chars}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "Download",
                    mastodon_content,
                    file_name=f"mastodon_{company_name}.txt",
                    use_container_width=True
                )
            with col2:
                if st.button("Copy", key="copy_mastodon", use_container_width=True):
                    st.toast("Copied to clipboard!")
            with col3:
                if st.button("Regenerate", key="regen_mastodon", use_container_width=True):
                    if not openai_api_key:
                        st.error("OpenAI API key required")
                    else:
                        with st.spinner("Regenerating Mastodon post..."):
                            output_capture = StringIO()
                            sys.stdout = output_capture

                            regen_result = brand_voice_analyzer.adapt_master_to_platforms(
                                company=company_name,
                                brand_voice=brand_voice,
                                master_message=st.session_state.master_message,
                                platforms=['mastodon'],
                                openai_api_key=openai_api_key
                            )

                            sys.stdout = sys.__stdout__

                            if regen_result.get('success'):
                                new_content = regen_result['adaptations']['mastodon']['content']
                                st.session_state.edited_content['mastodon'] = new_content
                                adaptations['mastodon']['content'] = new_content
                                st.success("Regenerated!")
                                st.rerun()

        # Reddit
        if 'reddit' in adaptations:
            st.subheader("Reddit")

            # Initialize with original content if not edited yet
            if 'reddit' not in st.session_state.edited_content:
                st.session_state.edited_content['reddit'] = adaptations['reddit']['content']

            reddit_content = st.text_area(
                "Edit Reddit post:",
                value=st.session_state.edited_content['reddit'],
                height=250,
                key="reddit_editor",
                help="Edit this post as needed. Includes title and body."
            )

            # Update edited content
            st.session_state.edited_content['reddit'] = reddit_content

            char_count = len(reddit_content)
            max_chars = adaptations['reddit']['max_length']
            color = "●" if char_count <= max_chars else "●"
            st.caption(f"{color} Character count: {char_count} (recommended max: {max_chars})")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "Download",
                    reddit_content,
                    file_name=f"reddit_{company_name}.txt",
                    use_container_width=True
                )
            with col2:
                if st.button("Copy", key="copy_reddit", use_container_width=True):
                    st.toast("Copied to clipboard!")
            with col3:
                if st.button("Regenerate", key="regen_reddit", use_container_width=True):
                    if not openai_api_key:
                        st.error("OpenAI API key required")
                    else:
                        with st.spinner("Regenerating Reddit post..."):
                            output_capture = StringIO()
                            sys.stdout = output_capture

                            regen_result = brand_voice_analyzer.adapt_master_to_platforms(
                                company=company_name,
                                brand_voice=brand_voice,
                                master_message=st.session_state.master_message,
                                platforms=['reddit'],
                                openai_api_key=openai_api_key
                            )

                            sys.stdout = sys.__stdout__

                            if regen_result.get('success'):
                                new_content = regen_result['adaptations']['reddit']['content']
                                st.session_state.edited_content['reddit'] = new_content
                                adaptations['reddit']['content'] = new_content
                                st.success("Regenerated!")
                                st.rerun()

        st.markdown("---")
        st.success("Content ready to post! Review and edit as needed before publishing.")

        # Step 4: Finalize & Schedule
        st.markdown("---")
        st.subheader("Step 4: Finalize & Schedule Post")
        st.markdown("Schedule your posts to be published automatically across all platforms.")

        # API Credentials for posting
        with st.expander("Social Media API Credentials", expanded=False):
            st.markdown("**Twitter/X API**")
            col1, col2 = st.columns(2)
            with col1:
                twitter_api_key = st.text_input("Twitter API Key", type="password", key="twitter_api_key",
                                                value=st.secrets.get("TWITTER_API_KEY", "") if hasattr(st, 'secrets') else "")
                twitter_api_secret = st.text_input("Twitter API Secret", type="password", key="twitter_api_secret",
                                                   value=st.secrets.get("TWITTER_API_SECRET", "") if hasattr(st, 'secrets') else "")
            with col2:
                twitter_access_token = st.text_input("Twitter Access Token", type="password", key="twitter_access_token",
                                                     value=st.secrets.get("TWITTER_ACCESS_TOKEN", "") if hasattr(st, 'secrets') else "")
                twitter_access_secret = st.text_input("Twitter Access Token Secret", type="password", key="twitter_access_secret",
                                                      value=st.secrets.get("TWITTER_ACCESS_SECRET", "") if hasattr(st, 'secrets') else "")

            st.markdown("**Reddit API**")
            col1, col2 = st.columns(2)
            with col1:
                reddit_post_client_id = st.text_input("Reddit Client ID", type="password", key="reddit_post_client_id",
                                                      value=st.secrets.get("REDDIT_CLIENT_ID", "") if hasattr(st, 'secrets') else "")
                reddit_post_client_secret = st.text_input("Reddit Client Secret", type="password", key="reddit_post_client_secret",
                                                          value=st.secrets.get("REDDIT_CLIENT_SECRET", "") if hasattr(st, 'secrets') else "")
            with col2:
                reddit_username = st.text_input("Reddit Username", key="reddit_username",
                                                value=st.secrets.get("REDDIT_USERNAME", "") if hasattr(st, 'secrets') else "")
                reddit_password = st.text_input("Reddit Password", type="password", key="reddit_password",
                                               value=st.secrets.get("REDDIT_PASSWORD", "") if hasattr(st, 'secrets') else "")

            st.markdown("**Mastodon API**")
            col1, col2 = st.columns(2)
            with col1:
                mastodon_instance = st.text_input("Mastodon Instance URL", key="mastodon_instance",
                                                  placeholder="https://mastodon.social",
                                                  value=st.secrets.get("MASTODON_INSTANCE", "") if hasattr(st, 'secrets') else "")
            with col2:
                mastodon_access_token = st.text_input("Mastodon Access Token", type="password", key="mastodon_access_token",
                                                      value=st.secrets.get("MASTODON_ACCESS_TOKEN", "") if hasattr(st, 'secrets') else "")

        # Scheduling interface
        st.markdown("**Schedule Date & Time:**")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1.5])
        with col1:
            st.caption("Date")
            schedule_date = st.date_input("Date", key="schedule_date", label_visibility="collapsed")
        with col2:
            st.caption("Hour")
            hour = st.number_input("Hour", min_value=1, max_value=12, value=9, key="schedule_hour", label_visibility="collapsed")
        with col3:
            st.caption("Minute")
            minute = st.number_input("Min", min_value=0, max_value=59, value=0, key="schedule_minute", label_visibility="collapsed")
        with col4:
            st.caption("AM/PM")
            am_pm = st.selectbox("AM/PM", ["AM", "PM"], key="schedule_ampm", label_visibility="collapsed")

        # Convert to 24-hour time
        hour_24 = hour if am_pm == "AM" and hour != 12 else (0 if am_pm == "AM" and hour == 12 else (hour if hour == 12 else hour + 12))
        schedule_time = datetime.time(hour_24, minute)

        # Platform selection for posting
        st.markdown("**Select platforms to post to:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            post_to_twitter = st.checkbox("Post to Twitter/X", value='twitter' in adaptations, key="post_to_twitter")
        with col2:
            post_to_mastodon = st.checkbox("Post to Mastodon", value='mastodon' in adaptations, key="post_to_mastodon")
        with col3:
            post_to_reddit = st.checkbox("Post to Reddit", value='reddit' in adaptations, key="post_to_reddit")

        if post_to_reddit:
            subreddit_name = st.text_input("Target Subreddit or Profile", placeholder="e.g., technology or u_yourusername", key="target_subreddit",
                                          help="Enter subreddit name (without r/) OR your user profile (u_username)")

            # Validate subreddit access
            if subreddit_name:
                with st.spinner("Validating subreddit access..."):
                    import praw

                    try:
                        # Check if Reddit credentials are available
                        reddit_creds = {
                            'client_id': reddit_post_client_id,
                            'client_secret': reddit_post_client_secret,
                            'username': reddit_username,
                            'password': reddit_password
                        }

                        if not all(reddit_creds.values()):
                            st.warning("Reddit credentials not provided. Cannot validate subreddit access.")
                        else:
                            # Create Reddit instance
                            reddit = praw.Reddit(
                                client_id=reddit_creds['client_id'],
                                client_secret=reddit_creds['client_secret'],
                                username=reddit_creds['username'],
                                password=reddit_creds['password'],
                                user_agent='paracket_poster/1.0'
                            )

                            # Test subreddit/profile access
                            try:
                                # Determine if it's a user profile or subreddit
                                is_user_profile = subreddit_name.startswith('u_')
                                display_prefix = "u/" if is_user_profile else "r/"

                                subreddit = reddit.subreddit(subreddit_name)
                                # Try to access basic properties (this will fail if subreddit doesn't exist)
                                _ = subreddit.display_name
                                _ = subreddit.subscribers

                                # Check if we can submit (some subreddits restrict posting)
                                can_submit = subreddit.user_is_contributor or not subreddit.subreddit_type == 'private'

                                # Check account requirements (approximate)
                                if can_submit:
                                    if is_user_profile:
                                        st.success(f"{display_prefix}{subreddit_name} (your profile) is ready for posting!")
                                    else:
                                        st.success(f"{display_prefix}{subreddit_name} exists and you can post there!")
                                        st.caption(f"{subreddit.subscribers:,} subscribers")
                                else:
                                    st.warning(f"{display_prefix}{subreddit_name} exists but may have posting restrictions")

                            except Exception as sub_error:
                                error_msg = str(sub_error).lower()
                                display_prefix = "u/" if subreddit_name.startswith('u_') else "r/"

                                if 'private' in error_msg or 'forbidden' in error_msg:
                                    st.error(f"{display_prefix}{subreddit_name} is private or you don't have access")
                                elif 'not found' in error_msg or 'redirect' in error_msg:
                                    st.error(f"{display_prefix}{subreddit_name} doesn't exist")
                                else:
                                    st.warning(f"Could not validate {display_prefix}{subreddit_name}: {sub_error}")

                    except Exception as e:
                        st.error(f"Error validating subreddit: {e}")

        # Finalize button
        if st.button("Finalize & Schedule Post", type="primary", use_container_width=True):
            import datetime
            import json
            import os

            # Validate selections
            if not post_to_twitter and not post_to_mastodon and not post_to_reddit:
                st.error("Please select at least one platform to post to")
                st.stop()

            if post_to_reddit and not subreddit_name:
                st.error("Please specify a target subreddit for Reddit")
                st.stop()

            # Validate character limits
            validation_errors = []

            if post_to_twitter and 'twitter' in st.session_state.edited_content:
                twitter_len = len(st.session_state.edited_content['twitter'])
                if twitter_len > 280:
                    validation_errors.append(f"Twitter post is {twitter_len} characters (max 280). Please edit it to be shorter.")

            if post_to_mastodon and 'mastodon' in st.session_state.edited_content:
                mastodon_len = len(st.session_state.edited_content['mastodon'])
                if mastodon_len > 500:
                    validation_errors.append(f"Mastodon post is {mastodon_len} characters (max 500). Please edit it to be shorter.")

            if post_to_reddit and 'reddit' in st.session_state.edited_content:
                reddit_len = len(st.session_state.edited_content['reddit'])
                if reddit_len > 40000:  # Reddit's actual limit
                    validation_errors.append(f"Reddit post is {reddit_len} characters (max 40,000). Please edit it to be shorter.")

            if validation_errors:
                st.error("Cannot finalize post - character limits exceeded:")
                for error in validation_errors:
                    st.error(error)
                st.warning("Scroll up to edit the platform-specific content and reduce the length.")
                st.stop()

            # Create scheduled datetime
            scheduled_datetime = datetime.datetime.combine(schedule_date, schedule_time)

            # Prepare scheduled post data
            scheduled_post = {
                'id': datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
                'company': company_name,
                'scheduled_time': scheduled_datetime.isoformat(),
                'created_at': datetime.datetime.now().isoformat(),
                'status': 'active',  # active, inactive, posted, failed
                'master_message': st.session_state.master_message,
                'theme': st.session_state.selected_post_idea.get('theme', 'N/A'),
                'platforms': {},
                'credentials': {}
            }

            # Add platform content
            if post_to_twitter and 'twitter' in st.session_state.edited_content:
                scheduled_post['platforms']['twitter'] = {
                    'content': st.session_state.edited_content['twitter'],
                    'enabled': True
                }
                if twitter_api_key and twitter_api_secret and twitter_access_token and twitter_access_secret:
                    scheduled_post['credentials']['twitter'] = {
                        'api_key': twitter_api_key,
                        'api_secret': twitter_api_secret,
                        'access_token': twitter_access_token,
                        'access_secret': twitter_access_secret
                    }

            if post_to_mastodon and 'mastodon' in st.session_state.edited_content:
                scheduled_post['platforms']['mastodon'] = {
                    'content': st.session_state.edited_content['mastodon'],
                    'enabled': True
                }
                if mastodon_instance and mastodon_access_token:
                    scheduled_post['credentials']['mastodon'] = {
                        'instance': mastodon_instance,
                        'access_token': mastodon_access_token
                    }

            if post_to_reddit and 'reddit' in st.session_state.edited_content:
                scheduled_post['platforms']['reddit'] = {
                    'content': st.session_state.edited_content['reddit'],
                    'enabled': True,
                    'subreddit': subreddit_name
                }
                if reddit_post_client_id and reddit_post_client_secret and reddit_username and reddit_password:
                    scheduled_post['credentials']['reddit'] = {
                        'client_id': reddit_post_client_id,
                        'client_secret': reddit_post_client_secret,
                        'username': reddit_username,
                        'password': reddit_password
                    }

            # Save scheduled post
            scheduled_posts_dir = os.path.join('streamlit_app', 'data', 'scheduled_posts')
            os.makedirs(scheduled_posts_dir, exist_ok=True)

            file_path = os.path.join(scheduled_posts_dir, f"scheduled_{scheduled_post['id']}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scheduled_post, f, indent=2)

            st.success(f"Post scheduled for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}!")
            st.info("Go to **Scheduled Posts** in the sidebar to view and manage your scheduled posts.")

            # Show what was scheduled
            with st.expander("Scheduled Post Details"):
                st.json(scheduled_post)
