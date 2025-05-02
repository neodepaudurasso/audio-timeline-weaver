
import os
import subprocess
import numpy as np
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

class AudioProcessor:
    def __init__(self):
        self.audio_files = {}  # Dictionary to store loaded audio files
        
        # Specify the ffmpeg path correctly with more comprehensive options
        ffmpeg_paths = [
            'ffmpeg.exe',                         # Local directory
            'ffmpge/bin/ffmpeg.exe',              # Path specified by user
            os.path.abspath('ffmpge/bin/ffmpeg.exe'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpge/bin/ffmpeg.exe'),
            'C:/ffmpeg/bin/ffmpeg.exe',           # Common installation locations
            'C:/Program Files/ffmpeg/bin/ffmpeg.exe',
            os.path.join(os.environ.get('ProgramFiles', ''), 'ffmpeg/bin/ffmpeg.exe')
        ]
        
        self.ffmpeg_path = None
        for path in ffmpeg_paths:
            if os.path.exists(path):
                self.ffmpeg_path = path
                break
        
        if self.ffmpeg_path:
            print(f"FFmpeg found at: {self.ffmpeg_path}")
            # Configure pydub to use our ffmpeg path
            AudioSegment.converter = self.ffmpeg_path
            os.environ["PATH"] += os.pathsep + os.path.dirname(self.ffmpeg_path)
        else:
            print("WARNING: FFmpeg not found. Please ensure it's installed correctly.")
            print("Searched in the following locations:")
            for path in ffmpeg_paths:
                print(f"- {path}")
        
        # Create temp directory for audio processing
        os.makedirs('temp', exist_ok=True)
    
    def load_file(self, file_path):
        """Load an audio file and store it in memory"""
        try:
            file_name = os.path.basename(file_path)
            print(f"Attempting to load audio file: {file_path}")
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            
            # Explicitly set the FFmpeg path for this operation
            AudioSegment.converter = self.ffmpeg_path
            
            # Try to load the audio file
            audio = AudioSegment.from_file(file_path)
            
            # Get and print some audio information for debugging
            print(f"Audio loaded successfully: {len(audio)/1000.0}s, {audio.channels} channels, {audio.frame_rate}Hz")
            
            self.audio_files[file_name] = {
                'path': file_path,
                'audio': audio,
                'samples': self._get_samples(audio),
                'duration': len(audio) / 1000.0  # Duration in seconds
            }
            return True
        except CouldntDecodeError:
            print(f"Error: Couldn't decode {file_path}")
            print("This often indicates that FFmpeg cannot process the file correctly.")
            return False
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            return False
        except Exception as e:
            print(f"Error loading file {file_path}: {str(e)}")
            # More detailed debugging information
            import traceback
            traceback.print_exc()
            return False
    
    def _get_samples(self, audio):
        """Extract sample array from audio segment"""
        try:
            # Convert stereo to mono for simplified processing
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Get array samples normalized between -1 and 1
            samples = np.array(audio.get_array_of_samples()).astype(float)
            max_value = np.iinfo(audio.array_type).max
            samples = samples / max_value
            
            return samples
        except Exception as e:
            print(f"Error extracting samples: {str(e)}")
            return np.array([0])  # Return empty array on error
    
    def get_audio_data(self, file_name):
        """Get audio data for a file by name"""
        return self.audio_files.get(file_name)
    
    def remove_file(self, file_name):
        """Remove a file from memory"""
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
