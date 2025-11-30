"""
Paracket - Automated Brand Voice Marketing System
Streamlit Application

Main entry point for the application
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Paracket - Brand Voice Marketing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fonts and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Afacad:wght@400;500;600;700&family=Homemade+Apple&display=swap');

    /* Apply Afacad as primary font */
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Afacad', sans-serif !important;
    }

    /* Apply Homemade Apple to main title */
    h1 {
        font-family: 'Homemade Apple', cursive !important;
        color: #780000 !important;
    }

    /* Custom styled boxes matching brand colors */
    .custom-info-box {
        background-color: #fdf0d5;
        border-left: 4px solid #780000;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .custom-success-box {
        background-color: #fff9f0;
        border-left: 4px solid #780000;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .custom-box h3 {
        color: #780000;
        margin-top: 0;
        font-family: 'Afacad', sans-serif !important;
        font-weight: 600;
    }

    .custom-box ul, .custom-box ol {
        margin: 0.5rem 0;
    }

    /* Style buttons with brand color */
    .stButton > button {
        background-color: #780000;
        color: white;
        border: none;
    }

    .stButton > button:hover {
        background-color: #5a0000;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'company_name' not in st.session_state:
    st.session_state.company_name = ''
if 'youtube_channel_id' not in st.session_state:
    st.session_state.youtube_channel_id = ''
if 'blog_url' not in st.session_state:
    st.session_state.blog_url = ''
if 'brand_voice' not in st.session_state:
    st.session_state.brand_voice = None
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = {}

# Sidebar
# with st.sidebar:
    # st.markdown('<h1 style="font-family: \'Homemade Apple\', cursive; color: #780000; font-size: 2rem;">Paracket</h1>', unsafe_allow_html=True)
    # st.markdown("### Automated Brand Voice Marketing")
    # st.markdown("---")
    # st.markdown("**Navigation**")
    # st.markdown("**Home** - Get started")
    # st.markdown("**Brand Analysis** - Analyze brand voice")
    # st.markdown("**Content Generator** - Create posts")
    # st.markdown("**Scheduled Posts** - Manage scheduled posts")
    # st.markdown("**History** - View past analyses")

# Main content
st.title("Paracket: Automated Brand Voice Marketing")
st.markdown("### Welcome to the future of authentic, AI-powered social media marketing")

# Quick Setup Section
st.markdown("---")
st.header("Quick Setup")

with st.form("quick_start_form"):

    company_name = st.text_input(
        "Company Name",
        value=st.session_state.company_name,
        placeholder="e.g., Unity, Apple, Notion",
        help="Enter the name of the company whose brand voice you want to analyze"
    )

    col1, col2 = st.columns(2)

    with col1:
        youtube_channel_id = st.text_input(
            "YouTube Channel ID (Optional)",
            value=st.session_state.youtube_channel_id,
            placeholder="e.g., UCKQdc0-Targ4nDIAUrlfKiA",
            help="If known, provide the YouTube channel ID. Otherwise, Paracket will try to find it."
        )

    with col2:
        blog_url = st.text_input(
            "Blog URL (Optional)",
            value=st.session_state.blog_url,
            placeholder="e.g., https://blog.unity.com",
            help="Direct URL to the company blog"
        )

    submitted = st.form_submit_button("Save & Continue to Analysis", use_container_width=True)

    if submitted:
        if company_name:
            st.session_state.company_name = company_name
            st.session_state.youtube_channel_id = youtube_channel_id
            st.session_state.blog_url = blog_url
            st.success(f"Saved settings for {company_name}!")
            st.info("Now go to the **Brand Analysis** page to start!")
        else:
            st.error("Please enter a company name")

# The Problem
st.markdown("---")
st.header("The Problem")

st.markdown("""
In today's digital landscape, brands face an increasingly complex challenge when it comes to social media presence. The pressure to maintain an active, engaging presence across multiple platforms has never been higher, yet the resources to do so effectively remain scarce. Marketing teams find themselves caught in a cycle of reactive content creation, scrambling to respond to trends hours or even days after they emerge. Meanwhile, the need for platform-specific content means the same core message must be manually adapted multiple times, each version requiring careful attention to maintain brand consistency while respecting the unique culture and constraints of each platform.

This problem becomes even more acute for smaller teams and individual creators who wear multiple hats. The hours spent crafting tweets, Reddit posts, and Mastodon updates are hours not spent on product development, customer engagement, or strategic planning. More critically, when different team members create content independently, subtle inconsistencies creep into the brand voice. What starts as a cohesive identity fragments across platforms, diluting the brand's impact and confusing its audience.

The traditional solution of hiring dedicated social media managers or agencies comes with its own challenges. Beyond the obvious cost implications, there's an inherent risk in outsourcing your brand voice. External teams, no matter how skilled, rarely capture the authentic nuances that make a brand's communication truly distinctive. The result is often content that feels professional but generic, technically correct but lacking soul.
""")

# The Journey
st.markdown("---")
st.header("Building Paracket: From Concept to Reality")

st.markdown("""
Paracket began as an exploration of a fundamental question: could AI truly understand and replicate a brand's voice well enough to create authentic content? The answer required more than just connecting APIs and prompting language models. It needed a systematic approach to capturing the essence of how a brand communicates across different contexts and platforms.

The initial development happened in n8n, a powerful workflow automation platform that provided the perfect environment for rapid prototyping and iteration. The n8n canvas became a living laboratory where I could visually map out the entire content creation pipeline. Starting with data collection, I built workflows that systematically gathered content from Reddit, YouTube, and company blogs. Each source required its own careful handling. Reddit's API presented unique challenges around rate limiting and content filtering. YouTube transcript extraction needed robust error handling for videos without captions. Blog scraping had to navigate the wild west of RSS feed formats and inconsistent HTML structures.

The breakthrough came with the brand voice analysis component. Rather than treating voice analysis as a simple sentiment classification task, I designed a multi-dimensional profiling system. Using GPT-4o, Paracket examines collected content samples to extract over ten distinct characteristics including tone, formality level, vocabulary patterns, sentence structure preferences, humor style, and topical focus. The prompt engineering for this analysis went through dozens of iterations, each refinement making the extracted profiles more nuanced and actionable. The goal was never to create a statistical model of word frequencies, but rather to capture the intangible qualities that make communication feel authentic.

Content generation required an equally sophisticated approach. The n8n workflow integrated with Hacker News to identify trending topics relevant to each brand's domain. This wasn't just keyword matching—the system evaluates relevance, filters out controversial subjects, and prioritizes topics that align with the brand's established themes. The generation process creates a master message first, then adapts it for each platform while maintaining the core voice characteristics identified in the analysis phase.

As the system matured in n8n, a new challenge emerged: accessibility. The workflow automation platform was powerful but required technical knowledge to configure and operate. To make Paracket truly useful, it needed an interface that anyone could use without understanding the underlying complexity. This realization led to the development of the Streamlit application you're using now.
""")

# The Streamlit Transition
st.markdown("---")
st.header("Making It Accessible")

st.markdown("""
Translating a sophisticated n8n workflow into an intuitive Streamlit application presented unique architectural challenges. The visual, node-based logic of n8n had to be transformed into Python modules that could run independently while maintaining the same level of sophistication. Each n8n node became a Python function, each workflow became a module, and the entire system had to be restructured around user interactions rather than automated triggers.

The Streamlit interface prioritizes clarity and progressive disclosure. Users start with a simple form—company name, YouTube channel, and blog URL—but behind this simplicity lies the complex orchestration of API calls, data processing, and AI analysis. The Brand Analysis page guides users through data collection and voice profiling with real-time feedback, turning what could be an opaque process into a transparent, understandable journey. The Content Generator then leverages this analysis to create platform-specific posts, presenting users with editable drafts rather than black-box outputs. This approach maintains user agency while providing AI-powered assistance.

The scheduling system deserves special mention. While Streamlit excels at interactive applications, it lacks built-in support for background tasks and scheduled execution. The solution came through GitHub Actions, which runs the posting scheduler every five minutes in the cloud. This architecture elegantly separates concerns: Streamlit handles the user interface and content creation, while GitHub Actions manages the time-based automation. Posts created in the Streamlit UI are saved as JSON files, committed to the repository, and picked up by the scheduler at the appropriate time. After posting, status updates flow back through the same channel, creating a seamless experience despite the distributed architecture.
""")

# Challenges and Learning
st.markdown("---")
st.header("Challenges and Evolution")

st.markdown("""
No development journey is without its obstacles, and Paracket encountered several significant challenges that shaped its current form. The most dramatic came from Reddit itself. The original design heavily relied on Reddit for both brand voice analysis and trend discovery. Reddit's rich discussion threads and authentic brand interactions made it an ideal data source. However, during development, my Reddit account was banned—apparently, the data collection patterns triggered automated fraud detection systems. This ban effectively shut down a critical component of the workflow.

The Reddit setback forced a fundamental rethinking of the trend discovery mechanism. Rather than treating it as a failure, I saw it as an opportunity to build something more resilient. The solution was to diversify beyond any single platform. I implemented Hacker News as the primary trend source, leveraging its reliable API and tech-focused community. To this, I added Product Hunt for product launch trends and Dev.to for developer content. This multi-source approach not only replaced the lost Reddit functionality but actually improved the system's robustness. If one source has limited data for a particular brand, others fill the gap.

The blog discovery process presented another persistent challenge. Early versions relied on pattern matching and domain guessing to find company blogs and RSS feeds. This worked for companies with obvious naming conventions but failed frequently for brands with unconventional blog locations or non-standard feed formats. The breakthrough came from applying AI to the problem itself. Rather than hardcoding patterns, Paracket now uses GPT-4o to intelligently suggest likely blog URLs based on company names and common patterns. The AI considers variations in naming, common subdomain structures, and even leverages knowledge about well-known companies. This approach dramatically improved the success rate of blog discovery.

Technical challenges extended to the nuances of each platform's API. Twitter's character limits required sophisticated text condensation that maintained meaning while fitting constraints. Mastodon's decentralized nature meant handling instance-specific variations. YouTube's transcript extraction needed to gracefully handle videos without captions, multiple language options, and auto-generated versus human transcripts. Each of these edge cases required careful handling to prevent the entire pipeline from failing due to a single problematic data source.
""")

# Current State
st.markdown("---")
st.header("Where Paracket Stands Today")

st.markdown("""
The current implementation of Paracket represents a mature, functional system that successfully addresses the core challenge of authentic, automated content creation. Users can analyze any brand's voice using YouTube videos and blog posts as primary sources, with optional Reddit data for those with active accounts. The AI-powered blog finder successfully locates RSS feeds for most companies, dramatically reducing the manual configuration required.

The content generation pipeline now pulls trends from three sources simultaneously—Hacker News, Product Hunt, and Dev.to—ensuring sufficient relevant topics for any tech-focused brand. The multi-platform adaptation system creates content optimized for Twitter's brevity, Mastodon's community focus, and Reddit's conversational depth. Each piece maintains the brand voice characteristics identified during analysis while respecting platform-specific conventions.

The scheduling infrastructure, powered by GitHub Actions, provides reliable time-based posting without requiring dedicated servers or complex infrastructure. Posts created in the Streamlit interface flow seamlessly through the system, get posted at the scheduled time, and report back their status. The entire process remains transparent to users through the Scheduled Posts interface, where they can monitor, edit, or cancel upcoming posts.

Perhaps most importantly, the system maintains a balance between automation and control. Users review and approve all generated content before scheduling. They can edit any aspect of the posts, adjust timing, or regenerate content that doesn't quite hit the mark. Paracket acts as an intelligent assistant rather than a black box, amplifying human creativity rather than replacing it.
""")

# Future Vision
st.markdown("---")
st.header("The Road Ahead")

st.markdown("""
The next phase of Paracket's evolution focuses on two major enhancements that will transform it from a content creation tool into a comprehensive social media management platform with learning capabilities.

The first priority involves restoring and improving Reddit integration. Once my account is unbanned, I'll rebuild the Reddit workflow with more sophisticated rate limiting and request patterns that respect platform guidelines. This isn't just about reinstating a lost feature—it's an opportunity to implement smarter data collection that adapts to API response patterns and proactively avoids behavior that triggers fraud detection. The new implementation will include better error handling, automatic backoff mechanisms, and more human-like interaction patterns.

The more ambitious enhancement involves adding a comprehensive analytics dashboard to the main page. This dashboard will integrate with each platform's API to track actual performance metrics for posts created by Paracket. Users will see impressions, engagement rates, click-throughs, and other key metrics directly within the application. But the dashboard serves a purpose beyond simple reporting—it becomes a feedback loop for the AI.

The vision is to create a self-improving system where Paracket learns from the performance of the content it generates. If certain voice characteristics or content structures consistently generate higher engagement, the system will weight those factors more heavily in future analysis and generation. If platform-specific adaptations perform differently across brands, the AI will adjust its approach accordingly. This transforms Paracket from a static content generator into an adaptive system that evolves with your brand and audience.

The machine learning component will analyze correlations between voice profile characteristics and engagement metrics. It will identify which topics resonate with which audiences, which posting times generate the most interaction, and which types of content adaptations work best for each platform. Over time, the brand voice profile becomes not just a snapshot of how you currently communicate, but a living model that incorporates what actually works.

This future vision maintains Paracket's core principle: augmenting human creativity rather than replacing it. The analytics and learning systems provide insights and suggestions, but users retain full control over their content and strategy. The goal is to make social media management not just easier, but genuinely more effective through intelligent automation that learns from real-world results.
""")

st.markdown("""
<div class="custom-info-box custom-box">
    <h3>Current Capabilities</h3>
    <p><strong>Data Sources:</strong> YouTube transcripts and descriptions, company blogs (AI-powered discovery), and optional Reddit content provide comprehensive brand voice samples.</p>
    <p><strong>Trend Discovery:</strong> Hacker News, Product Hunt, and Dev.to are monitored simultaneously to ensure sufficient relevant topics regardless of brand focus.</p>
    <p><strong>AI Technology:</strong> GPT-4o powers brand voice analysis, blog URL discovery, and multi-platform content generation with platform-specific optimization.</p>
    <p><strong>Supported Platforms:</strong> Twitter/X, Reddit, and Mastodon with automated posting via GitHub Actions scheduler.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-info-box custom-box">
    <h3>Key Capabilities</h3>
    <p><strong>Supported Platforms:</strong> Paracket currently supports posting to Twitter/X, Reddit, and Mastodon, with each platform receiving content optimized for its specific audience and format requirements.</p>
    <p><strong>Data Sources:</strong> The system analyzes content from YouTube transcripts and descriptions, Hacker News discussions, and company blogs to build a comprehensive understanding of your brand voice.</p>
    <p><strong>AI Technology:</strong> Powered by GPT-4o for both brand voice analysis and content generation, ensuring sophisticated understanding and high-quality output.</p>
</div>
""", unsafe_allow_html=True)

# How It Works
st.markdown("---")
st.header("How It Works")

tab1, tab2, tab3, tab4 = st.tabs(["1. Data Collection", "2. Voice Analysis", "3. Content Generation", "4. Multi-Platform Distribution"])

with tab1:
    st.markdown("""
    ### Data Collection Phase

    The data collection phase gathers authentic examples of your brand's communication across multiple platforms to build a comprehensive understanding of your voice.

    **Reddit Analysis**: Paracket searches for your official user accounts and subreddits, collecting posts and comments that demonstrate how your brand communicates in social settings. The system filters content for quality and relevance, ensuring only meaningful examples are included in the analysis.

    **YouTube Content**: The system locates your official YouTube channel and extracts video transcripts along with titles and descriptions. This captures your brand's authentic voice from spoken content, providing insights into how you communicate through video media.

    **Blog Content**: Paracket identifies RSS feeds from your company blog and scrapes full article content. This long-form writing style reveals how your brand communicates complex ideas and establishes thought leadership in your industry.

    The goal is to collect at least 150 samples from each source, providing sufficient data for comprehensive analysis and ensuring the brand voice profile accurately represents your communication style.
    """)

with tab2:
    st.markdown("""
    ### Brand Voice Analysis

    Using GPT-4o, Paracket performs deep analysis of your collected content to extract the unique characteristics that define your brand's communication style.

    **Tone and Personality**: The system examines your overall communication tone, identifying key personality traits and the emotional register you typically employ. This helps understand whether your brand is formal or casual, serious or playful, authoritative or approachable.

    **Language Patterns**: Paracket analyzes vocabulary level, sentence structure, and common phrases to understand how you construct messages. It identifies industry-specific jargon you use and how technical or accessible your language tends to be.

    **Content Themes**: The analysis identifies your main discussion topics, brand positioning, and core values as expressed through your communication. This reveals what subjects matter most to your brand and how you frame conversations in your industry.

    **Stylistic Elements**: The system examines your humor style, emoji usage, voice perspective (first person vs third person), and formatting preferences. These subtle elements contribute significantly to making your brand recognizable and distinctive.

    The output is a structured JSON profile containing over 10 distinct voice characteristics, providing a comprehensive blueprint for generating content that truly sounds like your brand.
    """)

with tab3:
    st.markdown("""
    ### Content Generation

    Paracket's content generation engine combines trend awareness with authentic brand voice to create engaging social media posts. The process begins with trend discovery, where the system continuously monitors Hacker News for trending topics in the technology and business space. This monitoring goes beyond simple keyword matching, using intelligent filters to assess relevance to your brand and industry while screening out controversial or inappropriate topics that could harm your brand reputation.

    Once relevant trends are identified, Paracket generates a master message that serves as the foundation for all platform-specific posts. This master message is carefully crafted to match your brand voice profile while naturally incorporating the trending topic. The AI ensures authenticity by avoiding fake product announcements or misleading claims, instead focusing on genuine commentary, insights, or perspectives that align with how your brand naturally participates in industry conversations.

    The platform adaptation process takes this master message and transforms it into optimized versions for each social media platform. For Twitter/X, content is condensed into a concise, punchy format that fits within the 280-character limit while maintaining impact. Reddit adaptations take a more detailed, conversational approach that fits the platform's discussion-oriented culture, encouraging meaningful engagement. Mastodon posts leverage the 500-character limit to provide community-focused messaging that resonates with the platform's collaborative ethos.

    Throughout this entire process, each platform-specific adaptation maintains the core elements of your brand voice while respecting the unique culture and expectations of each platform. This ensures your content feels native to each space while remaining unmistakably aligned with your brand identity.
    """)

with tab4:
    st.markdown("""
    ### Multi-Platform Distribution

    Paracket's distribution system provides comprehensive tools for managing and deploying your content across multiple social media platforms. Currently, the system offers essential features that allow you to preview all generated content before publication, ensuring you can review and approve posts while maintaining full control over your brand messaging. You can download posts as text files for record-keeping or further editing, and quickly copy content to your clipboard for immediate manual posting.

    The platform is designed with significant expansion capabilities in mind. Future enhancements will include direct posting to social accounts, eliminating the manual step and enabling true automation of your social media presence. Scheduling capabilities will allow you to plan content calendars in advance, posting at optimal times for maximum engagement. Engagement tracking will provide insights into how your audience interacts with your content, while A/B testing features will help identify which messaging approaches resonate most effectively. Performance analytics will give you a comprehensive view of your social media impact across all platforms.

    Paracket currently supports three major social media platforms, each with dedicated API integration. Twitter/X integration uses the official Twitter API to enable posting and engagement on the platform's fast-paced environment. Reddit integration leverages the Reddit API to participate in community discussions and share content in relevant subreddits. Mastodon integration uses the Mastodon API to connect with the decentralized social network's community-focused audience. Each platform integration is built with the platform's specific requirements and best practices in mind, ensuring seamless operation and compliance with API guidelines.
    """)

# Features Section
st.markdown("---")
st.header("Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Voice Analysis
    Paracket employs multi-source data collection to gather authentic examples of your brand communication. Using GPT-4o powered analysis, it creates a comprehensive voice profile that captures your unique style, tone, and messaging patterns with platform-specific insights.
    """)

with col2:
    st.markdown("""
    ### Trend Monitoring
    The system monitors real-time Hacker News trends to identify relevant conversation opportunities. Advanced topic relevance filtering and safety checks ensure you only engage with appropriate, brand-aligned discussions.
    """)

with col3:
    st.markdown("""
    ### Content Generation
    Generate authentic brand voice content that's platform-optimized and trend-aware. Every post maintains your unique communication style while being ready to publish across Twitter, Reddit, and Mastodon.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <p style='font-family: "Homemade Apple", cursive; color: #780000; font-size: 1.2rem; margin-bottom: 0.5rem;'>Paracket</p>
    <p style='color: #666; font-size: 0.9rem;'>Powered by GPT-4o | Built with Streamlit</p>
    <p style='color: #999; font-size: 0.85rem;'>Part of INFO7375 Assignment 9 - Northeastern University</p>
</div>
""", unsafe_allow_html=True)
