# Friends Meme Reel Generator

A Python-based video generation tool that creates short-form meme videos featuring Friends characters (Chandler and Joey) with AI-generated voices and custom dialogue.

## Core Functionality

**Video Generation**: Creates vertical 1080x1920 MP4 videos from gameplay footage with overlaid character images and text captions.

**Character Animation**: Positions Chandler (left) and Joey (right) to appear only during their respective dialogue lines with precise timing.

**Text-to-Speech Integration**: Uses ElevenLabs API to generate character-specific voices for each dialogue line, ensuring perfect audio-text synchronization.

**Dynamic Timing**: Automatically measures TTS audio durations and adjusts video timing to eliminate gaps and overlaps between dialogue segments.

**Customizable Content**: JSON-based configuration for dialogue, character positioning, colors, and timing without code changes.

## Key Features

- **Perfect Sync**: Audio, text, and characters align precisely using measured TTS durations
- **Character Timing**: Characters appear/disappear based on who's speaking
- **Text Wrapping**: Automatic text wrapping with custom colors and stroke effects
- **Environment Configuration**: API keys and settings managed via .env file
- **Optimized Output**: 8-second videos with no wasted time or dead air

## Usage

1. Set up your ElevenLabs API key in `.env`
2. Configure dialogue in `dialogue.json`
3. Run `python make_reel_dialogue.py`
4. Output: `friends_reel_voice_issues.mp4`

## Requirements

- Python 3.10+
- MoviePy 2.x
- ElevenLabs API key
- PNG character images
- MP4 gameplay footage

