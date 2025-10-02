#!/usr/bin/env python3
"""
Discord Chat Analyzer using Google Gemini AI
Analyzes Discord chat exports including messages, attachments, and media files.
"""

import os
import json
from datetime import datetime
from dataclasses import asdict

# Import from our library
from lib.parser import DiscordHTMLParser
from lib.gemini import GeminiAnalyzer, ConversationAnalysis
from lib.media import MediaAnalyzer


class DiscordAnalyzer:
    """Main class that orchestrates the entire analysis process."""
    
    def __init__(self, html_file: str, files_directory: str, gemini_api_key: str, model_name: str = 'gemini-1.5-flash'):
        self.html_file = html_file
        self.files_directory = files_directory
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Initialize components
        self.parser = DiscordHTMLParser(html_file)
        self.media_analyzer = MediaAnalyzer(files_directory)
        self.gemini_analyzer = GeminiAnalyzer(gemini_api_key, model_name)
        self.gemini_analyzer.set_media_analyzer(self.media_analyzer)
    
    def analyze(self) -> ConversationAnalysis:
        """Run the complete analysis pipeline."""
        print("Parsing Discord HTML export...")
        messages = self.parser.parse()
        print(f"Extracted {len(messages)} messages")
        
        print("Analyzing conversation with Gemini AI...")
        analysis = self.gemini_analyzer.analyze_conversation(messages)
        
        return analysis
    
    def export_results(self, analysis: ConversationAnalysis, output_file: str):
        """Export analysis results to JSON file."""
        # Convert analysis to dictionary, handling dataclasses
        analysis_dict = asdict(analysis)
        
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_file': self.html_file,
            'files_directory': self.files_directory,
            'analysis': analysis_dict
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results exported to {output_file}")
