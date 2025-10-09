# Manual Song Review Web App

A simple web application for manually reviewing and populating composer, lyricist, and translator information for songs that need manual review.

## Overview

This tool helps you manually review **327 songs** that couldn't be automatically parsed from their lyrics files. The app provides a clean interface to view each song's information and fill in the missing credits.

## Files

- **review_app.py** - Flask web server
- **templates/review.html** - Web interface
- **apply_manual_reviews.py** - Script to apply your manual edits
- **manual_reviews.json** - Persistent storage for your edits (created automatically)
- **songs/songs_enriched.json** - Input file (read-only, never modified)

## Getting Started

### 1. Start the Web App

```bash
cd /Users/alonc/mcp-intro
python3 review_app.py
```

The app will start on **http://localhost:5000**

You should see output like:
```
Loading songs from: /Users/alonc/mcp-intro/songs/songs_enriched.json
Manual reviews will be saved to: /Users/alonc/mcp-intro/manual_reviews.json
Found 327 songs needing manual review

Starting Flask app on http://localhost:5000
```

### 2. Open Your Browser

Navigate to: **http://localhost:5000**

You'll see the review interface with:
- Song information (name, singer, ID)
- Reference text (the unparsed string from the lyrics file)
- Input fields for composers, lyricists, and translators
- Navigation buttons (Previous, Skip, Save & Next)
- Progress indicator

### 3. Review Songs

For each song:

1. **Read the reference text** - This is the original unparsed line from the lyrics file
2. **Fill in the fields**:
   - **Composers**: Enter names separated by commas
   - **Lyricists**: Enter names separated by commas
   - **Translators**: Enter names separated by commas (leave empty if none)
3. **Click "Save & Next"** - Your edits are saved to `manual_reviews.json`
4. The app automatically moves to the next song

### 4. Navigation Tips

- **Previous** button: Go back to the previous song
- **Skip** button: Move to next song without saving
- **Keyboard shortcuts**:
  - `Ctrl+S` (or `Cmd+S` on Mac): Save current song
  - `Arrow Left`: Previous song
  - `Arrow Right`: Next song

### 5. Track Your Progress

The app shows:
- Current song number (e.g., "Song 15 of 327")
- Number of songs reviewed
- Number remaining
- Progress bar at the top

The app remembers your last position, so you can close and reopen it without losing progress.

## Apply Manual Reviews

Once you've reviewed songs, apply your edits to create a final JSON file:

```bash
cd /Users/alonc/mcp-intro
python3 apply_manual_reviews.py
```

This will:
1. Read `songs/songs_enriched.json` (original)
2. Read `manual_reviews.json` (your edits)
3. Apply your edits to the songs
4. Remove `needsManualReview` and `unparsedString` flags from reviewed songs
5. Create **`songs/songs_enriched_final.json`** (output file)

**Important**: The original `songs_enriched.json` is NEVER modified. This allows you to:
- Re-generate `songs_enriched.json` from scratch anytime
- Re-apply your manual reviews using the script

## Data Format

### manual_reviews.json Structure

```json
{
  "1000112": {
    "composers": ["דני סנדרסון"],
    "lyricists": ["דני סנדרסון"],
    "translators": []
  },
  "1000234": {
    "composers": ["מתי כספי", "יורם טהרלב"],
    "lyricists": ["אהוד מנור"],
    "translators": ["שלמה ארצי"]
  }
}
```

The key is the song ID, and the value contains arrays of names.

## Workflow Example

### Initial Setup
```bash
# Start the review app
python3 review_app.py
```

### Review Process
1. Open http://localhost:5000 in your browser
2. Review and fill in information for songs
3. Your edits are automatically saved to `manual_reviews.json`
4. You can stop and resume anytime - progress is saved

### When Done Reviewing
```bash
# Stop the Flask app (Ctrl+C in terminal)

# Apply your reviews to create the final file
python3 apply_manual_reviews.py
```

### If You Regenerate songs_enriched.json
```bash
# Run the enrichment script again
python3 enrich_songs.py

# Your manual_reviews.json is preserved!
# Just re-apply them:
python3 apply_manual_reviews.py
```

## Tips

1. **Reference Text**: The "unparsed string" shows the exact text from the lyrics file. Use it to understand what the script couldn't parse.

2. **Multiple Names**: Separate names with commas:
   - ✅ Good: `מתי כספי, אהוד מנור`
   - ❌ Bad: `מתי כספי ואהוד מנור`

3. **Empty Fields**: Leave translators empty if there's no translator (most songs won't have one)

4. **Already Reviewed**: Songs you've already reviewed show a green "✓ Reviewed" badge

5. **Batch Work**: You don't need to review all 327 songs at once. Review a few, stop, and continue later.

## Troubleshooting

### Port Already in Use
If port 5000 is taken:
```bash
# Edit review_app.py and change the port:
app.run(debug=True, port=5001)  # Use a different port
```

### Lost Progress
Your progress is saved in two places:
- `manual_reviews.json` - Permanent storage on disk
- Browser localStorage - Remembers your last position

If you lose localStorage (clear browser data), your reviews in `manual_reviews.json` are still safe.

### Reset Everything
```bash
# Delete manual reviews and start over
rm manual_reviews.json
```

## Statistics

After running `apply_manual_reviews.py`, you'll see:
```
Summary:
  Total songs: 1569
  Reviews applied: 50
  Still need manual review: 277
```

This shows how many songs you've reviewed and how many remain.

## Questions?

The app is self-contained and simple:
- No database required
- No authentication needed
- Runs locally on your machine
- All data stored in JSON files

Happy reviewing! 🎵

