"""
Brand Voice Analyzer Module
Refactored from brand_voice_ml_openai.py for Streamlit integration
"""
from openai import OpenAI
import os
import json
from datetime import datetime


def analyze_brand_voice(training_data, openai_api_key=None):
    """
    Analyze training data to extract brand voice characteristics
    Uses GPT-4o to identify patterns in tone, style, topics, etc.

    Args:
        training_data: List of dicts with 'source' and 'samples'
        openai_api_key: OpenAI API key

    Returns:
        Dict with brand voice characteristics
    """

    if not openai_api_key:
        openai_api_key = os.environ.get('OPENAI_API_KEY')

    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    # Create OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Prepare sample texts for analysis
    sample_texts = []

    # Take samples from each source
    for source_data in training_data:
        source = source_data.get('source', 'unknown')
        samples = source_data.get('samples', [])

        # Take first 20 samples from each source for analysis
        for sample in samples[:20]:
            text = sample.get('text', '')
            if len(text) > 100:  # Only meaningful content
                sample_texts.append({
                    'source': source,
                    'text': text[:2000]  # Limit length for API efficiency
                })

    if not sample_texts:
        raise ValueError("No valid training data found")

    # Create analysis prompt
    prompt = f"""You are a brand voice analyst. Analyze these {len(sample_texts)} samples from a company's content across different platforms (blog, reddit, youtube, social media).

TRAINING SAMPLES:
"""

    for i, sample in enumerate(sample_texts[:50]):  # Limit to 50 samples
        prompt += f"\n--- Sample {i+1} ({sample['source']}) ---\n{sample['text']}\n"

    prompt += """

Analyze this company's brand voice and provide a structured profile:

1. TONE & PERSONALITY
   - Overall tone (professional, casual, technical, friendly, etc.)
   - Personality traits
   - Emotional register

2. LANGUAGE PATTERNS
   - Vocabulary level (simple, technical, academic)
   - Sentence structure (short/punchy vs long/complex)
   - Common phrases or expressions
   - Use of jargon or industry terms

3. CONTENT THEMES
   - Main topics they discuss
   - How they position themselves
   - What values they emphasize

4. STYLISTIC ELEMENTS
   - Use of humor, emojis, exclamation marks
   - First person vs third person
   - Active vs passive voice
   - Formatting preferences

5. AUDIENCE APPROACH
   - How they address their audience
   - Level of formality
   - Educational vs promotional

6. PLATFORM VARIATIONS
   - Differences between blog, social, video content
   - Adaptation strategies

Provide your analysis in valid JSON format with these keys:
{
  "tone": "...",
  "personality_traits": ["trait1", "trait2", ...],
  "vocabulary_level": "...",
  "sentence_style": "...",
  "common_phrases": ["phrase1", "phrase2", ...],
  "main_topics": ["topic1", "topic2", ...],
  "values": ["value1", "value2", ...],
  "humor_style": "...",
  "formality_level": "...",
  "voice_consistency": "...",
  "writing_guidelines": ["guideline1", "guideline2", ...]
}

Return ONLY valid JSON, no additional text.
"""

    # Call OpenAI API using client
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a brand voice analyst. Return only valid JSON with no additional text or markdown formatting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=4096
    )

    # Parse response
    response_text = response.choices[0].message.content

    # Extract JSON from response
    try:
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]

        # Try to find JSON in the response
        response_text = response_text.strip()
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            brand_voice = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        print(f"Warning: Could not parse JSON: {e}")
        brand_voice = {
            "raw_analysis": response_text,
            "error": f"Could not parse structured JSON: {str(e)}"
        }

    return brand_voice


def analyze_brand_voice_endpoint(company, training_data, openai_api_key=None):
    """
    Main function to analyze brand voice from training data

    Args:
        company: Company name
        training_data: List of dicts with 'source' and 'samples'
        openai_api_key: OpenAI API key

    Returns:
        Dict with company, brand_voice, analyzed_at, etc.
    """
    try:
        print(f"\n{'='*50}")
        print(f"BRAND VOICE ANALYZER: {company}")
        print(f"{'='*50}\n")

        if not training_data:
            return {
                'error': 'No valid training data found',
                'success': False
            }

        # Count total samples
        total_samples = sum(
            td.get('total_samples', len(td.get('samples', [])))
            for td in training_data
        )

        print(f"\nAnalyzing {total_samples} total samples...\n")

        # Analyze brand voice
        brand_voice = analyze_brand_voice(training_data, openai_api_key)

        # Save brand voice profile
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_safe = company.replace(' ', '_').replace('/', '_')
        profile_filename = f"brand_voice_{company_safe}_{timestamp}.json"

        profile_data = {
            'company': company,
            'brand_voice': brand_voice,
            'analyzed_at': datetime.now().isoformat(),
            'total_samples_analyzed': total_samples,
            'sources': [td.get('source', 'unknown') for td in training_data]
        }

        # Save to data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        save_path = os.path.join(data_dir, profile_filename)

        # Delete old analyses for this company (keep only the most recent)
        existing_files = [f for f in os.listdir(data_dir) if f.startswith(f'brand_voice_{company_safe}_') and f.endswith('.json')]
        for old_file in existing_files:
            old_path = os.path.join(data_dir, old_file)
            try:
                os.remove(old_path)
                print(f"Deleted old analysis: {old_file}")
            except Exception as e:
                print(f"Warning: Could not delete old file {old_file}: {e}")

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2)

        print(f"\n{'='*50}")
        print(f"✓ Brand voice profile saved: {profile_filename}")
        print(f"{'='*50}\n")

        result = {
            'company': company,
            'brand_voice': brand_voice,
            'analyzed_at': datetime.now().isoformat(),
            'total_samples_analyzed': total_samples,
            'profile_file': profile_filename,
            'sources_analyzed': [td.get('source', 'unknown') for td in training_data],
            'success': True
        }

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'success': False
        }


def generate_post_ideas(company, brand_voice, trending_topics, num_ideas=3, openai_api_key=None):
    """
    Generate complete post draft ideas from trending topics

    Args:
        company: Company name
        brand_voice: Brand voice profile dict
        trending_topics: List of trending topic dicts
        num_ideas: Number of post ideas to generate (default 3)
        openai_api_key: OpenAI API key

    Returns:
        Dict with post ideas
    """
    try:
        print(f"\n{'='*50}")
        print(f"POST IDEA GENERATOR: {company}")
        print(f"{'='*50}\n")

        if not openai_api_key:
            openai_api_key = os.environ.get('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Prepare trending topics summary
        topics_summary = []
        for i, topic in enumerate(trending_topics[:20], 1):  # Limit to 20 topics
            topics_summary.append({
                'id': i,
                'title': topic.get('text', '')[:300],
                'type': topic.get('metadata', {}).get('topic_type', 'discussion'),
                'engagement': topic.get('metadata', {}).get('engagement', 0),
                'subreddit': topic.get('metadata', {}).get('subreddit', 'unknown')
            })

        # Create generation prompt
        generation_prompt = f"""You are a content strategist for {company}. Analyze these {len(topics_summary)} trending topics and generate {num_ideas} complete, ready-to-use social media post drafts.

COMPANY CONTEXT:
Brand Voice: {json.dumps(brand_voice, indent=2)[:1500]}...

TRENDING TOPICS:
{json.dumps(topics_summary, indent=2)}

CRITICAL RULES - MUST FOLLOW:
❌ DO NOT announce new products, features, or capabilities
❌ DO NOT make claims about what {company} is doing/building/releasing
❌ DO NOT create fake news or announcements
❌ DO NOT promise future developments or roadmap items

✅ DO provide commentary, insights, or opinions on trending topics
✅ DO share thoughts on industry trends and discussions
✅ DO ask questions to engage the community
✅ DO share general expertise related to the topics
✅ DO reference publicly known information only

TASK:
Create {num_ideas} strategic post ideas that:
1. COMMENT ON or DISCUSS the trending topics (not announce products)
2. Provide thought leadership, insights, or ask engaging questions
3. Match {company}'s brand voice EXACTLY (tone, style, personality)
4. Add value through expertise, perspective, or community engagement
5. Feel natural and conversational
6. Are ready to post with minimal editing

Post types to consider:
- Industry commentary/opinion pieces
- "What do you think about..." discussion starters
- Sharing insights or tips related to the trending topics
- Asking the community for their experiences
- Educational content related to the trends

Each post should be 150-300 words (suitable for adaptation to different platforms later).

For each post idea, provide:
- The actual post content (complete draft)
- Which trending topic(s) it addresses (by ID)
- The strategic theme/angle
- Why this would resonate with the audience

Return ONLY valid JSON in this format:
{{
  "post_ideas": [
    {{
      "content": "The complete post text here...",
      "topic_ids": [1, 3],
      "theme": "Brief description of the theme",
      "rationale": "Why this post would work well",
      "estimated_engagement": "high/medium/low"
    }}
  ]
}}

Return ONLY valid JSON, no additional text.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a content strategist for {company}. Write in their exact brand voice. NEVER announce fake products or features. Only provide commentary, insights, and thought leadership on existing topics and trends. Return only valid JSON with no additional text or markdown formatting."
                },
                {
                    "role": "user",
                    "content": generation_prompt
                }
            ],
            temperature=0.75,
            max_tokens=3000
        )

        # Parse response
        response_text = response.choices[0].message.content

        # Extract JSON from response
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]

            # Try to find JSON in the response
            response_text = response_text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                post_ideas = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Warning: Could not parse JSON: {e}")
            post_ideas = {
                "raw_analysis": response_text,
                "error": f"Could not parse structured JSON: {str(e)}"
            }

        print(f"\n✓ Generated {len(post_ideas.get('post_ideas', []))} post ideas")

        result = {
            'company': company,
            'post_ideas': post_ideas,
            'total_topics_analyzed': len(topics_summary),
            'generated_at': datetime.now().isoformat(),
            'success': True
        }

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'success': False
        }


def recommend_topic_combinations(company, brand_voice, trending_topics, num_combinations=5, openai_api_key=None):
    """
    Analyze trending topics and recommend combinations that work well together

    Args:
        company: Company name
        brand_voice: Brand voice profile dict
        trending_topics: List of trending topic dicts
        num_combinations: Number of combinations to recommend (default 5)
        openai_api_key: OpenAI API key

    Returns:
        Dict with recommended combinations
    """
    try:
        print(f"\n{'='*50}")
        print(f"TOPIC COMBINATION ANALYZER: {company}")
        print(f"{'='*50}\n")

        if not openai_api_key:
            openai_api_key = os.environ.get('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Prepare trending topics summary
        topics_summary = []
        for i, topic in enumerate(trending_topics[:20], 1):  # Limit to 20 topics
            topics_summary.append({
                'id': i,
                'title': topic.get('text', '')[:200],
                'type': topic.get('metadata', {}).get('topic_type', 'discussion'),
                'engagement': topic.get('metadata', {}).get('engagement', 0),
                'subreddit': topic.get('metadata', {}).get('subreddit', 'unknown')
            })

        # Create analysis prompt
        analysis_prompt = f"""You are a content strategy expert. Analyze these {len(topics_summary)} trending topics for {company} and recommend {num_combinations} strategic topic combinations that would make compelling, coherent social media posts.

COMPANY CONTEXT:
Brand Voice: {json.dumps(brand_voice, indent=2)[:1000]}...

TRENDING TOPICS:
{json.dumps(topics_summary, indent=2)}

TASK:
Recommend {num_combinations} topic combinations (each with 1-4 related topics) that:
1. Work well together thematically
2. Align with {company}'s brand voice and expertise areas
3. Would create engaging, valuable content (not just promotional)
4. Avoid controversial or sensitive topics
5. Provide thought leadership opportunities

For each combination, provide:
- Topic IDs to combine
- A brief rationale (why these topics work together)
- A suggested angle/narrative
- Content potential score (1-10)

Return ONLY valid JSON in this format:
{{
  "combinations": [
    {{
      "topic_ids": [1, 3, 7],
      "topics_preview": ["topic 1 title...", "topic 3 title...", "topic 7 title..."],
      "rationale": "Why these topics work together",
      "suggested_angle": "How to approach this combination",
      "content_potential": 9,
      "target_platforms": ["twitter", "mastodon", "reddit"]
    }}
  ]
}}

Return ONLY valid JSON, no additional text.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a content strategy expert specializing in social media and thought leadership. Return only valid JSON with no additional text or markdown formatting."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            temperature=0.8,
            max_tokens=2048
        )

        # Parse response
        response_text = response.choices[0].message.content

        # Extract JSON from response
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]

            # Try to find JSON in the response
            response_text = response_text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                recommendations = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Warning: Could not parse JSON: {e}")
            recommendations = {
                "raw_analysis": response_text,
                "error": f"Could not parse structured JSON: {str(e)}"
            }

        print(f"\n✓ Generated {len(recommendations.get('combinations', []))} topic combinations")

        result = {
            'company': company,
            'recommendations': recommendations,
            'total_topics_analyzed': len(topics_summary),
            'analyzed_at': datetime.now().isoformat(),
            'success': True
        }

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'success': False
        }


def adapt_master_to_platforms(company, brand_voice, master_message, platforms=['twitter', 'reddit', 'mastodon'], openai_api_key=None):
    """
    Adapt a master message to different social media platforms

    Args:
        company: Company name
        brand_voice: Brand voice profile dict
        master_message: The master message to adapt
        platforms: List of platforms to adapt for
        openai_api_key: OpenAI API key

    Returns:
        Dict with platform-specific adaptations
    """
    try:
        print(f"\n{'='*50}")
        print(f"PLATFORM ADAPTER: {company}")
        print(f"{'='*50}\n")

        if not openai_api_key:
            openai_api_key = os.environ.get('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)

        platform_specs = {
            'twitter': {
                'max_length': 280,
                'style': 'Concise, punchy, engaging. Use line breaks for readability. May include 1-2 relevant hashtags.',
                'format': 'Short-form microblog'
            },
            'mastodon': {
                'max_length': 500,
                'style': 'Conversational, community-focused. Include 3-5 relevant hashtags. More detailed than Twitter.',
                'format': 'Medium-form social post'
            },
            'reddit': {
                'max_length': 2000,
                'style': 'Detailed, conversational, authentic. The FIRST LINE is the post title (no markdown, no "Title:" prefix). The rest is the body (2-4 paragraphs). No hashtags.',
                'format': 'Long-form discussion post with title on first line'
            }
        }

        adaptations = {}

        for platform in platforms:
            if platform not in platform_specs:
                print(f"  Skipping unknown platform: {platform}")
                continue

            spec = platform_specs[platform]
            print(f"  Adapting for {platform}...")

            # Build platform-specific instructions
            reddit_instructions = """For Reddit:
FIRST LINE = Title only (plain text, no markdown, no 'Title:' prefix)
REMAINING LINES = Body paragraphs

Example format:
Your Engaging Title Here

First paragraph of your post...

Second paragraph continues..."""

            platform_specific = reddit_instructions if platform == 'reddit' else ""

            adaptation_prompt = f"""You are adapting content for {company} to be posted on {platform}.

BRAND VOICE PROFILE:
{json.dumps(brand_voice, indent=2)[:1000]}...

MASTER MESSAGE:
{master_message}

PLATFORM: {platform}
STYLE: {spec['style']}
FORMAT: {spec['format']}
MAX LENGTH: {spec['max_length']} characters

TASK:
Adapt the master message for {platform} while:
1. Maintaining {company}'s exact brand voice
2. Following {platform}'s culture and best practices
3. Staying within {spec['max_length']} characters
4. Keeping the core message and value intact
5. Making it native to the platform (not just shortened/lengthened)

{platform_specific}

Return ONLY the adapted content, no explanations or meta-commentary.
"""

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a social media expert for {company}. Adapt content to different platforms while maintaining brand voice. Return only the adapted content."
                    },
                    {
                        "role": "user",
                        "content": adaptation_prompt
                    }
                ],
                temperature=0.75,
                max_tokens=1500
            )

            adapted_content = response.choices[0].message.content.strip()

            # Remove quotes if GPT wrapped the content
            if adapted_content.startswith('"') and adapted_content.endswith('"'):
                adapted_content = adapted_content[1:-1]

            # Trim if too long
            if len(adapted_content) > spec['max_length']:
                adapted_content = adapted_content[:spec['max_length']-3] + "..."

            adaptations[platform] = {
                'content': adapted_content,
                'length': len(adapted_content),
                'max_length': spec['max_length']
            }

            print(f"    ✓ {len(adapted_content)}/{spec['max_length']} characters")

        result = {
            'company': company,
            'master_message': master_message,
            'adaptations': adaptations,
            'platforms': list(adaptations.keys()),
            'adapted_at': datetime.now().isoformat(),
            'success': True
        }

        print(f"\n✓ Adapted to {len(adaptations)} platforms")
        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'success': False
        }


def generate_content(company, brand_voice, prompt, platform='general', max_length=500, openai_api_key=None):
    """
    Generate content in the brand's voice

    Args:
        company: Company name
        brand_voice: Brand voice profile dict
        prompt: Content generation prompt
        platform: Target platform (twitter, linkedin, general, etc.)
        max_length: Maximum content length
        openai_api_key: OpenAI API key

    Returns:
        Dict with company, platform, content, etc.
    """
    try:
        print(f"\n{'='*50}")
        print(f"CONTENT GENERATOR: {company} for {platform}")
        print(f"{'='*50}\n")

        if not openai_api_key:
            openai_api_key = os.environ.get('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Create generation prompt
        generation_prompt = f"""You are a content writer for {company}. Generate content that matches their brand voice EXACTLY.

BRAND VOICE PROFILE:
{json.dumps(brand_voice, indent=2)}

TASK:
{prompt}

PLATFORM: {platform}
MAX LENGTH: {max_length} characters

REQUIREMENTS:
- Match the tone and personality EXACTLY
- Use similar language patterns and vocabulary
- Follow the writing guidelines
- Stay within {max_length} characters
- Make it platform-appropriate for {platform}

Generate ONLY the content, no explanations or meta-commentary.
"""

        # Call OpenAI API using client
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a content writer for {company}. Match their brand voice exactly. Return only the content, no explanations."
                },
                {
                    "role": "user",
                    "content": generation_prompt
                }
            ],
            temperature=0.8,
            max_tokens=2048
        )

        generated_content = response.choices[0].message.content.strip()

        # Remove quotes if GPT wrapped the content
        if generated_content.startswith('"') and generated_content.endswith('"'):
            generated_content = generated_content[1:-1]

        # Trim if too long
        if len(generated_content) > max_length:
            generated_content = generated_content[:max_length-3] + "..."

        print(f"\n✓ Generated {len(generated_content)} characters")
        print(f"\n{generated_content}\n")

        result = {
            'company': company,
            'platform': platform,
            'content': generated_content,
            'length': len(generated_content),
            'generated_at': datetime.now().isoformat(),
            'prompt': prompt,
            'success': True
        }

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'success': False
        }
