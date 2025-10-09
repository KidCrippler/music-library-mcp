# Quick Start Guide - Manual Review Web App

## What You Have

A complete web application for manually reviewing 327 songs that need credit information (composers, lyricists, translators).

## Quick Start (3 Steps)

### 1. Start the Web App

```bash
cd /Users/alonc/mcp-intro
python3 review_app.py
```

### 2. Open Browser

Go to: **http://localhost:5000**

### 3. Review Songs

- Fill in composers, lyricists, and translators for each song
- Click "Save & Next" to move to the next song
- Your progress is automatically saved

## When Done Reviewing

```bash
# Stop the app (Ctrl+C)

# Apply your manual reviews to create final JSON
python3 apply_manual_reviews.py
```

This creates: `songs/songs_enriched_final.json`

## Files Created

✅ **review_app.py** - Web server  
✅ **templates/review.html** - Web interface  
✅ **apply_manual_reviews.py** - Merge utility  
✅ **manual_reviews.json** - Your edits (created on first save)  
✅ **REVIEW_APP_README.md** - Full documentation  
✅ **requirements.txt** - Python dependencies  

## Key Features

- 🎯 Simple one-song-at-a-time interface
- 💾 Auto-saves your progress
- ⌨️ Keyboard shortcuts (Ctrl+S to save, arrows to navigate)
- 📊 Progress tracking (X of 327 completed)
- 🔒 Original JSON never modified
- 🔄 Can regenerate and re-apply reviews anytime

## Need Help?

See **REVIEW_APP_README.md** for detailed documentation.

