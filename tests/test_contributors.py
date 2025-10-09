#!/usr/bin/env python3
"""Test script to demonstrate the new contributors functionality."""

from music_library_mcp.database import SongsDatabase

def main():
    # Initialize database
    print("Initializing database with songs_enriched.json...")
    db = SongsDatabase('songs/songs_enriched.json')
    
    print("\n" + "="*70)
    print("DATABASE STATISTICS")
    print("="*70)
    stats = db.get_stats()
    print(f"Total songs:       {stats['total_songs']:,}")
    print(f"Total artists:     {stats['total_artists']:,}")
    print(f"Total composers:   {stats['total_composers']:,}")
    print(f"Total lyricists:   {stats['total_lyricists']:,}")
    print(f"Total translators: {stats['total_translators']:,}")
    print(f"Total categories:  {stats['total_categories']:,}")
    
    print("\n" + "="*70)
    print("TOP 10 COMPOSERS BY SONG COUNT")
    print("="*70)
    composers = sorted(db.get_all_composers(), key=lambda x: x['song_count'], reverse=True)[:10]
    for i, composer in enumerate(composers, 1):
        print(f"{i:2}. {composer['name']:40} {composer['song_count']:3} songs")
    
    print("\n" + "="*70)
    print("TOP 10 LYRICISTS BY SONG COUNT")
    print("="*70)
    lyricists = sorted(db.get_all_lyricists(), key=lambda x: x['song_count'], reverse=True)[:10]
    for i, lyricist in enumerate(lyricists, 1):
        print(f"{i:2}. {lyricist['name']:40} {lyricist['song_count']:3} songs")
    
    print("\n" + "="*70)
    print("ALL TRANSLATORS")
    print("="*70)
    translators = sorted(db.get_all_translators(), key=lambda x: x['song_count'], reverse=True)
    for i, translator in enumerate(translators, 1):
        print(f"{i:2}. {translator['name']:40} {translator['song_count']:3} songs")
    
    print("\n" + "="*70)
    print("EXAMPLE QUERIES")
    print("="*70)
    
    # Example 1: Songs by a specific composer
    composer_name = "נעמי שמר"
    songs = db.get_songs_by_composer(composer_name)
    print(f"\nSongs composed by {composer_name}: {len(songs)}")
    for song in songs[:3]:
        print(f"  • {song['name']} - {song['singer']}")
    if len(songs) > 3:
        print(f"  ... and {len(songs) - 3} more")
    
    # Example 2: Songs by a specific lyricist
    lyricist_name = "יהונתן גפן"
    songs = db.get_songs_by_lyricist(lyricist_name)
    print(f"\nSongs with lyrics by {lyricist_name}: {len(songs)}")
    for song in songs[:3]:
        print(f"  • {song['name']} - {song['singer']}")
    if len(songs) > 3:
        print(f"  ... and {len(songs) - 3} more")
    
    # Example 3: Multi-filter search
    print(f"\nHebrew songs (category 1) with lyrics by אהוד מנור:")
    results = db.search_songs(category_id='1', lyricist='אהוד מנור')
    print(f"  Found {len(results)} songs")
    for song in results[:3]:
        composers = song.get('composers', [])
        composers_str = ', '.join(composers) if composers else 'Unknown'
        print(f"  • {song['name']} - {song['singer']}")
        print(f"    Composer(s): {composers_str}")
    if len(results) > 3:
        print(f"  ... and {len(results) - 3} more")
    
    # Example 4: Songs by artist and composer (self-composed)
    artist_name = "מתי כספי"
    results = db.search_songs(artist=artist_name, composer=artist_name)
    print(f"\nSongs by {artist_name} that they also composed: {len(results)}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)

if __name__ == "__main__":
    main()

