"""
MP3 merging module using ffmpeg
"""

import subprocess
import shutil
from pathlib import Path
import tempfile

def check_ffmpeg():
    """Check if ffmpeg is available in PATH"""
    return shutil.which('ffmpeg') is not None

def merge_mp3_files(file_list, output_path, progress_callback=None, bitrate=None):
    """
    Merge MP3 files using ffmpeg concat demuxer
    
    Args:
        file_list: List of file_info dicts
        output_path: Path for output file
        progress_callback: Optional callback function(percent)
        bitrate: Optional target bitrate (e.g., '128k', '192k'). If None, uses copy codec.
    """
    if not file_list:
        raise ValueError("No files to merge")
    
    # Create temporary concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        concat_file = Path(f.name)
        for file_info in file_list:
            # Escape single quotes for ffmpeg
            file_path = str(file_info['path']).replace("'", r"'\''")
            f.write(f"file '{file_path}'\n")
    
    try:
        # Run ffmpeg
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
        ]
        
        # Add codec options based on bitrate
        if bitrate:
            cmd.extend(['-codec:a', 'libmp3lame', '-b:a', bitrate])
        else:
            cmd.extend(['-c', 'copy'])
        
        cmd.extend(['-y', str(output_path)])  # Overwrite output file
        
        # Execute ffmpeg
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {process.stderr}")
        
        if progress_callback:
            progress_callback(100)
            
    finally:
        # Clean up temp file
        concat_file.unlink(missing_ok=True)


def get_merged_metadata(file_list):
    """
    Analyze source files to determine merged metadata.
    
    Args:
        file_list: List of file_info dicts with 'artist' and 'album' keys
        
    Returns:
        dict with 'artist', 'album', and 'compilation' keys
        
    Logic:
        - Artist: If all files have the same artist, use that artist.
          If files have different artists, use 'Various Artists' and set compilation=True.
          If no artist tags exist, use 'Unknown Artist'.
        - Album: If all files have the same album, use that album.
          If files have different albums, use 'Compilation'.
          If no album tags exist, use 'Unknown Album'.
        - compilation: True when multiple different artists are detected, False otherwise.
    """
    if not file_list:
        return {'artist': 'Unknown Artist', 'album': 'Unknown Album', 'compilation': False}
    
    # Collect unique artists and albums (excluding None values)
    artists = set()
    albums = set()
    
    for file_info in file_list:
        artist = file_info.get('artist')
        album = file_info.get('album')
        if artist:
            artists.add(artist)
        if album:
            albums.add(album)
    
    # Determine artist
    if len(artists) == 0:
        result_artist = 'Unknown Artist'
        compilation = False
    elif len(artists) == 1:
        result_artist = artists.pop()
        compilation = False
    else:
        result_artist = 'Various Artists'
        compilation = True
    
    # Determine album
    if len(albums) == 0:
        result_album = 'Unknown Album'
    elif len(albums) == 1:
        result_album = albums.pop()
    else:
        result_album = 'Compilation'
    
    return {
        'artist': result_artist,
        'album': result_album,
        'compilation': compilation
    }