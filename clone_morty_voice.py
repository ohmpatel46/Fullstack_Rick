#!/usr/bin/env python3
"""
Morty Voice Cloning Script
Clean implementation with manually specified samples
"""

import os
from TTS.api import TTS

# =============================================================================
# MORTY SAMPLE CONFIGURATION - Edit these samples as needed
# =============================================================================

MORTY_SAMPLES = [
    "ep01_morty_0005.wav",
    "ep01_morty_0012.wav",
    "ep01_morty_0018.wav",
    "ep01_morty_0025.wav",
    "ep01_morty_0032.wav",
    "ep02_morty_0008.wav",
    "ep02_morty_0015.wav",
    "ep02_morty_0022.wav"
]

# Directory containing the audio samples
WAVS_DIR = "rick_and_morty_tts/wavs"

# Test phrases for Morty
MORTY_TEST_PHRASES = [
    "Oh geez Rick, I don't know about this!",
    "Aw man, this is really messed up!",
    "Rick, are you sure this is gonna work?",
    "I'm scared Rick, what if something goes wrong?",
    "Oh no, oh no, this is bad Rick, this is really bad!"
]

def clone_morty_voice():
    """Clone Morty's voice using manually specified samples"""
    print("🧪 Morty Voice Cloning")
    print("=" * 40)
    
    # Get full paths for Morty samples
    morty_paths = []
    print("📋 Loading Morty samples:")
    
    for filename in MORTY_SAMPLES:
        filepath = os.path.join(WAVS_DIR, filename)
        if os.path.exists(filepath):
            morty_paths.append(filepath)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"✅ {filename} - {size_kb:.1f}KB")
        else:
            print(f"❌ {filename} - Not found!")
    
    if not morty_paths:
        print("❌ No Morty samples found!")
        return
    
    print(f"\n🎤 Using {len(morty_paths)} Morty samples")
    
    try:
        # Load TTS model
        print("📦 Loading TTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
        print("✅ YourTTS loaded")
        
        # Generate test phrases
        for i, phrase in enumerate(MORTY_TEST_PHRASES, 1):
            output_file = f"morty_clone_{i:02d}.wav"
            print(f"\n🗣️  Generating: {phrase[:50]}...")
            
            tts.tts_to_file(
                text=phrase,
                speaker_wav=morty_paths,
                file_path=output_file,
                language="en"
            )
            print(f"✅ Saved: {output_file}")
        
        print(f"\n🎉 Morty voice cloning complete!")
        print(f"📁 Generated {len(MORTY_TEST_PHRASES)} test files")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🎬 Morty Smith Voice Cloner")
    print("=" * 50)
    print(f"📊 Configured with {len(MORTY_SAMPLES)} samples")
    print(f"📂 Source directory: {WAVS_DIR}")
    print()
    
    clone_morty_voice()

if __name__ == "__main__":
    main()
