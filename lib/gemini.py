"""
Gemini AI Analyzer
Uses Google Gemini AI to analyze chat content and media.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .wrapper import GeminiWrapper
from .media import MediaAnalyzer


@dataclass
class ParticipantProfile:
    """Profile information for a single participant."""
    name: str
    personality_traits: List[str]
    communication_style: str
    likes: List[str]
    dislikes: List[str]
    interests: List[str]
    important_ideas: List[str]
    emotional_patterns: List[str]
    role_in_conversation: str
    activity_level: str
    influence_level: str


@dataclass
class ConversationAnalysis:
    """Results of conversation analysis."""
    total_messages: int
    participants: List[str]
    date_range: tuple
    sentiment_analysis: Dict[str, Any]
    topics: List[str]
    key_insights: List[str]
    relationship_dynamics: Dict[str, Any]
    media_summary: Dict[str, Any]
    participant_profiles: Dict[str, ParticipantProfile]


class GeminiAnalyzer:
    """Uses Google Gemini AI to analyze chat content and media."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-pro'):
        self.api_key = api_key
        self.gemini = GeminiWrapper(api_key, model_name)
        self.media_analyzer = None
    
    def set_media_analyzer(self, media_analyzer: MediaAnalyzer):
        """Set the media analyzer for file analysis."""
        self.media_analyzer = media_analyzer
    
    def analyze_conversation(self, messages: List[Any]) -> ConversationAnalysis:
        """Analyze the entire conversation using Gemini with chunking for large conversations."""
        print(f"Analyzing {len(messages)} messages...")
        
        # Extract basic info first
        participants = list(set(msg.author for msg in messages))
        timestamps = [msg.timestamp for msg in messages if msg.timestamp]
        date_range = (min(timestamps), max(timestamps)) if timestamps else ('', '')
        
        # Analyze media attachments
        media_summary = self._analyze_media_attachments(messages)
        
        # Chunk messages for analysis (max 2000 messages per chunk)
        chunk_size = 2000
        message_chunks = [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]
        
        print(f"Processing {len(message_chunks)} chunks of messages...")
        
        # Analyze each chunk
        chunk_analyses = []
        for i, chunk in enumerate(message_chunks):
            print(f"Analyzing chunk {i+1}/{len(message_chunks)} ({len(chunk)} messages)...")
            chunk_analysis = self._analyze_message_chunk(chunk, i+1, len(message_chunks))
            if chunk_analysis:
                chunk_analyses.append(chunk_analysis)
        
        # Combine chunk analyses
        if chunk_analyses:
            combined_analysis = self._combine_chunk_analyses(chunk_analyses, messages)
        else:
            print("No successful chunk analyses, creating fallback analysis...")
            combined_analysis = self._create_fallback_analysis(messages)
        
        # Generate participant profiles
        print("Generating detailed participant profiles...")
        participant_profiles = self._generate_participant_profiles(messages, combined_analysis, participants)
        
        # Print API usage statistics
        stats = self.gemini.get_stats()
        print(f"API Usage: {stats['total_requests']} requests made to {stats['model_name']}")
        
        return ConversationAnalysis(
            total_messages=len(messages),
            participants=participants,
            date_range=date_range,
            sentiment_analysis=combined_analysis.get('sentiment_analysis', {}),
            topics=combined_analysis.get('topics', []),
            key_insights=combined_analysis.get('key_insights', []),
            relationship_dynamics=combined_analysis.get('relationship_dynamics', {}),
            media_summary=media_summary,
            participant_profiles=participant_profiles
        )
    
    def _analyze_message_chunk(self, messages: List[Any], chunk_num: int, total_chunks: int) -> Optional[Dict]:
        """Analyze a chunk of messages using the Gemini wrapper."""
        # Convert ChatMessage objects to dictionaries for the wrapper
        message_dicts = []
        for msg in messages:
            message_dicts.append({
                'timestamp': msg.timestamp,
                'author': msg.author,
                'content': msg.content,
                'attachments': msg.attachments,
                'reactions': msg.reactions
            })
        
        # Use the wrapper to analyze the chunk
        return self.gemini.analyze_conversation_chunk(message_dicts, chunk_num, total_chunks)
    
    def _combine_chunk_analyses(self, chunk_analyses: List[Dict], all_messages: List[Any]) -> Dict:
        """Combine multiple chunk analyses into a comprehensive analysis."""
        print("Combining chunk analyses...")
        print(f"Number of chunk analyses: {len(chunk_analyses)}")
        
        # Debug: Check types of chunk analyses
        for i, analysis in enumerate(chunk_analyses):
            print(f"Chunk {i+1} type: {type(analysis)}")
            if isinstance(analysis, dict):
                print(f"Chunk {i+1} keys: {list(analysis.keys())}")
            else:
                print(f"Chunk {i+1} content: {str(analysis)[:200]}...")
        
        # Combine all topics
        all_topics = []
        for analysis in chunk_analyses:
            if isinstance(analysis, dict):
                topics = analysis.get('topics', [])
                if isinstance(topics, list):
                    all_topics.extend(topics)
        
        # Get unique topics and count frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by frequency and take top topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        main_topics = [topic for topic, count in sorted_topics[:15]]
        
        # Combine sentiment analysis
        sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
        participant_sentiments = {}
        emotional_highlights = []
        
        for analysis in chunk_analyses:
            if not isinstance(analysis, dict):
                print(f"Warning: Skipping non-dict analysis: {type(analysis)}")
                continue
                
            sentiment = analysis.get('sentiment_analysis', {})
            if not isinstance(sentiment, dict):
                print(f"Warning: sentiment_analysis is not a dict: {type(sentiment)}")
                continue
                
            overall = sentiment.get('overall_sentiment', 'neutral')
            if overall in sentiment_scores:
                sentiment_scores[overall] += 1
            
            # Combine participant sentiments
            participant_sentiment_data = sentiment.get('sentiment_by_participant', {})
            if isinstance(participant_sentiment_data, dict):
                for participant, sentiment_value in participant_sentiment_data.items():
                    if participant not in participant_sentiments:
                        participant_sentiments[participant] = []
                    participant_sentiments[participant].append(sentiment_value)
            
            # Collect emotional highlights
            highlights = sentiment.get('emotional_highlights', [])
            if isinstance(highlights, list):
                emotional_highlights.extend(highlights)
        
        # Determine overall sentiment
        overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        
        # Average participant sentiments
        avg_participant_sentiments = {}
        for participant, sentiments in participant_sentiments.items():
            # Simple majority vote for participant sentiment
            sentiment_counts = {}
            for sentiment in sentiments:
                # Extract main sentiment from detailed descriptions
                main_sentiment = 'neutral'
                if 'positive' in sentiment.lower():
                    main_sentiment = 'positive'
                elif 'negative' in sentiment.lower():
                    main_sentiment = 'negative'
                sentiment_counts[main_sentiment] = sentiment_counts.get(main_sentiment, 0) + 1
            avg_participant_sentiments[participant] = max(sentiment_counts, key=sentiment_counts.get)
        
        # Combine relationship dynamics
        all_insights = []
        communication_styles = []
        power_dynamics = []
        intimacy_levels = []
        
        for analysis in chunk_analyses:
            if not isinstance(analysis, dict):
                continue
                
            insights = analysis.get('key_insights', [])
            if isinstance(insights, list):
                all_insights.extend(insights)
            
            rd = analysis.get('relationship_dynamics', {})
            if isinstance(rd, dict):
                if rd.get('interaction_patterns'):
                    communication_styles.append(rd['interaction_patterns'])
                if rd.get('power_dynamics'):
                    power_dynamics.append(rd['power_dynamics'])
                if rd.get('intimacy_level'):
                    intimacy_levels.append(rd['intimacy_level'])
        
        # Create comprehensive analysis
        combined_analysis = {
            'sentiment_analysis': {
                'overall_sentiment': overall_sentiment,
                'sentiment_breakdown': sentiment_scores,
                'sentiment_by_participant': avg_participant_sentiments,
                'emotional_highlights': emotional_highlights[:10],  # Top 10 highlights
                'emotional_tone': f"Mixed emotional journey with {overall_sentiment} overall tone"
            },
            'topics': main_topics,
            'key_insights': list(set(all_insights))[:20],  # Unique insights, top 20
            'relationship_dynamics': {
                'communication_style': '; '.join(set(communication_styles))[:500],
                'power_dynamics': '; '.join(set(power_dynamics))[:500],
                'intimacy_level': '; '.join(set(intimacy_levels))[:500],
                'interaction_patterns': f"Analyzed {len(chunk_analyses)} conversation segments",
                'conflict_patterns': "Patterns observed across multiple conversation segments"
            },
            'conversation_flow': {
                'structure': f"Multi-segment conversation with {len(chunk_analyses)} distinct phases",
                'engagement_level': "high" if len(all_messages) > 1000 else "medium",
                'response_patterns': "Complex interaction patterns across extended conversation"
            }
        }
        
        return combined_analysis
    
    def _analyze_media_attachments(self, messages: List[Any]) -> Dict[str, Any]:
        """Analyze media attachments in the conversation."""
        if not self.media_analyzer:
            return {'error': 'Media analyzer not configured'}
        
        media_files = []
        for msg in messages:
            for attachment in msg.attachments:
                if attachment.startswith('files/'):
                    file_path = self.media_analyzer.files_directory / attachment
                    if file_path.exists():
                        analysis = self.media_analyzer.analyze_file(str(file_path))
                        media_files.append(analysis)
        
        # Categorize media
        media_types = {}
        for media in media_files:
            media_type = media.get('type', 'unknown')
            if media_type not in media_types:
                media_types[media_type] = []
            media_types[media_type].append(media)
        
        return {
            'total_files': len(media_files),
            'by_type': {k: len(v) for k, v in media_types.items()},
            'files': media_files
        }
    
    def _create_fallback_analysis(self, messages: List[Any]) -> Dict:
        """Create a basic analysis when Gemini fails."""
        participants = list(set(msg.author for msg in messages))
        timestamps = [msg.timestamp for msg in messages if msg.timestamp]
        date_range = (min(timestamps), max(timestamps)) if timestamps else ('', '')
        
        return {
            'sentiment_analysis': {
                'overall_sentiment': 'unknown',
                'error': 'Analysis failed'
            },
            'topics': [],
            'key_insights': ['Analysis could not be completed due to API error'],
            'relationship_dynamics': {},
            'media_summary': {'error': 'Media analysis not available'}
        }
    
    def _generate_participant_profiles(self, messages: List[Any], combined_analysis: Dict, participants: List[str]) -> Dict[str, ParticipantProfile]:
        """Generate detailed profiles for each participant."""
        profiles = {}
        
        for participant in participants:
            print(f"Creating profile for {participant}...")
            
            # Filter messages for this participant
            participant_messages = [msg for msg in messages if msg.author == participant]
            
            if not participant_messages:
                continue
            
            # Generate profile using Gemini
            profile_data = self._analyze_participant_profile(participant, participant_messages, combined_analysis)
            
            if profile_data:
                profiles[participant] = ParticipantProfile(
                    name=participant,
                    personality_traits=profile_data.get('personality_traits', []),
                    communication_style=profile_data.get('communication_style', 'Unknown'),
                    likes=profile_data.get('likes', []),
                    dislikes=profile_data.get('dislikes', []),
                    interests=profile_data.get('interests', []),
                    important_ideas=profile_data.get('important_ideas', []),
                    emotional_patterns=profile_data.get('emotional_patterns', []),
                    role_in_conversation=profile_data.get('role_in_conversation', 'Participant'),
                    activity_level=profile_data.get('activity_level', 'Medium'),
                    influence_level=profile_data.get('influence_level', 'Medium')
                )
            else:
                # Fallback profile
                profiles[participant] = ParticipantProfile(
                    name=participant,
                    personality_traits=['Unable to analyze'],
                    communication_style='Unknown',
                    likes=[],
                    dislikes=[],
                    interests=[],
                    important_ideas=[],
                    emotional_patterns=[],
                    role_in_conversation='Participant',
                    activity_level='Unknown',
                    influence_level='Unknown'
                )
        
        return profiles
    
    def _analyze_participant_profile(self, participant: str, messages: List[Any], context: Dict) -> Optional[Dict]:
        """Use Gemini to analyze a specific participant's profile."""
        # Prepare participant's message history
        participant_text = self._prepare_participant_messages(participant, messages)
        
        # Extract context from combined analysis
        overall_sentiment = context.get('sentiment_analysis', {}).get('overall_sentiment', 'unknown')
        main_topics = context.get('topics', [])[:10]  # Top 10 topics
        
        prompt = f"""
        Analyze this participant's profile based on their messages in a Discord conversation.

        Participant: {participant}
        Number of messages: {len(messages)}
        Overall conversation sentiment: {overall_sentiment}
        Main conversation topics: {', '.join(main_topics)}

        Participant's messages:
        {participant_text}

        Create a comprehensive profile analyzing:

        1. **Personality Traits**: Key characteristics that define this person
        2. **Communication Style**: How they express themselves
        3. **Likes/Interests**: Things they enjoy or are passionate about
        4. **Dislikes**: Things they dislike or complain about
        5. **Important Ideas**: Key concepts, beliefs, or values they express
        6. **Emotional Patterns**: How they typically express emotions
        7. **Role in Conversation**: Their function in the group dynamic
        8. **Activity & Influence**: How active and influential they are

        Provide detailed analysis in JSON format:
        {{
            "personality_traits": ["trait 1", "trait 2", "trait 3", "trait 4", "trait 5"],
            "communication_style": "detailed description of how they communicate",
            "likes": ["specific thing they like 1", "specific thing they like 2", "specific thing they like 3"],
            "dislikes": ["specific thing they dislike 1", "specific thing they dislike 2"],
            "interests": ["interest/hobby 1", "interest/hobby 2", "interest/hobby 3"],
            "important_ideas": ["key idea/belief 1", "key idea/belief 2", "key idea/belief 3"],
            "emotional_patterns": ["emotional pattern 1", "emotional pattern 2"],
            "role_in_conversation": "their role (e.g., leader, supporter, questioner, entertainer)",
            "activity_level": "high/medium/low - based on message frequency and engagement",
            "influence_level": "high/medium/low - based on how others respond to them"
        }}
        """
        
        return self.gemini.generate_content(prompt)
    
    def _prepare_participant_messages(self, participant: str, messages: List[Any]) -> str:
        """Prepare a participant's messages for analysis."""
        message_lines = []
        
        for msg in messages[:200]:  # Limit to last 200 messages for analysis
            # Extract time from timestamp
            timestamp = msg.timestamp or 'Unknown time'
            if ' ' in timestamp:
                timestamp = timestamp.split(' ')[-1]
            
            # Prepare content
            content = msg.content.strip() if msg.content else "[No text content]"
            
            line = f"[{timestamp}] {content}"
            
            # Add attachment info
            if msg.attachments:
                attachment_types = []
                for attachment in msg.attachments:
                    if any(ext in attachment.lower() for ext in ['.jpg', '.png', '.gif']):
                        attachment_types.append('image')
                    elif any(ext in attachment.lower() for ext in ['.mp4', '.avi', '.mov']):
                        attachment_types.append('video')
                    elif any(ext in attachment.lower() for ext in ['.ogg', '.mp3', '.wav']):
                        attachment_types.append('audio')
                    else:
                        attachment_types.append('file')
                line += f" [Shared: {', '.join(set(attachment_types))}]"
            
            # Add reaction info
            if msg.reactions:
                reaction_emojis = [r.get('emoji', '') for r in msg.reactions[:3]]
                line += f" [Reactions: {', '.join(reaction_emojis)}]"
            
            message_lines.append(line)
        
        return '\n'.join(message_lines)
