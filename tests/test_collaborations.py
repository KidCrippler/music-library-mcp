#!/usr/bin/env python3
"""Test script to demonstrate the new collaboration cache features."""

from music_library_mcp.database import SongsDatabase

def main():
    # Initialize database
    print("Initializing database with songs_enriched.json...")
    db = SongsDatabase('songs/songs_enriched.json')
    
    print("\n" + "="*80)
    print("COLLABORATION CACHE STATISTICS")
    print("="*80)
    stats = db.get_stats()
    print(f"Total songs:          {stats['total_songs']:,}")
    print(f"Total composers:      {stats['total_composers']:,}")
    print(f"Total lyricists:      {stats['total_lyricists']:,}")
    print(f"Total collaborations: {stats['total_collaborations']:,}")
    print(f"\nNote: {stats['total_collaborations']:,} unique lyricist-composer pairs found")
    
    print("\n" + "="*80)
    print("TOP 20 COLLABORATIONS (by song count)")
    print("="*80)
    collabs = db.get_all_collaborations(limit=20)
    for i, collab in enumerate(collabs, 1):
        lyr = collab['lyricist']
        comp = collab['composer']
        count = collab['song_count']
        
        if lyr.lower().strip() == comp.lower().strip():
            # Self-collaboration
            print(f"{i:2}. {lyr:40} (SELF) → {count:3} songs")
        else:
            # True collaboration
            print(f"{i:2}. {lyr:35} × {comp:35} → {count:2} songs")
    
    print("\n" + "="*80)
    print("SELF-COLLABORATIONS (Artists who write both lyrics and music)")
    print("="*80)
    all_collabs = db.get_all_collaborations()
    self_collabs = [c for c in all_collabs if c['lyricist'].lower().strip() == c['composer'].lower().strip()]
    print(f"Found {len(self_collabs)} self-collaborations")
    print("\nTop 10 self-collaborators:")
    for i, collab in enumerate(self_collabs[:10], 1):
        print(f"{i:2}. {collab['lyricist']:40} {collab['song_count']:3} songs")
    
    print("\n" + "="*80)
    print("SPECIFIC COLLABORATION ANALYSIS: שלמה ארצי (self)")
    print("="*80)
    collab = db.get_collaboration_songs('שלמה ארצי', 'שלמה ארצי')
    if collab:
        print(f"Artist: {collab['lyricist']}")
        print(f"Total songs: {collab['song_count']}")
        print(f"\nSample songs where שלמה ארצי wrote both lyrics and music:")
        for i, song in enumerate(collab['songs'][:5], 1):
            print(f"  {i}. {song['name']}")
            print(f"     Performed by: {song['singer']}")
    
    print("\n" + "="*80)
    print("SPECIFIC COLLABORATION ANALYSIS: אהוד מנור × מתי כספי")
    print("="*80)
    collab = db.get_collaboration_songs('אהוד מנור', 'מתי כספי')
    if collab:
        print(f"Lyricist: {collab['lyricist']}")
        print(f"Composer: {collab['composer']}")
        print(f"Total collaborations: {collab['song_count']}")
        print(f"\nSongs from this collaboration:")
        for i, song in enumerate(collab['songs'][:5], 1):
            print(f"  {i}. {song['name']} - {song['singer']}")
        if len(collab['songs']) > 5:
            print(f"  ... and {len(collab['songs']) - 5} more")
    
    print("\n" + "="*80)
    print("COLLABORATIONS BY LYRICIST: אהוד מנור")
    print("="*80)
    collabs = db.get_collaborations_by_lyricist('אהוד מנור')
    print(f"אהוד מנור worked with {len(collabs)} different composers")
    print("\nTop 10 composer collaborations:")
    for i, collab in enumerate(collabs[:10], 1):
        is_self = collab['lyricist'].lower().strip() == collab['composer'].lower().strip()
        marker = "(self)" if is_self else ""
        print(f"{i:2}. {collab['composer']:40} {marker:7} {collab['song_count']:2} songs")
    
    print("\n" + "="*80)
    print("COLLABORATIONS BY COMPOSER: מתי כספי")
    print("="*80)
    collabs = db.get_collaborations_by_composer('מתי כספי')
    print(f"מתי כספי worked with {len(collabs)} different lyricists")
    print("\nTop 10 lyricist collaborations:")
    for i, collab in enumerate(collabs[:10], 1):
        is_self = collab['lyricist'].lower().strip() == collab['composer'].lower().strip()
        marker = "(self)" if is_self else ""
        print(f"{i:2}. {collab['lyricist']:40} {marker:7} {collab['song_count']:2} songs")
    
    print("\n" + "="*80)
    print("CARTESIAN PRODUCT EXAMPLE")
    print("="*80)
    print("Finding a song with multiple lyricists and composers...")
    for song in db.songs:
        lyricists = song.get('lyricists', [])
        composers = song.get('composers', [])
        if len(lyricists) >= 2 and len(composers) >= 2:
            print(f"\nSong: {song['name']}")
            print(f"Lyricists: {', '.join(lyricists)}")
            print(f"Composers: {', '.join(composers)}")
            print(f"\nThis creates {len(lyricists)} × {len(composers)} = {len(lyricists) * len(composers)} collaboration entries:")
            for lyr in lyricists:
                for comp in composers:
                    print(f"  - {lyr} × {comp}")
            break
    
    print("\n" + "="*80)
    print("INTERESTING INSIGHTS")
    print("="*80)
    
    # Find collaborations with exactly 1 song (rare collaborations)
    rare_collabs = [c for c in all_collabs if c['song_count'] == 1]
    prolific_collabs = [c for c in all_collabs if c['song_count'] >= 10]
    true_collabs = [c for c in all_collabs if c['lyricist'].lower().strip() != c['composer'].lower().strip()]
    
    print(f"Rare collaborations (1 song): {len(rare_collabs):,}")
    print(f"Prolific collaborations (10+ songs): {len(prolific_collabs):,}")
    print(f"True collaborations (different people): {len(true_collabs):,}")
    print(f"Self-collaborations (same person): {len(self_collabs):,}")
    print(f"\nAverage songs per collaboration: {sum(c['song_count'] for c in all_collabs) / len(all_collabs):.2f}")
    
    print("\n" + "="*80)
    print("✅ ALL COLLABORATION TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)

if __name__ == "__main__":
    main()

