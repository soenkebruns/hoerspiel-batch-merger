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

def merge_mp3_files(file_list, output_path, progress_callback=None):
    """
    Merge MP3 files using ffmpeg concat demuxer
    
    Args:
        file_list: List of file_info dicts
        output_path: Path for output file
        progress_callback: Optional callback function(percent)
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
            '-c', 'copy',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
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