#!/usr/bin/env python3
"""
Flask web app for manually reviewing and editing song credits.
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from pathlib import Path

app = Flask(__name__)

# Paths (script is in scripts/, data is in parent directory)
SONGS_PATH = Path(__file__).parent.parent / "songs" / "songs_enriched.json"
MANUAL_REVIEWS_PATH = Path(__file__).parent.parent / "songs" / "manual_reviews.json"

# Cache for songs data
_songs_cache = None
_manual_reviews_cache = None


def load_songs():
    """Load songs from songs_enriched.json"""
    global _songs_cache
    if _songs_cache is None:
        with open(SONGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Filter only songs that need manual review
            _songs_cache = [
                song for song in data.get('songs', [])
                if song.get('needsManualReview')
            ]
    return _songs_cache


def load_manual_reviews():
    """Load manual reviews from file"""
    global _manual_reviews_cache
    if _manual_reviews_cache is None:
        if MANUAL_REVIEWS_PATH.exists():
            with open(MANUAL_REVIEWS_PATH, 'r', encoding='utf-8') as f:
                _manual_reviews_cache = json.load(f)
        else:
            _manual_reviews_cache = {}
    return _manual_reviews_cache


def save_manual_reviews(reviews):
    """Save manual reviews to file"""
    global _manual_reviews_cache
    _manual_reviews_cache = reviews
    with open(MANUAL_REVIEWS_PATH, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    """Serve the main review interface"""
    return render_template('review.html')


@app.route('/api/songs')
def get_songs():
    """Get all songs needing manual review"""
    songs = load_songs()
    manual_reviews = load_manual_reviews()
    
    # Merge manual reviews into songs
    result = []
    for song in songs:
        song_id = str(song['id'])
        song_data = {
            'id': song['id'],
            'name': song.get('name', ''),
            'singer': song.get('singer', ''),
            'unparsedString': song.get('unparsedString', ''),
            'composers': song.get('composers', []),
            'lyricists': song.get('lyricists', []),
            'translators': song.get('translators', []),
            'isReviewed': song_id in manual_reviews
        }
        
        # Override with manual review data if exists
        if song_id in manual_reviews:
            review = manual_reviews[song_id]
            song_data['composers'] = review.get('composers', [])
            song_data['lyricists'] = review.get('lyricists', [])
            song_data['translators'] = review.get('translators', [])
        
        result.append(song_data)
    
    return jsonify(result)


@app.route('/api/songs/<int:song_id>')
def get_song(song_id):
    """Get specific song details"""
    songs = load_songs()
    manual_reviews = load_manual_reviews()
    
    for song in songs:
        if song['id'] == song_id:
            song_data = {
                'id': song['id'],
                'name': song.get('name', ''),
                'singer': song.get('singer', ''),
                'unparsedString': song.get('unparsedString', ''),
                'composers': song.get('composers', []),
                'lyricists': song.get('lyricists', []),
                'translators': song.get('translators', []),
                'isReviewed': str(song_id) in manual_reviews
            }
            
            # Override with manual review data if exists
            if str(song_id) in manual_reviews:
                review = manual_reviews[str(song_id)]
                song_data['composers'] = review.get('composers', [])
                song_data['lyricists'] = review.get('lyricists', [])
                song_data['translators'] = review.get('translators', [])
            
            return jsonify(song_data)
    
    return jsonify({'error': 'Song not found'}), 404


@app.route('/api/songs/<int:song_id>', methods=['POST'])
def save_song(song_id):
    """Save manual edits for a song"""
    data = request.json
    manual_reviews = load_manual_reviews()
    
    # Parse comma-separated strings into arrays
    def parse_names(value):
        if isinstance(value, list):
            return [name.strip() for name in value if name.strip()]
        if isinstance(value, str):
            return [name.strip() for name in value.split(',') if name.strip()]
        return []
    
    manual_reviews[str(song_id)] = {
        'composers': parse_names(data.get('composers', [])),
        'lyricists': parse_names(data.get('lyricists', [])),
        'translators': parse_names(data.get('translators', []))
    }
    
    save_manual_reviews(manual_reviews)
    
    return jsonify({'success': True, 'message': 'Song saved successfully'})


@app.route('/api/stats')
def get_stats():
    """Get progress statistics"""
    songs = load_songs()
    manual_reviews = load_manual_reviews()
    
    total = len(songs)
    reviewed = len(manual_reviews)
    
    return jsonify({
        'total': total,
        'reviewed': reviewed,
        'remaining': total - reviewed,
        'percentage': round((reviewed / total * 100) if total > 0 else 0, 1)
    })


if __name__ == '__main__':
    print(f"Loading songs from: {SONGS_PATH}")
    print(f"Manual reviews will be saved to: {MANUAL_REVIEWS_PATH}")
    
    # Load songs to verify path
    songs = load_songs()
    print(f"Found {len(songs)} songs needing manual review")
    
    print("\nStarting Flask app on http://localhost:5000")
    app.run(debug=True, port=5000)

