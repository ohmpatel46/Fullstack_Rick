import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_elevenlabs_voices(api_key):
    """List all available ElevenLabs voices"""
    
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        print("🔍 Fetching available voices from ElevenLabs...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            print(f"\n✅ Found {len(voices['voices'])} voices:\n")
            
            # Group voices by category for easier selection
            voice_categories = {
                "Male Voices": [],
                "Female Voices": [],
                "Character Voices": [],
                "Other": []
            }
            
            for voice in voices['voices']:
                voice_info = {
                    "id": voice['voice_id'],
                    "name": voice['name'],
                    "description": voice.get('labels', {}).get('description', 'No description'),
                    "category": voice.get('labels', {}).get('category', 'Other')
                }
                
                # Categorize voices
                if 'male' in voice_info['description'].lower() or 'man' in voice_info['description'].lower():
                    voice_categories["Male Voices"].append(voice_info)
                elif 'female' in voice_info['description'].lower() or 'woman' in voice_info['description'].lower():
                    voice_categories["Female Voices"].append(voice_info)
                elif 'character' in voice_info['description'].lower() or 'cartoon' in voice_info['description'].lower():
                    voice_categories["Character Voices"].append(voice_info)
                else:
                    voice_categories["Other"].append(voice_info)
            
            # Display voices by category
            for category, voice_list in voice_categories.items():
                if voice_list:
                    print(f"\n📁 {category}:")
                    print("-" * 50)
                    for voice in voice_list:
                        print(f"🎤 {voice['name']}")
                        print(f"   ID: {voice['id']}")
                        print(f"   Description: {voice['description']}")
                        print()
            
            # Suggest voices for Chandler and Joey
            print("\n🎭 **Suggested Voices for Friends Characters:**")
            print("=" * 50)
            
            chandler_suggestions = []
            joey_suggestions = []
            
            for voice in voices['voices']:
                description = voice.get('labels', {}).get('description', '').lower()
                name = voice['name'].lower()
                
                # Chandler: sarcastic, confused, male
                if any(word in description for word in ['sarcastic', 'confused', 'dry', 'witty', 'male']):
                    chandler_suggestions.append(voice)
                
                # Joey: friendly, enthusiastic, male
                if any(word in description for word in ['friendly', 'enthusiastic', 'happy', 'energetic', 'male']):
                    joey_suggestions.append(voice)
            
            print("\n👨 **Chandler (Sarcastic/Confused):**")
            for voice in chandler_suggestions[:3]:  # Top 3 suggestions
                print(f"   • {voice['name']} (ID: {voice['voice_id']})")
                print(f"     {voice.get('labels', {}).get('description', 'No description')}")
            
            print("\n😊 **Joey (Friendly/Enthusiastic):**")
            for voice in joey_suggestions[:3]:  # Top 3 suggestions
                print(f"   • {voice['name']} (ID: {voice['voice_id']})")
                print(f"     {voice.get('labels', {}).get('description', 'No description')}")
            
            # Show current configuration
            print(f"\n💡 **Current Configuration:**")
            print(f"   Chandler: {os.getenv('CHANDLER_VOICE_ID', 'Not set in .env')}")
            print(f"   Joey: {os.getenv('JOEY_VOICE_ID', 'Not set in .env')}")
            
            # Also check dialogue.json
            try:
                with open('dialogue.json', 'r') as f:
                    config = json.load(f)
                    chandler_id = config.get('tts_settings', {}).get('voices', {}).get('chandler', {}).get('voice_id', 'Not set')
                    joey_id = config.get('tts_settings', {}).get('voices', {}).get('joey', {}).get('voice_id', 'Not set')
                    print(f"   From dialogue.json - Chandler: {chandler_id}")
                    print(f"   From dialogue.json - Joey: {joey_id}")
            except:
                print("   Could not read dialogue.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to fetch voices: {e}")

def test_voice_sample(api_key, voice_id, text="Hello, this is a test of the voice."):
    """Test a specific voice with sample text"""
    
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
            "stability": float(os.getenv('TTS_STABILITY', 0.5)),
            "similarity_boost": float(os.getenv('TTS_SIMILARITY_BOOST', 0.75))
        }
    }
    
    try:
        print(f"🎤 Testing voice {voice_id}...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save test audio
            filename = f"voice_test_{voice_id}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Test audio saved as {filename}")
            print(f"🎵 Play this file to hear the voice!")
        else:
            print(f"❌ Test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def suggest_voices_for_characters():
    """Suggest voices for Chandler and Joey based on available voices"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("❌ No API key found. Please set ELEVENLABS_API_KEY in your .env file")
        return
    
    # Get configured voice IDs from environment
    chandler_voice_id = os.getenv('CHANDLER_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
    joey_voice_id = os.getenv('JOEY_VOICE_ID', 'VR6AewLTigWG4xSOukaG')
    
    print(f"\n🎭 Current Voice Configuration:")
    print(f"  Chandler: {chandler_voice_id}")
    print(f"  Joey: {joey_voice_id}")
    
    # Get available voices
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            voices = response.json()
            
            print(f"\n🎯 Available Voices ({len(voices.get('voices', []))} total):")
            
            # Categorize voices
            male_voices = []
            female_voices = []
            other_voices = []
            
            for voice in voices.get('voices', []):
                voice_info = {
                    'name': voice['name'],
                    'voice_id': voice['voice_id'],
                    'category': voice.get('category', 'unknown')
                }
                
                # Simple categorization based on name and category
                name_lower = voice['name'].lower()
                if any(gender in name_lower for gender in ['male', 'man', 'guy', 'dude', 'chandler', 'joey']):
                    male_voices.append(voice_info)
                elif any(gender in name_lower for gender in ['female', 'woman', 'girl', 'lady', 'rachel', 'monica']):
                    female_voices.append(voice_info)
                else:
                    other_voices.append(voice_info)
            
            # Show male voices (most relevant for Chandler and Joey)
            if male_voices:
                print(f"\n👨 Male Voices ({len(male_voices)}):")
                for voice in male_voices[:10]:  # Show first 10
                    current_marker = " (CURRENT)" if voice['voice_id'] == chandler_voice_id or voice['voice_id'] == joey_voice_id else ""
                    print(f"  - {voice['name']} (ID: {voice['voice_id']}){current_marker}")
            
            # Show other voices
            if other_voices:
                print(f"\n🎭 Other Voices ({len(other_voices)}):")
                for voice in other_voices[:5]:  # Show first 5
                    current_marker = " (CURRENT)" if voice['voice_id'] == chandler_voice_id or voice['voice_id'] == joey_voice_id else ""
                    print(f"  - {voice['name']} (ID: {voice['voice_id']}){current_marker}")
            
            # Show female voices
            if female_voices:
                print(f"\n👩 Female Voices ({len(female_voices)}):")
                for voice in female_voices[:5]:  # Show first 5
                    current_marker = " (CURRENT)" if voice['voice_id'] == chandler_voice_id or voice['voice_id'] == joey_voice_id else ""
                    print(f"  - {voice['name']} (ID: {voice['voice_id']}){current_marker}")
            
            print(f"\n💡 To change voices, update your .env file with new voice IDs")
            print(f"   CHANDLER_VOICE_ID=new_id_here")
            print(f"   JOEY_VOICE_ID=new_id_here")
            
        else:
            print(f"❌ Failed to get voices: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting voices: {e}")

if __name__ == "__main__":
    print("🎤 ElevenLabs Voice Explorer")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("❌ No API key found!")
        print("Please set ELEVENLABS_API_KEY in your .env file")
        print("\nTo get an API key:")
        print("1. Go to https://elevenlabs.io")
        print("2. Sign up for a free account")
        print("3. Get your API key from the dashboard")
        print("4. Add it to your .env file")
        exit(1)
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Show current voice configuration
    suggest_voices_for_characters()
    
    # List all voices
    list_elevenlabs_voices(api_key)
    
    # Test specific voice if provided
    test_choice = input("\n🧪 **Test Specific Voices:**\nWould you like to test a specific voice? (y/n): ").lower()
    
    if test_choice == 'y':
        voice_id = input("Enter voice ID to test: ").strip()
        test_text = input("Enter test text (or press Enter for default): ").strip()
        if not test_text:
            test_text = "Hello, this is a test of the voice."
        
        test_voice_sample(api_key, voice_id, test_text)
