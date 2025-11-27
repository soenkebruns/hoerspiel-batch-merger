"""
File scanning and ID3 tag reading module
"""

from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import re

def scan_folder(folder_path, recursive=True):
    """
    Scan folder for MP3 files
    Returns list of Path objects
    """
    folder = Path(folder_path)
    if recursive:
        mp3_files = list(folder.rglob("*.mp3"))
    else:
        mp3_files = list(folder.glob("*.mp3"))
    
    # Read ID3 tags for each file
    files_with_tags = []
    for mp3_file in mp3_files:
        file_info = read_id3_tags(mp3_file)
        if file_info:
            files_with_tags.append(file_info)
    
    return files_with_tags

def read_id3_tags(file_path):
    """
    Read ID3 tags from MP3 file
    Returns dict with: path, album, artist, track, title, duration
    """
    try:
        audio = MP3(file_path)
        
        # Get duration in seconds
        duration = audio.info.length
        
        # Try to get ID3 tags
        tags = {}
        try:
            id3 = ID3(file_path)
            tags['album'] = str(id3.get('TALB', [''])[0]) or None
            tags['artist'] = str(id3.get('TPE1', [''])[0]) or None
            tags['title'] = str(id3.get('TIT2', [''])[0]) or None
            
            # Track number
            track_str = str(id3.get('TRCK', [''])[0])
            if track_str:
                # Handle formats like "1/12" or just "1"
                match = re.match(r'(\d+)', track_str)
                tags['track'] = int(match.group(1)) if match else None
            else:
                tags['track'] = None
        except:
            tags = {'album': None, 'artist': None, 'title': None, 'track': None}
        
        return {
            'path': Path(file_path),
            'album': tags['album'],
            'artist': tags['artist'],
            'title': tags['title'],
            'track': tags['track'],
            'duration': duration
        }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def group_by_album(files):
    """
    Group files by album tag
    Returns dict: {album_name: [file_info, ...]}
    """
    groups = {}
    for file_info in files:
        album = file_info.get('album') or 'Unknown Album'
        artist = file_info.get('artist') or 'Unknown Artist'
        key = f"{artist} - {album}"
        
        if key not in groups:
            groups[key] = []
        groups[key].append(file_info)
    
    return groups

def group_by_folder(files):
    """
    Group files by folder
    Returns dict: {folder_path: [file_info, ...]}
    """
    groups = {}
    for file_info in files:
        folder = str(file_info['path'].parent)
        
        if folder not in groups:
            groups[folder] = []
        groups[folder].append(file_info)
    
    return groups

def sort_files(files):
    """
    Sort files by track number (if available) or filename
    """
    def sort_key(file_info):
        # Primary: track number
        if file_info.get('track') is not None:
            return (0, file_info['track'], '')
        # Fallback: filename alphabetically
        return (1, 0, file_info['path'].name.lower())
    
    return sorted(files, key=sort_key)