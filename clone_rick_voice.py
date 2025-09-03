#!/usr/bin/env python3
"""
Rick Voice Cloning Script
Clean implementation with manually specified samples
"""

import os
from TTS.api import TTS

# =============================================================================
# RICK SAMPLE CONFIGURATION - Edit these samples as needed
# =============================================================================

RICK_SAMPLES = [
    "ep02_rick_0008.wav",
    "ep02_rick_0009.wav", 
    "ep02_rick_0016.wav",
    "ep02_rick_0021.wav",
    "ep02_rick_0036.wav"
]

# Directory containing the audio samples
WAVS_DIR = "rick_and_morty_tts/wavs"

# Test phrases for Rick
RICK_TEST_PHRASES = [
    "Morty, we gotta go! Science waits for no one!",
    "Wubba lubba dub dub! This is gonna be great!",
    "Listen Morty, this is a quick twenty-minute adventure.",
    "Oh geez Rick, I don't know about this.",
    "Morty, you gotta understand that sometimes science requires sacrifice."
]

def clone_rick_voice():
    """Clone Rick's voice using manually specified samples"""
    print("🧪 Rick Voice Cloning")
    print("=" * 40)
    
    # Get full paths for Rick samples
    rick_paths = []
    print("📋 Loading Rick samples:")
    
    for filename in RICK_SAMPLES:
        filepath = os.path.join(WAVS_DIR, filename)
        if os.path.exists(filepath):
            rick_paths.append(filepath)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"✅ {filename} - {size_kb:.1f}KB")
        else:
            print(f"❌ {filename} - Not found!")
    
    if not rick_paths:
        print("❌ No Rick samples found!")
        return
    
    print(f"\n🎤 Using {len(rick_paths)} Rick samples")
    
    try:
        # Load TTS model
        print("📦 Loading TTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
        print("✅ YourTTS loaded")
        
        # Generate test phrases
        for i, phrase in enumerate(RICK_TEST_PHRASES, 1):
            output_file = f"rick_clone_{i:02d}.wav"
            print(f"\n🗣️  Generating: {phrase[:50]}...")
            
            tts.tts_to_file(
                text=phrase,
                speaker_wav=rick_paths,
                file_path=output_file,
                language="en"
            )
            print(f"✅ Saved: {output_file}")
        
        print(f"\n🎉 Rick voice cloning complete!")
        print(f"📁 Generated {len(RICK_TEST_PHRASES)} test files")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🎬 Rick Sanchez Voice Cloner")
    print("=" * 50)
    print(f"📊 Configured with {len(RICK_SAMPLES)} samples")
    print(f"📂 Source directory: {WAVS_DIR}")
    print()
    
    clone_rick_voice()

if __name__ == "__main__":
    main()
