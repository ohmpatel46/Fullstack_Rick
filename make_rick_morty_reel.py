#!/usr/bin/env python3
"""
Rick & Morty Tech Reel Generator
Adapted from the existing Friends reel system to use Coqui TTS voice cloning
"""

import json
import os
import tempfile
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from TTS.api import TTS

class RickMortyReelGenerator:
    def __init__(self, config_file="rick_morty_dialogue.json"):
        """Initialize the generator with configuration file"""
        self.config = self.load_config(config_file)
        self.temp_files = []
        self.tts = None
        
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
            self.config['characters']['rick']['image'],
            self.config['characters']['morty']['image']
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"❌ Error: {file_path} not found!")
                exit(1)
        
        print("✅ All required files found!")
    
    def load_tts_model(self):
        """Load the Coqui TTS model"""
        if self.tts is None:
            print("📦 Loading Coqui TTS model...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
            print("✅ YourTTS model loaded")
    
    def generate_coqui_audio(self, text, character, output_path):
        """Generate TTS audio using Coqui voice cloning"""
        if not self.config['tts_settings']['enabled']:
            print(f"⚠️ TTS disabled for '{text}'")
            return None
        
        # Load TTS model if not already loaded
        self.load_tts_model()
        
        # Get voice samples for the character
        voice_samples = self.config['tts_settings']['voices'][character]['samples']
        
        # Convert sample filenames to full paths
        wavs_dir = "rick_and_morty_tts/wavs"
        sample_paths = []
        
        for sample in voice_samples:
            sample_path = os.path.join(wavs_dir, sample)
            if os.path.exists(sample_path):
                sample_paths.append(sample_path)
            else:
                print(f"⚠️ Warning: Sample {sample} not found")
        
        if not sample_paths:
            print(f"❌ No voice samples found for {character}")
            return None
        
        try:
            print(f"🎤 Generating {character} voice: '{text[:50]}...'")
            
            # Generate speech using Coqui TTS
            self.tts.tts_to_file(
                text=text,
                speaker_wav=sample_paths,
                file_path=output_path,
                language="en"
            )
            
            print(f"✅ Audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Coqui TTS generation failed: {e}")
            return None
    
    def create_character_clips(self):
        """Create character image clips with proper timing - only show during their dialogue"""
        character_clips = []
        
        # Track when each character should be visible
        rick_times = []
        morty_times = []
        
        for dialogue in self.config['dialogue']:
            if dialogue['character'] == 'rick':
                rick_times.append((dialogue['start_time'], dialogue['start_time'] + dialogue['duration']))
            elif dialogue['character'] == 'morty':
                morty_times.append((dialogue['start_time'], dialogue['start_time'] + dialogue['duration']))
        
        # Create Rick clips (one for each dialogue time)
        for start_time, end_time in rick_times:
            rick_clip = ImageClip(self.config['characters']['rick']['image'])
            rick_clip = rick_clip.resized(width=self.config['characters']['rick']['size'])
            rick_clip = rick_clip.with_position(("left", "center"))
            rick_clip = rick_clip.with_start(start_time).with_duration(end_time - start_time)
            character_clips.append(rick_clip)
        
        # Create Morty clips (one for each dialogue time)
        for start_time, end_time in morty_times:
            morty_clip = ImageClip(self.config['characters']['morty']['image'])
            morty_clip = morty_clip.resized(width=self.config['characters']['morty']['size'])
            morty_clip = morty_clip.with_position(("right", "center"))
            morty_clip = morty_clip.with_start(start_time).with_duration(end_time - start_time)
            character_clips.append(morty_clip)
        
        return character_clips
    
    def create_dialogue_clips(self):
        """Create text clips for dialogue with Coqui TTS audio"""
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
            
            # Generate Coqui TTS audio if enabled
            if self.config['tts_settings']['enabled']:
                temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_audio.close()
                self.temp_files.append(temp_audio.name)
                
                audio_path = self.generate_coqui_audio(
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
        """Generate the complete reel with dialogue and Coqui TTS"""
        print("🎬 Starting Rick & Morty reel generation...")
        
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
        
        # Create dialogue clips and Coqui TTS audio
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
        
        print("🎉 Rick & Morty reel generation complete!")
        print(f"📁 Output saved as: {output_path}")
        print(f"📱 Video specs: {self.config['metadata']['width']}x{self.config['metadata']['height']}, {self.config['metadata']['fps']}fps, {self.config['metadata']['duration']} seconds")
    
    def cleanup(self):
        """Clean up temporary files"""
        print("🧹 Cleaning up temporary files...")
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️ Removed {temp_file}")

def main():
    """Main function to generate Rick & Morty reel"""
    print("🧪 Rick & Morty Tech Reel Generator")
    print("=" * 50)
    
    generator = RickMortyReelGenerator()
    generator.generate_reel()

if __name__ == "__main__":
    main()
