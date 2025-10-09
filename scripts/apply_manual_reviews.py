#!/usr/bin/env python3
"""
Apply manual reviews from manual_reviews.json to songs_enriched.json.
Creates a new file songs_enriched_final.json without modifying the original.
"""

import json
import sys
from pathlib import Path


def apply_manual_reviews(
    songs_path: str,
    reviews_path: str,
    output_path: str
):
    """
    Apply manual reviews to songs and save to a new file.
    
    Args:
        songs_path: Path to songs_enriched.json
        reviews_path: Path to manual_reviews.json
        output_path: Path to output file
    """
    
    # Load songs
    print(f"Loading songs from: {songs_path}")
    with open(songs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Load manual reviews
    print(f"Loading manual reviews from: {reviews_path}")
    if not Path(reviews_path).exists():
        print("Warning: manual_reviews.json not found. No reviews to apply.")
        return
    
    with open(reviews_path, 'r', encoding='utf-8') as f:
        manual_reviews = json.load(f)
    
    print(f"Found {len(manual_reviews)} manual reviews to apply")
    
    # Apply reviews to songs
    applied_count = 0
    songs = data.get('songs', [])
    
    for song in songs:
        song_id = str(song['id'])
        
        if song_id in manual_reviews:
            review = manual_reviews[song_id]
            
            # Build a temporary dict with all data
            temp_song = {}
            for key in song.keys():
                if key not in ['needsManualReview', 'unparsedString', 'composers', 'lyricists', 'translators']:
                    temp_song[key] = song[key]
            
            # Add review data
            if 'composers' in review and review['composers']:
                temp_song['composers'] = review['composers']
            if 'lyricists' in review and review['lyricists']:
                temp_song['lyricists'] = review['lyricists']
            if 'translators' in review and review['translators']:
                temp_song['translators'] = review['translators']
            
            # Rebuild song dictionary with correct field order
            # Order: id, name, singer, composers, lyricists, translators, playback, isPrivate, categoryIds, lyrics, dateCreated, dateModified
            final_song = {}
            field_order = ['id', 'name', 'singer', 'composers', 'lyricists', 'translators', 
                          'playback', 'isPrivate', 'categoryIds', 'lyrics', 'dateCreated', 'dateModified']
            
            for field in field_order:
                if field in temp_song:
                    final_song[field] = temp_song[field]
            
            # Add any remaining fields not in field_order
            for key, value in temp_song.items():
                if key not in final_song:
                    final_song[key] = value
            
            # Update the song dictionary
            song.clear()
            song.update(final_song)
            
            applied_count += 1
    
    # Save to output file
    print(f"\nApplied {applied_count} manual reviews")
    print(f"Saving to: {output_path}")
    
    # Use same formatting as enriched file (tabs, one-liner arrays)
    import re
    
    json_str = json.dumps(data, ensure_ascii=False, indent="\t")
    
    # Format arrays as one-liners
    def compress_array(match):
        field_name = match.group(1)
        array_content = match.group(2)
        array_items = re.findall(r'"([^"]*)"', array_content)
        one_liner = ', '.join([f'"{item}"' for item in array_items])
        return f'"{field_name}": [{one_liner}]'
    
    pattern = r'"(composers|lyricists|translators|categoryIds)":\s*\[\s*((?:"[^"]*"\s*,?\s*)*)\s*\]'
    json_str = re.sub(pattern, compress_array, json_str, flags=re.MULTILINE | re.DOTALL)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    print(f"\n✓ Successfully created {output_path}")
    
    # Summary
    remaining_reviews = sum(1 for song in songs if song.get('needsManualReview'))
    print(f"\nSummary:")
    print(f"  Total songs: {len(songs)}")
    print(f"  Reviews applied: {applied_count}")
    print(f"  Still need manual review: {remaining_reviews}")


def main():
    # Default paths (script is in scripts/, data is in parent directory)
    base_path = Path(__file__).parent.parent
    songs_path = base_path / "songs" / "songs_enriched.json"
    reviews_path = base_path / "songs" / "manual_reviews.json"
    output_path = base_path / "songs" / "songs_enriched_final.json"
    
    # Check if custom paths provided
    if len(sys.argv) > 1:
        songs_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        reviews_path = Path(sys.argv[2])
    if len(sys.argv) > 3:
        output_path = Path(sys.argv[3])
    
    # Verify input files exist
    if not songs_path.exists():
        print(f"Error: Songs file not found: {songs_path}")
        sys.exit(1)
    
    if not reviews_path.exists():
        print(f"Warning: Reviews file not found: {reviews_path}")
        print("Creating output file without any manual reviews applied.")
    
    apply_manual_reviews(str(songs_path), str(reviews_path), str(output_path))


if __name__ == '__main__':
    main()

