"""Core database layer for songs management and indexing."""

import json
from pathlib import Path
from typing import Any, Union, Optional
from collections import defaultdict
import httpx


class SongsDatabase:
    """Manages the songs database with efficient indexing for queries."""

    def __init__(self, json_source: Union[str, Path]):
        """Initialize the database from a JSON file or URL.
        
        Args:
            json_source: Either a local file path or a URL to fetch the JSON from
        """
        self.json_source = str(json_source)
        self.is_url = self.json_source.startswith('http://') or self.json_source.startswith('https://')
        self.data: dict[str, Any] = {}
        self.songs: list[dict[str, Any]] = []
        self.categories: list[dict[str, Any]] = []

        # Indexes for efficient lookups
        self.songs_by_id: dict[int, dict[str, Any]] = {}
        self.songs_by_artist: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.songs_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.songs_by_composer: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.songs_by_lyricist: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.songs_by_translator: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.categories_by_id: dict[str, dict[str, Any]] = {}
        
        # Collaboration cache: (lyricist_key, composer_key) -> collaboration data
        self.collaborations_cache: dict[tuple[str, str], dict[str, Any]] = {}

        self._load_data()
        self._build_indexes()

    def _load_data(self) -> None:
        """Load the JSON data from file or URL."""
        if self.is_url:
            # Fetch from URL
            with httpx.Client() as client:
                response = client.get(self.json_source, timeout=30.0)
                response.raise_for_status()
                self.data = response.json()
        else:
            # Load from local file
            with open(self.json_source, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

        self.songs = self.data.get('songs', [])
        self.categories = self.data.get('categories', [])

    def _build_indexes(self) -> None:
        """Build indexes for efficient querying."""
        # Index songs by ID
        for song in self.songs:
            song_id = song.get('id')
            if song_id:
                self.songs_by_id[song_id] = song

        # Index songs by artist (normalized lowercase for matching)
        for song in self.songs:
            artist = song.get('singer', '').strip()
            if artist:
                artist_key = artist.lower()
                self.songs_by_artist[artist_key].append(song)

        # Index songs by category
        for song in self.songs:
            category_ids = song.get('categoryIds', [])
            for cat_id in category_ids:
                self.songs_by_category[cat_id].append(song)

        # Index categories by ID
        for category in self.categories:
            cat_id = category.get('id')
            if cat_id:
                self.categories_by_id[cat_id] = category

        # Index songs by composer
        for song in self.songs:
            composers = song.get('composers', [])
            for composer in composers:
                if composer:
                    composer_key = composer.lower().strip()
                    self.songs_by_composer[composer_key].append(song)

        # Index songs by lyricist
        for song in self.songs:
            lyricists = song.get('lyricists', [])
            for lyricist in lyricists:
                if lyricist:
                    lyricist_key = lyricist.lower().strip()
                    self.songs_by_lyricist[lyricist_key].append(song)

        # Index songs by translator
        for song in self.songs:
            translators = song.get('translators', [])
            for translator in translators:
                if translator:
                    translator_key = translator.lower().strip()
                    self.songs_by_translator[translator_key].append(song)

        # Build collaborations cache (lyricist × composer pairs)
        for song in self.songs:
            song_id = song.get('id')
            if not song_id:
                continue
                
            lyricists = song.get('lyricists', [])
            composers = song.get('composers', [])
            
            # Skip songs without both lyricist and composer
            if not lyricists or not composers:
                continue
            
            # Create cartesian product of lyricists × composers
            for lyricist in lyricists:
                if not lyricist:
                    continue
                lyricist_key = lyricist.lower().strip()
                
                for composer in composers:
                    if not composer:
                        continue
                    composer_key = composer.lower().strip()
                    
                    # Use tuple as key (lyricist, composer)
                    collab_key = (lyricist_key, composer_key)
                    
                    if collab_key not in self.collaborations_cache:
                        self.collaborations_cache[collab_key] = {
                            'lyricist': lyricist,
                            'composer': composer,
                            'song_ids': [],
                            'song_count': 0
                        }
                    
                    # Add song ID if not already present
                    if song_id not in self.collaborations_cache[collab_key]['song_ids']:
                        self.collaborations_cache[collab_key]['song_ids'].append(song_id)
                        self.collaborations_cache[collab_key]['song_count'] += 1

    def get_song_by_id(self, song_id: int) -> Optional[dict[str, Any]]:
        """Get a song by its ID."""
        return self.songs_by_id.get(song_id)

    def get_songs_by_artist(self, artist_name: str) -> list[dict[str, Any]]:
        """Get all songs by an artist (case-insensitive)."""
        artist_key = artist_name.lower().strip()
        return self.songs_by_artist.get(artist_key, [])

    def get_songs_by_category(self, category_id: str) -> list[dict[str, Any]]:
        """Get all songs in a category."""
        return self.songs_by_category.get(category_id, [])

    def get_category_by_id(self, category_id: str) -> Optional[dict[str, Any]]:
        """Get category information by ID."""
        return self.categories_by_id.get(category_id)

    def get_all_songs(self, limit: Optional[int] = None, offset: int = 0) -> list[dict[str, Any]]:
        """Get all songs with optional pagination."""
        if limit is None:
            return self.songs[offset:]
        return self.songs[offset:offset + limit]

    def get_all_categories(self) -> list[dict[str, Any]]:
        """Get all categories."""
        return self.categories

    def get_all_artists(self) -> list[dict[str, Union[str, int]]]:
        """Get all unique artists with song counts."""
        artists = []
        for artist_key, songs in self.songs_by_artist.items():
            # Get the original artist name from the first song
            original_name = songs[0].get('singer', artist_key)
            artists.append({
                'name': original_name,
                'song_count': len(songs)
            })

        # Sort by name
        artists.sort(key=lambda x: x['name'])
        return artists

    def get_songs_by_composer(self, composer_name: str) -> list[dict[str, Any]]:
        """Get all songs by a composer (case-insensitive)."""
        composer_key = composer_name.lower().strip()
        return self.songs_by_composer.get(composer_key, [])

    def get_songs_by_lyricist(self, lyricist_name: str) -> list[dict[str, Any]]:
        """Get all songs by a lyricist (case-insensitive)."""
        lyricist_key = lyricist_name.lower().strip()
        return self.songs_by_lyricist.get(lyricist_key, [])

    def get_songs_by_translator(self, translator_name: str) -> list[dict[str, Any]]:
        """Get all songs by a translator (case-insensitive)."""
        translator_key = translator_name.lower().strip()
        return self.songs_by_translator.get(translator_key, [])

    def get_all_composers(self) -> list[dict[str, Union[str, int]]]:
        """Get all unique composers with song counts."""
        composers = []
        for composer_key, songs in self.songs_by_composer.items():
            # Get the original composer name by finding it in the first song's composers array
            original_name = composer_key
            for song in songs:
                composers_list = song.get('composers', [])
                for composer in composers_list:
                    if composer.lower().strip() == composer_key:
                        original_name = composer
                        break
                if original_name != composer_key:
                    break
            
            composers.append({
                'name': original_name,
                'song_count': len(songs)
            })

        # Sort by name
        composers.sort(key=lambda x: x['name'])
        return composers

    def get_all_lyricists(self) -> list[dict[str, Union[str, int]]]:
        """Get all unique lyricists with song counts."""
        lyricists = []
        for lyricist_key, songs in self.songs_by_lyricist.items():
            # Get the original lyricist name by finding it in the first song's lyricists array
            original_name = lyricist_key
            for song in songs:
                lyricists_list = song.get('lyricists', [])
                for lyricist in lyricists_list:
                    if lyricist.lower().strip() == lyricist_key:
                        original_name = lyricist
                        break
                if original_name != lyricist_key:
                    break
            
            lyricists.append({
                'name': original_name,
                'song_count': len(songs)
            })

        # Sort by name
        lyricists.sort(key=lambda x: x['name'])
        return lyricists

    def get_all_translators(self) -> list[dict[str, Union[str, int]]]:
        """Get all unique translators with song counts."""
        translators = []
        for translator_key, songs in self.songs_by_translator.items():
            # Get the original translator name by finding it in the first song's translators array
            original_name = translator_key
            for song in songs:
                translators_list = song.get('translators', [])
                for translator in translators_list:
                    if translator.lower().strip() == translator_key:
                        original_name = translator
                        break
                if original_name != translator_key:
                    break
            
            translators.append({
                'name': original_name,
                'song_count': len(songs)
            })

        # Sort by name
        translators.sort(key=lambda x: x['name'])
        return translators

    def get_all_collaborations(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """Get all lyricist-composer collaborations sorted by song count."""
        collaborations = []
        for (lyricist_key, composer_key), data in self.collaborations_cache.items():
            collaborations.append({
                'lyricist': data['lyricist'],
                'composer': data['composer'],
                'song_count': data['song_count'],
                'song_ids': data['song_ids']
            })
        
        # Sort by song count (descending), then by lyricist name, then by composer name
        collaborations.sort(key=lambda x: (-x['song_count'], x['lyricist'], x['composer']))
        
        if limit:
            return collaborations[:limit]
        return collaborations

    def get_collaboration_songs(self, lyricist: str, composer: str) -> Optional[dict[str, Any]]:
        """Get collaboration data for a specific lyricist-composer pair."""
        lyricist_key = lyricist.lower().strip()
        composer_key = composer.lower().strip()
        collab_key = (lyricist_key, composer_key)
        
        if collab_key in self.collaborations_cache:
            data = self.collaborations_cache[collab_key]
            # Return full song objects, not just IDs
            songs = [self.songs_by_id[sid] for sid in data['song_ids'] if sid in self.songs_by_id]
            return {
                'lyricist': data['lyricist'],
                'composer': data['composer'],
                'song_count': data['song_count'],
                'song_ids': data['song_ids'],
                'songs': songs
            }
        return None

    def get_collaborations_by_lyricist(self, lyricist: str) -> list[dict[str, Any]]:
        """Get all composers who collaborated with a specific lyricist."""
        lyricist_key = lyricist.lower().strip()
        collaborations = []
        
        for (lyr_key, comp_key), data in self.collaborations_cache.items():
            if lyr_key == lyricist_key:
                collaborations.append({
                    'lyricist': data['lyricist'],
                    'composer': data['composer'],
                    'song_count': data['song_count'],
                    'song_ids': data['song_ids']
                })
        
        # Sort by song count (descending)
        collaborations.sort(key=lambda x: -x['song_count'])
        return collaborations

    def get_collaborations_by_composer(self, composer: str) -> list[dict[str, Any]]:
        """Get all lyricists who collaborated with a specific composer."""
        composer_key = composer.lower().strip()
        collaborations = []
        
        for (lyr_key, comp_key), data in self.collaborations_cache.items():
            if comp_key == composer_key:
                collaborations.append({
                    'lyricist': data['lyricist'],
                    'composer': data['composer'],
                    'song_count': data['song_count'],
                    'song_ids': data['song_ids']
                })
        
        # Sort by song count (descending)
        collaborations.sort(key=lambda x: -x['song_count'])
        return collaborations

    def search_songs(
        self,
        query: Optional[str] = None,
        artist: Optional[str] = None,
        category_id: Optional[str] = None,
        composer: Optional[str] = None,
        lyricist: Optional[str] = None,
        translator: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Search songs with multiple criteria."""
        results = self.songs.copy()

        # Filter by artist if specified
        if artist:
            artist_songs = self.get_songs_by_artist(artist)
            artist_ids = {s['id'] for s in artist_songs}
            results = [s for s in results if s['id'] in artist_ids]

        # Filter by category if specified
        if category_id:
            category_songs = self.get_songs_by_category(category_id)
            category_ids = {s['id'] for s in category_songs}
            results = [s for s in results if s['id'] in category_ids]

        # Filter by composer if specified
        if composer:
            composer_songs = self.get_songs_by_composer(composer)
            composer_ids = {s['id'] for s in composer_songs}
            results = [s for s in results if s['id'] in composer_ids]

        # Filter by lyricist if specified
        if lyricist:
            lyricist_songs = self.get_songs_by_lyricist(lyricist)
            lyricist_ids = {s['id'] for s in lyricist_songs}
            results = [s for s in results if s['id'] in lyricist_ids]

        # Filter by translator if specified
        if translator:
            translator_songs = self.get_songs_by_translator(translator)
            translator_ids = {s['id'] for s in translator_songs}
            results = [s for s in results if s['id'] in translator_ids]

        # Filter by name query (case-insensitive partial match)
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.get('name', '').lower()
                or query_lower in s.get('singer', '').lower()
            ]

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        return {
            'total_songs': len(self.songs),
            'total_artists': len(self.songs_by_artist),
            'total_composers': len(self.songs_by_composer),
            'total_lyricists': len(self.songs_by_lyricist),
            'total_translators': len(self.songs_by_translator),
            'total_collaborations': len(self.collaborations_cache),
            'total_categories': len(self.categories),
            'version': self.data.get('version', 'unknown'),
            'title': self.data.get('title', 'unknown'),
            'categories': [
                {
                    'id': cat['id'],
                    'name': cat['name'],
                    'song_count': len(self.songs_by_category.get(cat['id'], []))
                }
                for cat in self.categories
            ]
        }

    def _calculate_fame_rank(self, song_count: int, all_counts: list[int]) -> int:
        """Calculate fame rank (0-100) based on percentile.
        
        Higher rank = more famous. Rank of 100 = most prolific, 0 = least.
        """
        if not all_counts or song_count == 0:
            return 0
        
        # Count how many have fewer songs
        fewer_count = sum(1 for count in all_counts if count < song_count)
        
        # Calculate percentile rank (0-100)
        rank = int((fewer_count / len(all_counts)) * 100)
        return rank

    def get_random_discovery(
        self,
        language: str = "both",
        count: int = 10
    ) -> dict[str, Any]:
        """Get random songs, artists, composers, and lyricists for discovery with fame scores.
        
        Args:
            language: Filter by language - "hebrew", "english", or "both"
            count: Number of items to return for each category (default: 10)
            
        Returns:
            Dictionary with random songs, artists, composers, and lyricists, all with fame scores.
            Results are sorted by fame score (most famous first) within each category.
        """
        import random
        
        # Determine which songs to sample from based on language filter
        if language.lower() == "hebrew":
            # Find Hebrew category ID by searching categories
            hebrew_cat_id = None
            for cat in self.categories:
                if cat.get('name', '').lower() in ['עברית', 'hebrew']:
                    hebrew_cat_id = cat.get('id')
                    break
            
            if hebrew_cat_id:
                filtered_songs = self.songs_by_category.get(hebrew_cat_id, [])
            else:
                filtered_songs = self.songs
                
        elif language.lower() == "english":
            # Find English category ID by searching categories
            english_cat_id = None
            for cat in self.categories:
                if cat.get('name', '').lower() in ['english', 'אנגלית']:
                    english_cat_id = cat.get('id')
                    break
            
            if english_cat_id:
                filtered_songs = self.songs_by_category.get(english_cat_id, [])
            else:
                filtered_songs = self.songs
        else:
            # Both - use all songs
            filtered_songs = self.songs
        
        # Sample random songs
        sample_size = min(count, len(filtered_songs))
        random_songs = random.sample(filtered_songs, sample_size) if sample_size > 0 else []
        
        # Extract unique artists, composers, lyricists from filtered songs
        artists_set = set()
        composers_set = set()
        lyricists_set = set()
        
        for song in filtered_songs:
            artist = song.get('singer', '').strip()
            if artist:
                artists_set.add(artist)
            
            for composer in song.get('composers', []):
                if composer:
                    composers_set.add(composer)
            
            for lyricist in song.get('lyricists', []):
                if lyricist:
                    lyricists_set.add(lyricist)
        
        # Sample from each set
        artists_sample = random.sample(list(artists_set), min(count, len(artists_set))) if artists_set else []
        composers_sample = random.sample(list(composers_set), min(count, len(composers_set))) if composers_set else []
        lyricists_sample = random.sample(list(lyricists_set), min(count, len(lyricists_set))) if lyricists_set else []
        
        # Get all song counts for rank calculation
        all_artist_counts = [len(songs) for songs in self.songs_by_artist.values()]
        all_composer_counts = [len(songs) for songs in self.songs_by_composer.values()]
        all_lyricist_counts = [len(songs) for songs in self.songs_by_lyricist.values()]
        
        # Build cache for contributor fame scores
        artist_fame_cache = {}
        composer_fame_cache = {}
        lyricist_fame_cache = {}
        
        # Calculate fame scores for artists
        artists_with_fame = []
        for artist in artists_sample:
            artist_key = artist.lower()
            song_count = len(self.songs_by_artist.get(artist_key, []))
            fame_rank = self._calculate_fame_rank(song_count, all_artist_counts)
            artist_fame_cache[artist_key] = fame_rank
            artists_with_fame.append({
                'name': artist,
                'song_count': song_count,
                'fame_score': fame_rank
            })
        
        # Calculate fame scores for composers
        composers_with_fame = []
        for composer in composers_sample:
            composer_key = composer.lower().strip()
            song_count = len(self.songs_by_composer.get(composer_key, []))
            fame_rank = self._calculate_fame_rank(song_count, all_composer_counts)
            composer_fame_cache[composer_key] = fame_rank
            composers_with_fame.append({
                'name': composer,
                'song_count': song_count,
                'fame_score': fame_rank
            })
        
        # Calculate fame scores for lyricists
        lyricists_with_fame = []
        for lyricist in lyricists_sample:
            lyricist_key = lyricist.lower().strip()
            song_count = len(self.songs_by_lyricist.get(lyricist_key, []))
            fame_rank = self._calculate_fame_rank(song_count, all_lyricist_counts)
            lyricist_fame_cache[lyricist_key] = fame_rank
            lyricists_with_fame.append({
                'name': lyricist,
                'song_count': song_count,
                'fame_score': fame_rank
            })
        
        # Calculate composite fame scores for songs
        # Weights: artist (heavy), composer (modest), lyricist (modest)
        enriched_songs = []
        for song in random_songs:
            # Get artist fame (heavy weight: 0.6)
            artist_key = song.get('singer', '').lower()
            if artist_key not in artist_fame_cache:
                song_count = len(self.songs_by_artist.get(artist_key, []))
                artist_fame_cache[artist_key] = self._calculate_fame_rank(song_count, all_artist_counts)
            artist_fame = artist_fame_cache[artist_key]
            
            # Get average composer fame (modest weight: 0.25)
            composers = song.get('composers', [])
            composer_fames = []
            for composer in composers:
                composer_key = composer.lower().strip()
                if composer_key not in composer_fame_cache:
                    song_count = len(self.songs_by_composer.get(composer_key, []))
                    composer_fame_cache[composer_key] = self._calculate_fame_rank(song_count, all_composer_counts)
                composer_fames.append(composer_fame_cache[composer_key])
            avg_composer_fame = sum(composer_fames) / len(composer_fames) if composer_fames else 0
            
            # Get average lyricist fame (modest weight: 0.15)
            lyricists = song.get('lyricists', [])
            lyricist_fames = []
            for lyricist in lyricists:
                lyricist_key = lyricist.lower().strip()
                if lyricist_key not in lyricist_fame_cache:
                    song_count = len(self.songs_by_lyricist.get(lyricist_key, []))
                    lyricist_fame_cache[lyricist_key] = self._calculate_fame_rank(song_count, all_lyricist_counts)
                lyricist_fames.append(lyricist_fame_cache[lyricist_key])
            avg_lyricist_fame = sum(lyricist_fames) / len(lyricist_fames) if lyricist_fames else 0
            
            # Calculate composite fame score
            composite_fame = int(
                artist_fame * 0.6 +
                avg_composer_fame * 0.25 +
                avg_lyricist_fame * 0.15
            )
            
            enriched_song = song.copy()
            enriched_song['fame_score'] = composite_fame
            enriched_songs.append(enriched_song)
        
        # Sort all results by fame score (descending - most famous first)
        artists_with_fame.sort(key=lambda x: x['fame_score'], reverse=True)
        composers_with_fame.sort(key=lambda x: x['fame_score'], reverse=True)
        lyricists_with_fame.sort(key=lambda x: x['fame_score'], reverse=True)
        enriched_songs.sort(key=lambda x: x['fame_score'], reverse=True)
        
        return {
            'language_filter': language,
            'songs': enriched_songs,
            'artists': artists_with_fame,
            'composers': composers_with_fame,
            'lyricists': lyricists_with_fame,
            'counts': {
                'songs': len(enriched_songs),
                'artists': len(artists_with_fame),
                'composers': len(composers_with_fame),
                'lyricists': len(lyricists_with_fame)
            }
        }
