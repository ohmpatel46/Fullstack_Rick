#!/usr/bin/env python3
"""
Rick and Morty Coqui TTS Fine-tuning Script
Trains a custom TTS model using extracted audio clips and metadata.
"""

import os
import json
import argparse
from pathlib import Path
import subprocess
import sys

class RickMortyTTSTrainer:
    def __init__(self, dataset_dir: str, output_dir: str):
        """
        Initialize the TTS trainer
        
        Args:
            dataset_dir: Directory containing the Rick and Morty dataset
            output_dir: Directory to save the trained model
        """
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.wavs_dir = self.dataset_dir / "wavs"
        self.metadata_file = self.dataset_dir / "metadata.csv"
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Model configuration
        self.model_config = {
            "model_name": "rick_morty_tts",
            "run_name": "rick_morty_finetune",
            "run_description": "Fine-tuned Rick and Morty voices using Coqui TTS"
        }
    
    def check_dataset(self):
        """Check if the dataset is ready for training"""
        print("🔍 Checking dataset...")
        
        if not self.dataset_dir.exists():
            print(f"❌ Dataset directory not found: {self.dataset_dir}")
            return False
        
        if not self.wavs_dir.exists():
            print(f"❌ WAV files directory not found: {self.wavs_dir}")
            return False
        
        if not self.metadata_file.exists():
            print(f"❌ Metadata file not found: {self.metadata_file}")
            return False
        
        # Count audio files
        wav_files = list(self.wavs_dir.glob("*.wav"))
        print(f"✅ Found {len(wav_files)} WAV files")
        
        # Check metadata
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) < 2:  # Header + at least one data line
                    print("❌ Metadata file is empty or missing data")
                    return False
                
                # Parse first few lines to check format
                header = lines[0].strip().split('|')
                expected_header = ['filename', 'speaker', 'text']
                
                if header != expected_header:
                    print(f"❌ Metadata format incorrect. Expected: {expected_header}")
                    print(f"   Found: {header}")
                    return False
                
                print(f"✅ Metadata format correct with {len(lines)-1} entries")
                
        except Exception as e:
            print(f"❌ Error reading metadata: {e}")
            return False
        
        return True
    
    def install_coqui_tts(self):
        """Install Coqui TTS if not already installed"""
        try:
            import TTS
            print(f"✅ Coqui TTS already installed: {TTS.__version__}")
            return True
        except ImportError:
            print("📦 Installing Coqui TTS...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "TTS>=0.22.0"])
                print("✅ Coqui TTS installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Coqui TTS: {e}")
                return False
    
    def prepare_training_data(self):
        """Prepare the dataset for TTS training"""
        print("📊 Preparing training data...")
        
        # Read metadata and organize by speaker
        speakers = {}
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:]  # Skip header
            
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    filename, speaker, text = parts[0], parts[1], parts[2]
                    
                    if speaker not in speakers:
                        speakers[speaker] = []
                    
                    # Check if audio file exists
                    audio_path = self.wavs_dir / filename
                    if audio_path.exists():
                        speakers[speaker].append({
                            'filename': filename,
                            'text': text,
                            'audio_path': str(audio_path)
                        })
        
        # Show dataset statistics
        print(f"\n📈 Dataset Statistics:")
        total_clips = 0
        for speaker, clips in speakers.items():
            print(f"   {speaker.capitalize()}: {len(clips)} clips")
            total_clips += len(clips)
        
        print(f"   Total: {total_clips} clips")
        
        # Save organized data
        training_data_file = self.output_dir / "training_data.json"
        with open(training_data_file, 'w', encoding='utf-8') as f:
            json.dump(speakers, f, indent=2)
        
        print(f"✅ Training data saved to: {training_data_file}")
        return speakers
    
    def create_training_config(self, speakers):
        """Create Coqui TTS training configuration"""
        print("⚙️ Creating training configuration...")
        
        # Base configuration for fine-tuning
        config = {
            "model": "tts_models/en/multilingual/multi-dataset/your_tts",
            "run_name": self.model_config["run_name"],
            "run_description": self.model_config["run_description"],
            "audio": {
                "sample_rate": 22050,
                "hop_length": 256,
                "win_length": 1024,
                "n_fft": 1024,
                "mel_channels": 80,
                "mel_fmin": 0.0,
                "mel_fmax": 8000.0
            },
            "training": {
                "batch_size": 8,
                "eval_batch_size": 8,
                "num_loader_workers": 4,
                "num_eval_loader_workers": 4,
                "run_eval": True,
                "test_delay_epochs": -1,
                "epochs": 1000,
                "text_cleaner": "english_cleaners",
                "use_phonemes": False,
                "phoneme_language": "en-us",
                "phoneme_cache_path": "phoneme_cache",
                "print_step": 25,
                "print_eval": True,
                "mixed_precision": True,
                "output_path": str(self.output_dir),
                "datasets": []
            }
        }
        
        # Add dataset configuration for each speaker
        for speaker, clips in speakers.items():
            dataset_config = {
                "name": f"rick_morty_{speaker}",
                "path": str(self.dataset_dir),
                "meta_file_train": f"train_{speaker}.csv",
                "meta_file_val": f"val_{speaker}.csv",
                "path": str(self.dataset_dir),
                "language": "en"
            }
            config["training"]["datasets"].append(dataset_config)
        
        # Save configuration
        config_file = self.output_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Training configuration saved to: {config_file}")
        return config_file
    
    def split_train_val_data(self, speakers):
        """Split data into training and validation sets"""
        print("✂️ Splitting data into train/validation sets...")
        
        for speaker, clips in speakers.items():
            # 80% train, 20% validation
            split_point = int(len(clips) * 0.8)
            train_clips = clips[:split_point]
            val_clips = clips[split_point:]
            
            # Create train CSV
            train_file = self.dataset_dir / f"train_{speaker}.csv"
            with open(train_file, 'w', newline='', encoding='utf-8') as f:
                f.write("filename|speaker|text\n")
                for clip in train_clips:
                    f.write(f"{clip['filename']}|{clip['speaker']}|{clip['text']}\n")
            
            # Create validation CSV
            val_file = self.dataset_dir / f"val_{speaker}.csv"
            with open(val_file, 'w', newline='', encoding='utf-8') as f:
                f.write("filename|speaker|text\n")
                for clip in val_clips:
                    f.write(f"{clip['filename']}|{clip['speaker']}|{clip['text']}\n")
            
            print(f"   {speaker.capitalize()}: {len(train_clips)} train, {len(val_clips)} validation")
    
    def start_training(self, config_file):
        """Start the TTS training process"""
        print("🚀 Starting TTS training...")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"⚙️ Config file: {config_file}")
        
        # Training command
        cmd = [
            "tts",
            "--config_path", str(config_file),
            "--coqpit.datasets.0.path", str(self.dataset_dir),
            "--coqpit.output_path", str(self.output_dir)
        ]
        
        print(f"\n🎯 Training command:")
        print(" ".join(cmd))
        
        print(f"\n💡 To start training manually, run:")
        print(f"   cd {self.output_dir}")
        print(f"   tts --config_path config.json")
        
        print(f"\n📚 Training will create:")
        print(f"   - Model checkpoints in {self.output_dir}/checkpoint_*.pth")
        print(f"   - Training logs in {self.output_dir}/train.log")
        print(f"   - Final model in {self.output_dir}/best_model.pth")
        
        # Ask if user wants to start training now
        start_now = input("\n🤔 Start training now? (y/n): ").lower().strip()
        
        if start_now == 'y':
            try:
                print("🎬 Starting training process...")
                subprocess.run(cmd, cwd=self.output_dir, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Training failed: {e}")
                print("💡 You can start training manually using the command above")
        else:
            print("⏸️ Training not started. Use the command above when ready.")
    
    def train(self):
        """Main training pipeline"""
        print("🎭 Rick and Morty TTS Fine-tuning Pipeline")
        print("=" * 50)
        
        # Check dataset
        if not self.check_dataset():
            print("❌ Dataset check failed. Please ensure your dataset is ready.")
            return False
        
        # Install Coqui TTS
        if not self.install_coqui_tts():
            print("❌ Failed to install Coqui TTS. Please install manually.")
            return False
        
        # Prepare training data
        speakers = self.prepare_training_data()
        if not speakers:
            print("❌ No training data found.")
            return False
        
        # Split data
        self.split_train_val_data(speakers)
        
        # Create configuration
        config_file = self.create_training_config(speakers)
        
        # Start training
        self.start_training(config_file)
        
        print("\n🎉 Training pipeline setup complete!")
        return True

def main():
    parser = argparse.ArgumentParser(description="Train Rick and Morty TTS model using Coqui TTS")
    parser.add_argument("--dataset-dir", default="rick_and_morty_tts", 
                       help="Directory containing the Rick and Morty dataset")
    parser.add_argument("--output-dir", default="rick_morty_tts_model", 
                       help="Directory to save the trained model")
    
    args = parser.parse_args()
    
    # Create trainer and start
    trainer = RickMortyTTSTrainer(args.dataset_dir, args.output_dir)
    trainer.train()

if __name__ == "__main__":
    main()
