"""
Chapter marker and tag writing module
"""

from mutagen.id3 import ID3, CTOC, CHAP, TIT2, TPE1, TALB, TCMP, CTOCFlags
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus


def add_chapters_and_tags(audio_path, chapters_data, metadata=None, output_format='mp3'):
    """
    Add chapter markers and tags to audio file based on format
    
    Args:
        audio_path: Path to audio file
        chapters_data: List of dicts with: title, start_ms, duration_ms
        metadata: Optional dict with 'artist', 'album', and 'compilation' keys
        output_format: Format of the output file ('mp3', 'flac', 'opus')
    """
    if output_format == 'mp3':
        _add_chapters_to_mp3(audio_path, chapters_data, metadata)
    elif output_format == 'flac':
        _add_tags_to_flac(audio_path, chapters_data, metadata)
    elif output_format == 'opus':
        _add_tags_to_opus(audio_path, chapters_data, metadata)
    else:
        raise ValueError(f"Unsupported format: {output_format}")


def _add_chapters_to_mp3(mp3_path, chapters_data, metadata=None):
    """
    Add chapter markers to MP3 file using ID3v2 CHAP frames
    
    Args:
        mp3_path: Path to MP3 file
        chapters_data: List of dicts with: title, start_ms, duration_ms
        metadata: Optional dict with 'artist', 'album', and 'compilation' keys
    """
    try:
        audio = MP3(mp3_path, ID3=ID3)
        
        # Remove existing chapter frames
        audio.tags.delall('CTOC')
        audio.tags.delall('CHAP')
        
        # Add CHAP frames
        chapter_ids = []
        for idx, chapter in enumerate(chapters_data):
            chap_id = f"chp{idx}"
            chapter_ids.append(chap_id)
            
            start_time = chapter['start_ms']
            end_time = start_time + chapter['duration_ms']
            
            # Create CHAP frame
            chap = CHAP(
                element_id=chap_id,
                start_time=start_time,
                end_time=end_time,
                sub_frames=[
                    TIT2(encoding=3, text=chapter['title'])
                ]
            )
            audio.tags.add(chap)
        
        # Add CTOC (Table of Contents)
        ctoc = CTOC(
            element_id='toc',
            flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
            child_element_ids=chapter_ids,
            sub_frames=[
                TIT2(encoding=3, text='Table of Contents')
            ]
        )
        audio.tags.add(ctoc)
        
        # Add metadata tags if provided
        if metadata:
            # Artist tag
            if metadata.get('artist'):
                audio.tags.delall('TPE1')
                audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
            
            # Album tag
            if metadata.get('album'):
                audio.tags.delall('TALB')
                audio.tags.add(TALB(encoding=3, text=metadata['album']))
            
            # Compilation flag - explicitly set or clear
            audio.tags.delall('TCMP')
            if metadata.get('compilation'):
                audio.tags.add(TCMP(encoding=3, text='1'))
        
        audio.save()
        
    except Exception as e:
        raise Exception(f"Error adding chapters: {str(e)}")


def _add_tags_to_flac(flac_path, chapters_data, metadata=None):
    """
    Add Vorbis Comments tags to FLAC file
    
    Note: FLAC does not have a standardized chapter format like ID3.
    We store chapter info in custom tags for reference.
    
    Args:
        flac_path: Path to FLAC file
        chapters_data: List of dicts with: title, start_ms, duration_ms
        metadata: Optional dict with 'artist', 'album', and 'compilation' keys
    """
    try:
        audio = FLAC(flac_path)
        
        # Add metadata tags if provided
        if metadata:
            if metadata.get('artist'):
                audio['ARTIST'] = metadata['artist']
            if metadata.get('album'):
                audio['ALBUM'] = metadata['album']
            if metadata.get('compilation'):
                audio['COMPILATION'] = '1'
        
        # Store chapter information in custom tags
        # Format: CHAPTER001=00:00:00.000, CHAPTER001NAME=Title
        for idx, chapter in enumerate(chapters_data):
            chapter_num = f"{idx + 1:03d}"
            start_ms = chapter['start_ms']
            
            # Convert to timestamp format HH:MM:SS.mmm
            hours = start_ms // 3600000
            minutes = (start_ms % 3600000) // 60000
            seconds = (start_ms % 60000) // 1000
            milliseconds = start_ms % 1000
            
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            audio[f'CHAPTER{chapter_num}'] = timestamp
            audio[f'CHAPTER{chapter_num}NAME'] = chapter['title']
        
        audio.save()
        
    except Exception as e:
        raise Exception(f"Error adding tags to FLAC: {str(e)}")


def _add_tags_to_opus(opus_path, chapters_data, metadata=None):
    """
    Add Vorbis Comments tags to Opus file
    
    Note: Opus uses the same Vorbis Comments format as FLAC.
    
    Args:
        opus_path: Path to Opus file
        chapters_data: List of dicts with: title, start_ms, duration_ms
        metadata: Optional dict with 'artist', 'album', and 'compilation' keys
    """
    try:
        audio = OggOpus(opus_path)
        
        # Add metadata tags if provided
        if metadata:
            if metadata.get('artist'):
                audio['ARTIST'] = metadata['artist']
            if metadata.get('album'):
                audio['ALBUM'] = metadata['album']
            if metadata.get('compilation'):
                audio['COMPILATION'] = '1'
        
        # Store chapter information in custom tags
        # Format: CHAPTER001=00:00:00.000, CHAPTER001NAME=Title
        for idx, chapter in enumerate(chapters_data):
            chapter_num = f"{idx + 1:03d}"
            start_ms = chapter['start_ms']
            
            # Convert to timestamp format HH:MM:SS.mmm
            hours = start_ms // 3600000
            minutes = (start_ms % 3600000) // 60000
            seconds = (start_ms % 60000) // 1000
            milliseconds = start_ms % 1000
            
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            audio[f'CHAPTER{chapter_num}'] = timestamp
            audio[f'CHAPTER{chapter_num}NAME'] = chapter['title']
        
        audio.save()
        
    except Exception as e:
        raise Exception(f"Error adding tags to Opus: {str(e)}")


# Backward compatibility alias
def add_chapters_to_mp3(mp3_path, chapters_data, metadata=None):
    """
    Add chapter markers to MP3 file (deprecated, use add_chapters_and_tags)
    """
    return add_chapters_and_tags(mp3_path, chapters_data, metadata, 'mp3')
