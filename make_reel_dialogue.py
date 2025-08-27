import json
import os
import requests
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DialogueReelGenerator:
    def __init__(self, config_file="dialogue.json"):
        """Initialize the generator with configuration file"""
        self.config = self.load_config(config_file)
        self.temp_files = []
        
        # Override config with environment variables if available
        self.override_with_env_vars()
        
    def override_with_env_vars(self):
        """Override config values with environment variables if they exist"""
        # TTS API Key
        env_api_key = os.getenv('ELEVENLABS_API_KEY')
        if env_api_key and env_api_key != 'your_api_key_here':
            self.config['tts_settings']['api_key'] = env_api_key
        
        # Override voice IDs
        chandler_voice_id = os.getenv('CHANDLER_VOICE_ID')
        joey_voice_id = os.getenv('JOEY_VOICE_ID')
        
        if chandler_voice_id:
            self.config['tts_settings']['voices']['chandler']['voice_id'] = chandler_voice_id
        if joey_voice_id:
            self.config['tts_settings']['voices']['joey']['voice_id'] = joey_voice_id
        
        # Override TTS settings
        stability = os.getenv('TTS_STABILITY')
        similarity_boost = os.getenv('TTS_SIMILARITY_BOOST')
        
        if stability:
            self.config['tts_settings']['voices']['chandler']['stability'] = float(stability)
            self.config['tts_settings']['voices']['joey']['stability'] = float(stability)
        if similarity_boost:
            self.config['tts_settings']['voices']['chandler']['similarity_boost'] = float(similarity_boost)
            self.config['tts_settings']['voices']['joey']['similarity_boost'] = float(similarity_boost)
        
        # Override character sizes
        chandler_size = os.getenv('CHANDLER_SIZE')
        joey_size = os.getenv('JOEY_SIZE')
        
        if chandler_size:
            self.config['characters']['chandler']['size'] = int(chandler_size)
        if joey_size:
            self.config['characters']['joey']['size'] = int(joey_size)
        
        # Override video settings
        duration = os.getenv('DEFAULT_VIDEO_DURATION')
        fps = os.getenv('DEFAULT_VIDEO_FPS')
        width = os.getenv('DEFAULT_VIDEO_WIDTH')
        height = os.getenv('DEFAULT_VIDEO_HEIGHT')
        
        if duration:
            self.config['metadata']['duration'] = int(duration)
        if fps:
            self.config['metadata']['fps'] = int(fps)
        if width:
            self.config['metadata']['width'] = int(width)
        if height:
            self.config['metadata']['height'] = int(height)
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {config_file} not found!")
            exit(1)
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {config_file}")
            exit(1)
    
    def check_files(self):
        """Check if all required files exist"""
        required_files = [
            self.config['metadata']['background_video'],
            self.config['characters']['chandler']['image'],
            self.config['characters']['joey']['image']
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"❌ Error: {file_path} not found!")
                exit(1)
        
        print("✅ All required files found!")
    
    def generate_tts_audio(self, text, character, output_path):
        """Generate TTS audio using ElevenLabs API"""
        if not self.config['tts_settings']['enabled']:
            print(f"⚠️ TTS disabled for '{text}'")
            return None
            
        api_key = self.config['tts_settings']['api_key']
        if api_key == "YOUR_ELEVENLABS_API_KEY_HERE" or not api_key:
            print(f"⚠️ Please set your ElevenLabs API key in .env file or dialogue.json for TTS")
            return None
            
        voice_id = self.config['tts_settings']['voices'][character]['voice_id']
        stability = self.config['tts_settings']['voices'][character]['stability']
        similarity_boost = self.config['tts_settings']['voices'][character]['similarity_boost']
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        try:
            print(f"🎤 Generating TTS for {character}: '{text}'")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ TTS audio saved to {output_path}")
                return output_path
            else:
                print(f"❌ TTS API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            return None
    
    def create_character_clips(self):
        """Create character image clips with proper timing - only show during their dialogue"""
        character_clips = []
        
        # Track when each character should be visible
        chandler_times = []
        joey_times = []
        
        for dialogue in self.config['dialogue']:
            if dialogue['character'] == 'chandler':
                chandler_times.append((dialogue['start_time'], dialogue['start_time'] + dialogue['duration']))
            elif dialogue['character'] == 'joey':
                joey_times.append((dialogue['start_time'], dialogue['start_time'] + dialogue['duration']))
        
        # Create Chandler clips (one for each dialogue time)
        for start_time, end_time in chandler_times:
            chandler_clip = ImageClip(self.config['characters']['chandler']['image'])
            chandler_clip = chandler_clip.resized(width=self.config['characters']['chandler']['size'])
            chandler_clip = chandler_clip.with_position(("left", "center"))
            chandler_clip = chandler_clip.with_start(start_time).with_duration(end_time - start_time)
            character_clips.append(chandler_clip)
        
        # Create Joey clips (one for each dialogue time)
        for start_time, end_time in joey_times:
            joey_clip = ImageClip(self.config['characters']['joey']['image'])
            joey_clip = joey_clip.resized(width=self.config['characters']['joey']['size'])
            joey_clip = joey_clip.with_position(("right", "center"))
            joey_clip = joey_clip.with_start(start_time).with_duration(end_time - start_time)
            character_clips.append(joey_clip)
        
        return character_clips
    
    def create_dialogue_clips(self):
        """Create text clips for dialogue with TTS audio"""
        dialogue_clips = []
        audio_clips = []
        
        for dialogue in self.config['dialogue']:
            # Wrap text if it's too long for the screen width
            wrapped_text = self.wrap_text_to_width(
                dialogue['text'], 
                dialogue['font_size'],
                max_width=1000  # 1080 - 80px padding (40px each side)
            )
            
            # Create text clip with wrapped text and better rendering
            text_clip = TextClip(
                text=wrapped_text,
                font_size=dialogue['font_size'],
                color=dialogue['text_color'],
                stroke_color=dialogue['stroke_color'],
                stroke_width=dialogue['stroke_width'],
                method='caption',  # Better text rendering
                size=(1000, None)  # Set width, let height auto-adjust with padding
            ).with_start(dialogue['start_time']).with_duration(dialogue['duration'])
            
            # Position text with better margins to avoid cutoff
            if dialogue['position'] == 'center':
                text_clip = text_clip.with_position(("center", "center"))
            elif dialogue['position'] == 'top':
                # Position at top with margin to avoid cutoff
                text_clip = text_clip.with_position(("center", 160))  # Increased margin
            elif dialogue['position'] == 'bottom':
                # Position at bottom with margin to avoid cutoff
                text_clip = text_clip.with_position(("center", "bottom"))
            
            dialogue_clips.append(text_clip)
            
            # Generate TTS audio if enabled
            if self.config['tts_settings']['enabled']:
                temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_audio.close()
                self.temp_files.append(temp_audio.name)
                
                audio_path = self.generate_tts_audio(
                    dialogue['text'], 
                    dialogue['character'], 
                    temp_audio.name
                )
                
                if audio_path and os.path.exists(audio_path):
                    # Create audio clip with proper timing
                    audio_clip = AudioFileClip(audio_path)
                    audio_clip = audio_clip.with_start(dialogue['start_time'])
                    audio_clips.append(audio_clip)
        
        return dialogue_clips, audio_clips
    
    def wrap_text_to_width(self, text, font_size, max_width=1000):
        """Wrap text to fit within specified width, maintaining font size"""
        # Rough estimate: each character is about font_size * 0.6 pixels wide
        char_width = font_size * 0.6
        
        # Calculate how many characters can fit on one line
        chars_per_line = int(max_width / char_width)
        
        if len(text) <= chars_per_line:
            return text  # No wrapping needed
        
        # Split text into words
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed the line length
            test_line = current_line + " " + word if current_line else word
            
            if len(test_line) <= chars_per_line:
                current_line = test_line
            else:
                # Current line is full, start a new one
                if current_line:
                    lines.append(current_line.strip())
                current_line = word
        
        # Add the last line
        if current_line:
            lines.append(current_line.strip())
        
        # Join lines with newline characters
        return "\n".join(lines)
    
    def generate_reel(self):
        """Generate the complete reel with dialogue and TTS"""
        print("🎬 Starting reel generation...")
        
        # Check files
        self.check_files()
        
        # Load background video
        print("🎬 Loading background video...")
        bg = VideoFileClip(self.config['metadata']['background_video'])
        
        # Debug: Show what duration we're using
        print(f"📏 Video duration from config: {self.config['metadata']['duration']} seconds")
        print(f"📏 Background video duration: {bg.duration} seconds")
        
        # Take a segment from the beginning since the clip is short
        start_time = 0
        end_time = start_time + self.config['metadata']['duration']
        print(f"📏 Clipping from {start_time}s to {end_time}s")
        
        bg = bg.subclipped(start_time, end_time)
        
        # Resize to vertical format
        bg = bg.resized(height=1920)
        bg = bg.cropped(width=1080, height=1920, x_center=bg.w/2, y_center=bg.h/2)
        
        # Create character clips
        print("👥 Creating character clips...")
        character_clips = self.create_character_clips()
        
        # Create dialogue clips and TTS audio
        print("💬 Creating dialogue clips...")
        dialogue_clips, audio_clips = self.create_dialogue_clips()
        
        # Composite video
        print("🎭 Compositing video...")
        all_video_clips = [bg] + character_clips + dialogue_clips
        final_video = CompositeVideoClip(all_video_clips)
        
        # Mix background audio with TTS audio
        if audio_clips:
            print("🔊 Compositing audio...")
            
            # Get background audio
            bg_audio = bg.audio
            
            # Reduce background audio volume - use the correct MoviePy 2.x method
            if bg_audio:
                try:
                    bg_audio = bg_audio.volumex(0.3)  # Try MoviePy 1.x method
                except AttributeError:
                    try:
                        bg_audio = bg_audio.with_volume(0.3)  # Try MoviePy 2.x method
                    except AttributeError:
                        # If neither method works, just use the original audio
                        print("⚠️  Could not adjust background volume, using original")
                
                # Combine all audio clips
                final_audio = CompositeAudioClip([bg_audio] + audio_clips)
            else:
                final_audio = CompositeAudioClip(audio_clips)
        else:
            final_audio = bg.audio if bg.audio else None
        
        final_video = final_video.with_audio(final_audio)
        
        # Export
        output_path = self.config['metadata']['output_file']
        print(f"📤 Exporting to {output_path}...")
        final_video.write_videofile(output_path, fps=self.config['metadata']['fps'], codec="libx264", audio_codec="aac")
        
        # Cleanup
        self.cleanup()
        
        print("🎉 Reel generation complete!")
        print(f"📁 Output saved as: {output_path}")
        print(f"📱 Video specs: {self.config['metadata']['width']}x{self.config['metadata']['height']}, {self.config['metadata']['fps']}fps, {self.config['metadata']['duration']} seconds")
    
    def cleanup(self):
        """Clean up temporary files"""
        print("🧹 Cleaning up temporary files...")
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️ Removed {temp_file}")

if __name__ == "__main__":
    generator = DialogueReelGenerator()
    generator.generate_reel()
