# Project Structure

The project has been organized into logical folders for better maintainability.

## Directory Layout

```
mcp-intro/
├── README.md                    # Main project documentation
├── pyproject.toml              # Package configuration
├── requirements.txt            # Python dependencies
│
├── music_library_mcp/          # Main MCP server package
│   ├── __init__.py
│   ├── server.py              # MCP server implementation
│   └── database.py            # Database layer with indexing
│
├── .venv/                      # Python virtual environment (Python 3.11)
│
├── songs/                      # Song data files
│   ├── songs.json             # Main songs database
│   ├── songs_enriched.json    # Enriched song data
│   ├── songs_enriched_final.json  # Final enriched data with manual reviews
│   └── manual_reviews.json    # Manual review data
│
├── scripts/                    # Utility scripts and tools
│   ├── start_server.sh        # Server launcher script
│   ├── test_setup.sh          # Setup verification script
│   ├── enrich_songs.py        # Song enrichment utility
│   ├── apply_manual_reviews.py # Apply manual reviews to songs
│   ├── review_app.py          # Flask web app for reviewing songs
│   └── templates/             # Flask templates for review app
│       └── review.html
│
├── tests/                      # Test files
│   ├── test_server.py         # Server tests
│   ├── test_contributors.py   # Contributors feature tests
│   └── test_collaborations.py # Collaborations feature tests
│
├── docs/                       # Documentation
│   ├── PROJECT_STRUCTURE.md   # This file
│   ├── SETUP.md              # Setup instructions
│   ├── QUICK_START.md        # Quick start guide
│   ├── QUICKSTART.md         # Alternative quick start
│   ├── USAGE_EXAMPLES.md     # Usage examples
│   ├── CLAUDE.md             # Claude AI integration notes
│   ├── CONTRIBUTORS_FEATURE.md   # Contributors feature docs
│   ├── COLLABORATION_FEATURE.md  # Collaboration feature docs
│   ├── COLLABORATION_SUMMARY.md  # Collaboration summary
│   └── REVIEW_APP_README.md  # Review app documentation
│
└── examples/                   # Example configurations
    └── claude_desktop_config.example.json
```

## Key Directories

### `music_library_mcp/`
The main Python package containing the MCP server implementation. This is the core of the project.

### `.venv/`
Python 3.11 virtual environment with all dependencies installed. This ensures consistent Python version and isolated dependencies.

### `songs/`
All song data files, including the main database, enriched versions, and manual reviews.

### `scripts/`
Utility scripts for development and maintenance:
- **start_server.sh**: Convenient way to start the MCP server
- **test_setup.sh**: Verify the setup is correct
- **enrich_songs.py**: Enrich song data with additional information
- **apply_manual_reviews.py**: Apply manual reviews to enriched songs
- **review_app.py**: Web interface for manually reviewing songs

### `tests/`
All test files for the project. Run tests with:
```bash
python -m pytest tests/
```

### `docs/`
All project documentation in one place.

### `examples/`
Example configuration files that users can copy and customize.

## Running Scripts

Since scripts are now in the `scripts/` folder, run them like this:

```bash
# Start the MCP server
./scripts/start_server.sh

# Test the setup
./scripts/test_setup.sh

# Run Python scripts
python scripts/enrich_songs.py
python scripts/apply_manual_reviews.py
python scripts/review_app.py
```

Or from anywhere:
```bash
/Users/alonc/mcp-intro/scripts/start_server.sh
```

## Running Tests

```bash
# From project root
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_server.py
```

## Benefits of This Structure

1. **Clean Root Directory**: Only essential config files and main package
2. **Logical Grouping**: Related files are together
3. **Easy Navigation**: Know exactly where to find things
4. **Professional**: Follows Python project best practices
5. **Scalable**: Easy to add new features without clutter

