"""
File scanning and ID3 tag reading module
"""

from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
import re
import base64

# Supported audio file extensions
SUPPORTED_EXTENSIONS = ['*.mp3', '*.flac', '*.opus']


def scan_folder(folder_path, recursive=True):
    """
    Scan folder for audio files (MP3, FLAC, Opus)
    Returns list of file_info dicts
    """
    folder = Path(folder_path)
    audio_files = []
    
    for ext in SUPPORTED_EXTENSIONS:
        if recursive:
            audio_files.extend(folder.rglob(ext))
        else:
            audio_files.extend(folder.glob(ext))
    
    # Read tags for each file
    files_with_tags = []
    for audio_file in audio_files:
        file_info = read_id3_tags(audio_file)
        if file_info:
            files_with_tags.append(file_info)
    
    return files_with_tags


def read_id3_tags(file_path):
    """
    Read tags from audio file (MP3, FLAC, or Opus)
    Returns dict with: path, album, artist, track, title, duration, format
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.mp3':
            return _read_mp3_tags(file_path)
        elif suffix == '.flac':
            return _read_flac_tags(file_path)
        elif suffix == '.opus':
            return _read_opus_tags(file_path)
        else:
            print(f"Unsupported format: {file_path}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def _read_mp3_tags(file_path):
    """Read tags from MP3 file using ID3"""
    audio = MP3(file_path)
    duration = audio.info.length
    
    tags = {}
    try:
        id3 = ID3(file_path)
        tags['album'] = str(id3.get('TALB', [''])[0]) or None
        tags['artist'] = str(id3.get('TPE1', [''])[0]) or None
        tags['title'] = str(id3.get('TIT2', [''])[0]) or None
        
        # Track number
        track_str = str(id3.get('TRCK', [''])[0])
        if track_str:
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
        'duration': duration,
        'format': 'mp3'
    }


def _read_flac_tags(file_path):
    """Read tags from FLAC file using Vorbis Comments"""
    audio = FLAC(file_path)
    duration = audio.info.length
    
    tags = {}
    try:
        # FLAC uses Vorbis Comments (case-insensitive keys)
        tags['album'] = audio.get('album', [None])[0]
        tags['artist'] = audio.get('artist', [None])[0]
        tags['title'] = audio.get('title', [None])[0]
        
        # Track number
        track_str = audio.get('tracknumber', [''])[0]
        if track_str:
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
        'duration': duration,
        'format': 'flac'
    }


def _read_opus_tags(file_path):
    """Read tags from Opus file using Vorbis Comments"""
    audio = OggOpus(file_path)
    duration = audio.info.length
    
    tags = {}
    try:
        # Opus uses Vorbis Comments (case-insensitive keys)
        tags['album'] = audio.get('album', [None])[0]
        tags['artist'] = audio.get('artist', [None])[0]
        tags['title'] = audio.get('title', [None])[0]
        
        # Track number
        track_str = audio.get('tracknumber', [''])[0]
        if track_str:
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
        'duration': duration,
        'format': 'opus'
    }

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


def extract_album_art(file_path):
    """
    Extract album art from audio file (MP3, FLAC, or Opus)
    
    Args:
        file_path: Path to audio file
        
    Returns:
        dict with 'data' (bytes), 'mime' (str), and 'desc' (str)
        or None if no album art found
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.mp3':
            return _extract_mp3_album_art(file_path)
        elif suffix == '.flac':
            return _extract_flac_album_art(file_path)
        elif suffix == '.opus':
            return _extract_opus_album_art(file_path)
        else:
            return None
    except Exception as e:
        print(f"Error extracting album art from {file_path}: {e}")
        return None


def _extract_mp3_album_art(file_path):
    """Extract album art from MP3 file using APIC frames"""
    try:
        id3 = ID3(file_path)
        
        # Look for APIC (Attached Picture) frames
        for key in id3.keys():
            if key.startswith('APIC'):
                apic = id3[key]
                return {
                    'data': apic.data,
                    'mime': apic.mime,
                    'desc': apic.desc or 'Cover'
                }
        return None
    except Exception:
        return None


def _extract_flac_album_art(file_path):
    """Extract album art from FLAC file using pictures attribute"""
    try:
        audio = FLAC(file_path)
        pictures = audio.pictures
        
        if pictures:
            # Prefer front cover (type 3), otherwise use first picture
            for pic in pictures:
                if pic.type == 3:  # Front cover
                    return {
                        'data': pic.data,
                        'mime': pic.mime,
                        'desc': pic.desc or 'Front cover'
                    }
            # Fall back to first picture
            pic = pictures[0]
            return {
                'data': pic.data,
                'mime': pic.mime,
                'desc': pic.desc or 'Cover'
            }
        return None
    except Exception:
        return None


def _extract_opus_album_art(file_path):
    """Extract album art from Opus file using METADATA_BLOCK_PICTURE"""
    try:
        from mutagen.flac import Picture
        
        audio = OggOpus(file_path)
        
        # Opus stores pictures as base64-encoded METADATA_BLOCK_PICTURE
        pictures_data = audio.get('METADATA_BLOCK_PICTURE', [])
        
        for pic_data in pictures_data:
            try:
                # Decode base64 and parse as FLAC Picture
                picture = Picture(base64.b64decode(pic_data))
                if picture.type == 3:  # Front cover
                    return {
                        'data': picture.data,
                        'mime': picture.mime,
                        'desc': picture.desc or 'Front cover'
                    }
            except Exception:
                continue
        
        # Fall back to first picture if no front cover
        for pic_data in pictures_data:
            try:
                picture = Picture(base64.b64decode(pic_data))
                return {
                    'data': picture.data,
                    'mime': picture.mime,
                    'desc': picture.desc or 'Cover'
                }
            except Exception:
                continue
        
        return None
    except Exception:
        return None