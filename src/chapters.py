"""
ID3 Chapter marker module
"""

from mutagen.id3 import ID3, CTOC, CHAP, TIT2, TPE1, TALB, TCMP, CTOCFlags
from mutagen.mp3 import MP3


def add_chapters_to_mp3(mp3_path, chapters_data, metadata=None):
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
            
            # Compilation flag
            if metadata.get('compilation'):
                audio.tags.delall('TCMP')
                audio.tags.add(TCMP(encoding=3, text='1'))
        
        audio.save()
        
    except Exception as e:
        raise Exception(f"Error adding chapters: {str(e)}")
