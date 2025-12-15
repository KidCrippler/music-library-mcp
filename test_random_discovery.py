#!/usr/bin/env python3
"""Test the random discovery functionality."""

import json
from music_library_mcp.database import SongsDatabase

# Initialize database
SONGS_INDEX_URL = "https://raw.githubusercontent.com/KidCrippler/songs/master/songs.json"

print("🔍 Testing Random Discovery Feature\n")
print("=" * 60)

try:
    print("\n📥 Loading database from remote URL...")
    db = SongsDatabase(SONGS_INDEX_URL)
    
    stats = db.get_stats()
    print(f"✓ Database loaded successfully!")
    print(f"  - Total songs: {stats['total_songs']}")
    print(f"  - Total artists: {stats['total_artists']}")
    print(f"  - Total composers: {stats['total_composers']}")
    print(f"  - Total lyricists: {stats['total_lyricists']}")
    print(f"  - Total translators: {stats['total_translators']}")
    
    # Show available categories
    print(f"\n📂 Available categories:")
    for cat in stats['categories'][:10]:  # Show first 10
        print(f"  - {cat['name']} (ID: {cat['id']}, {cat['song_count']} songs)")
    
    # Test 1: Get random content (all languages)
    print("\n" + "=" * 60)
    print("\n🎲 TEST 1: Random discovery (all languages)")
    print("-" * 60)
    result = db.get_random_discovery(language="both", count=5)
    
    print(f"\nLanguage filter: {result['language_filter']}")
    print(f"\nSample counts:")
    for key, count in result['counts'].items():
        print(f"  - {key}: {count}")
    
    print(f"\n🎵 Sample songs:")
    for i, song in enumerate(result['songs'][:3], 1):
        print(f"  {i}. {song.get('name')} - {song.get('singer')}")
    
    print(f"\n🎤 Sample artists:")
    for i, artist in enumerate(result['artists'][:3], 1):
        print(f"  {i}. {artist}")
    
    print(f"\n🎼 Sample composers:")
    for i, composer in enumerate(result['composers'][:3], 1):
        print(f"  {i}. {composer}")
    
    # Test 2: Hebrew only
    print("\n" + "=" * 60)
    print("\n🇮🇱 TEST 2: Random discovery (Hebrew only)")
    print("-" * 60)
    result_hebrew = db.get_random_discovery(language="hebrew", count=5)
    
    print(f"\nLanguage filter: {result_hebrew['language_filter']}")
    print(f"Found {result_hebrew['counts']['songs']} Hebrew songs")
    
    if result_hebrew['songs']:
        print(f"\n🎵 Sample Hebrew songs:")
        for i, song in enumerate(result_hebrew['songs'][:3], 1):
            print(f"  {i}. {song.get('name')} - {song.get('singer')}")
    
    # Test 3: English only
    print("\n" + "=" * 60)
    print("\n🇬🇧 TEST 3: Random discovery (English only)")
    print("-" * 60)
    result_english = db.get_random_discovery(language="english", count=5)
    
    print(f"\nLanguage filter: {result_english['language_filter']}")
    print(f"Found {result_english['counts']['songs']} English songs")
    
    if result_english['songs']:
        print(f"\n🎵 Sample English songs:")
        for i, song in enumerate(result_english['songs'][:3], 1):
            print(f"  {i}. {song.get('name')} - {song.get('singer')}")
    
    print("\n" + "=" * 60)
    print("\n✅ All tests completed successfully!")
    print("\n💡 The random discovery tool is working correctly.")
    print("   AI assistants can now use this to explore the library.\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

