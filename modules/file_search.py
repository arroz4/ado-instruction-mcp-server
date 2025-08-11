"""
File search functionality for finding images and text files on the PC

This module provides tools to locate files for processing by the ADO Instructions system
without requiring users to know exact file paths.
"""

import os
import glob
import json
from pathlib import Path
from typing import Dict, List, Any


def search_files_for_processing(
    search_pattern: str = "",
    file_types: str = "images,text", 
    search_locations: str = "desktop,documents,downloads"
) -> Dict[str, Any]:
    """
    Search for image or text files on the PC that can be processed by the ADO system.
    
    This function helps users locate files for processing without knowing exact paths.
    Searches common locations and returns a list of matching files with their full paths.
    
    Args:
        search_pattern: Optional filename pattern to search for (e.g., "wireframe", "meeting", "*.png")
        file_types: Comma-separated list of file types to search for. Options: "images", "text", "all"
        search_locations: Comma-separated list of locations to search. Options: "desktop", "documents", "downloads", "pictures", "current", "all"
        
    Returns:
        Dictionary with found files categorized by type and location
    """
    
    # Define file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']
    text_extensions = ['.txt', '.md', '.doc', '.docx', '.pdf', '.rtf', '.csv']
    
    # Parse file types to search for
    search_file_types = [ft.strip().lower() for ft in file_types.split(',')]
    extensions_to_search = []
    
    if 'all' in search_file_types:
        extensions_to_search = image_extensions + text_extensions
    else:
        if 'images' in search_file_types:
            extensions_to_search.extend(image_extensions)
        if 'text' in search_file_types:
            extensions_to_search.extend(text_extensions)
    
    # Define search locations
    locations = {}
    user_home = Path.home()
    
    possible_locations = {
        'desktop': user_home / 'Desktop',
        'documents': user_home / 'Documents', 
        'downloads': user_home / 'Downloads',
        'pictures': user_home / 'Pictures',
        'current': Path.cwd()
    }
    
    # Parse search locations
    search_locs = [loc.strip().lower() for loc in search_locations.split(',')]
    
    if 'all' in search_locs:
        locations = possible_locations
    else:
        for loc in search_locs:
            if loc in possible_locations:
                locations[loc] = possible_locations[loc]
    
    # Search for files
    found_files = {
        'images': [],
        'text_files': [],
        'search_summary': {
            'pattern': search_pattern,
            'locations_searched': list(locations.keys()),
            'file_types': search_file_types,
            'total_found': 0
        }
    }
    
    for location_name, location_path in locations.items():
        if not location_path.exists():
            continue
            
        try:
            # Search recursively in the location
            for ext in extensions_to_search:
                if search_pattern:
                    # If pattern specified, use it
                    if '*' in search_pattern or '?' in search_pattern:
                        pattern = f"**/{search_pattern}"
                    else:
                        pattern = f"**/*{search_pattern}*{ext}"
                else:
                    # Search for all files with the extension
                    pattern = f"**/*{ext}"
                
                try:
                    matches = list(location_path.glob(pattern))
                    
                    for match in matches:
                        if match.is_file():
                            try:
                                file_info = {
                                    'name': match.name,
                                    'path': str(match),
                                    'location': location_name,
                                    'size_mb': round(match.stat().st_size / (1024 * 1024), 2),
                                    'extension': match.suffix.lower()
                                }
                                
                                # Categorize file
                                if match.suffix.lower() in image_extensions:
                                    found_files['images'].append(file_info)
                                elif match.suffix.lower() in text_extensions:
                                    found_files['text_files'].append(file_info)
                                    
                            except (OSError, PermissionError):
                                # Skip files that can't be accessed (e.g., long paths, permission issues)
                                continue
                                
                except (OSError, PermissionError):
                    # Skip patterns that cause issues (e.g., path too long)
                    continue
        
        except (PermissionError, OSError):
            # Skip locations we can't access
            continue
    
    # Update summary
    found_files['search_summary']['total_found'] = len(found_files['images']) + len(found_files['text_files'])
    
    # Sort files by name for better presentation
    found_files['images'].sort(key=lambda x: x['name'].lower())
    found_files['text_files'].sort(key=lambda x: x['name'].lower())
    
    return found_files


def format_search_results_for_display(search_results: Dict[str, Any]) -> str:
    """
    Format search results into a user-friendly display string
    
    Args:
        search_results: Results from search_files_for_processing function
        
    Returns:
        Formatted string suitable for display to users
    """
    if not search_results or search_results.get('search_summary', {}).get('total_found', 0) == 0:
        return """
🔍 No files found matching your criteria

💡 Suggestions:
   • Try a broader search pattern
   • Check if files are in the searched locations  
   • Use "all" for file_types or search_locations to expand search
        """.strip()
    
    summary = search_results['search_summary']
    lines = []
    
    lines.append("🔍 FILE SEARCH RESULTS")
    lines.append("=" * 40)
    lines.append(f"🎯 Pattern: '{summary['pattern']}' (empty = all files)")
    lines.append(f"📁 Locations: {', '.join(summary['locations_searched'])}")
    lines.append(f"📄 File types: {', '.join(summary['file_types'])}")
    lines.append(f"📊 Total found: {summary['total_found']} files")
    lines.append("")
    
    # Show images
    if search_results.get('images'):
        lines.append(f"🖼️  IMAGES ({len(search_results['images'])}):")
        for img in search_results['images'][:10]:  # Show first 10
            lines.append(f"   • {img['name']} ({img['size_mb']} MB) - {img['location']}")
            lines.append(f"     📂 {img['path']}")
        if len(search_results['images']) > 10:
            lines.append(f"   ... and {len(search_results['images']) - 10} more images")
        lines.append("")
    
    # Show text files
    if search_results.get('text_files'):
        lines.append(f"📝 TEXT FILES ({len(search_results['text_files'])}):")
        for txt in search_results['text_files'][:10]:  # Show first 10
            lines.append(f"   • {txt['name']} ({txt['size_mb']} MB) - {txt['location']}")
            lines.append(f"     📂 {txt['path']}")
        if len(search_results['text_files']) > 10:
            lines.append(f"   ... and {len(search_results['text_files']) - 10} more text files")
        lines.append("")
    
    lines.append("💡 Next steps:")
    lines.append("   1. Copy the full path of the file you want to process")
    lines.append("   2. Use load_image_from_file() with the file path")
    lines.append("   3. Process with process_meeting_transcript()")
    
    return "\n".join(lines)


def get_search_usage_examples() -> str:
    """
    Get usage examples for the file search functionality
    
    Returns:
        String with usage examples and tips
    """
    return """
🔍 FILE SEARCH USAGE EXAMPLES

📋 Basic Searches:
   • search_files_for_processing() - Find all images and text files in common locations
   • search_files_for_processing("", "images", "desktop") - Images on desktop only
   • search_files_for_processing("", "text", "documents") - Text files in documents

🎯 Pattern Searches:
   • search_files_for_processing("wireframe", "images", "all") - Wireframe images everywhere
   • search_files_for_processing("meeting", "text", "documents,desktop") - Meeting notes
   • search_files_for_processing("*.png", "images", "current") - PNG files in current folder

📁 Location Options:
   • "desktop" - User's desktop folder
   • "documents" - User's documents folder
   • "downloads" - User's downloads folder
   • "pictures" - User's pictures folder
   • "current" - Current working directory
   • "all" - Search all above locations

📄 File Type Options:
   • "images" - .jpg, .png, .gif, .bmp, .webp, .svg, .tiff
   • "text" - .txt, .md, .doc, .docx, .pdf, .rtf, .csv
   • "all" - Both images and text files

🚀 Integration Workflow:
   1. Search: search_files_for_processing("meeting", "text", "desktop")
   2. Load text file content
   3. Process: process_meeting_transcript(text_content)
   4. Review: format_ado_instructions_summary(result)
    """.strip()
