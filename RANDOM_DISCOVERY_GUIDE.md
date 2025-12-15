# Random Discovery Tool - Quick Reference

## Overview

The `get_random_discovery` tool helps AI assistants (and users) explore the music library by providing random samples of content. This is useful when you don't know what to search for yet.

## Tool Parameters

```json
{
  "language": "hebrew" | "english" | "both",  // optional, default: "both"
  "count": 10                                  // optional, default: 10
}
```

## Example Requests

### Example 1: Get Random Content (Any Language)

**User asks:** "Show me some random songs from the library"

**AI uses:**
```json
{
  "tool": "get_random_discovery",
  "arguments": {
    "language": "both",
    "count": 10
  }
}
```

### Example 2: Hebrew Content Only

**User asks:** "Give me 10 random Hebrew songs and artists to explore"

**AI uses:**
```json
{
  "tool": "get_random_discovery",
  "arguments": {
    "language": "hebrew",
    "count": 10
  }
}
```

### Example 3: English Content Only

**User asks:** "Show me some English composers from the library"

**AI uses:**
```json
{
  "tool": "get_random_discovery",
  "arguments": {
    "language": "english",
    "count": 10
  }
}
```

## Response Structure

All results include **fame scores** (0-100 rank) and are **sorted by fame score** (most famous first).

```json
{
  "language_filter": "hebrew",
  "songs": [
    {
      "id": 1000001,
      "name": "שם השיר",
      "singer": "שם האמן",
      "composers": ["מלחין"],
      "lyricists": ["מילים"],
      "categoryIds": ["1"],
      "fame_score": 85,
      ...
    }
  ],
  "artists": [
    {
      "name": "אמן 1",
      "song_count": 150,
      "fame_score": 92
    },
    {
      "name": "אמן 2",
      "song_count": 80,
      "fame_score": 75
    }
  ],
  "composers": [
    {
      "name": "מלחין 1",
      "song_count": 200,
      "fame_score": 95
    }
  ],
  "lyricists": [
    {
      "name": "פזמונאי 1",
      "song_count": 120,
      "fame_score": 88
    }
  ],
  "counts": {
    "songs": 10,
    "artists": 10,
    "composers": 10,
    "lyricists": 10
  }
}
```

### Fame Score Details

- **0-100 Rank**: Higher = more famous/prolific
- **Artists/Composers/Lyricists**: Based on percentile of song count
  - 100 = most prolific contributor in the library
  - 50 = more prolific than 50% of contributors
  - 0 = least prolific
- **Songs**: Composite score calculated as:
  - Artist fame: 60% weight (heavy reliance)
  - Composer fame: 25% weight (modest reliance)
  - Lyricist fame: 15% weight (modest reliance)

## Use Cases

### 1. Initial Exploration
"I want to see what's in this music library"
→ Use `get_random_discovery` with `language: "both"`

### 2. Language-Specific Discovery
"Show me Hebrew music"
→ Use `get_random_discovery` with `language: "hebrew"`

### 3. Finding Starting Points
"I don't know what to search for"
→ Use `get_random_discovery` to get artist/composer names, then search for their work

### 4. Serendipitous Discovery
"Surprise me with something from the library"
→ Use `get_random_discovery` and pick a random result

## How It Works

1. **Language Filtering**: The tool searches for category names matching:
   - Hebrew: "עברית" or "hebrew"
   - English: "english" or "אנגלית"
   - Both: all songs regardless of category

2. **Random Sampling**: Uses Python's `random.sample()` to select truly random items

3. **Uniqueness**: All contributors (artists, composers, etc.) are unique in the results

4. **Balanced Results**: Returns equal counts for each category (songs, artists, composers, lyricists, translators)

## Comparison with Old Approach

### Before (Dynamic Resources)
- Resource list had ~200+ items (50 artists + 50 composers + 50 lyricists + 50 translators + 30 collaborations)
- Slow to load
- Fixed list, not randomized
- Overwhelming to browse

### After (Random Discovery Tool)
- Resource list has only 10 collaboration resources
- Fast to load
- Randomized results on each call
- Focused and manageable

## Tips for AI Assistants

1. **Use this tool first** when the user wants to explore without specific criteria
2. **Parse the results** to suggest specific items to the user
3. **Follow up** with specific searches using `search_songs` or resources like `songs://artist/{name}`
4. **Vary the language** based on user preferences or conversation context

## Example Workflow

```
User: "What kind of music is in this library?"

AI: [Calls get_random_discovery with language="both"]
AI: "The library has a diverse collection! Here are some examples:

Hebrew Songs:
- שיר 1 by אמן 1
- שיר 2 by אמן 2

English Songs:
- Song 1 by Artist 1
- Song 2 by Artist 2

Popular Artists: אמן 1, אמן 2, Artist 1, Artist 2...

Would you like to explore any of these artists in depth, or search for something specific?"

User: "Tell me more about אמן 1"

AI: [Calls songs://artist/אמן 1 resource or search_songs with artist filter]
```

## Testing

Run the validation test:
```bash
cd /Users/alonc/mcp-intro
python3 test_random_discovery_local.py
```

Run with actual data (requires dependencies):
```bash
pip install -r requirements.txt
python3 test_random_discovery.py
```

## Related Documentation

- [DYNAMIC_RESOURCES_OPTIMIZATION.md](./DYNAMIC_RESOURCES_OPTIMIZATION.md) - Full details on the optimization
- [USAGE_EXAMPLES.md](./docs/USAGE_EXAMPLES.md) - General usage examples for the MCP server
- [QUICK_START.md](./docs/QUICK_START.md) - Getting started guide

