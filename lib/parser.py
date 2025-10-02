"""
Discord HTML Parser
Extracts chat messages and metadata from Discord HTML exports.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class ChatMessage:
    """Represents a single chat message with all its metadata."""
    message_id: str
    author: str
    author_id: str
    timestamp: str
    content: str
    attachments: List[str]
    reactions: List[Dict[str, Any]]
    reply_to: Optional[str] = None
    edited: bool = False
    edited_timestamp: Optional[str] = None


class DiscordHTMLParser:
    """Parses Discord HTML export files to extract chat data."""
    
    def __init__(self, html_file_path: str):
        self.html_file_path = html_file_path
        self.soup = None
        self.messages = []
        
    def parse(self) -> List[ChatMessage]:
        """Parse the HTML file and extract all messages."""
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.soup = BeautifulSoup(content, 'html.parser')
        self._extract_messages()
        return self.messages
    
    def _extract_messages(self):
        """Extract messages from the parsed HTML."""
        message_groups = self.soup.find_all('div', class_='chatlog__message-group')
        
        for group in message_groups:
            message_containers = group.find_all('div', class_='chatlog__message-container')
            
            for container in message_containers:
                message = self._parse_message_container(container)
                if message:
                    self.messages.append(message)
    
    def _parse_message_container(self, container) -> Optional[ChatMessage]:
        """Parse a single message container."""
        try:
            # Extract message ID
            message_id = container.get('data-message-id', '')
            
            # Find the main message div
            message_div = container.find('div', class_='chatlog__message')
            if not message_div:
                return None
            
            # Extract author information
            author_span = message_div.find('span', class_='chatlog__author')
            author = author_span.text.strip() if author_span else 'Unknown'
            author_id = author_span.get('data-user-id', '') if author_span else ''
            
            # Extract timestamp
            timestamp_span = message_div.find('span', class_='chatlog__timestamp')
            timestamp = timestamp_span.get('title', '') if timestamp_span else ''
            
            # Extract content
            content_div = message_div.find('div', class_='chatlog__content')
            content = self._extract_message_content(content_div) if content_div else ''
            
            # Extract attachments
            attachments = self._extract_attachments(message_div)
            
            # Extract reactions
            reactions = self._extract_reactions(message_div)
            
            # Check if message is edited
            edited_span = message_div.find('span', class_='chatlog__edited-timestamp')
            edited = edited_span is not None
            edited_timestamp = edited_span.get('title', '') if edited_span else None
            
            # Check for reply
            reply_div = message_div.find('div', class_='chatlog__reply')
            reply_to = None
            if reply_div:
                reply_link = reply_div.find('span', class_='chatlog__reply-link')
                if reply_link and reply_link.get('onclick'):
                    # Extract message ID from onclick
                    onclick = reply_link.get('onclick')
                    match = re.search(r"scrollToMessage\(event,'(\d+)'\)", onclick)
                    if match:
                        reply_to = match.group(1)
            
            return ChatMessage(
                message_id=message_id,
                author=author,
                author_id=author_id,
                timestamp=timestamp,
                content=content,
                attachments=attachments,
                reactions=reactions,
                reply_to=reply_to,
                edited=edited,
                edited_timestamp=edited_timestamp
            )
            
        except Exception as e:
            print(f"Error parsing message container: {e}")
            return None
    
    def _extract_message_content(self, content_div) -> str:
        """Extract text content from message, handling markdown and emojis."""
        if not content_div:
            return ''
        
        # Remove HTML tags but preserve text content
        text_parts = []
        
        for element in content_div.find_all(['span', 'img']):
            if element.name == 'span':
                text_parts.append(element.get_text())
            elif element.name == 'img' and 'emoji' in element.get('class', []):
                # Handle emoji images
                alt_text = element.get('alt', '')
                title = element.get('title', '')
                if alt_text:
                    text_parts.append(alt_text)
                elif title:
                    text_parts.append(title)
        
        return ' '.join(text_parts).strip()
    
    def _extract_attachments(self, message_div) -> List[str]:
        """Extract attachment file paths from message."""
        attachments = []
        attachment_divs = message_div.find_all('div', class_='chatlog__attachment')
        
        for attachment_div in attachment_divs:
            # Look for various media types
            media_elements = attachment_div.find_all(['img', 'video', 'audio'])
            for media in media_elements:
                src = media.get('src')
                if src:
                    attachments.append(src)
            
            # Look for generic attachments
            generic_div = attachment_div.find('div', class_='chatlog__attachment-generic')
            if generic_div:
                # Extract filename from generic attachment
                name_div = generic_div.find('div', class_='chatlog__attachment-generic-name')
                if name_div:
                    attachments.append(name_div.text.strip())
        
        return attachments
    
    def _extract_reactions(self, message_div) -> List[Dict[str, Any]]:
        """Extract reactions from message."""
        reactions = []
        reactions_div = message_div.find_all('div', class_='chatlog__reactions')
        
        if reactions_div:
            reaction_divs = reactions_div[0].find_all('div', class_='chatlog__reaction')
            for reaction_div in reaction_divs:
                # Extract emoji and count
                emoji_img = reaction_div.find('img')
                count_span = reaction_div.find('span', class_='chatlog__reaction-count')
                
                emoji = ''
                if emoji_img:
                    emoji = emoji_img.get('alt', '') or emoji_img.get('title', '')
                
                count = 0
                if count_span:
                    try:
                        count = int(count_span.text.strip())
                    except ValueError:
                        pass
                
                if emoji:
                    reactions.append({'emoji': emoji, 'count': count})
        
        return reactions
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the parsed conversation."""
        if not self.messages:
            return {}
        
        participants = list(set(msg.author for msg in self.messages))
        timestamps = [msg.timestamp for msg in self.messages if msg.timestamp]
        
        # Count messages by participant
        message_counts = {}
        for msg in self.messages:
            message_counts[msg.author] = message_counts.get(msg.author, 0) + 1
        
        # Count attachments
        total_attachments = sum(len(msg.attachments) for msg in self.messages)
        
        # Count reactions
        total_reactions = sum(len(msg.reactions) for msg in self.messages)
        
        return {
            'total_messages': len(self.messages),
            'participants': participants,
            'participant_message_counts': message_counts,
            'date_range': (min(timestamps), max(timestamps)) if timestamps else ('', ''),
            'total_attachments': total_attachments,
            'total_reactions': total_reactions,
            'edited_messages': sum(1 for msg in self.messages if msg.edited)
        }
