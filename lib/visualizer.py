"""
Visualization module for Discord chat analysis results.
Creates charts, graphs, and interactive visualizations.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np


class DiscordVisualizer:
    """Creates visualizations for Discord chat analysis."""
    
    def __init__(self, output_directory: str = './visualizations'):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_message_timeline(self, messages: List[Dict], output_file: str = 'message_timeline.png'):
        """Create a timeline visualization of messages."""
        if not messages:
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        
        if df.empty:
            return
        
        # Group by date and author
        df['date'] = df['timestamp'].dt.date
        daily_counts = df.groupby(['date', 'author']).size().unstack(fill_value=0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(15, 8))
        daily_counts.plot(kind='bar', stacked=True, ax=ax, width=0.8)
        
        ax.set_title('Message Activity Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Messages', fontsize=12)
        ax.legend(title='Author', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_sentiment_analysis_chart(self, sentiment_data: Dict, output_file: str = 'sentiment_analysis.png'):
        """Create sentiment analysis visualization."""
        if not sentiment_data:
            return
        
        # Extract sentiment data
        overall_sentiment = sentiment_data.get('overall_sentiment', 'unknown')
        participant_sentiments = sentiment_data.get('sentiment_by_participant', {})
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Overall sentiment pie chart
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        if overall_sentiment in sentiment_counts:
            sentiment_counts[overall_sentiment] = 1
        
        # Only create pie chart if we have valid data
        if sum(sentiment_counts.values()) > 0:
            colors = ['#2ecc71', '#e74c3c', '#95a5a6']
            ax1.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), 
                    autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Overall Sentiment', fontsize=14, fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No sentiment data available', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('Overall Sentiment', fontsize=14, fontweight='bold')
        
        # Participant sentiment bar chart
        if participant_sentiments:
            participants = list(participant_sentiments.keys())
            sentiments = list(participant_sentiments.values())
            
            # Map sentiment to numeric values for visualization
            sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
            numeric_sentiments = [sentiment_map.get(s, 0) for s in sentiments]
            
            colors = ['#2ecc71' if s > 0 else '#e74c3c' if s < 0 else '#95a5a6' for s in numeric_sentiments]
            bars = ax2.bar(participants, numeric_sentiments, color=colors)
            ax2.set_title('Sentiment by Participant', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Sentiment Score')
            ax2.set_ylim(-1.5, 1.5)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for bar, sentiment in zip(bars, sentiments):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1 if height >= 0 else height - 0.1,
                        sentiment, ha='center', va='bottom' if height >= 0 else 'top')
        else:
            ax2.text(0.5, 0.5, 'No participant sentiment data available', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Sentiment by Participant', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_topic_wordcloud(self, topics: List[str], output_file: str = 'topic_wordcloud.png'):
        """Create a word cloud from topics."""
        if not topics:
            return
        
        # Combine topics into text
        text = ' '.join(topics)
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(text)
        
        # Plot
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Topic Word Cloud', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_media_analysis_chart(self, media_summary: Dict, output_file: str = 'media_analysis.png'):
        """Create media analysis visualization."""
        if not media_summary or 'by_type' not in media_summary:
            return
        
        media_types = media_summary['by_type']
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        labels = list(media_types.keys())
        sizes = list(media_types.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('Media Files by Type', fontsize=16, fontweight='bold')
        
        # Add total count
        total_files = sum(sizes)
        ax.text(0, -1.2, f'Total Files: {total_files}', ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_interactive_dashboard(self, analysis_data: Dict, output_file: str = 'interactive_dashboard.html'):
        """Create an interactive Plotly dashboard."""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Message Activity', 'Sentiment Analysis', 'Media Types', 'Topic Distribution'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Message activity over time (placeholder - would need actual time series data)
        fig.add_trace(
            go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode='lines+markers', name='Messages'),
            row=1, col=1
        )
        
        # Sentiment analysis
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        participant_sentiments = sentiment_data.get('sentiment_by_participant', {})
        
        if participant_sentiments:
            participants = list(participant_sentiments.keys())
            sentiments = list(participant_sentiments.values())
            
            # Map sentiment to numeric values
            sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
            numeric_sentiments = [sentiment_map.get(s, 0) for s in sentiments]
            
            fig.add_trace(
                go.Bar(x=participants, y=numeric_sentiments, name='Sentiment'),
                row=1, col=2
            )
        
        # Media types
        media_summary = analysis_data.get('media_summary', {})
        media_types = media_summary.get('by_type', {})
        
        if media_types:
            fig.add_trace(
                go.Pie(labels=list(media_types.keys()), values=list(media_types.values()), name='Media Types'),
                row=2, col=1
            )
        
        # Topic distribution (placeholder)
        topics = analysis_data.get('topics', [])
        if topics:
            topic_counts = pd.Series(topics).value_counts().head(10)
            fig.add_trace(
                go.Bar(x=topic_counts.index, y=topic_counts.values, name='Topics'),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Discord Chat Analysis Dashboard",
            showlegend=False,
            height=800
        )
        
        # Save as HTML
        fig.write_html(self.output_directory / output_file)
    
    def create_participant_profiles_chart(self, participant_profiles: Dict, output_file: str = 'participant_profiles.png'):
        """Create participant profiles visualization."""
        if not participant_profiles:
            return
        
        # Create subplots for each participant
        num_participants = len(participant_profiles)
        if num_participants == 0:
            return
        
        # Calculate subplot layout
        cols = min(2, num_participants)
        rows = (num_participants + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 6 * rows), subplot_kw=dict(projection='polar'))
        
        # Handle single participant case and array issues
        if num_participants == 1:
            axes = [axes]
        elif rows == 1 and cols > 1:
            # For single row multiple columns, ensure we have a list
            axes = list(axes) if hasattr(axes, '__iter__') and not hasattr(axes, 'plot') else [axes]
        elif rows > 1:
            # For multiple rows, flatten the array
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        else:
            axes = [axes]
        
        # Define profile metrics for radar chart
        metrics = ['Activity Level', 'Influence Level', 'Engagement', 'Emotional Expression', 'Knowledge Sharing']
        
        for i, (name, profile) in enumerate(participant_profiles.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Map profile attributes to numeric values
            values = []
            
            # Activity Level
            activity_map = {'high': 5, 'medium': 3, 'low': 1, 'unknown': 2}
            values.append(activity_map.get(profile.activity_level.lower(), 2))
            
            # Influence Level
            influence_map = {'high': 5, 'medium': 3, 'low': 1, 'unknown': 2}
            values.append(influence_map.get(profile.influence_level.lower(), 2))
            
            # Engagement (based on number of interests)
            values.append(min(5, len(profile.interests)))
            
            # Emotional Expression (based on emotional patterns)
            values.append(min(5, len(profile.emotional_patterns)))
            
            # Knowledge Sharing (based on important ideas)
            values.append(min(5, len(profile.important_ideas)))
            
            # Create radar chart
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            values = values + values[:1]  # Complete the circle
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=name)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_ylim(0, 5)
            ax.set_title(f'{name} Profile', fontsize=12, fontweight='bold', pad=20)
            ax.grid(True)
            
            # Add profile details as text
            details = []
            if profile.personality_traits:
                details.append(f"Traits: {', '.join(profile.personality_traits[:2])}")
            if profile.likes:
                details.append(f"Likes: {', '.join(profile.likes[:2])}")
                
            if details:
                ax.text(0, -6, '\n'.join(details), ha='center', va='top', 
                       fontsize=8, transform=ax.transData)
        
        # Hide empty subplots
        for i in range(num_participants, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_participant_interests_wordcloud(self, participant_profiles: Dict, output_file: str = 'participant_interests.png'):
        """Create word clouds for participant interests."""
        if not participant_profiles:
            return
        
        # Create subplots for each participant
        num_participants = len(participant_profiles)
        if num_participants == 0:
            return
            
        cols = min(2, num_participants)
        rows = (num_participants + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(12, 4 * rows))
        
        # Handle single participant case and array issues
        if num_participants == 1:
            axes = [axes]
        elif rows == 1 and cols > 1:
            # For single row multiple columns, ensure we have a list
            axes = list(axes) if hasattr(axes, '__iter__') and not hasattr(axes, 'plot') else [axes]
        elif rows > 1:
            # For multiple rows, flatten the array
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        else:
            axes = [axes]
        
        for i, (name, profile) in enumerate(participant_profiles.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Combine likes, interests, and important ideas
            all_interests = profile.likes + profile.interests + profile.important_ideas
            
            if all_interests:
                text = ' '.join(all_interests)
                
                # Create word cloud
                wordcloud = WordCloud(
                    width=400, 
                    height=300, 
                    background_color='white',
                    max_words=50,
                    colormap='viridis'
                ).generate(text)
                
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title(f'{name} - Interests & Ideas', fontsize=12, fontweight='bold')
            else:
                ax.text(0.5, 0.5, f'{name}\nNo interests data available', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{name} - Interests & Ideas', fontsize=12, fontweight='bold')
                ax.axis('off')
        
        # Hide empty subplots
        for i in range(num_participants, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_relationship_dynamics_chart(self, relationship_data: Dict, output_file: str = 'relationship_dynamics.png'):
        if not relationship_data:
            return
        
        # Extract key metrics
        metrics = []
        values = []
        
        for key, value in relationship_data.items():
            if isinstance(value, str) and len(value) > 10:  # Skip long text descriptions
                continue
            metrics.append(key.replace('_', ' ').title())
            values.append(len(str(value)))  # Use length as proxy for complexity
        
        if not metrics:
            return
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
        
        # Convert to radians
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        values = values + values[:1]  # Complete the circle
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label='Relationship Dynamics')
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, max(values) * 1.1)
        ax.set_title('Relationship Dynamics Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_comprehensive_report(self, analysis_data: Dict, messages: List[Dict] = None):
        """Create a comprehensive visualization report."""
        print("Creating comprehensive visualization report...")
        
        # Create all visualizations
        if messages:
            self.create_message_timeline(messages, 'message_timeline.png')
        
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        if sentiment_data:
            self.create_sentiment_analysis_chart(sentiment_data, 'sentiment_analysis.png')
        
        topics = analysis_data.get('topics', [])
        if topics:
            self.create_topic_wordcloud(topics, 'topic_wordcloud.png')
        
        media_summary = analysis_data.get('media_summary', {})
        if media_summary:
            self.create_media_analysis_chart(media_summary, 'media_analysis.png')
        
        relationship_data = analysis_data.get('relationship_dynamics', {})
        if relationship_data:
            self.create_relationship_dynamics_chart(relationship_data, 'relationship_dynamics.png')
        
        # Create participant profile visualizations
        participant_profiles = analysis_data.get('participant_profiles', {})
        if participant_profiles:
            self.create_participant_profiles_chart(participant_profiles, 'participant_profiles.png')
            self.create_participant_interests_wordcloud(participant_profiles, 'participant_interests.png')
        
        # Create interactive dashboard
        self.create_interactive_dashboard(analysis_data, 'interactive_dashboard.html')
        
        print(f"Visualizations saved to: {self.output_directory}")
        
        # Create index HTML file
        self._create_index_html()
    
    def _create_index_html(self):
        """Create an index HTML file to view all visualizations."""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Discord Chat Analysis - Visualizations</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
                .visualization { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                .visualization h2 { color: #34495e; margin-top: 0; }
                img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }
                .interactive { background-color: #ecf0f1; padding: 15px; border-radius: 5px; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Discord Chat Analysis - Visualizations</h1>
                
                <div class="visualization">
                    <h2>Interactive Dashboard</h2>
                    <div class="interactive">
                        <p>Comprehensive interactive dashboard with all analysis results:</p>
                        <a href="interactive_dashboard.html" target="_blank">Open Interactive Dashboard</a>
                    </div>
                </div>
                
                <div class="visualization">
                    <h2>Message Timeline</h2>
                    <img src="message_timeline.png" alt="Message Timeline">
                </div>
                
                <div class="visualization">
                    <h2>Sentiment Analysis</h2>
                    <img src="sentiment_analysis.png" alt="Sentiment Analysis">
                </div>
                
                <div class="visualization">
                    <h2>Topic Word Cloud</h2>
                    <img src="topic_wordcloud.png" alt="Topic Word Cloud">
                </div>
                
                <div class="visualization">
                    <h2>Media Analysis</h2>
                    <img src="media_analysis.png" alt="Media Analysis">
                </div>
                
                <div class="visualization">
                    <h2>Relationship Dynamics</h2>
                    <img src="relationship_dynamics.png" alt="Relationship Dynamics">
                </div>
                
                <div class="visualization">
                    <h2>Participant Profiles</h2>
                    <img src="participant_profiles.png" alt="Participant Profiles">
                </div>
                
                <div class="visualization">
                    <h2>Participant Interests & Ideas</h2>
                    <img src="participant_interests.png" alt="Participant Interests">
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(self.output_directory / 'index.html', 'w') as f:
            f.write(html_content)
        
        print(f"Index HTML created: {self.output_directory / 'index.html'}")


def create_visualizations(analysis_data: Dict, messages: List[Dict] = None, 
                         output_directory: str = './visualizations'):
    """Convenience function to create all visualizations."""
    visualizer = DiscordVisualizer(output_directory)
    visualizer.create_comprehensive_report(analysis_data, messages)
    return visualizer
