# Collaboration Cache Feature

## Overview

The collaboration cache is a high-performance indexing system that tracks all lyricist-composer pairs in the music library, enabling fast queries and deep analysis of creative partnerships.

## Key Features

- **Cartesian Product Indexing**: For songs with multiple lyricists and composers, automatically creates all possible collaboration pairs
- **Self-Collaboration Support**: Special handling for artists who write both lyrics and music (e.g., שלמה ארצי)
- **Fast Lookups**: Pre-computed cache eliminates need for expensive searches at query time
- **Comprehensive Stats**: Track collaboration patterns, frequency, and trends

## Database Statistics

From the enriched songs database:
- **Total collaborations**: 1,725 unique lyricist-composer pairs
- **Self-collaborations**: 488 artists who write both lyrics and music
- **True collaborations**: 1,237 pairs of different people
- **Average songs per collaboration**: 1.42

### Top Self-Collaborators
1. **שלמה ארצי** - 35 songs (both lyrics and music)
2. **דני סנדרסון** - 31 songs
3. **נעמי שמר** - 21 songs
4. **שלום חנוך** - 21 songs

### Top True Collaborations
1. **אהוד מנור × מתי כספי** - 16 songs
2. **Lennon × McCartney** - 12 songs (each direction)
3. **זאב נחמה × תמיר קליסקי** - 11 songs

## Database Layer (`music_library_mcp/database.py`)

### New Data Structure

```python
collaborations_cache: dict[tuple[str, str], dict[str, Any]]
```

**Key**: `(lyricist_normalized, composer_normalized)` - tuple of lowercase, stripped names  
**Value**:
```python
{
    'lyricist': str,        # Original name with proper casing
    'composer': str,        # Original name with proper casing
    'song_ids': list[int],  # List of song IDs for this collaboration
    'song_count': int       # Number of songs (same as len(song_ids))
}
```

### Cartesian Product Example

For a song with:
- Lyricists: `["אלי לו-לאי", "ברוך בן יצחק", "דני רכט"]`
- Composers: `["אלי לו-לאי", "ברוך בן יצחק"]`

Creates **6 collaboration entries** (3 × 2):
1. `אלי לו-לאי × אלי לו-לאי` (self)
2. `אלי לו-לאי × ברוך בן יצחק`
3. `ברוך בן יצחק × אלי לו-לאי`
4. `ברוך בן יצחק × ברוך בן יצחק` (self)
5. `דני רכט × אלי לו-לאי`
6. `דני רכט × ברוך בן יצחק`

### New Query Methods

#### `get_all_collaborations(limit=None)`
Returns all collaborations sorted by song count (descending).

```python
collabs = db.get_all_collaborations(limit=10)
# [
#   {'lyricist': 'שלמה ארצי', 'composer': 'שלמה ארצי', 'song_count': 35, 'song_ids': [...]},
#   {'lyricist': 'דני סנדרסון', 'composer': 'דני סנדרסון', 'song_count': 31, 'song_ids': [...]},
#   ...
# ]
```

#### `get_collaboration_songs(lyricist, composer)`
Returns detailed information about a specific collaboration, including full song objects.

```python
collab = db.get_collaboration_songs('אהוד מנור', 'מתי כספי')
# {
#   'lyricist': 'אהוד מנור',
#   'composer': 'מתי כספי',
#   'song_count': 16,
#   'song_ids': [1000002, 1000055, ...],
#   'songs': [<full song objects>]
# }
```

#### `get_collaborations_by_lyricist(lyricist)`
Returns all composers who worked with a specific lyricist.

```python
collabs = db.get_collaborations_by_lyricist('אהוד מנור')
# [
#   {'lyricist': 'אהוד מנור', 'composer': 'מתי כספי', 'song_count': 16, ...},
#   {'lyricist': 'אהוד מנור', 'composer': 'נורית הירש', 'song_count': 6, ...},
#   ...
# ]
```

#### `get_collaborations_by_composer(composer)`
Returns all lyricists who worked with a specific composer.

```python
collabs = db.get_collaborations_by_composer('מתי כספי')
# [
#   {'lyricist': 'אהוד מנור', 'composer': 'מתי כספי', 'song_count': 16, ...},
#   {'lyricist': 'יורם טהרלב', 'composer': 'מתי כספי', 'song_count': 3, ...},
#   ...
# ]
```

### Updated `get_stats()`

Now includes `total_collaborations` count:

```python
stats = db.get_stats()
# {
#   'total_songs': 1569,
#   'total_collaborations': 1725,
#   ...
# }
```

## MCP Server (`music_library_mcp/server.py`)

### New Resources

#### Static Resources
- `songs://collaborations` - Browse all collaborations (top 100, sorted by song count)

#### Dynamic Resources
- `songs://collaboration/{lyricist}/{composer}` - Detailed info for a specific pair
- Top 30 collaborations automatically exposed as browsable resources

**Example URIs**:
```
songs://collaborations
songs://collaboration/שלמה ארצי/שלמה ארצי
songs://collaboration/אהוד מנור/מתי כספי
```

### New Tool: `get_collaborations`

Query and filter collaborations with flexible parameters.

**Parameters**:
- `lyricist` (optional) - Filter by specific lyricist
- `composer` (optional) - Filter by specific composer
- `min_songs` (optional, default: 1) - Minimum collaboration count
- `limit` (optional, default: 50) - Maximum results to return

**Examples**:

```json
// Get top 10 collaborations
{
  "tool": "get_collaborations",
  "arguments": {
    "limit": 10
  }
}

// Get all collaborations for a lyricist
{
  "tool": "get_collaborations",
  "arguments": {
    "lyricist": "אהוד מנור"
  }
}

// Get prolific collaborations (10+ songs)
{
  "tool": "get_collaborations",
  "arguments": {
    "min_songs": 10,
    "limit": 20
  }
}

// Get specific collaboration
{
  "tool": "get_collaborations",
  "arguments": {
    "lyricist": "אהוד מנור",
    "composer": "מתי כספי"
  }
}
```

### New Prompt: `analyze_collaboration`

A creative, insightful prompt for analyzing lyricist-composer partnerships.

**Features**:
- **Self-Collaboration Detection**: Automatically detects and provides specialized analysis for artists who write both lyrics and music
- **Partnership Analysis**: Deep dive into true collaborations between two different creators
- **Full Song Data**: Includes complete song information for context

**Usage**:

```json
// Analyze self-collaboration
{
  "prompt": "analyze_collaboration",
  "arguments": {
    "lyricist": "שלמה ארצי",
    "composer": "שלמה ארצי"
  }
}

// Analyze true collaboration
{
  "prompt": "analyze_collaboration",
  "arguments": {
    "lyricist": "אהוד מנור",
    "composer": "מתי כספי"
  }
}
```

**Self-Collaboration Prompt** (when lyricist == composer):
- Explores complete artistic control
- Analyzes musical identity and themes
- Examines stylistic signatures
- Studies evolution and growth
- Highlights standout works
- Discusses artistic legacy

**True Collaboration Prompt** (when lyricist ≠ composer):
- Explores partnership chemistry
- Analyzes complementary styles
- Identifies creative patterns
- Studies which artists performed their work
- Examines timeline and evolution
- Highlights standout collaborations
- Discusses partnership legacy
- Imagines creative dynamics

## Usage Examples

### Python API

```python
from music_library_mcp.database import SongsDatabase

db = SongsDatabase('songs/songs_enriched.json')

# Get top collaborations
collabs = db.get_all_collaborations(limit=10)
for collab in collabs:
    print(f"{collab['lyricist']} × {collab['composer']}: {collab['song_count']} songs")

# Analyze a specific collaboration
collab = db.get_collaboration_songs('שלמה ארצי', 'שלמה ארצי')
print(f"Self-collaboration: {collab['song_count']} songs")
for song in collab['songs'][:5]:
    print(f"  - {song['name']}")

# Find all collaborators of a lyricist
collabs = db.get_collaborations_by_lyricist('אהוד מנור')
print(f"אהוד מנור worked with {len(collabs)} composers")
```

### MCP Resources

Access via Claude Desktop or other MCP clients:

```
"Show me the top collaborations in the music library"
"Analyze the collaboration between אהוד מנור and מתי כספי"
"Who did שלמה ארצי collaborate with most?"
"Find all self-collaborations (artists who write both lyrics and music)"
```

## Analytics Opportunities

With the collaboration cache, you can:

1. **Discover Creative Partnerships** - Find prolific lyricist-composer pairs
2. **Identify Self-Collaborators** - Artists with complete creative control
3. **Track Collaboration Networks** - See who works with whom
4. **Analyze Patterns** - Common themes in collaborations
5. **Study Evolution** - How partnerships develop over time
6. **Compare Styles** - How collaborators differ when working with others
7. **Rare Collaborations** - One-time partnerships vs. long-term relationships

## Interesting Insights

From the current database:

- **84.5%** of collaborations are single-song partnerships (rare collaborations)
- **Only 1%** of collaborations have 10+ songs (prolific partnerships)
- **28.3%** of collaborations are self-collaborations
- **Lennon & McCartney** appear as both "Lennon × McCartney" and "McCartney × Lennon" (both directions tracked)

## Performance

- **Build Time**: All collaborations indexed during database initialization
- **Query Time**: O(1) lookup for specific collaborations, O(n) for filtered queries
- **Memory**: ~1,725 cache entries for current database
- **Scalability**: Linear growth with number of unique lyricist-composer pairs

## Testing

Run comprehensive tests:

```bash
python test_collaborations.py
```

This will display:
- Collaboration statistics
- Top collaborations
- Self-collaborations analysis
- Specific collaboration examples
- Cartesian product demonstration
- Interesting insights

