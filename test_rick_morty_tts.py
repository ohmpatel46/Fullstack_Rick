#!/usr/bin/env python3
"""
Test script for Rick and Morty TTS using Coqui TTS
Tests basic TTS functionality and dataset compatibility.
"""

import os
import json
from pathlib import Path
import argparse

def test_coqui_installation():
    """Test if Coqui TTS is properly installed"""
    try:
        import TTS
        print(f"✅ Coqui TTS installed: {TTS.__version__}")
        return True
    except ImportError:
        print("❌ Coqui TTS not installed. Run: pip install TTS>=0.22.0")
        return False

def test_basic_tts():
    """Test basic TTS functionality"""
    try:
        from TTS.api import TTS
        
        print("🎤 Testing basic TTS functionality...")
        
        # Try to load a basic model
        print("🔧 Loading basic TTS model...")
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        
        # Test basic text-to-speech
        test_text = "Hello, this is a test of the TTS system."
        output_file = "test_output.wav"
        
        print(f"🎵 Generating test audio: '{test_text}'")
        tts.tts_to_file(text=test_text, file_path=output_file)
        
        if os.path.exists(output_file):
            print(f"✅ Test audio generated: {output_file}")
            os.remove(output_file)  # Clean up
            return True
        else:
            print("❌ Test audio generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Basic TTS test failed: {e}")
        return False

def test_dataset_format(dataset_dir):
    """Test if the dataset format is compatible"""
    dataset_path = Path(dataset_dir)
    
    print(f"🔍 Testing dataset format in: {dataset_path}")
    
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_path}")
        return False
    
    # Check for required files
    wavs_dir = dataset_path / "wavs"
    metadata_file = dataset_path / "metadata.csv"
    
    if not wavs_dir.exists():
        print(f"❌ WAV files directory not found: {wavs_dir}")
        return False
    
    if not metadata_file.exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        return False
    
    # Check WAV files
    wav_files = list(wavs_dir.glob("*.wav"))
    print(f"✅ Found {len(wav_files)} WAV files")
    
    if len(wav_files) == 0:
        print("❌ No WAV files found in dataset")
        return False
    
    # Check metadata format
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) < 2:
            print("❌ Metadata file is empty or missing data")
            return False
        
        # Check header
        header = lines[0].strip().split('|')
        expected_header = ['filename', 'speaker', 'text']
        
        if header != expected_header:
            print(f"❌ Metadata format incorrect")
            print(f"   Expected: {expected_header}")
            print(f"   Found: {header}")
            return False
        
        print(f"✅ Metadata format correct with {len(lines)-1} entries")
        
        # Check a few entries
        print("\n📋 Sample metadata entries:")
        for i, line in enumerate(lines[1:4]):  # Show first 3 data entries
            parts = line.strip().split('|')
            if len(parts) >= 3:
                filename, speaker, text = parts[0], parts[1], parts[2]
                print(f"   {i+1}. {filename} | {speaker} | {text[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
        return False

def test_speaker_identification(dataset_dir):
    """Test speaker identification in the dataset"""
    dataset_path = Path(dataset_dir)
    metadata_file = dataset_path / "metadata.csv"
    
    print("\n👥 Testing speaker identification...")
    
    try:
        speakers = {}
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:]  # Skip header
            
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    speaker = parts[1]
                    if speaker not in speakers:
                        speakers[speaker] = 0
                    speakers[speaker] += 1
        
        print(f"✅ Found {len(speakers)} speakers:")
        for speaker, count in speakers.items():
            print(f"   {speaker.capitalize()}: {count} clips")
        
        # Check if we have the expected speakers
        expected_speakers = ['rick', 'morty']
        for expected in expected_speakers:
            if expected in speakers:
                print(f"✅ {expected.capitalize()} speaker found")
            else:
                print(f"⚠️ {expected.capitalize()} speaker not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Speaker identification test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Rick and Morty TTS setup")
    parser.add_argument("--dataset-dir", default="rick_and_morty_tts", 
                       help="Directory containing the Rick and Morty dataset")
    
    args = parser.parse_args()
    
    print("🧪 Rick and Morty TTS Test Suite")
    print("=" * 40)
    
    # Test 1: Coqui TTS installation
    print("\n1️⃣ Testing Coqui TTS installation...")
    if not test_coqui_installation():
        print("❌ Installation test failed. Please install Coqui TTS first.")
        return
    
    # Test 2: Basic TTS functionality
    print("\n2️⃣ Testing basic TTS functionality...")
    if not test_basic_tts():
        print("❌ Basic TTS test failed. There may be an issue with the TTS installation.")
        return
    
    # Test 3: Dataset format
    print("\n3️⃣ Testing dataset format...")
    if not test_dataset_format(args.dataset_dir):
        print("❌ Dataset format test failed. Please check your dataset.")
        return
    
    # Test 4: Speaker identification
    print("\n4️⃣ Testing speaker identification...")
    if not test_speaker_identification(args.dataset_dir):
        print("❌ Speaker identification test failed.")
        return
    
    print("\n🎉 All tests passed! Your Rick and Morty TTS setup is ready.")
    print("\n💡 Next steps:")
    print("   1. Run the training script: python train_rick_morty_tts.py")
    print("   2. Wait for training to complete")
    print("   3. Use the trained model in your video generation")

if __name__ == "__main__":
    main()
