
import os
import subprocess
import numpy as np
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

class AudioProcessor:
    def __init__(self):
        self.audio_files = {}  # Dictionary to store loaded audio files
        self.ffmpeg_path = 'ffmpeg'  # Assume ffmpeg is in the same directory
        
        # Check if ffmpeg exists
        if os.path.exists('ffmpeg.exe'):
            self.ffmpeg_path = os.path.abspath('ffmpeg.exe')
        
        # Create temp directory for audio processing
        os.makedirs('temp', exist_ok=True)
    
    def load_file(self, file_path):
        """Load an audio file and store it in memory"""
        try:
            file_name = os.path.basename(file_path)
            audio = AudioSegment.from_file(file_path)
            self.audio_files[file_name] = {
                'path': file_path,
                'audio': audio,
                'samples': self._get_samples(audio),
                'duration': len(audio) / 1000.0  # Duration in seconds
            }
            return True
        except CouldntDecodeError:
            print(f"Error: Couldn't decode {file_path}")
            return False
        except Exception as e:
            print(f"Error loading file {file_path}: {str(e)}")
            return False
    
    def _get_samples(self, audio):
        """Convert audio segment to numpy array of samples for visualization"""
        # Convert to mono for simpler processing
        audio = audio.set_channels(1)
        samples = np.array(audio.get_array_of_samples())
        
        # Normalize samples
        max_sample = np.max(np.abs(samples))
        if max_sample > 0:
            samples = samples / max_sample
        
        # Downsample for visualization if too large
        if len(samples) > 100000:
            # Get a downsampled version for visualization
            ratio = len(samples) // 100000 + 1
            samples = samples[::ratio]
        
        return samples
    
    def get_audio_data(self, file_name):
        """Get audio data for a specific file"""
        return self.audio_files.get(file_name)
    
    def remove_file(self, file_name):
        """Remove an audio file from memory"""
        if file_name in self.audio_files:
            del self.audio_files[file_name]
            return True
        return False
    
    def cut_audio(self, file_name, start_time, end_time):
        """Cut a segment from an audio file"""
        if file_name not in self.audio_files:
            return None
        
        audio = self.audio_files[file_name]['audio']
        
        # Convert times to milliseconds
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        
        # Perform the cut
        cut_audio = audio[start_ms:end_ms]
        
        # Generate a new file name
        new_file_name = f"{os.path.splitext(file_name)[0]}_cut{os.path.splitext(file_name)[1]}"
        
        # Store the new audio segment
        self.audio_files[new_file_name] = {
            'path': None,  # No file path yet
            'audio': cut_audio,
            'samples': self._get_samples(cut_audio),
            'duration': len(cut_audio) / 1000.0
        }
        
        return new_file_name
    
    def split_audio(self, file_name, split_time):
        """Split an audio file at a specific time"""
        if file_name not in self.audio_files:
            return None
        
        audio = self.audio_files[file_name]['audio']
        
        # Convert time to milliseconds
        split_ms = int(split_time * 1000)
        
        # Perform the split
        first_part = audio[:split_ms]
        second_part = audio[split_ms:]
        
        # Generate new file names
        name_base = os.path.splitext(file_name)[0]
        ext = os.path.splitext(file_name)[1]
        first_file_name = f"{name_base}_part1{ext}"
        second_file_name = f"{name_base}_part2{ext}"
        
        # Store the new audio segments
        self.audio_files[first_file_name] = {
            'path': None,
            'audio': first_part,
            'samples': self._get_samples(first_part),
            'duration': len(first_part) / 1000.0
        }
        
        self.audio_files[second_file_name] = {
            'path': None,
            'audio': second_part,
            'samples': self._get_samples(second_part),
            'duration': len(second_part) / 1000.0
        }
        
        return first_file_name, second_file_name
    
    def export_audio(self, file_path, timeline_clips):
        """Export audio from timeline to file"""
        try:
            # If no clips, return error
            if not timeline_clips:
                return False, "No audio clips to export"
            
            # Combine all clips
            combined = AudioSegment.empty()
            for clip in timeline_clips:
                file_name = clip['file_name']
                start_time = clip['start_time']
                
                if file_name in self.audio_files:
                    audio = self.audio_files[file_name]['audio']
                    # Add silence before if needed
                    if start_time > len(combined) / 1000.0:
                        silence_ms = int((start_time - len(combined) / 1000.0) * 1000)
                        combined += AudioSegment.silent(duration=silence_ms)
                    
                    combined += audio
            
            # Export the combined audio
            format_type = os.path.splitext(file_path)[1][1:]  # Get format from extension
            combined.export(file_path, format=format_type)
            
            return True, "Export completed successfully"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def clean_temp_files(self):
        """Clean up temporary files"""
        try:
            for file in os.listdir('temp'):
                file_path = os.path.join('temp', file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning temp files: {str(e)}")
