#!/usr/bin/env python3
"""
Simple script to check the currently configured voice IDs for Chandler and Joey
"""

import os
import json
from dotenv import load_dotenv

def check_voice_configuration():
    """Check voice configuration from both .env and dialogue.json"""
    print("🎭 Voice Configuration Checker")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check .env file
    print("🔍 Checking .env file...")
    env_chandler = os.getenv('CHANDLER_VOICE_ID')
    env_joey = os.getenv('JOEY_VOICE_ID')
    env_api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if env_chandler:
        print(f"✅ Chandler voice ID: {env_chandler}")
    else:
        print("❌ CHANDLER_VOICE_ID not found in .env")
    
    if env_joey:
        print(f"✅ Joey voice ID: {env_joey}")
    else:
        print("❌ JOEY_VOICE_ID not found in .env")
    
    if env_api_key and env_api_key != 'your_api_key_here':
        print(f"✅ API Key: {env_api_key[:8]}...")
    else:
        print("❌ ELEVENLABS_API_KEY not found or not set in .env")
    
    # Check dialogue.json
    print("\n🔍 Checking dialogue.json...")
    try:
        with open('dialogue.json', 'r') as f:
            config = json.load(f)
            
        tts_settings = config.get('tts_settings', {})
        voices = tts_settings.get('voices', {})
        
        chandler_config = voices.get('chandler', {})
        joey_config = voices.get('joey', {})
        
        if chandler_config.get('voice_id'):
            print(f"✅ Chandler voice ID: {chandler_config['voice_id']}")
        else:
            print("❌ Chandler voice ID not found in dialogue.json")
            
        if joey_config.get('voice_id'):
            print(f"✅ Joey voice ID: {joey_config['voice_id']}")
        else:
            print("❌ Joey voice ID not found in dialogue.json")
            
        if tts_settings.get('api_key') and tts_settings['api_key'] != 'YOUR_ELEVENLABS_API_KEY_HERE':
            print(f"✅ API Key: {tts_settings['api_key'][:8]}...")
        else:
            print("❌ API key not found or not set in dialogue.json")
            
    except FileNotFoundError:
        print("❌ dialogue.json not found")
    except json.JSONDecodeError:
        print("❌ dialogue.json is not valid JSON")
    except Exception as e:
        print(f"❌ Error reading dialogue.json: {e}")
    
    # Show which source takes precedence
    print("\n📋 Configuration Priority:")
    print("1. .env file (highest priority)")
    print("2. dialogue.json (fallback)")
    print("3. Hardcoded defaults (lowest priority)")
    
    if env_chandler and env_joey and env_api_key and env_api_key != 'your_api_key_here':
        print("\n🎉 Your .env file is properly configured!")
        print("   The script will use these values.")
    else:
        print("\n⚠️  Your .env file needs configuration.")
        print("   Please add your ElevenLabs API key and voice IDs.")

if __name__ == "__main__":
    check_voice_configuration()
