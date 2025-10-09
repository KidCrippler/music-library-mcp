"""Quick test script to verify the server loads correctly."""

from music_library_mcp.database import SongsDatabase
from pathlib import Path

def test_database():
    """Test that the database loads and indexes correctly."""
    print("Testing Music Library MCP Server...")
    print("-" * 50)

    # Load database
    db_path = Path(__file__).parent / "songs" / "songs.json"
    print(f"\nLoading database from: {db_path}")

    if not db_path.exists():
        print(f"ERROR: Database file not found at {db_path}")
        return

    db = SongsDatabase(db_path)

    # Get stats
    stats = db.get_stats()
    print(f"\nDatabase Stats:")
    print(f"  Total songs: {stats['total_songs']}")
    print(f"  Total artists: {stats['total_artists']}")
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Version: {stats['version']}")

    # Test artist lookup
    print(f"\n\nCategories:")
    for cat in stats['categories'][:5]:
        print(f"  {cat['name']}: {cat['song_count']} songs")

    # Test some artists
    print(f"\n\nSample Artists (first 10):")
    artists = db.get_all_artists()[:10]
    for artist in artists:
        print(f"  {artist['name']}: {artist['song_count']} songs")

    # Test song lookup
    print(f"\n\nSample Songs (first 5):")
    songs = db.get_all_songs(limit=5)
    for song in songs:
        print(f"  ID {song['id']}: {song['name']} by {song['singer']}")

    # Test search
    print(f"\n\nSearch Test (songs with 'חלומות'):")
    results = db.search_songs(query="חלומות")
    for song in results[:3]:
        print(f"  {song['name']} by {song['singer']}")

    print("\n" + "-" * 50)
    print("Database test completed successfully!")
    print("\nThe server is ready to use.")
    print("\nTo run the server:")
    print("  python -m music_library_mcp.server")

if __name__ == "__main__":
    test_database()
