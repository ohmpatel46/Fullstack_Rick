#!/usr/bin/env python3
"""
Setup script to help get Rick and Morty character images
"""

import os

def setup_character_images():
    """Check for Rick and Morty images and provide instructions"""
    print("🎭 Rick & Morty Character Image Setup")
    print("=" * 40)
    
    characters_dir = "Data/Characters"
    rick_image = os.path.join(characters_dir, "rick.png")
    morty_image = os.path.join(characters_dir, "morty.png")
    
    # Check current status
    rick_exists = os.path.exists(rick_image)
    morty_exists = os.path.exists(morty_image)
    
    print(f"📁 Characters directory: {characters_dir}")
    print(f"🧪 Rick image: {'✅ Found' if rick_exists else '❌ Missing'} - {rick_image}")
    print(f"👦 Morty image: {'✅ Found' if morty_exists else '❌ Missing'} - {morty_image}")
    
    if rick_exists and morty_exists:
        print("\n🎉 All character images are ready!")
        return True
    
    print(f"\n📋 Next Steps:")
    if not rick_exists:
        print(f"1. Find a Rick Sanchez character image (PNG with transparent background preferred)")
        print(f"2. Save it as: {rick_image}")
    
    if not morty_exists:
        print(f"3. Find a Morty Smith character image (PNG with transparent background preferred)")
        print(f"4. Save it as: {morty_image}")
    
    print(f"\n💡 Tips:")
    print(f"   - Use transparent PNG images for best results")
    print(f"   - Images should be roughly 500x500 pixels or larger")
    print(f"   - Character should be facing forward or slightly to the side")
    print(f"   - Avoid copyrighted official images - use fan art or create your own")
    
    print(f"\n🔍 Good sources:")
    print(f"   - Search for 'Rick and Morty PNG transparent'")
    print(f"   - Look for fan art with transparent backgrounds")
    print(f"   - Consider simple vector-style images")
    
    return False

def main():
    """Main setup function"""
    ready = setup_character_images()
    
    if ready:
        print(f"\n🚀 Ready to generate Rick & Morty reels!")
        print(f"   Run: python make_rick_morty_reel.py")
    else:
        print(f"\n⏳ Please add the missing character images first")

if __name__ == "__main__":
    main()

