"""
History Page
View past brand voice analyses
"""
import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="History - Paracket",
    page_icon="📁",
    layout="wide"
)

st.title("Analysis History")
st.markdown("### View and manage past brand voice analyses")

# Get data directory - same path as Brand Analysis page
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)

# List all brand voice files
brand_voice_files = []
if os.path.exists(data_dir):
    try:
        brand_voice_files = [f for f in os.listdir(data_dir) if f.startswith('brand_voice_') and f.endswith('.json')]
    except Exception as e:
        st.error(f"Error reading data directory: {e}")

if not brand_voice_files:
    st.info("No brand voice analyses found yet. Complete your first analysis in the Brand Analysis page!")
    if st.button("Go to Brand Analysis"):
        st.switch_page("pages/1_Brand_Analysis.py")
else:
    st.success(f"**Found {len(brand_voice_files)} saved analyses**")

    # Sort by modification time (newest first)
    brand_voice_files.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)

    # Display each analysis
    for i, filename in enumerate(brand_voice_files, 1):
        filepath = os.path.join(data_dir, filename)

        # Load the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            company = data.get('company', 'Unknown')
            analyzed_at = data.get('analyzed_at', '')
            total_samples = data.get('total_samples_analyzed', 0)
            sources = data.get('sources', [])
            brand_voice = data.get('brand_voice', {})

            # Parse datetime
            try:
                dt = datetime.fromisoformat(analyzed_at)
                date_str = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                date_str = analyzed_at

            with st.expander(f"#{i} - {company} ({date_str})", expanded=(i == 1)):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(f"{company}")
                    st.caption(f"Analyzed: {date_str}")

                    # Quick summary
                    if 'tone' in brand_voice:
                        st.markdown(f"**Tone:** {brand_voice['tone']}")

                    if 'personality_traits' in brand_voice:
                        traits = ', '.join(brand_voice['personality_traits'][:3])
                        st.markdown(f"**Personality:** {traits}")

                    if 'formality_level' in brand_voice:
                        st.markdown(f"**Formality:** {brand_voice['formality_level']}")

                with col2:
                    st.metric("Total Samples", total_samples)
                    st.metric("Sources", len(sources))

                    # Load button
                    if st.button(f"Load This Analysis", key=f"load_{i}", use_container_width=True):
                        st.session_state.company_name = company
                        st.session_state.brand_voice = data
                        st.success(f"Loaded analysis for {company}!")
                        st.balloons()

                # Full details
                with st.container():
                    tab1, tab2, tab3 = st.tabs(["Summary", "Details", "Export"])

                    with tab1:
                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.markdown("**Sources Used:**")
                            for source in sources:
                                st.markdown(f"- {source}")

                        with col_b:
                            st.markdown("**Voice Characteristics:**")
                            if 'vocabulary_level' in brand_voice:
                                st.markdown(f"- Vocabulary: {brand_voice['vocabulary_level']}")
                            if 'sentence_style' in brand_voice:
                                st.markdown(f"- Style: {brand_voice['sentence_style']}")
                            if 'humor_style' in brand_voice:
                                st.markdown(f"- Humor: {brand_voice['humor_style']}")

                        # Main Topics
                        if 'main_topics' in brand_voice:
                            st.markdown("**Main Topics:**")
                            topics_str = ', '.join(brand_voice['main_topics'])
                            st.info(topics_str)

                    with tab2:
                        # Personality Traits
                        if 'personality_traits' in brand_voice:
                            st.markdown("**Personality Traits:**")
                            for trait in brand_voice['personality_traits']:
                                st.markdown(f"• {trait}")

                        # Values
                        if 'values' in brand_voice:
                            st.markdown("**Core Values:**")
                            for value in brand_voice['values']:
                                st.markdown(f"• {value}")

                        # Common Phrases
                        if 'common_phrases' in brand_voice:
                            st.markdown("**Common Phrases:**")
                            for phrase in brand_voice['common_phrases']:
                                st.markdown(f"- \"{phrase}\"")

                        # Writing Guidelines
                        if 'writing_guidelines' in brand_voice:
                            st.markdown("**Writing Guidelines:**")
                            for guideline in brand_voice['writing_guidelines']:
                                st.markdown(f"→ {guideline}")

                    with tab3:
                        # Download options
                        json_str = json.dumps(data, indent=2)

                        col_x, col_y = st.columns(2)

                        with col_x:
                            st.download_button(
                                label="Download JSON",
                                data=json_str,
                                file_name=filename,
                                mime="application/json",
                                use_container_width=True,
                                key=f"download_json_{i}"
                            )

                        with col_y:
                            # Create summary text
                            summary = f"""Brand Voice Analysis: {company}
Analyzed: {date_str}
Total Samples: {total_samples}
Sources: {', '.join(sources)}

TONE: {brand_voice.get('tone', 'N/A')}
FORMALITY: {brand_voice.get('formality_level', 'N/A')}
VOCABULARY: {brand_voice.get('vocabulary_level', 'N/A')}

PERSONALITY TRAITS:
{chr(10).join('- ' + t for t in brand_voice.get('personality_traits', []))}

MAIN TOPICS:
{chr(10).join('- ' + t for t in brand_voice.get('main_topics', []))}
"""

                            st.download_button(
                                label="Download Summary",
                                data=summary,
                                file_name=f"summary_{filename.replace('.json', '.txt')}",
                                mime="text/plain",
                                use_container_width=True,
                                key=f"download_txt_{i}"
                            )

                        # Delete button
                        st.markdown("---")
                        if st.button(f"Delete This Analysis", key=f"delete_{i}", type="secondary", use_container_width=True):
                            try:
                                os.remove(filepath)
                                st.success(f"Deleted analysis for {company}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting file: {e}")

        except Exception as e:
            st.error(f"Error loading {filename}: {e}")

# Cleanup section
st.markdown("---")
st.subheader("Maintenance")

col1, col2 = st.columns(2)

with col1:
    if st.button("Refresh List", use_container_width=True):
        st.rerun()

with col2:
    if brand_voice_files:
        if st.button("Delete All Analyses", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_delete_all'):
                # Actually delete
                for filename in brand_voice_files:
                    try:
                        os.remove(os.path.join(data_dir, filename))
                    except:
                        pass
                st.session_state.confirm_delete_all = False
                st.success("All analyses deleted")
                st.rerun()
            else:
                # Ask for confirmation
                st.session_state.confirm_delete_all = True
                st.warning("Click again to confirm deletion of ALL analyses")
