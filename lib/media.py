"""
Media File Analyzer
Analyzes media files (images, videos, audio) using various techniques.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

# Optional imports with fallbacks
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class MediaAnalyzer:
    """Analyzes media files (images, videos, audio) using various techniques."""
    
    def __init__(self, files_directory: str):
        self.files_directory = Path(files_directory)
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.supported_video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        self.supported_audio_formats = {'.ogg', '.mp3', '.wav', '.m4a', '.flac'}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single media file and return metadata."""
        file_path = Path(file_path)
        if not file_path.exists():
            return {'error': 'File not found'}
        
        file_ext = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        analysis = {
            'filename': file_path.name,
            'size': file_size,
            'extension': file_ext,
            'type': self._get_file_type(file_ext)
        }
        
        try:
            if file_ext in self.supported_image_formats:
                analysis.update(self._analyze_image(file_path))
            elif file_ext in self.supported_video_formats:
                analysis.update(self._analyze_video(file_path))
            elif file_ext in self.supported_audio_formats:
                analysis.update(self._analyze_audio(file_path))
            else:
                analysis['type'] = 'unknown'
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension."""
        if extension in self.supported_image_formats:
            return 'image'
        elif extension in self.supported_video_formats:
            return 'video'
        elif extension in self.supported_audio_formats:
            return 'audio'
        else:
            return 'document'
    
    def _analyze_image(self, file_path: Path) -> Dict[str, Any]:
        """Analyze image file and extract metadata."""
        if not PIL_AVAILABLE:
            return {'error': 'PIL not available for image analysis'}
        
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            return {'error': f'Image analysis failed: {e}'}
    
    def _analyze_video(self, file_path: Path) -> Dict[str, Any]:
        """Analyze video file and extract metadata."""
        if not CV2_AVAILABLE:
            return {'error': 'OpenCV not available for video analysis'}
        
        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                return {'error': 'Could not open video file'}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration
            }
        except Exception as e:
            return {'error': f'Video analysis failed: {e}'}
    
    def _analyze_audio(self, file_path: Path) -> Dict[str, Any]:
        """Analyze audio file and extract metadata."""
        if not LIBROSA_AVAILABLE:
            return {'error': 'Librosa not available for audio analysis'}
        
        try:
            y, sr = librosa.load(str(file_path))
            duration = len(y) / sr
            
            return {
                'sample_rate': sr,
                'duration': duration,
                'channels': 1 if y.ndim == 1 else y.shape[0],
                'rms_energy': float(np.sqrt(np.mean(y**2))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            }
        except Exception as e:
            return {'error': f'Audio analysis failed: {e}'}
    
    def analyze_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple files and return summary statistics."""
        analyses = []
        errors = []
        
        for file_path in file_paths:
            analysis = self.analyze_file(file_path)
            if 'error' in analysis:
                errors.append({'file': file_path, 'error': analysis['error']})
            else:
                analyses.append(analysis)
        
        # Categorize by type
        by_type = {}
        for analysis in analyses:
            file_type = analysis.get('type', 'unknown')
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(analysis)
        
        # Calculate statistics
        total_size = sum(a.get('size', 0) for a in analyses)
        
        return {
            'total_files': len(analyses),
            'total_errors': len(errors),
            'total_size': total_size,
            'by_type': {k: len(v) for k, v in by_type.items()},
            'analyses': analyses,
            'errors': errors
        }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats."""
        return {
            'images': list(self.supported_image_formats),
            'videos': list(self.supported_video_formats),
            'audio': list(self.supported_audio_formats)
        }
