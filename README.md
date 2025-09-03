# AI Voice Cloning for Meme Videos: Rick & Morty TTS Pipeline

A complete Python pipeline for creating viral Instagram-style reels with AI-generated character voices, featuring data collection, voice cloning, and video generation.

**Check out the demo reel on my [LinkedIn post](https://www.linkedin.com/feed/update/urn:li:activity:7368487143922434048/)**

## Project Overview

This project demonstrates a full-stack approach to AI content creation, from manual data annotation to fine-tuned voice synthesis. Inspired by viral Instagram reels where animated characters discuss current tech trends, this system creates similar content using Rick & Morty characters with AI-generated voices.

## Demo

Check out the demo reel showcasing the voice cloning results:

![Demo Reel](Data/Artifacts/Rick_n_Morty_CoQui_TTS.mp4)

The demo demonstrates the complete pipeline in action, featuring Rick and Morty characters with AI-generated voices discussing tech topics over Minecraft gameplay footage.

## Core Components

### Data Collection Pipeline
- Manual subtitle annotation for Rick & Morty episodes
- Automated audio extraction using precise timestamps
- Quality control filtering for clean training data
- Metadata generation for TTS training

### Voice Cloning System
- Fine-tuned Coqui TTS with YourTTS model
- Character-specific voice synthesis for Rick and Morty
- Zero-shot voice cloning capabilities
- Training on 314 cleaned audio samples

### Video Generation Engine
- MoviePy-based video composition
- Background gameplay footage integration
- Character image layering with precise timing
- Text overlay with custom styling and wrapping
- Perfect audio-video synchronization

## Technical Stack

- **Python 3.10+** with MoviePy for video processing
- **Coqui TTS** for voice synthesis and cloning
- **Manual annotation** for data preparation
- **JSON configuration** for dialogue and timing
- **Fine-tuned models** for character voice generation

## Key Features

- Complete data collection and annotation workflow
- Fine-tuned voice cloning for distinct character voices
- Automated video generation with perfect synchronization
- Customizable dialogue and character positioning
- Quality control for training data preparation
- Support for multiple character voices in single reels

## Usage

### Data Collection
1. Annotate subtitle files with character tags
2. Run `python parse_rick_morty_srt.py` to extract audio clips
3. Review and clean extracted samples

### Voice Cloning
1. Prepare cleaned dataset in `rick_and_morty_tts/`
2. Fine-tune model using Coqui TTS
3. Test voice cloning with `clone_rick_voice.py` and `clone_morty_voice.py`

### Video Generation
1. Configure dialogue in `rick_morty_dialogue.json`
2. Run `python make_rick_morty_reel.py` for Rick & Morty content
3. Run `python make_reel_dialogue.py` for Friends content

## Project Structure

```
├── Data/
│   ├── Artifacts/         # Demo videos and outputs
│   ├── Characters/        # Character PNG images
│   └── Gameplay/         # Background video footage
├── rick_and_morty_tts/   # Training dataset and metadata
├── audio_clips/         # Generated audio samples
├── parse_rick_morty_srt.py # Data collection pipeline
├── clone_*_voice.py     # Voice cloning scripts
├── make_*_reel.py      # Video generation scripts
└── *.json              # Configuration files
```

## Requirements

- Python 3.10+
- MoviePy 2.x
- Coqui TTS
- PyDub for audio processing
- Character images and background footage
- GPU recommended for TTS training

## Educational Purpose

This project was created for educational purposes to demonstrate the complete pipeline of AI-powered content creation, from data collection to final video generation. All character voices and content are used under fair use principles for non-commercial, educational content creation.

