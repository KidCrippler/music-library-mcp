# Music Library MCP Server - Usage Examples

Once you've configured the MCP server in Claude Desktop or Cursor, you can interact with your music library using natural language. Here are some example queries:

## Exploring Artists

### Get all songs by a specific artist
```
"Show me all songs by יהודית רביץ"
"What songs does Adele have in the library?"
"List all tracks by ABBA"
```

The assistant will use the `songs://artist/{name}` resource.

## Searching Songs

### Search by song name
```
"Find songs with 'חלומות' in the title"
"Search for songs about love"
```

### Search by multiple criteria
```
"Find Hebrew songs by Matti Caspi"
"Show me English songs in the children's category"
```

The assistant will use the `search_songs` tool.

## Browsing Categories

### List all categories
```
"What categories are available in the library?"
"Show me all music categories"
```

### Get songs in a category
```
"Show me all Hebrew songs"
"List children's songs (ילדים)"
"What are the independence day songs (עצמאות)?"
```

The assistant will use `songs://category/{id}` resources.

## Getting Song Details

### Fetch lyrics
```
"Get the lyrics for 'בך לא נוגע'"
"Show me the lyrics for song ID 1000001"
```

The assistant will use the `get_lyrics` tool.

### Get YouTube information
```
"Get the YouTube video for song 1000001"
"Show me the YouTube link for 'חלומות שמורים'"
```

The assistant will use the `get_youtube_metadata` tool.

## Library Statistics

### Get overview
```
"How many songs are in the library?"
"Show me library statistics"
"What's the distribution of songs by category?"
```

The assistant will use the `songs://stats` resource.

### List all artists
```
"Show me all artists in the library"
"How many artists are there?"
"List artists with the most songs"
```

The assistant will use the `songs://artists` resource.

## Using Prompts (Guided Workflows)

### Explore an artist's discography
```
"Explore the discography of יהודית רביץ"
"Analyze Adele's songs in the library"
```

The assistant will use the `explore_artist` prompt, which provides:
- Overview of their presence in the library
- Categories/genres they appear in
- Patterns and themes in song titles
- Notable recommendations

### Create a playlist
```
"Create an upbeat playlist with 10 Hebrew songs"
"Make me a playlist of romantic duets, 15 songs"
"Generate a children's party playlist"
```

The assistant will use the `create_playlist` prompt, which:
- Selects songs matching the theme
- Explains why each song fits
- Arranges them in a logical order
- Provides a catchy playlist name

### Discover similar songs
```
"Find songs similar to 'בך לא נוגע'"
"What other songs are like song ID 1000002?"
"Recommend songs similar to this one"
```

The assistant will use the `discover_similar` prompt, which:
- Finds songs by the same artist
- Finds songs in the same categories
- Ranks them by similarity
- Explains the similarity factors

## Complex Queries

The MCP server supports complex, multi-step queries:

```
"Find all Hebrew songs by female artists, create a playlist of the top 20,
and show me the YouTube links for the first 5"

"Analyze the distribution of songs across categories, then create a balanced
playlist with 2 songs from each category"

"Find the artist with the most songs, explore their discography, and create
a 'best of' playlist with their top 10 tracks"
```

## Tips for Best Results

1. **Be specific**: The more details you provide, the better the results
2. **Use artist names exactly**: Artist matching is case-insensitive but exact
3. **Refer to categories by name or ID**: Both work fine
4. **Combine criteria**: You can search by artist AND category simultaneously
5. **Use song IDs for precision**: When you know the exact song ID, use it

## Available Resources

- `songs://list` - Browse all songs (paginated)
- `songs://artist/{name}` - Songs by specific artist
- `songs://category/{id}` - Songs in a category
- `songs://song/{id}` - Individual song details
- `songs://categories` - List all categories
- `songs://artists` - List all artists with counts
- `songs://stats` - Library statistics

## Available Tools

- `search_songs` - Multi-criteria search
- `get_lyrics` - Fetch lyrics from URL
- `get_youtube_metadata` - Get video information

## Available Prompts

- `explore_artist` - Artist discography analysis
- `create_playlist` - Themed playlist generation
- `discover_similar` - Similar song recommendations
