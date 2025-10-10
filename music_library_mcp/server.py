"""MCP server implementation for the Music Library."""

import json
import asyncio
from pathlib import Path
from urllib.parse import urlparse

import httpx
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)
from mcp.server.stdio import stdio_server

from .database import SongsDatabase


# Initialize the database
DB_PATH = Path(__file__).parent.parent / "songs" / "songs.json"
db = SongsDatabase(DB_PATH)

# Create MCP server
app = Server("music-library-mcp")


# ============================================================================
# MCP RESOURCES - Expose queryable data endpoints
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available resources."""
    resources = [
        Resource(
            uri="songs://schema",
            name="Data Schema & Field Meanings",
            description="Documentation explaining what each field in the song data represents. IMPORTANT: Read this first to understand field meanings, especially dateCreated/dateModified which are internal timestamps, NOT actual song creation dates.",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://list",
            name="All Songs",
            description="Browse all songs in the library with pagination",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://categories",
            name="All Categories",
            description="List all song categories",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://artists",
            name="All Artists",
            description="List all artists with song counts",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://composers",
            name="All Composers",
            description="List all composers with song counts",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://lyricists",
            name="All Lyricists",
            description="List all lyricists with song counts",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://translators",
            name="All Translators",
            description="List all translators with song counts",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://collaborations",
            name="All Collaborations",
            description="List all lyricist-composer collaborations sorted by song count",
            mimeType="application/json",
        ),
        Resource(
            uri="songs://stats",
            name="Library Statistics",
            description="Get statistics about the music library",
            mimeType="application/json",
        ),
    ]

    # Add dynamic resources for each artist
    artists = db.get_all_artists()
    for artist in artists[:50]:  # Limit to first 50 to avoid overwhelming the list
        resources.append(
            Resource(
                uri=f"songs://artist/{artist['name']}",
                name=f"Songs by {artist['name']}",
                description=f"All songs by {artist['name']} ({artist['song_count']} songs)",
                mimeType="application/json",
            )
        )

    # Add dynamic resources for each composer
    composers = db.get_all_composers()
    for composer in composers[:50]:  # Limit to first 50 to avoid overwhelming the list
        resources.append(
            Resource(
                uri=f"songs://composer/{composer['name']}",
                name=f"Songs composed by {composer['name']}",
                description=f"All songs composed by {composer['name']} ({composer['song_count']} songs)",
                mimeType="application/json",
            )
        )

    # Add dynamic resources for each lyricist
    lyricists = db.get_all_lyricists()
    for lyricist in lyricists[:50]:  # Limit to first 50 to avoid overwhelming the list
        resources.append(
            Resource(
                uri=f"songs://lyricist/{lyricist['name']}",
                name=f"Songs with lyrics by {lyricist['name']}",
                description=f"All songs with lyrics by {lyricist['name']} ({lyricist['song_count']} songs)",
                mimeType="application/json",
            )
        )

    # Add dynamic resources for each translator
    translators = db.get_all_translators()
    for translator in translators[:50]:  # Limit to first 50 to avoid overwhelming the list
        resources.append(
            Resource(
                uri=f"songs://translator/{translator['name']}",
                name=f"Songs translated by {translator['name']}",
                description=f"All songs translated by {translator['name']} ({translator['song_count']} songs)",
                mimeType="application/json",
            )
        )

    # Add dynamic resources for top collaborations
    collaborations = db.get_all_collaborations(limit=30)  # Top 30 collaborations
    for collab in collaborations:
        lyricist = collab['lyricist']
        composer = collab['composer']
        count = collab['song_count']
        
        # Create descriptive name
        if lyricist.lower().strip() == composer.lower().strip():
            # Self-collaboration (same person as lyricist and composer)
            name = f"{lyricist} (self-collaboration)"
            description = f"{lyricist} wrote both lyrics and music for {count} songs"
        else:
            name = f"{lyricist} × {composer}"
            description = f"{lyricist} (lyrics) and {composer} (music) collaborated on {count} songs"
        
        resources.append(
            Resource(
                uri=f"songs://collaboration/{lyricist}/{composer}",
                name=name,
                description=description,
                mimeType="application/json",
            )
        )

    return resources


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource."""
    parsed = urlparse(uri)

    if parsed.scheme != "songs":
        raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")

    path = parsed.path.lstrip("/")

    # Handle different resource paths
    if path == "schema":
        schema_doc = {
            "title": "Music Library Data Schema",
            "description": "Field definitions and meanings for song data",
            "important_notes": [
                "⚠️ CRITICAL: dateCreated and dateModified are INTERNAL SYSTEM TIMESTAMPS for database management.",
                "These fields DO NOT represent when the actual songs were created or released.",
                "These timestamps relate to when entries were added/modified in the database system.",
                "DO NOT use these fields to analyze song eras, release dates, or music history timelines."
            ],
            "song_fields": {
                "id": {
                    "type": "integer",
                    "description": "Unique identifier for the song"
                },
                "name": {
                    "type": "string",
                    "description": "The song title"
                },
                "singer": {
                    "type": "string",
                    "description": "The performing artist or singer"
                },
                "composers": {
                    "type": "array of strings",
                    "description": "The person(s) who composed the music"
                },
                "lyricists": {
                    "type": "array of strings",
                    "description": "The person(s) who wrote the lyrics"
                },
                "translators": {
                    "type": "array of strings",
                    "description": "The person(s) who translated the lyrics (if applicable)",
                    "optional": True
                },
                "categoryIds": {
                    "type": "array of strings",
                    "description": "IDs of categories this song belongs to (e.g., Hebrew, English, children's songs, etc.)"
                },
                "playback": {
                    "type": "object",
                    "description": "Playback information",
                    "fields": {
                        "youTubeVideoId": "The YouTube video ID for this song"
                    }
                },
                "lyrics": {
                    "type": "object",
                    "description": "Lyrics information",
                    "fields": {
                        "markupUrl": "URL to the lyrics text file",
                        "markupVersion": "Version of the markup format (optional)"
                    }
                },
                "dateCreated": {
                    "type": "timestamp (milliseconds)",
                    "description": "⚠️ INTERNAL USE ONLY: Database entry creation timestamp. NOT the song's actual creation/release date.",
                    "warning": "This is a system timestamp for when the entry was added to the database. It has nothing to do with when the song was actually written, recorded, or released."
                },
                "dateModified": {
                    "type": "timestamp (milliseconds)",
                    "description": "⚠️ INTERNAL USE ONLY: Database entry last modification timestamp. NOT when the song was modified.",
                    "warning": "This is a system timestamp for when the database entry was last updated. It has nothing to do with the song itself."
                }
            },
            "usage_guidelines": {
                "analyzing_music_history": "Do NOT use dateCreated/dateModified fields. These are database timestamps, not music metadata.",
                "finding_new_songs": "Use the 'newSongIds' array in the root data structure, not dateCreated.",
                "timeline_analysis": "Date fields in this database cannot be used for temporal analysis of music trends or eras.",
                "collaborations": "Use composer/lyricist fields to analyze creative partnerships.",
                "categorization": "Use categoryIds and the categories list for genre and theme analysis."
            }
        }
        return json.dumps(schema_doc, ensure_ascii=False, indent=2)

    elif path == "list":
        songs = db.get_all_songs(limit=100)
        return json.dumps(songs, ensure_ascii=False, indent=2)

    elif path == "categories":
        categories = db.get_all_categories()
        return json.dumps(categories, ensure_ascii=False, indent=2)

    elif path == "artists":
        artists = db.get_all_artists()
        return json.dumps(artists, ensure_ascii=False, indent=2)

    elif path == "composers":
        composers = db.get_all_composers()
        return json.dumps(composers, ensure_ascii=False, indent=2)

    elif path == "lyricists":
        lyricists = db.get_all_lyricists()
        return json.dumps(lyricists, ensure_ascii=False, indent=2)

    elif path == "translators":
        translators = db.get_all_translators()
        return json.dumps(translators, ensure_ascii=False, indent=2)

    elif path == "collaborations":
        collaborations = db.get_all_collaborations(limit=100)
        return json.dumps(collaborations, ensure_ascii=False, indent=2)

    elif path == "stats":
        stats = db.get_stats()
        return json.dumps(stats, ensure_ascii=False, indent=2)

    elif path.startswith("song/"):
        song_id = int(path.split("/")[1])
        song = db.get_song_by_id(song_id)
        if not song:
            raise ValueError(f"Song not found: {song_id}")
        return json.dumps(song, ensure_ascii=False, indent=2)

    elif path.startswith("artist/"):
        artist_name = path.split("/", 1)[1]
        songs = db.get_songs_by_artist(artist_name)
        if not songs:
            raise ValueError(f"No songs found for artist: {artist_name}")
        return json.dumps(songs, ensure_ascii=False, indent=2)

    elif path.startswith("composer/"):
        composer_name = path.split("/", 1)[1]
        songs = db.get_songs_by_composer(composer_name)
        if not songs:
            raise ValueError(f"No songs found for composer: {composer_name}")
        return json.dumps(songs, ensure_ascii=False, indent=2)

    elif path.startswith("lyricist/"):
        lyricist_name = path.split("/", 1)[1]
        songs = db.get_songs_by_lyricist(lyricist_name)
        if not songs:
            raise ValueError(f"No songs found for lyricist: {lyricist_name}")
        return json.dumps(songs, ensure_ascii=False, indent=2)

    elif path.startswith("translator/"):
        translator_name = path.split("/", 1)[1]
        songs = db.get_songs_by_translator(translator_name)
        if not songs:
            raise ValueError(f"No songs found for translator: {translator_name}")
        return json.dumps(songs, ensure_ascii=False, indent=2)

    elif path.startswith("collaboration/"):
        # Parse lyricist/composer from path
        parts = path.split("/", 2)
        if len(parts) < 3:
            raise ValueError("Invalid collaboration path format")
        lyricist_name = parts[1]
        composer_name = parts[2]
        
        collab_data = db.get_collaboration_songs(lyricist_name, composer_name)
        if not collab_data:
            raise ValueError(f"No collaboration found for {lyricist_name} and {composer_name}")
        return json.dumps(collab_data, ensure_ascii=False, indent=2)

    elif path.startswith("category/"):
        category_id = path.split("/")[1]
        songs = db.get_songs_by_category(category_id)
        category = db.get_category_by_id(category_id)
        result = {
            "category": category,
            "songs": songs
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    else:
        raise ValueError(f"Unknown resource path: {path}")


# ============================================================================
# MCP TOOLS - Operations for searching and data fetching
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="search_songs",
            description="Search for songs by name, artist, category, composer, lyricist, or translator. Supports partial matching. IMPORTANT: Results include dateCreated/dateModified fields which are internal database timestamps, NOT actual song creation dates. See the schema resource for field meanings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for song name or artist (optional)",
                    },
                    "artist": {
                        "type": "string",
                        "description": "Filter by specific artist name (optional)",
                    },
                    "category_id": {
                        "type": "string",
                        "description": "Filter by category ID (optional)",
                    },
                    "composer": {
                        "type": "string",
                        "description": "Filter by composer name (optional)",
                    },
                    "lyricist": {
                        "type": "string",
                        "description": "Filter by lyricist name (optional)",
                    },
                    "translator": {
                        "type": "string",
                        "description": "Filter by translator name (optional)",
                    },
                },
            },
        ),
        Tool(
            name="get_lyrics",
            description="Fetch lyrics content from a song's markup URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "song_id": {
                        "type": "number",
                        "description": "The ID of the song to fetch lyrics for",
                    },
                },
                "required": ["song_id"],
            },
        ),
        Tool(
            name="get_youtube_metadata",
            description="Get metadata for a YouTube video (title, description, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "song_id": {
                        "type": "number",
                        "description": "The ID of the song to fetch YouTube metadata for",
                    },
                },
                "required": ["song_id"],
            },
        ),
        Tool(
            name="get_collaborations",
            description="Query lyricist-composer collaborations with optional filters. Returns pairs sorted by number of songs they created together.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lyricist": {
                        "type": "string",
                        "description": "Filter by specific lyricist name (optional)",
                    },
                    "composer": {
                        "type": "string",
                        "description": "Filter by specific composer name (optional)",
                    },
                    "min_songs": {
                        "type": "number",
                        "description": "Minimum number of songs in collaboration (optional, default: 1)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (optional, default: 50)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "search_songs":
        query = arguments.get("query")
        artist = arguments.get("artist")
        category_id = arguments.get("category_id")
        composer = arguments.get("composer")
        lyricist = arguments.get("lyricist")
        translator = arguments.get("translator")

        results = db.search_songs(
            query=query,
            artist=artist,
            category_id=category_id,
            composer=composer,
            lyricist=lyricist,
            translator=translator
        )

        # Wrap results with metadata note
        response_data = {
            "_note": "⚠️ IMPORTANT: dateCreated and dateModified are internal database timestamps, NOT actual song creation dates. See the schema resource (songs://schema) for complete field documentation.",
            "result_count": len(results),
            "songs": results
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(response_data, ensure_ascii=False, indent=2),
            )
        ]

    elif name == "get_lyrics":
        song_id = arguments["song_id"]
        song = db.get_song_by_id(song_id)

        if not song:
            return [TextContent(type="text", text=f"Song not found: {song_id}")]

        lyrics_info = song.get("lyrics", {})
        markup_url = lyrics_info.get("markupUrl")

        if not markup_url:
            return [TextContent(type="text", text="No lyrics URL found for this song")]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(markup_url, timeout=10.0)
                response.raise_for_status()
                lyrics_text = response.text

            result = {
                "song_id": song_id,
                "song_name": song.get("name"),
                "artist": song.get("singer"),
                "lyrics": lyrics_text,
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2),
                )
            ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error fetching lyrics: {str(e)}",
                )
            ]

    elif name == "get_youtube_metadata":
        song_id = arguments["song_id"]
        song = db.get_song_by_id(song_id)

        if not song:
            return [TextContent(type="text", text=f"Song not found: {song_id}")]

        playback = song.get("playback", {})
        video_id = playback.get("youTubeVideoId")

        if not video_id:
            return [
                TextContent(type="text", text="No YouTube video ID found for this song")
            ]

        result = {
            "song_id": song_id,
            "song_name": song.get("name"),
            "artist": song.get("singer"),
            "youtube_video_id": video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "note": "Full YouTube API integration would require API key. This shows the basic video information.",
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ]

    elif name == "get_collaborations":
        lyricist = arguments.get("lyricist")
        composer = arguments.get("composer")
        min_songs = arguments.get("min_songs", 1)
        limit = arguments.get("limit", 50)

        # Get collaborations based on filters
        if lyricist and composer:
            # Specific collaboration
            collab_data = db.get_collaboration_songs(lyricist, composer)
            if collab_data:
                results = [collab_data]
            else:
                results = []
        elif lyricist:
            # All collaborations for this lyricist
            results = db.get_collaborations_by_lyricist(lyricist)
        elif composer:
            # All collaborations for this composer
            results = db.get_collaborations_by_composer(composer)
        else:
            # All collaborations
            results = db.get_all_collaborations()

        # Apply min_songs filter
        if min_songs > 1:
            results = [r for r in results if r['song_count'] >= min_songs]

        # Apply limit
        if limit:
            results = results[:limit]

        return [
            TextContent(
                type="text",
                text=json.dumps(results, ensure_ascii=False, indent=2),
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


# ============================================================================
# MCP PROMPTS - Guided workflows
# ============================================================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available prompts."""
    return [
        Prompt(
            name="explore_artist",
            description="Deep dive into an artist's discography with analysis and insights",
            arguments=[
                {
                    "name": "artist_name",
                    "description": "The name of the artist to explore",
                    "required": True,
                }
            ],
        ),
        Prompt(
            name="create_playlist",
            description="Generate a curated playlist based on specific criteria",
            arguments=[
                {
                    "name": "theme",
                    "description": "Theme or mood for the playlist (e.g., 'upbeat Hebrew songs', 'romantic duets')",
                    "required": True,
                },
                {
                    "name": "size",
                    "description": "Number of songs in the playlist (default: 10)",
                    "required": False,
                }
            ],
        ),
        Prompt(
            name="discover_similar",
            description="Find songs similar to a given song based on artist, category, or era",
            arguments=[
                {
                    "name": "song_id",
                    "description": "ID of the song to find similar songs for",
                    "required": True,
                },
                {
                    "name": "limit",
                    "description": "Maximum number of similar songs to return (default: 5)",
                    "required": False,
                }
            ],
        ),
        Prompt(
            name="explore_contributor",
            description="Deep dive into a composer, lyricist, or translator's work with analysis and insights",
            arguments=[
                {
                    "name": "contributor_name",
                    "description": "The name of the composer, lyricist, or translator to explore",
                    "required": True,
                },
                {
                    "name": "contributor_type",
                    "description": "Type of contributor: 'composer', 'lyricist', or 'translator'",
                    "required": True,
                }
            ],
        ),
        Prompt(
            name="analyze_collaboration",
            description="Explore the creative partnership between a lyricist and composer, including self-collaborations where one person does both",
            arguments=[
                {
                    "name": "lyricist",
                    "description": "The name of the lyricist",
                    "required": True,
                },
                {
                    "name": "composer",
                    "description": "The name of the composer (can be the same as lyricist for self-collaborations)",
                    "required": True,
                }
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Handle prompt requests."""

    if name == "explore_artist":
        artist_name = arguments["artist_name"]
        songs = db.get_songs_by_artist(artist_name)

        if not songs:
            prompt_text = f"No songs found for artist: {artist_name}. Please check the artist name and try again."
        else:
            songs_data = json.dumps(songs, ensure_ascii=False, indent=2)
            prompt_text = f"""Analyze the discography of {artist_name} based on the following songs:

{songs_data}

Please provide:
1. An overview of their musical presence in this library ({len(songs)} songs)
2. The categories/genres they appear in
3. Any patterns in their song titles or themes
4. Notable collaborations with composers, lyricists, and translators
5. Notable songs or recommendations from their collection
"""

        return GetPromptResult(
            description=f"Exploring the discography of {artist_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "create_playlist":
        theme = arguments["theme"]
        size = int(arguments.get("size", 10))

        stats = db.get_stats()
        all_songs = db.get_all_songs(limit=200)

        songs_data = json.dumps(all_songs, ensure_ascii=False, indent=2)
        categories_data = json.dumps(stats["categories"], ensure_ascii=False, indent=2)

        prompt_text = f"""Create a playlist with the theme: "{theme}"

The playlist should contain {size} songs.

Available categories:
{categories_data}

Sample of available songs:
{songs_data}

Please:
1. Select {size} songs that best match the theme "{theme}"
2. Explain why each song fits the theme
3. Arrange them in a logical order
4. Provide a catchy name for the playlist
"""

        return GetPromptResult(
            description=f"Creating a playlist: {theme}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "discover_similar":
        song_id = int(arguments["song_id"])
        limit = int(arguments.get("limit", 5))

        song = db.get_song_by_id(song_id)

        if not song:
            prompt_text = f"Song with ID {song_id} not found."
        else:
            artist = song.get("singer", "")
            category_ids = song.get("categoryIds", [])

            # Get songs by same artist
            artist_songs = db.get_songs_by_artist(artist) if artist else []

            # Get songs in same categories
            category_songs = []
            for cat_id in category_ids:
                category_songs.extend(db.get_songs_by_category(cat_id))

            # Combine and deduplicate
            similar_songs = {s["id"]: s for s in artist_songs + category_songs}
            # Remove the original song
            similar_songs.pop(song_id, None)

            similar_list = list(similar_songs.values())[:limit * 2]

            song_data = json.dumps(song, ensure_ascii=False, indent=2)
            similar_data = json.dumps(similar_list, ensure_ascii=False, indent=2)

            prompt_text = f"""Find songs similar to:

{song_data}

Candidates from the same artist and categories:
{similar_data}

Please:
1. Select the top {limit} most similar songs
2. Explain the similarity factors (artist, category, era, theme, etc.)
3. Rank them by similarity
"""

        return GetPromptResult(
            description=f"Finding songs similar to song ID {song_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "explore_contributor":
        contributor_name = arguments["contributor_name"]
        contributor_type = arguments["contributor_type"].lower()

        if contributor_type == "composer":
            songs = db.get_songs_by_composer(contributor_name)
            role_desc = "composed"
        elif contributor_type == "lyricist":
            songs = db.get_songs_by_lyricist(contributor_name)
            role_desc = "wrote lyrics for"
        elif contributor_type == "translator":
            songs = db.get_songs_by_translator(contributor_name)
            role_desc = "translated"
        else:
            prompt_text = f"Invalid contributor type: {contributor_type}. Must be 'composer', 'lyricist', or 'translator'."
            return GetPromptResult(
                description=f"Error exploring contributor",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt_text),
                    )
                ],
            )

        if not songs:
            prompt_text = f"No songs found for {contributor_type} {contributor_name}. Please check the name and try again."
        else:
            songs_data = json.dumps(songs, ensure_ascii=False, indent=2)
            prompt_text = f"""Analyze the work of {contributor_type} {contributor_name} based on the following songs they {role_desc}:

{songs_data}

Please provide:
1. An overview of their contribution to this library ({len(songs)} songs)
2. The artists they worked with most frequently
3. The categories/genres they contributed to
4. Any patterns in the songs they worked on (themes, styles, eras)
5. Notable collaborations with other composers, lyricists, or translators
6. Their most significant or representative works from this collection
"""

        return GetPromptResult(
            description=f"Exploring the work of {contributor_type} {contributor_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "analyze_collaboration":
        lyricist = arguments["lyricist"]
        composer = arguments["composer"]
        
        collab_data = db.get_collaboration_songs(lyricist, composer)
        
        if not collab_data:
            prompt_text = f"No collaboration found between {lyricist} (lyrics) and {composer} (music). Please check the names and try again."
            return GetPromptResult(
                description="Collaboration not found",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt_text),
                    )
                ],
            )
        
        songs = collab_data['songs']
        song_count = collab_data['song_count']
        is_self_collab = lyricist.lower().strip() == composer.lower().strip()
        
        songs_data = json.dumps(songs, ensure_ascii=False, indent=2)
        
        if is_self_collab:
            # Self-collaboration prompt (one person doing both lyrics and music)
            prompt_text = f"""Analyze the creative artistry of {lyricist}, who wrote both the lyrics and music for {song_count} songs in this collection.

{songs_data}

This is a fascinating case of complete artistic control where one person crafts both the words and the melodies. Please provide:

1. **The Complete Artist**: What does it mean when someone writes both lyrics and music? How does this level of creative control shape their work?

2. **Musical Identity**: Based on these {song_count} songs, what themes, emotions, or stories does {lyricist} consistently explore?

3. **Stylistic Signature**: Are there patterns in song titles, musical themes, or lyrical approaches that reveal {lyricist}'s unique voice?

4. **Evolution & Growth**: If there are dates available, how has their self-composed work evolved over time?

5. **Standout Works**: Which songs best represent {lyricist}'s ability to seamlessly blend lyrics and music?

6. **The Artist's Legacy**: What makes {lyricist}'s self-collaborations special or memorable? What can we learn about their artistic vision?

Think of this as understanding the mind of an auteur - someone whose complete creative vision flows through every note and word."""

        else:
            # True collaboration between two different people
            prompt_text = f"""Analyze the creative partnership between {lyricist} (lyrics) and {composer} (music), who collaborated on {song_count} songs together.

{songs_data}

This is a dance between words and music, where two creative minds come together. Please provide:

1. **The Partnership Chemistry**: What makes the collaboration between {lyricist} and {composer} work? How do their individual styles complement each other?

2. **Musical Themes**: Based on these {song_count} collaborations, what themes, emotions, or stories do they explore together?

3. **Creative Patterns**: Are there recurring patterns in song titles, musical motifs, or lyrical approaches that define this partnership?

4. **Artists They Worked With**: Which performers recorded their collaborations? Are there favorite interpreters of their work?

5. **Timeline & Evolution**: If dates are available, how did their collaboration evolve? Did their style change over time?

6. **Standout Collaborations**: Which songs best exemplify the magic that happens when {lyricist}'s words meet {composer}'s music?

7. **The Partnership's Legacy**: What is unique about this lyricist-composer pairing? How do they differ when working with other collaborators?

8. **Creative Dynamics**: Imagine the creative process - how might {lyricist}'s words inspire {composer}'s melodies, and vice versa?

Think of this as exploring a creative marriage - two artists whose combined work is greater than the sum of its parts."""

        return GetPromptResult(
            description=f"Analyzing collaboration: {lyricist} × {composer}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


# ============================================================================
# Main entry point
# ============================================================================

async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def run():
    """Run the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
