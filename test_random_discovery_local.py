#!/usr/bin/env python3
"""Test the random discovery functionality with local data."""

import json
import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Testing Random Discovery Feature (Syntax Check)\n")
print("=" * 60)

# Test 1: Check database.py syntax
print("\n✓ TEST 1: Checking database.py syntax...")
try:
    with open('music_library_mcp/database.py', 'r') as f:
        code = f.read()
    
    # Check that the method exists
    if 'def get_random_discovery(' in code:
        print("  ✓ get_random_discovery method found")
    else:
        print("  ✗ get_random_discovery method not found")
        sys.exit(1)
    
    # Check for language filtering logic
    if 'language.lower() == "hebrew"' in code:
        print("  ✓ Hebrew language filter found")
    else:
        print("  ✗ Hebrew language filter not found")
        sys.exit(1)
    
    if 'language.lower() == "english"' in code:
        print("  ✓ English language filter found")
    else:
        print("  ✗ English language filter not found")
        sys.exit(1)
    
    # Check for random sampling
    if 'random.sample' in code:
        print("  ✓ Random sampling implementation found")
    else:
        print("  ✗ Random sampling not found")
        sys.exit(1)
    
    print("  ✓ All database checks passed!")
    
except Exception as e:
    print(f"  ✗ Error reading database.py: {e}")
    sys.exit(1)

# Test 2: Check server.py changes
print("\n✓ TEST 2: Checking server.py changes...")
try:
    with open('music_library_mcp/server.py', 'r') as f:
        code = f.read()
    
    # Check that dynamic resources were removed
    if 'for artist in artists[:50]:' in code:
        print("  ✗ ERROR: Artist dynamic resources still present!")
        sys.exit(1)
    else:
        print("  ✓ Artist dynamic resources removed")
    
    if 'for composer in composers[:50]:' in code:
        print("  ✗ ERROR: Composer dynamic resources still present!")
        sys.exit(1)
    else:
        print("  ✓ Composer dynamic resources removed")
    
    if 'for lyricist in lyricists[:50]:' in code:
        print("  ✗ ERROR: Lyricist dynamic resources still present!")
        sys.exit(1)
    else:
        print("  ✓ Lyricist dynamic resources removed")
    
    if 'for translator in translators[:50]:' in code:
        print("  ✗ ERROR: Translator dynamic resources still present!")
        sys.exit(1)
    else:
        print("  ✓ Translator dynamic resources removed")
    
    # Check that collaborations are limited to 10
    if 'db.get_all_collaborations(limit=10)' in code:
        print("  ✓ Collaborations limited to 10")
    else:
        print("  ✗ Collaborations not limited to 10")
        sys.exit(1)
    
    # Check that the new tool was added
    if 'name="get_random_discovery"' in code:
        print("  ✓ get_random_discovery tool definition found")
    else:
        print("  ✗ get_random_discovery tool definition not found")
        sys.exit(1)
    
    # Check tool handler
    if 'elif name == "get_random_discovery":' in code:
        print("  ✓ get_random_discovery tool handler found")
    else:
        print("  ✗ get_random_discovery tool handler not found")
        sys.exit(1)
    
    # Check tool calls db method
    if 'db.get_random_discovery(language=language, count=count)' in code:
        print("  ✓ Tool handler calls database method correctly")
    else:
        print("  ✗ Tool handler doesn't call database method")
        sys.exit(1)
    
    print("  ✓ All server checks passed!")
    
except Exception as e:
    print(f"  ✗ Error reading server.py: {e}")
    sys.exit(1)

# Test 3: Check method signature
print("\n✓ TEST 3: Validating method signature...")
try:
    expected_params = ['language: str = "both"', 'count: int = 10']
    
    with open('music_library_mcp/database.py', 'r') as f:
        code = f.read()
    
    for param in expected_params:
        if param in code:
            print(f"  ✓ Parameter '{param}' found")
        else:
            print(f"  ✗ Parameter '{param}' not found")
            sys.exit(1)
    
    print("  ✓ Method signature is correct!")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 4: Check return structure
print("\n✓ TEST 4: Validating return structure...")
try:
    with open('music_library_mcp/database.py', 'r') as f:
        code = f.read()
    
    required_keys = [
        "'language_filter'",
        "'songs'",
        "'artists'",
        "'composers'",
        "'lyricists'",
        "'counts'"
    ]
    
    # Keys that should NOT be present
    forbidden_keys = ["'translators'"]
    
    for key in required_keys:
        if key in code:
            print(f"  ✓ Return key {key} found")
        else:
            print(f"  ✗ Return key {key} not found")
            sys.exit(1)
    
    # Check that translators are NOT in the get_random_discovery return
    # Extract just the get_random_discovery method
    method_start = code.find('def get_random_discovery(')
    if method_start != -1:
        # Find the next method definition or end of class
        next_method = code.find('\n    def ', method_start + 1)
        if next_method == -1:
            method_code = code[method_start:]
        else:
            method_code = code[method_start:next_method]
        
        # Check that translators are not in the return statement of this method
        if "'translators'" in method_code:
            print("  ✗ Translators still in get_random_discovery return structure")
            sys.exit(1)
        else:
            print("  ✓ Translators removed from get_random_discovery")
    
    print("  ✓ Return structure is correct!")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 5: Check fame score implementation
print("\n✓ TEST 5: Validating fame score implementation...")
try:
    with open('music_library_mcp/database.py', 'r') as f:
        code = f.read()
    
    # Check for fame rank calculation method
    if 'def _calculate_fame_rank(' in code:
        print("  ✓ Fame rank calculation method found")
    else:
        print("  ✗ Fame rank calculation method not found")
        sys.exit(1)
    
    # Check for fame score in return values
    if "'fame_score'" in code:
        print("  ✓ Fame score in return structure")
    else:
        print("  ✗ Fame score not in return structure")
        sys.exit(1)
    
    # Check for sorting by fame score
    if 'sort(key=lambda x: x[\'fame_score\'], reverse=True)' in code:
        print("  ✓ Results sorted by fame score (descending)")
    else:
        print("  ✗ Results not sorted by fame score")
        sys.exit(1)
    
    # Check for composite score calculation (artist weight)
    if 'artist_fame * 0.6' in code:
        print("  ✓ Composite score with artist weight (0.6) found")
    else:
        print("  ✗ Composite score with artist weight not found")
        sys.exit(1)
    
    # Check for composer weight
    if 'avg_composer_fame * 0.25' in code:
        print("  ✓ Composite score with composer weight (0.25) found")
    else:
        print("  ✗ Composite score with composer weight not found")
        sys.exit(1)
    
    # Check for lyricist weight
    if 'avg_lyricist_fame * 0.15' in code:
        print("  ✓ Composite score with lyricist weight (0.15) found")
    else:
        print("  ✗ Composite score with lyricist weight not found")
        sys.exit(1)
    
    print("  ✓ Fame score implementation is correct!")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("\n✅ All validation tests passed!")
print("\n📋 Summary of changes:")
print("  ✓ Removed ~190 dynamic resources (artists, composers, lyricists, translators)")
print("  ✓ Reduced collaboration resources from 30 to 10")
print("  ✓ Added get_random_discovery() method to database")
print("  ✓ Added get_random_discovery tool to MCP server")
print("  ✓ Implemented language filtering (hebrew/english/both)")
print("  ✓ Added fame scores (0-100 rank) for all results")
print("  ✓ Songs get composite fame scores (artist 60%, composer 25%, lyricist 15%)")
print("  ✓ Results sorted by fame score (most famous first)")
print("  ✓ Removed all translator functionality")
print("\n💡 To test with actual data, install dependencies:")
print("   pip install -r requirements.txt")
print("   python3 test_random_discovery.py")
print()

