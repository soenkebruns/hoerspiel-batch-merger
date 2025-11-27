# MP3 Album Merger

A desktop application for merging MP3 files (especially audiobooks and Hörspiele) with automatic chapter markers.

## Features

- 🎵 **Recursive Folder Scanning** - Automatically finds all MP3 files in subdirectories
- 📚 **Smart Grouping** - Group files by Album Tag or Folder structure
- 🔢 **Intelligent Sorting** - Sorts by track number (ID3) or filename
- ✅ **Manual Selection** - Choose exactly which files to merge
- ⚡ **Fast Merging** - Uses FFmpeg for quick, lossless merging
- 🎯 **Chapter Markers** - Automatically adds ID3 chapter markers (CHAP frames)
- 💾 **Clean Output** - Creates `Artist-AlbumName_merged.mp3` files
- 📊 **Real-time Progress Bar** - Shows encoding progress during merge operations
- 🏷️ **Tag Editor Dialog** - Edit metadata (Artist, Album, Year, Genre, etc.) before merging
- 🎨 **Album Art Support** - Automatically extracts, displays, and embeds album art

## Installation

### Prerequisites

1. **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for merging MP3 files

#### Installing FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Install Application

1. Clone the repository:
```bash
git clone https://github.com/soenkebruns/hoerspiel-batch-merger.git
cd hoerspiel-batch-merger
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. **Select Folder** - Click "Select Folder..." and choose a folder containing MP3 files

3. **Choose Grouping Mode:**
   - **By Album Tag** - Groups MP3s with the same Album metadata
   - **By Folder** - Groups MP3s in the same directory

4. **Review Groups** - The application shows:
   - Album/Group name
   - Number of files
   - Total duration
   - Individual tracks

5. **Select Files to Merge:**
   - By default, all files are selected (☑)
   - Click on any group or file to toggle selection (☐)
   - Space bar also toggles selection

6. **Merge** - Click "Merge Selected Albums" to start

7. **Edit Tags** - A Tag Editor dialog appears with:
   - Auto-detected Artist, Album, Year, Genre
   - Editable fields for all metadata
   - Album art preview (extracted from source files)
   - Options to change or remove album art
   - Click "Start Merge" to proceed or "Cancel" to abort

8. **Watch Progress** - A real-time progress bar shows:
   - Current group being processed
   - Encoding percentage
   - Track count information

9. **Output** - Merged files are saved in the same folder as source files with the format:
   ```
   Artist-AlbumName_merged.mp3
   ```

## Chapter Markers

The application automatically adds ID3v2 chapter markers (CHAP frames) to merged files:
- Each original track becomes a chapter
- Chapter title = ID3 Title tag (or filename if no tag)
- Chapter start time = exact position in merged file

### Compatible Players

Chapter markers work in:
- VLC Media Player
- foobar2000
- MusicBee
- Most modern podcast apps

## Troubleshooting

### "FFmpeg Not Found" Error
- Make sure FFmpeg is installed and in your system PATH
- Test by running `ffmpeg -version` in terminal/command prompt

### No Files Found
- Ensure the folder contains .mp3 files
- Check that files aren't corrupted
- Try enabling "Show hidden files" in your file manager

### Missing Chapter Markers
- Verify that your media player supports ID3v2 CHAP frames
- Try opening the file in VLC to test

### Merge Fails
- Check that you have write permissions in the output folder
- Ensure enough disk space is available
- Verify that source files aren't corrupted

## Technical Details

### File Structure
```
hoerspiel-batch-merger/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore
└── src/
    ├── __init__.py
    ├── gui.py          # Tkinter GUI
    ├── scanner.py      # MP3 scanning & ID3 reading
    ├── merger.py       # FFmpeg integration
    ├── chapters.py     # Chapter marker creation
    └── utils.py        # Helper functions
```

### Dependencies
- **mutagen** - ID3 tag reading/writing and chapter markers
- **Pillow** - Album art display in Tag Editor dialog
- **tkinter** - GUI (included with Python)
- **FFmpeg** - External tool for MP3 merging

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created by @soenkebruns