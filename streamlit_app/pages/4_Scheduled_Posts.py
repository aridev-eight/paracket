"""
Scheduled Posts Page
View and manage scheduled social media posts
"""
import streamlit as st
import os
import json
import glob
from datetime import datetime, time

st.set_page_config(
    page_title="Scheduled Posts - Paracket",
    page_icon="📅",
    layout="wide"
)

st.title("Scheduled Posts")
st.markdown("### View and manage your scheduled social media posts")

# Load all scheduled posts
scheduled_posts_dir = os.path.join('streamlit_app', 'data', 'scheduled_posts')
os.makedirs(scheduled_posts_dir, exist_ok=True)

# Try both paths (in case we're in streamlit_app directory)
pattern1 = os.path.join(scheduled_posts_dir, 'scheduled_*.json')
pattern2 = os.path.join('data', 'scheduled_posts', 'scheduled_*.json')

post_files = glob.glob(pattern1) or glob.glob(pattern2)

if not post_files:
    st.info("No scheduled posts yet. Create one in the **Content Generator** page!")
    st.stop()

# Load and parse posts
scheduled_posts = []
for file_path in post_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = json.load(f)
            post['file_path'] = file_path
            scheduled_posts.append(post)
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")

# Sort by scheduled time
scheduled_posts.sort(key=lambda x: x['scheduled_time'], reverse=True)

# Filter options
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    status_filter = st.multiselect(
        "Filter by status:",
        options=['active', 'inactive', 'posted', 'failed'],
        default=['active']
    )
with col2:
    st.metric("Total Posts", len(scheduled_posts))

# Filter posts
filtered_posts = [p for p in scheduled_posts if p.get('status', 'active') in status_filter]

st.markdown("---")

# Display posts
for post in filtered_posts:
    post_id = post['id']
    scheduled_time = datetime.fromisoformat(post['scheduled_time'])
    now = datetime.now()
    is_past = scheduled_time < now
    status = post.get('status', 'active')

    # Status indicator
    status_colors = {
        'active': '●',
        'inactive': '⚪',
        'posted': '●',
        'failed': '●'
    }
    status_icon = status_colors.get(status, '⚪')

    # Time indicator
    if is_past and status == 'active':
        time_indicator = "●"
        time_text = f"PAST DUE: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"
    elif status == 'posted':
        time_indicator = "[Posted]"
        time_text = f"Posted on {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"
    else:
        time_indicator = "●"
        time_text = f"Scheduled for {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"

    # Create expander for each post
    with st.expander(f"{status_icon} {post.get('company', 'Unknown')} - {post.get('theme', 'Untitled')} | {time_indicator} {time_text}"):

        # Show message if past due and active
        if is_past and status == 'active':
            minutes_past = int((now - scheduled_time).total_seconds() / 60)
            if minutes_past <= 10:
                st.info(f"Post is {minutes_past} minute(s) past due. The cron job runs every 5 minutes and will post it shortly.")
            else:
                st.warning(f"Post is {minutes_past} minutes past due. The cron job should have posted this already. Check the scheduler logs or update the schedule.")

        # Show post details
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Company:** {post.get('company', 'N/A')}")
            st.markdown(f"**Theme:** {post.get('theme', 'N/A')}")
            st.markdown(f"**Status:** {status.upper()}")
        with col2:
            st.markdown(f"**Created:** {datetime.fromisoformat(post['created_at']).strftime('%B %d, %Y')}")
            st.markdown(f"**Post ID:** `{post_id}`")

        # Master message
        st.markdown("---")
        st.markdown("**Master Message:**")
        st.info(post.get('master_message', 'N/A'))

        # Platform content
        st.markdown("**Platform-Specific Content:**")
        platforms = post.get('platforms', {})

        tabs_list = []
        if 'twitter' in platforms:
            tabs_list.append("Twitter")
        if 'mastodon' in platforms:
            tabs_list.append("Mastodon")
        if 'reddit' in platforms:
            tabs_list.append("Reddit")

        if tabs_list:
            tabs = st.tabs(tabs_list)

            tab_idx = 0
            if 'twitter' in platforms:
                with tabs[tab_idx]:
                    st.text_area("Twitter Content", value=platforms['twitter']['content'], height=100, key=f"view_twitter_{post_id}", disabled=True)
                    st.caption(f"Character count: {len(platforms['twitter']['content'])}/280")
                tab_idx += 1

            if 'mastodon' in platforms:
                with tabs[tab_idx]:
                    st.text_area("Mastodon Content", value=platforms['mastodon']['content'], height=120, key=f"view_mastodon_{post_id}", disabled=True)
                    st.caption(f"Character count: {len(platforms['mastodon']['content'])}/500")
                tab_idx += 1

            if 'reddit' in platforms:
                with tabs[tab_idx]:
                    st.text_area("Reddit Content", value=platforms['reddit']['content'], height=200, key=f"view_reddit_{post_id}", disabled=True)
                    st.caption(f"Target subreddit: r/{platforms['reddit'].get('subreddit', 'N/A')}")

        # Management actions
        st.markdown("---")
        st.markdown("**Actions:**")

        col1, col2, col3, col4 = st.columns(4)

        # Edit Schedule
        with col1:
            if st.button("Edit Schedule", key=f"edit_schedule_{post_id}", use_container_width=True):
                st.session_state[f'editing_schedule_{post_id}'] = True
                st.rerun()

        # Toggle Status
        with col2:
            if status == 'active':
                if st.button("Deactivate", key=f"deactivate_{post_id}", use_container_width=True):
                    post['status'] = 'inactive'
                    with open(post['file_path'], 'w', encoding='utf-8') as f:
                        json.dump(post, f, indent=2)
                    st.success("Post deactivated")
                    st.rerun()
            elif status == 'inactive':
                if st.button("Activate", key=f"activate_{post_id}", use_container_width=True):
                    post['status'] = 'active'
                    with open(post['file_path'], 'w', encoding='utf-8') as f:
                        json.dump(post, f, indent=2)
                    st.success("Post activated")
                    st.rerun()

        # Edit Content
        with col3:
            if st.button("Edit Content", key=f"edit_content_{post_id}", use_container_width=True):
                st.session_state[f'editing_content_{post_id}'] = True
                st.rerun()

        # Delete
        with col4:
            if st.button("Delete", key=f"delete_{post_id}", use_container_width=True):
                os.remove(post['file_path'])
                st.success("Post deleted")
                st.rerun()

        # Edit Schedule Form
        if st.session_state.get(f'editing_schedule_{post_id}'):
            st.markdown("---")
            st.markdown("**Update Schedule:**")

            current_dt = datetime.fromisoformat(post['scheduled_time'])

            # Convert current time to 12-hour format
            current_hour_24 = current_dt.hour
            current_am_pm = "AM" if current_hour_24 < 12 else "PM"
            current_hour_12 = current_hour_24 if current_hour_24 <= 12 else current_hour_24 - 12
            if current_hour_12 == 0:
                current_hour_12 = 12

            col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 1.5, 1.5])
            with col1:
                st.caption("Date")
                new_date = st.date_input("New Date", value=current_dt.date(), key=f"new_date_{post_id}", label_visibility="collapsed")
            with col2:
                st.caption("Hour")
                new_hour = st.number_input("Hour", min_value=1, max_value=12, value=current_hour_12, key=f"new_hour_{post_id}", label_visibility="collapsed")
            with col3:
                st.caption("Minute")
                new_minute = st.number_input("Min", min_value=0, max_value=59, value=current_dt.minute, key=f"new_minute_{post_id}", label_visibility="collapsed")
            with col4:
                st.caption("AM/PM")
                new_am_pm = st.selectbox("AM/PM", ["AM", "PM"], index=0 if current_am_pm == "AM" else 1, key=f"new_ampm_{post_id}", label_visibility="collapsed")
            with col5:
                st.caption(" ")  # Spacing for alignment
                if st.button("Save", key=f"save_schedule_{post_id}", use_container_width=True):
                    # Convert to 24-hour time
                    new_hour_24 = new_hour if new_am_pm == "AM" and new_hour != 12 else (0 if new_am_pm == "AM" and new_hour == 12 else (new_hour if new_hour == 12 else new_hour + 12))
                    new_time = time(new_hour_24, new_minute)
                    new_datetime = datetime.combine(new_date, new_time)
                    post['scheduled_time'] = new_datetime.isoformat()

                    with open(post['file_path'], 'w', encoding='utf-8') as f:
                        json.dump(post, f, indent=2)

                    st.session_state[f'editing_schedule_{post_id}'] = False
                    st.success(f"Schedule updated to {new_datetime.strftime('%B %d, %Y at %I:%M %p')}")
                    st.rerun()

            if st.button("Cancel", key=f"cancel_schedule_{post_id}"):
                st.session_state[f'editing_schedule_{post_id}'] = False
                st.rerun()

        # Edit Content Form
        if st.session_state.get(f'editing_content_{post_id}'):
            st.markdown("---")
            st.markdown("**Edit Content:**")

            # Edit master message
            new_master = st.text_area("Master Message", value=post.get('master_message', ''), height=150, key=f"edit_master_{post_id}")

            # Edit platform content
            if 'twitter' in platforms:
                st.markdown("**Twitter:**")
                new_twitter = st.text_area("Twitter Content", value=platforms['twitter']['content'], height=100, key=f"edit_twitter_content_{post_id}")
                st.caption(f"Character count: {len(new_twitter)}/280")

            if 'mastodon' in platforms:
                st.markdown("**Mastodon:**")
                new_mastodon = st.text_area("Mastodon Content", value=platforms['mastodon']['content'], height=120, key=f"edit_mastodon_content_{post_id}")
                st.caption(f"Character count: {len(new_mastodon)}/500")

            if 'reddit' in platforms:
                st.markdown("**Reddit:**")
                new_reddit = st.text_area("Reddit Content", value=platforms['reddit']['content'], height=200, key=f"edit_reddit_content_{post_id}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes", key=f"save_content_{post_id}", use_container_width=True):
                    post['master_message'] = new_master

                    if 'twitter' in platforms:
                        post['platforms']['twitter']['content'] = new_twitter
                    if 'mastodon' in platforms:
                        post['platforms']['mastodon']['content'] = new_mastodon
                    if 'reddit' in platforms:
                        post['platforms']['reddit']['content'] = new_reddit

                    with open(post['file_path'], 'w', encoding='utf-8') as f:
                        json.dump(post, f, indent=2)

                    st.session_state[f'editing_content_{post_id}'] = False
                    st.success("Content updated successfully")
                    st.rerun()

            with col2:
                if st.button("Cancel", key=f"cancel_content_{post_id}", use_container_width=True):
                    st.session_state[f'editing_content_{post_id}'] = False
                    st.rerun()

# Summary stats
st.markdown("---")
st.header("Summary")

# Calculate counts and categorize posts
active_posts = [p for p in scheduled_posts if p.get('status') == 'active']
inactive_posts = [p for p in scheduled_posts if p.get('status') == 'inactive']
posted_posts = [p for p in scheduled_posts if p.get('status') == 'posted']
failed_posts = [p for p in scheduled_posts if p.get('status') == 'failed']
past_due_posts = [p for p in scheduled_posts if datetime.fromisoformat(p['scheduled_time']) < datetime.now() and p.get('status') == 'active']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("● Active", len(active_posts))
with col2:
    st.metric("⚪ Inactive", len(inactive_posts))
with col3:
    st.metric("Posted", len(posted_posts))
with col4:
    st.metric("Failed", len(failed_posts))

# Detailed breakdown sections
st.markdown("---")
st.markdown("### Detailed Breakdown")

# Active Posts
if active_posts:
    with st.expander(f"Active Posts ({len(active_posts)})", expanded=False):
        for post in active_posts:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            st.markdown(f"**{post.get('company', 'Unknown')}** - {post.get('theme', 'Untitled')}")
            st.caption(f"Scheduled: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"ID: `{post['id']}`")
            st.markdown("---")

# Inactive Posts
if inactive_posts:
    with st.expander(f"Inactive Posts ({len(inactive_posts)})", expanded=False):
        for post in inactive_posts:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            st.markdown(f"**{post.get('company', 'Unknown')}** - {post.get('theme', 'Untitled')}")
            st.caption(f"Scheduled: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"ID: `{post['id']}`")
            st.markdown("---")

# Posted Posts
if posted_posts:
    with st.expander(f"Posted Posts ({len(posted_posts)})", expanded=False):
        for post in posted_posts:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            st.markdown(f"**{post.get('company', 'Unknown')}** - {post.get('theme', 'Untitled')}")
            st.caption(f"Posted: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"ID: `{post['id']}`")

            # Show which platforms it was posted to
            platforms = post.get('platforms', {}).keys()
            st.caption(f"Platforms: {', '.join(platforms).title()}")
            st.markdown("---")

# Failed Posts
if failed_posts:
    with st.expander(f"Failed Posts ({len(failed_posts)})", expanded=False):
        for post in failed_posts:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            st.markdown(f"**{post.get('company', 'Unknown')}** - {post.get('theme', 'Untitled')}")
            st.caption(f"Failed at: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"ID: `{post['id']}`")

            # Show error message if available
            if 'error' in post:
                st.error(f"Error: {post['error']}")
            st.markdown("---")

# Past Due Posts (subset of active)
if past_due_posts:
    with st.expander(f"Past Due Posts ({len(past_due_posts)})", expanded=True):
        st.warning("These posts are past their scheduled time but still marked as active. The scheduler should process them soon.")
        for post in past_due_posts:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            minutes_past = int((datetime.now() - scheduled_time).total_seconds() / 60)
            st.markdown(f"**{post.get('company', 'Unknown')}** - {post.get('theme', 'Untitled')}")
            st.caption(f"Scheduled: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"Past due by: {minutes_past} minutes")
            st.caption(f"ID: `{post['id']}`")
            st.markdown("---")
