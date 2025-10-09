#!/usr/bin/env python3
"""
Enrich songs.json with lyricist and composer information extracted from lyrics files.
"""

import json
import re
import os
from typing import Tuple, List, Optional, Dict
from pathlib import Path


def url_to_filepath(url: str) -> str:
    """Convert GitHub raw URL to local file path."""
    # https://raw.githubusercontent.com/KidCrippler/songs/master/hebrew_ophir/page2.txt
    # -> /Users/alonc/songs/hebrew_ophir/page2.txt
    base_path = "/Users/alonc/songs/"
    if "raw.githubusercontent.com/KidCrippler/songs/master/" in url:
        relative_path = url.split("raw.githubusercontent.com/KidCrippler/songs/master/")[1]
        return base_path + relative_path
    return None


def is_image_file(filepath: str) -> bool:
    """Check if file is an image."""
    extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    return any(filepath.lower().endswith(ext) for ext in extensions)


def split_names(name_string: str) -> List[str]:
    """Split multiple names on various connectors."""
    # Split on: &, –, -, and, ו (Hebrew vav conjunction), ,
    # Hebrew ו can appear as " ו" or " ו[letter]" (attached to next word)
    # Use regex to split on these delimiters
    separators = r'[&,]|–(?!-)|\sand\s|\sו'
    parts = re.split(separators, name_string)
    
    # Clean up whitespace, remove (+X) patterns, and filter empty strings
    names = []
    for name in parts:
        name = name.strip()
        # Remove (+X) patterns like (+1), (+2), etc.
        name = re.sub(r'\s*\(\+\d+\)\s*', '', name).strip()
        if name:
            names.append(name)
    return names


def parse_hebrew_slash_format(first_line: str) -> Tuple[Optional[List[str]], Optional[List[str]], bool, str]:
    """
    Parse Hebrew format: [title] – [singer] / [composer] / [lyricist]
    Returns: (composers, lyricists, uncertain, unparsed_string)
    """
    # Look for pattern with slashes
    if '/' in first_line:
        parts = first_line.split('/')
        if len(parts) == 3:
            # parts[0] = title – singer
            # parts[1] = composer
            # parts[2] = lyricist
            composers = split_names(parts[1].strip())
            lyricists = split_names(parts[2].strip())
            return composers, lyricists, False, ""
        else:
            # Uncertain: has slashes but not 3 parts
            return None, None, True, first_line.strip()
    
    return None, None, False, ""


def parse_hebrew_labels(first_lines: List[str]) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[List[str]], bool, str]:
    """
    Parse Hebrew format with explicit labels:
    - מילים: [names]   לחן: [names]   תרגום: [names]
    - מילים ולחן: [names]
    Returns: (composers, lyricists, translators, uncertain, unparsed_string)
    """
    text = '\n'.join(first_lines[:3])  # Check first 3 lines
    
    # Pattern for translator
    translator_pattern = r'תרגום\s*:\s*([^\n]+?)(?:\s+(?:מילים|לחן)|$)'
    translator_match = re.search(translator_pattern, text)
    translators = split_names(translator_match.group(1).strip()) if translator_match else None
    
    # Pattern for combined: מילים ולחן:
    # Need to exclude translator part if it exists
    combined_pattern = r'מילים\s*ולחן\s*:\s*([^\n\t]+?)(?:\s+תרגום|$)'
    combined_match = re.search(combined_pattern, text)
    if combined_match:
        names = split_names(combined_match.group(1).strip())
        return names, names, translators, False, ""
    
    # Pattern for separate labels
    lyrics_pattern = r'מילים\s*:\s*([^\n\t]+?)(?:\s+(?:לחן|תרגום)|$)'
    music_pattern = r'לחן\s*:\s*([^\n\t]+?)(?:\s+(?:מילים|תרגום)|$)'
    
    lyrics_match = re.search(lyrics_pattern, text)
    music_match = re.search(music_pattern, text)
    
    if lyrics_match or music_match:
        lyricists = split_names(lyrics_match.group(1).strip()) if lyrics_match else None
        composers = split_names(music_match.group(1).strip()) if music_match else None
        return composers, lyricists, translators, False, ""
    
    return None, None, translators, False, ""


def parse_english_labels(first_lines: List[str]) -> Tuple[Optional[List[str]], Optional[List[str]], bool, str]:
    """
    Parse English format:
    - Lyrics and Music: [names]
    - Lyrics: [names]   Music: [names]
    """
    text = '\n'.join(first_lines[:3])  # Check first 3 lines
    
    # Pattern for combined: Lyrics and Music:
    combined_pattern = r'Lyrics\s+and\s+Music\s*:\s*([^\n]+)'
    combined_match = re.search(combined_pattern, text, re.IGNORECASE)
    if combined_match:
        names = split_names(combined_match.group(1).strip())
        return names, names, False, ""
    
    # Pattern for separate labels
    lyrics_pattern = r'Lyrics\s*:\s*([^\n]+?)(?:\s+Music|$)'
    music_pattern = r'Music\s*:\s*([^\n]+?)(?:\s+Lyrics|$)'
    
    lyrics_match = re.search(lyrics_pattern, text, re.IGNORECASE)
    music_match = re.search(music_pattern, text, re.IGNORECASE)
    
    if lyrics_match or music_match:
        lyricists = split_names(lyrics_match.group(1).strip()) if lyrics_match else None
        composers = split_names(music_match.group(1).strip()) if music_match else None
        return composers, lyricists, False, ""
    
    return None, None, False, ""


def extract_credits(filepath: str) -> Dict:
    """
    Extract composer, lyricist, and translator information from a lyrics file.
    Returns dict with keys: composers, lyricists, translators, needsManualReview, parsingUncertain, unparsedString
    """
    result = {
        "composers": None,
        "lyricists": None,
        "translators": None,
        "needsManualReview": False,
        "parsingUncertain": False,
        "unparsedString": None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()[:5]]  # Read first 5 lines
            
        if not lines:
            result["needsManualReview"] = True
            return result
        
        # Try Hebrew slash format first
        composers, lyricists, uncertain, unparsed = parse_hebrew_slash_format(lines[0])
        if composers or lyricists:
            result["composers"] = composers
            result["lyricists"] = lyricists
            result["parsingUncertain"] = uncertain
            if uncertain:
                result["unparsedString"] = unparsed
            # Check for translators in label format even if slash format matched
            _, _, translators, _, _ = parse_hebrew_labels(lines)
            result["translators"] = translators
            return result
        
        # Try Hebrew label format
        composers, lyricists, translators, uncertain, unparsed = parse_hebrew_labels(lines)
        if composers or lyricists or translators:
            result["composers"] = composers
            result["lyricists"] = lyricists
            result["translators"] = translators
            result["parsingUncertain"] = uncertain
            if uncertain:
                result["unparsedString"] = unparsed
            return result
        
        # Try English label format
        composers, lyricists, uncertain, unparsed = parse_english_labels(lines)
        if composers or lyricists:
            result["composers"] = composers
            result["lyricists"] = lyricists
            result["parsingUncertain"] = uncertain
            if uncertain:
                result["unparsedString"] = unparsed
            return result
        
        # If nothing matched, mark for manual review
        result["needsManualReview"] = True
        result["unparsedString"] = lines[0] if lines else ""
        
    except FileNotFoundError:
        result["needsManualReview"] = True
        result["unparsedString"] = "File not found"
    except Exception as e:
        result["needsManualReview"] = True
        result["unparsedString"] = f"Error: {str(e)}"
    
    return result


def enrich_songs(input_path: str, output_path: str):
    """Main function to enrich songs.json with composer/lyricist data."""
    
    # Statistics
    stats = {
        "total_songs": 0,
        "successfully_parsed": 0,
        "needs_manual_review": 0,
        "parsing_uncertain": 0,
        "image_files_skipped": 0,
        "missing_files": 0,
        "no_lyrics_url": 0,
        "with_translators": 0
    }
    
    # Read input JSON
    print(f"Reading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update version
    data["version"] = "2025_10_09"
    
    # Process each song
    songs = data.get("songs", [])
    stats["total_songs"] = len(songs)
    
    print(f"Processing {stats['total_songs']} songs...")
    
    for i, song in enumerate(songs):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{stats['total_songs']} songs...")
        
        # Check if song has lyrics URL
        lyrics = song.get("lyrics", {})
        markup_url = lyrics.get("markupUrl")
        
        if not markup_url:
            # Add needsManualReview flag for songs without lyrics URL
            ordered_song = {}
            isPrivate_value = song.get("isPrivate")
            
            for key in song.keys():
                if key == "isPrivate":
                    continue  # Will add after playback
                ordered_song[key] = song[key]
                if key == "singer":
                    ordered_song["needsManualReview"] = True
                elif key == "playback" and isPrivate_value is not None:
                    ordered_song["isPrivate"] = isPrivate_value
            
            song.clear()
            song.update(ordered_song)
            stats["no_lyrics_url"] += 1
            stats["needs_manual_review"] += 1
            continue
        
        # Convert URL to filepath
        filepath = url_to_filepath(markup_url)
        if not filepath:
            # Create ordered dict with needsManualReview after singer
            ordered_song = {}
            isPrivate_value = song.get("isPrivate")
            
            for key in song.keys():
                if key == "isPrivate":
                    continue  # Will add after playback
                ordered_song[key] = song[key]
                if key == "singer":
                    ordered_song["needsManualReview"] = True
                elif key == "playback" and isPrivate_value is not None:
                    ordered_song["isPrivate"] = isPrivate_value
            
            song.clear()
            song.update(ordered_song)
            stats["needs_manual_review"] += 1
            continue
        
        # Skip image files
        if is_image_file(filepath):
            # Add needsManualReview flag for image files
            ordered_song = {}
            isPrivate_value = song.get("isPrivate")
            
            for key in song.keys():
                if key == "isPrivate":
                    continue  # Will add after playback
                ordered_song[key] = song[key]
                if key == "singer":
                    ordered_song["needsManualReview"] = True
                elif key == "playback" and isPrivate_value is not None:
                    ordered_song["isPrivate"] = isPrivate_value
            
            song.clear()
            song.update(ordered_song)
            stats["image_files_skipped"] += 1
            stats["needs_manual_review"] += 1
            continue
        
        # Extract credits
        credits = extract_credits(filepath)
        
        # Build temp dict excluding fields we'll position explicitly
        temp_song = {}
        isPrivate_value = None
        
        for key in song.keys():
            if key == "isPrivate":
                isPrivate_value = song[key]
            elif key not in ["composers", "lyricists", "translators"]:
                temp_song[key] = song[key]
        
        # Reconstruct song dict with proper field order
        # Order: id, name, singer, composers, lyricists, translators, needsManualReview, unparsedString, playback, isPrivate, categoryIds, ...rest
        ordered_song = {}
        
        for key in temp_song.keys():
            ordered_song[key] = temp_song[key]
            
            # After "singer", insert the credit fields
            if key == "singer":
                if credits["composers"]:
                    ordered_song["composers"] = credits["composers"]
                if credits["lyricists"]:
                    ordered_song["lyricists"] = credits["lyricists"]
                if credits["translators"]:
                    ordered_song["translators"] = credits["translators"]
                    stats["with_translators"] += 1
                
                if credits["needsManualReview"]:
                    ordered_song["needsManualReview"] = True
                    stats["needs_manual_review"] += 1
                    if credits["unparsedString"]:
                        ordered_song["unparsedString"] = credits["unparsedString"]
                
                if credits["parsingUncertain"]:
                    ordered_song["parsingUncertain"] = True
                    stats["parsing_uncertain"] += 1
                    if credits["unparsedString"]:
                        ordered_song["unparsedString"] = credits["unparsedString"]
            
            # After "playback", insert isPrivate if it exists
            elif key == "playback" and isPrivate_value is not None:
                ordered_song["isPrivate"] = isPrivate_value
        
        # Update the song dictionary
        song.clear()
        song.update(ordered_song)
        
        if credits["composers"] or credits["lyricists"]:
            if not credits["needsManualReview"] and not credits["parsingUncertain"]:
                stats["successfully_parsed"] += 1
    
    # Write output JSON with custom formatting (arrays as one-liners)
    print(f"\nWriting enriched data to {output_path}...")
    
    # First, dump with standard indentation
    json_str = json.dumps(data, ensure_ascii=False, indent="\t")
    
    # Post-process to format specific array fields as one-liners
    # Match multi-line arrays for these specific fields
    def compress_array(match):
        field_name = match.group(1)
        array_content = match.group(2)
        # Remove newlines and extra whitespace from array content
        array_items = re.findall(r'"([^"]*)"', array_content)
        # Format as one-liner
        one_liner = ', '.join([f'"{item}"' for item in array_items])
        return f'"{field_name}": [{one_liner}]'
    
    # Pattern for composers, lyricists, translators, categoryIds arrays
    pattern = r'"(composers|lyricists|translators|categoryIds)":\s*\[\s*((?:"[^"]*"\s*,?\s*)*)\s*\]'
    json_str = re.sub(pattern, compress_array, json_str, flags=re.MULTILINE | re.DOTALL)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    # Print statistics
    print("\n" + "="*60)
    print("ENRICHMENT STATISTICS")
    print("="*60)
    print(f"Total songs:              {stats['total_songs']}")
    print(f"Successfully parsed:      {stats['successfully_parsed']}")
    print(f"With translators:         {stats['with_translators']}")
    print(f"Needs manual review:      {stats['needs_manual_review']}")
    print(f"Parsing uncertain:        {stats['parsing_uncertain']}")
    print(f"Image files skipped:      {stats['image_files_skipped']}")
    print(f"No lyrics URL:            {stats['no_lyrics_url']}")
    print("="*60)
    
    # Calculate percentage
    processed = stats['total_songs'] - stats['no_lyrics_url'] - stats['image_files_skipped']
    if processed > 0:
        success_rate = (stats['successfully_parsed'] / processed) * 100
        print(f"\nSuccess rate: {success_rate:.1f}% ({stats['successfully_parsed']}/{processed})")
    
    print(f"\nEnriched data saved to: {output_path}")


if __name__ == "__main__":
    input_file = "/Users/alonc/mcp-intro/songs/songs.json"
    output_file = "/Users/alonc/mcp-intro/songs/songs_enriched.json"
    
    enrich_songs(input_file, output_file)

