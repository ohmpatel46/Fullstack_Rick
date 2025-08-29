#!/usr/bin/env python3
"""
Rick and Morty SRT Parser and Audio Extractor
Parses .srt subtitle files, extracts audio clips, and generates metadata for TTS training.
"""

import os
import re
import csv
import json
from pathlib import Path
from pydub import AudioSegment
import argparse
from typing import List, Dict, Tuple

class RickMortySRTParser:
    def __init__(self, srt_dir: str, audio_dir: str, output_dir: str):
        """
        Initialize the parser
        
        Args:
            srt_dir: Directory containing .srt files
            audio_dir: Directory containing .mp3 episode files
            output_dir: Directory to save extracted audio clips and metadata
        """
        self.srt_dir = Path(srt_dir)
        self.audio_dir = Path(audio_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directories
        self.wavs_dir = self.output_dir / "wavs"
        self.wavs_dir.mkdir(parents=True, exist_ok=True)
        
        # Character mapping
        self.characters = {
            'rick': 'Rick',
            'morty': 'Morty'
        }
        
        # Episode mapping (SRT filename -> MP3 filename)
        self.episode_mapping = self._create_episode_mapping()
        
    def _create_episode_mapping(self) -> Dict[str, str]:
        """Create mapping between SRT files and MP3 files"""
        mapping = {}
        
        # Get all SRT files
        srt_files = list(self.srt_dir.glob("*.srt"))
        mp3_files = list(self.audio_dir.glob("*.mp3"))
        
        print(f"📁 Found {len(srt_files)} SRT files and {len(mp3_files)} MP3 files")
        
        # Create mapping based on episode numbers
        for srt_file in srt_files:
            srt_name = srt_file.stem.lower()
            
            # Find matching MP3 file
            for mp3_file in mp3_files:
                mp3_name = mp3_file.stem.lower()
                
                # Check if they're the same episode
                if self._episodes_match(srt_name, mp3_name):
                    mapping[srt_file.name] = mp3_file.name
                    print(f"🔗 Mapped: {srt_file.name} → {mp3_file.name}")
                    break
        
        return mapping
    
    def _episodes_match(self, srt_name: str, mp3_name: str) -> bool:
        """Check if SRT and MP3 files are from the same episode"""
        # Extract episode numbers (e.g., S01E01, E01, etc.)
        srt_ep = re.search(r'[sS](\d{1,2})[eE](\d{1,2})', srt_name)
        mp3_ep = re.search(r'[sS](\d{1,2})[eE](\d{1,2})', mp3_name)
        
        if srt_ep and mp3_ep:
            return srt_ep.group(1) == mp3_ep.group(1) and srt_ep.group(2) == mp3_ep.group(2)
        
        # Fallback: check if names are similar
        return any(word in mp3_name for word in srt_name.split())
    
    def parse_srt_file(self, srt_file: Path) -> List[Dict]:
        """Parse a single SRT file and extract tagged dialogue"""
        print(f"📖 Parsing {srt_file.name}...")
        
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into subtitle blocks
        blocks = content.strip().split('\n\n')
        dialogue_entries = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Extract subtitle number, timestamp, and text
            try:
                subtitle_num = int(lines[0])
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
                
                # Check if this line contains tagged dialogue
                tagged_dialogue = self._extract_tagged_dialogue(text)
                
                if tagged_dialogue:
                    # Parse timestamp
                    start_time, end_time = self._parse_timestamp(timestamp)
                    
                    dialogue_entries.append({
                        'subtitle_num': subtitle_num,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time,
                        'text': text,
                        'tagged_dialogue': tagged_dialogue
                    })
                    
            except (ValueError, IndexError) as e:
                print(f"⚠️  Error parsing block: {e}")
                continue
        
        print(f"✅ Found {len(dialogue_entries)} tagged dialogue entries")
        return dialogue_entries
    
    def _extract_tagged_dialogue(self, text: str) -> List[Dict]:
        """Extract tagged dialogue from subtitle text"""
        tagged_lines = []
        
        # Look for patterns like [[Rick: ...]] or [[Morty: ...]]
        pattern = r'\[\[(Rick|Morty):\s*([^\]]+)\]\]'
        matches = re.findall(pattern, text)
        
        for speaker, dialogue in matches:
            tagged_lines.append({
                'speaker': speaker.lower(),
                'text': dialogue.strip()
            })
        
        return tagged_lines
    
    def _parse_timestamp(self, timestamp: str) -> Tuple[float, float]:
        """Parse SRT timestamp format (HH:MM:SS,mmm) to seconds"""
        # Remove milliseconds and split
        time_parts = timestamp.replace(',', '.').split(' --> ')
        
        start_time = self._time_to_seconds(time_parts[0])
        end_time = self._time_to_seconds(time_parts[1])
        
        return start_time, end_time
    
    def _time_to_seconds(self, time_str: str) -> float:
        """Convert time string (HH:MM:SS.mmm) to seconds"""
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        return hours * 3600 + minutes * 60 + seconds
    
    def extract_audio_clips(self, srt_file: Path, dialogue_entries: List[Dict]) -> List[Dict]:
        """Extract audio clips from MP3 file based on dialogue timestamps"""
        if srt_file.name not in self.episode_mapping:
            print(f"❌ No MP3 file found for {srt_file.name}")
            return []
        
        mp3_file = self.audio_dir / self.episode_mapping[srt_file.name]
        print(f"🎵 Loading audio from {mp3_file.name}...")
        
        # Load audio file
        try:
            audio = AudioSegment.from_mp3(mp3_file)
            print(f"✅ Loaded audio: {len(audio) / 1000:.1f}s duration")
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            return []
        
        extracted_clips = []
        clip_counter = 1
        
        for entry in dialogue_entries:
            for dialogue in entry['tagged_dialogue']:
                # Convert times to milliseconds
                start_ms = int(entry['start_time'] * 1000)
                end_ms = int(entry['end_time'] * 1000)
                
                # Extract audio segment
                audio_segment = audio[start_ms:end_ms]
                
                # Generate filename
                speaker = dialogue['speaker']
                filename = f"{speaker}_{clip_counter:04d}.wav"
                filepath = self.wavs_dir / filename
                
                # Export as WAV
                try:
                    audio_segment.export(filepath, format="wav")
                    
                    extracted_clips.append({
                        'filename': filename,
                        'speaker': speaker,
                        'text': dialogue['text'],
                        'start_time': entry['start_time'],
                        'end_time': entry['end_time'],
                        'duration': entry['duration'],
                        'episode': srt_file.stem
                    })
                    
                    print(f"🎵 Exported: {filename} ({entry['duration']:.2f}s)")
                    clip_counter += 1
                    
                except Exception as e:
                    print(f"❌ Error exporting {filename}: {e}")
        
        return extracted_clips
    
    def generate_metadata_csv(self, all_clips: List[Dict]):
        """Generate metadata.csv file for TTS training"""
        metadata_file = self.output_dir / "metadata.csv"
        
        with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            
            # Write header
            writer.writerow(['filename', 'speaker', 'text'])
            
            # Write data
            for clip in all_clips:
                writer.writerow([
                    clip['filename'],
                    clip['speaker'],
                    clip['text']
                ])
        
        print(f"📊 Generated metadata.csv with {len(all_clips)} entries")
        
        # Also save detailed metadata as JSON
        detailed_metadata = {
            'total_clips': len(all_clips),
            'speakers': {},
            'episodes': {},
            'clips': all_clips
        }
        
        # Count by speaker
        for clip in all_clips:
            speaker = clip['speaker']
            if speaker not in detailed_metadata['speakers']:
                detailed_metadata['speakers'][speaker] = 0
            detailed_metadata['speakers'][speaker] += 1
        
        # Count by episode
        for clip in all_clips:
            episode = clip['episode']
            if episode not in detailed_metadata['episodes']:
                detailed_metadata['episodes'][episode] = 0
            detailed_metadata['episodes'][episode] += 1
        
        json_file = self.output_dir / "detailed_metadata.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_metadata, f, indent=2)
        
        print(f"📋 Generated detailed_metadata.json")
    
    def process_all_episodes(self):
        """Process all SRT files and extract audio clips"""
        print("🚀 Starting Rick and Morty audio extraction...")
        print("=" * 60)
        
        all_clips = []
        
        # Process each SRT file
        for srt_file in self.srt_dir.glob("*.srt"):
            if srt_file.name not in self.episode_mapping:
                print(f"⚠️  Skipping {srt_file.name} (no matching MP3)")
                continue
            
            print(f"\n🎬 Processing episode: {srt_file.name}")
            print("-" * 40)
            
            # Parse SRT file
            dialogue_entries = self.parse_srt_file(srt_file)
            
            if dialogue_entries:
                # Extract audio clips
                episode_clips = self.extract_audio_clips(srt_file, dialogue_entries)
                all_clips.extend(episode_clips)
            else:
                print("⚠️  No tagged dialogue found in this episode")
        
        # Generate metadata
        if all_clips:
            print(f"\n📊 Processing complete!")
            print(f"🎵 Total clips extracted: {len(all_clips)}")
            
            # Show summary by speaker
            speaker_counts = {}
            for clip in all_clips:
                speaker = clip['speaker']
                speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
            
            for speaker, count in speaker_counts.items():
                print(f"   {speaker.capitalize()}: {count} clips")
            
            # Generate metadata files
            self.generate_metadata_csv(all_clips)
            
            print(f"\n✅ Dataset ready in: {self.output_dir}")
            print(f"📁 Audio clips: {self.wavs_dir}")
            print(f"📊 Metadata: metadata.csv")
            
        else:
            print("❌ No clips were extracted. Check your SRT files for tagged dialogue.")

def main():
    parser = argparse.ArgumentParser(description="Parse Rick and Morty SRT files and extract audio clips")
    parser.add_argument("--srt-dir", default="Data/Rick_n_Morty/Subtitles", help="Directory containing .srt files")
    parser.add_argument("--audio-dir", default="Data/Rick_n_Morty/Audio", help="Directory containing .mp3 episode files")
    parser.add_argument("--output-dir", default="rick_and_morty_tts", help="Output directory for extracted clips and metadata")
    
    args = parser.parse_args()
    
    # Create parser and process episodes
    parser = RickMortySRTParser(args.srt_dir, args.audio_dir, args.output_dir)
    parser.process_all_episodes()

if __name__ == "__main__":
    main()
