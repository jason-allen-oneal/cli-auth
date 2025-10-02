"""
Gemini API Wrapper for Discord Chat Analysis
Handles API calls, retries, rate limiting, and error management.
"""

import json
import time
import random
from typing import Dict, List, Optional, Any
import google.generativeai as genai


class GeminiWrapper:
    """Wrapper class for Gemini API calls with retry logic and error handling."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-pro'):
        """Initialize the Gemini wrapper."""
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        # Initialize the model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate_content(self, prompt: str, max_retries: int = 3, 
                        retry_delay: int = 5, temperature: float = 0.7) -> Optional[Dict]:
        """
        Generate content using Gemini API with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            temperature: Model temperature for generation
            
        Returns:
            Parsed JSON response or None if failed
        """
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self._rate_limit()
                
                # Generate content
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=8192,
                    )
                )
                
                # Parse response
                parsed_response = self._parse_response(response.text)
                if parsed_response:
                    self.request_count += 1
                    return parsed_response
                
            except Exception as e:
                error_msg = str(e)
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {error_msg}")
                
                # Handle specific error types
                if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    # Quota/rate limit error - wait longer
                    wait_time = retry_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"Rate limit hit. Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                elif "timeout" in error_msg.lower():
                    # Timeout error - shorter wait
                    wait_time = retry_delay + random.uniform(1, 3)
                    print(f"Timeout error. Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    # Other errors - standard retry
                    if attempt < max_retries - 1:
                        wait_time = retry_delay + random.uniform(0, 2)
                        print(f"Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
        
        print(f"Failed to generate content after {max_retries} attempts")
        return None
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse the response text and extract JSON."""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Try to parse as JSON
            return json.loads(cleaned_text)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response (first 500 chars): {response_text[:500]}")
            
            # Try to extract JSON from the response
            try:
                # Look for JSON-like content between curly braces
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    return json.loads(json_text)
            except:
                pass
            
            return None
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            return None
    
    def analyze_conversation_chunk(self, messages: List[Dict], chunk_num: int, 
                                 total_chunks: int) -> Optional[Dict]:
        """
        Analyze a chunk of conversation messages.
        
        Args:
            messages: List of message dictionaries
            chunk_num: Current chunk number
            total_chunks: Total number of chunks
            
        Returns:
            Analysis results or None if failed
        """
        # Prepare conversation text
        conversation_text = self._prepare_conversation_text(messages)
        
        # Create analysis prompt
        prompt = f"""
        Analyze this portion of a Discord conversation (chunk {chunk_num} of {total_chunks}). 
        This contains {len(messages)} messages. Provide detailed insights on:
        
        1. Sentiment and emotional tone in this section
        2. Main topics and themes discussed
        3. Relationship dynamics and communication patterns
        4. Key events or moments
        5. Participant behaviors and characteristics
        
        Conversation chunk:
        {conversation_text}
        
        Please provide a detailed analysis in JSON format:
        {{
            "sentiment_analysis": {{
                "overall_sentiment": "positive/negative/neutral/mixed",
                "emotional_tone": "detailed description of emotional atmosphere",
                "sentiment_by_participant": {{"participant_name": "sentiment with reasoning"}},
                "emotional_highlights": ["key emotional moments or shifts"]
            }},
            "topics": ["specific topic 1", "specific topic 2", "specific topic 3"],
            "key_events": ["important event 1", "important event 2"],
            "participant_insights": {{
                "participant_name": {{
                    "communication_style": "description",
                    "key_behaviors": ["behavior 1", "behavior 2"],
                    "emotional_state": "description"
                }}
            }},
            "relationship_dynamics": {{
                "interaction_patterns": "description",
                "power_dynamics": "description", 
                "intimacy_level": "description",
                "conflict_resolution": "description"
            }},
            "key_insights": ["insight 1", "insight 2", "insight 3"]
        }}
        """
        
        return self.generate_content(prompt)
    
    def analyze_media_content(self, media_description: str) -> Optional[Dict]:
        """
        Analyze media content description.
        
        Args:
            media_description: Description of media files
            
        Returns:
            Media analysis results or None if failed
        """
        prompt = f"""
        Analyze the media content shared in this Discord conversation:
        
        {media_description}
        
        Provide insights on:
        1. Types of media shared
        2. Content themes and patterns
        3. Sharing behavior and frequency
        4. Relationship context of media sharing
        
        Return analysis in JSON format:
        {{
            "media_types": ["type1", "type2"],
            "content_themes": ["theme1", "theme2"],
            "sharing_patterns": "description",
            "relationship_context": "description",
            "insights": ["insight1", "insight2"]
        }}
        """
        
        return self.generate_content(prompt)
    
    def summarize_analysis(self, chunk_analyses: List[Dict], 
                          total_messages: int) -> Optional[Dict]:
        """
        Create a comprehensive summary from multiple chunk analyses.
        
        Args:
            chunk_analyses: List of chunk analysis results
            total_messages: Total number of messages analyzed
            
        Returns:
            Comprehensive summary or None if failed
        """
        # Prepare summary data
        summary_data = {
            "total_chunks": len(chunk_analyses),
            "total_messages": total_messages,
            "chunk_summaries": []
        }
        
        for i, analysis in enumerate(chunk_analyses):
            if analysis:
                summary_data["chunk_summaries"].append({
                    "chunk_number": i + 1,
                    "topics": analysis.get("topics", []),
                    "sentiment": analysis.get("sentiment_analysis", {}).get("overall_sentiment", "unknown"),
                    "key_insights": analysis.get("key_insights", [])
                })
        
        prompt = f"""
        Create a comprehensive summary of this Discord conversation analysis.
        
        Analysis data:
        {json.dumps(summary_data, indent=2)}
        
        Provide a final comprehensive analysis in JSON format:
        {{
            "executive_summary": "Overall summary of the conversation",
            "relationship_overview": "Description of the relationship dynamics",
            "communication_patterns": "How participants communicate",
            "emotional_journey": "Description of emotional progression",
            "key_themes": ["main theme 1", "main theme 2"],
            "notable_events": ["significant event 1", "significant event 2"],
            "participant_profiles": {{
                "participant_name": {{
                    "personality_traits": ["trait1", "trait2"],
                    "communication_style": "description",
                    "role_in_relationship": "description"
                }}
            }},
            "relationship_health": "assessment of relationship dynamics",
            "recommendations": ["recommendation 1", "recommendation 2"]
        }}
        """
        
        return self.generate_content(prompt)
    
    def _prepare_conversation_text(self, messages: List[Dict]) -> str:
        """Prepare conversation text for analysis."""
        conversation_lines = []
        
        for msg in messages:
            # Extract time from timestamp
            timestamp = msg.get('timestamp', 'Unknown time')
            if ' ' in timestamp:
                timestamp = timestamp.split(' ')[-1]
            
            # Clean author name
            author = msg.get('author', 'Unknown')
            author = author.replace('7h3 R3v3n4n7', 'Jason').replace('whatsfappening', 'Sarah')
            
            # Prepare content
            content = msg.get('content', '').strip()
            if not content:
                content = "[No text content]"
            
            line = f"[{timestamp}] {author}: {content}"
            
            # Add attachment info
            attachments = msg.get('attachments', [])
            if attachments:
                attachment_types = []
                for attachment in attachments:
                    if attachment.endswith(('.jpg', '.png', '.gif')):
                        attachment_types.append('image')
                    elif attachment.endswith(('.mp4', '.avi', '.mov')):
                        attachment_types.append('video')
                    elif attachment.endswith(('.ogg', '.mp3', '.wav')):
                        attachment_types.append('audio')
                    else:
                        attachment_types.append('file')
                line += f" [Shared: {', '.join(set(attachment_types))}]"
            
            # Add reaction info
            reactions = msg.get('reactions', [])
            if reactions:
                reaction_emojis = [r.get('emoji', '') for r in reactions[:3]]
                line += f" [Reactions: {', '.join(reaction_emojis)}]"
            
            conversation_lines.append(line)
        
        # Limit total length
        full_text = '\n'.join(conversation_lines)
        if len(full_text) > 100000:
            lines = conversation_lines
            mid_point = len(lines) // 2
            selected_lines = lines[:mid_point//2] + lines[mid_point + mid_point//2:]
            full_text = '\n'.join(selected_lines)
            full_text = f"[Note: This is a condensed version of {len(messages)} messages]\n\n{full_text}"
        
        return full_text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about API usage."""
        return {
            "total_requests": self.request_count,
            "model_name": self.model_name,
            "last_request_time": self.last_request_time
        }
