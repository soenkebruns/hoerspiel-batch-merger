"""
Tkinter GUI for Audio Album Merger
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from .scanner import scan_folder, group_by_album, group_by_folder, sort_files
from .merger import check_ffmpeg, merge_audio_files, get_merged_metadata
from .chapters import add_chapters_and_tags
from .utils import format_duration, sanitize_filename


# Output format options
FORMAT_OPTIONS = [
    ("MP3", "mp3"),
    ("FLAC", "flac"),
    ("Opus", "opus"),
]

# Bitrate options for each format
BITRATE_OPTIONS = {
    'mp3': [
        ("Original (no re-encoding)", None),
        ("64 kbps", "64k"),
        ("128 kbps", "128k"),
        ("192 kbps", "192k"),
        ("256 kbps", "256k"),
        ("320 kbps", "320k"),
    ],
    'flac': [
        ("Compression 0 (fastest)", "0"),
        ("Compression 1", "1"),
        ("Compression 2", "2"),
        ("Compression 3", "3"),
        ("Compression 4", "4"),
        ("Compression 5 (default)", "5"),
        ("Compression 6", "6"),
        ("Compression 7", "7"),
        ("Compression 8 (best)", "8"),
    ],
    'opus': [
        ("64 kbps", "64k"),
        ("96 kbps", "96k"),
        ("128 kbps (default)", "128k"),
        ("192 kbps", "192k"),
        ("256 kbps", "256k"),
    ],
}

# Lookup dictionaries for format and bitrate values
FORMAT_LOOKUP = {label: value for label, value in FORMAT_OPTIONS}
FORMAT_REVERSE_LOOKUP = {value: label for label, value in FORMAT_OPTIONS}


class MP3AlbumMergerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Album Merger")
        self.root.geometry("900x700")
        
        self.selected_folder = None
        self.all_files = []
        self.groups = {}
        self.grouping_mode = tk.StringVar(value="album")
        self.selected_format = tk.StringVar(value=FORMAT_OPTIONS[0][0])
        self.selected_bitrate = tk.StringVar()
        
        self.setup_ui()
        self._update_bitrate_options()  # Initialize bitrate options
        
        # Check ffmpeg on startup
        if not check_ffmpeg():
            messagebox.showwarning(
                "FFmpeg Not Found",
                "FFmpeg is not installed or not in PATH.\n"
                "Please install FFmpeg to merge audio files.\n\n"
                "Visit: https://ffmpeg.org/download.html"
            )
    
    def setup_ui(self):
        """Setup the user interface"""
        # Top frame - folder selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Folder:").pack(side=tk.LEFT)
        self.folder_label = ttk.Label(top_frame, text="No folder selected", foreground="gray")
        self.folder_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Button(top_frame, text="Select Folder...", command=self.select_folder).pack(side=tk.RIGHT)
        
        # Grouping mode frame
        mode_frame = ttk.LabelFrame(self.root, text="Grouping Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Radiobutton(
            mode_frame, 
            text="By Album Tag", 
            variable=self.grouping_mode, 
            value="album",
            command=self.regroup_files
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, 
            text="By Folder", 
            variable=self.grouping_mode, 
            value="folder",
            command=self.regroup_files
        ).pack(side=tk.LEFT, padx=5)
        
        # Output settings frame
        output_frame = ttk.LabelFrame(self.root, text="Output Settings", padding="10")
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Format selection
        ttk.Label(output_frame, text="Format:").pack(side=tk.LEFT, padx=5)
        self.format_combo = ttk.Combobox(
            output_frame,
            textvariable=self.selected_format,
            values=[opt[0] for opt in FORMAT_OPTIONS],
            state="readonly",
            width=10
        )
        self.format_combo.pack(side=tk.LEFT, padx=5)
        self.format_combo.bind('<<ComboboxSelected>>', self._on_format_change)
        
        # Separator
        ttk.Separator(output_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        # Bitrate selection
        ttk.Label(output_frame, text="Quality:").pack(side=tk.LEFT, padx=5)
        self.bitrate_combo = ttk.Combobox(
            output_frame,
            textvariable=self.selected_bitrate,
            state="readonly",
            width=25
        )
        self.bitrate_combo.pack(side=tk.LEFT, padx=5)
        
        # Main treeview
        tree_frame = ttk.Frame(self.root, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("files", "duration"),
            yscrollcommand=scrollbar.set,
            selectmode="extended"
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Columns
        self.tree.heading("#0", text="Album / Track")
        self.tree.heading("files", text="Files")
        self.tree.heading("duration", text="Duration")
        
        self.tree.column("#0", width=500)
        self.tree.column("files", width=80, anchor="center")
        self.tree.column("duration", width=120, anchor="center")
        
        # Bind space key for toggle
        self.tree.bind("<space>", self.toggle_selection)
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Bottom frame - actions
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(bottom_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Button(
            bottom_frame, 
            text="Merge Selected Albums", 
            command=self.merge_selected
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            bottom_frame, 
            text="Select All", 
            command=self.select_all
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            bottom_frame, 
            text="Deselect All", 
            command=self.deselect_all
        ).pack(side=tk.RIGHT, padx=5)
    
    def _on_format_change(self, event=None):
        """Handle format selection change"""
        self._update_bitrate_options()
    
    def _update_bitrate_options(self):
        """Update bitrate dropdown options based on selected format"""
        output_format = self._get_selected_format()
        options = BITRATE_OPTIONS.get(output_format, BITRATE_OPTIONS['mp3'])
        
        self.bitrate_combo['values'] = [opt[0] for opt in options]
        
        # Select default option
        if output_format == 'mp3':
            self.selected_bitrate.set(options[0][0])  # Original (no re-encoding)
        elif output_format == 'flac':
            self.selected_bitrate.set(options[5][0])  # Compression 5 (default)
        elif output_format == 'opus':
            self.selected_bitrate.set(options[2][0])  # 128 kbps (default)
    
    def select_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = Path(folder)
            self.folder_label.config(text=str(self.selected_folder), foreground="black")
            self.scan_folder()
    
    def scan_folder(self):
        """Scan folder for audio files"""
        if not self.selected_folder:
            return
        
        self.status_label.config(text="Scanning folder...")
        self.root.update()
        
        try:
            self.all_files = scan_folder(self.selected_folder)
            
            if not self.all_files:
                messagebox.showinfo("No Files", "No audio files found in the selected folder.\n(Supported: MP3, FLAC, Opus)")
                self.status_label.config(text="No files found")
                return
            
            self.regroup_files()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning folder:\n{str(e)}")
            self.status_label.config(text="Error scanning")
    
    def regroup_files(self):
        """Regroup files based on selected mode"""
        if not self.all_files:
            return
        
        mode = self.grouping_mode.get()
        
        if mode == "album":
            self.groups = group_by_album(self.all_files)
        else:
            self.groups = group_by_folder(self.all_files)
        
        self.populate_tree()
    
    def populate_tree(self):
        """Populate treeview with groups and files"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add groups
        for group_name, files in self.groups.items():
            files_sorted = sort_files(files)
            total_duration = sum(f['duration'] for f in files_sorted)
            
            # Add group
            group_id = self.tree.insert(
                "",
                "end",
                text=f"☑ {group_name}",
                values=(len(files_sorted), format_duration(total_duration)),
                tags=("checked", "group")
            )
            
            # Add files
            for file_info in files_sorted:
                title = file_info.get('title') or file_info['path'].name
                track_num = file_info.get('track')
                if track_num:
                    title = f"{track_num:02d}. {title}"
                
                self.tree.insert(
                    group_id,
                    "end",
                    text=f"☑ {title}",
                    values=("", format_duration(file_info['duration'])),
                    tags=("checked", "file")
                )
        
        self.status_label.config(text=f"Found {len(self.groups)} groups with {len(self.all_files)} files")
    
    def on_tree_click(self, event):
        """Handle tree click to toggle selection"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                self.toggle_item(item)
    
    def toggle_selection(self, event):
        """Toggle selection on space key"""
        selection = self.tree.selection()
        for item in selection:
            self.toggle_item(item)
    
    def toggle_item(self, item):
        """Toggle checkbox for item"""
        tags = self.tree.item(item, "tags")
        text = self.tree.item(item, "text")
        
        if "checked" in tags:
            # Uncheck
            new_text = text.replace("☑", "☐")
            new_tags = [t for t in tags if t != "checked"]
            new_tags.append("unchecked")
        else:
            # Check
            new_text = text.replace("☐", "☑")
            new_tags = [t for t in tags if t != "unchecked"]
            new_tags.append("checked")
        
        self.tree.item(item, text=new_text, tags=new_tags)
        
        # If group, toggle all children
        if "group" in tags:
            for child in self.tree.get_children(item):
                child_text = self.tree.item(child, "text")
                child_tags = self.tree.item(child, "tags")
                
                if "checked" in tags:
                    # Parent was checked, uncheck children
                    child_text = child_text.replace("☑", "☐")
                    child_tags = [t for t in child_tags if t != "checked"]
                    child_tags.append("unchecked")
                else:
                    # Parent was unchecked, check children
                    child_text = child_text.replace("☐", "☑")
                    child_tags = [t for t in child_tags if t != "unchecked"]
                    child_tags.append("checked")
                
                self.tree.item(child, text=child_text, tags=child_tags)
    
    def select_all(self):
        """Select all items"""
        for item in self.tree.get_children():
            self.check_item_recursive(item, True)
    
    def deselect_all(self):
        """Deselect all items"""
        for item in self.tree.get_children():
            self.check_item_recursive(item, False)
    
    def check_item_recursive(self, item, checked):
        """Recursively check/uncheck item and children"""
        text = self.tree.item(item, "text")
        tags = list(self.tree.item(item, "tags"))
        
        if checked:
            text = text.replace("☐", "☑")
            if "unchecked" in tags:
                tags.remove("unchecked")
            if "checked" not in tags:
                tags.append("checked")
        else:
            text = text.replace("☑", "☐")
            if "checked" in tags:
                tags.remove("checked")
            if "unchecked" not in tags:
                tags.append("unchecked")
        
        self.tree.item(item, text=text, tags=tags)
        
        # Recurse children
        for child in self.tree.get_children(item):
            self.check_item_recursive(child, checked)
    
    def merge_selected(self):
        """Merge selected albums"""
        # Get selected groups
        selected_groups = []
        
        for group_item in self.tree.get_children():
            tags = self.tree.item(group_item, "tags")
            if "checked" not in tags:
                continue
            
            # Get group name
            group_name = self.tree.item(group_item, "text").replace("☑ ", "").replace("☐ ", "")
            
            # Get checked files in this group
            group_files = []
            for file_item in self.tree.get_children(group_item):
                file_tags = self.tree.item(file_item, "tags")
                if "checked" in file_tags:
                    # Get file index based on position
                    file_index = self.tree.index(file_item)
                    files_sorted = sort_files(self.groups[group_name])
                    if file_index < len(files_sorted):
                        group_files.append(files_sorted[file_index])
            
            if group_files:
                selected_groups.append({
                    'name': group_name,
                    'files': group_files
                })
        
        if not selected_groups:
            messagebox.showinfo("No Selection", "Please select at least one album to merge.")
            return
        
        # Get output format
        output_format = self._get_selected_format()
        format_label = FORMAT_REVERSE_LOOKUP.get(output_format, output_format.upper())
        
        # Confirm
        total_files = sum(len(g['files']) for g in selected_groups)
        result = messagebox.askyesno(
            "Confirm Merge",
            f"Merge {len(selected_groups)} album(s) with {total_files} files to {format_label}?"
        )
        
        if not result:
            return
        
        # Start merging in thread
        thread = threading.Thread(target=self.do_merge, args=(selected_groups,))
        thread.daemon = True
        thread.start()
    
    def do_merge(self, selected_groups):
        """Perform the actual merging"""
        # Get output format and bitrate
        output_format = self._get_selected_format()
        bitrate = self._get_selected_bitrate()
        format_label = FORMAT_REVERSE_LOOKUP.get(output_format, output_format.upper())
        
        # Get file extension for output
        extensions = {'mp3': '.mp3', 'flac': '.flac', 'opus': '.opus'}
        extension = extensions.get(output_format, '.mp3')
        
        try:
            for idx, group in enumerate(selected_groups):
                group_name = group['name']
                files = sort_files(group['files'])
                
                # Build status message
                bitrate_info = ""
                if bitrate:
                    if output_format == 'flac':
                        bitrate_info = f" (compression {bitrate})"
                    else:
                        bitrate_info = f" @ {bitrate}"
                
                status_msg = f"Merging {idx+1}/{len(selected_groups)}: {group_name} → {format_label}{bitrate_info}"
                self.status_label.config(text=status_msg)
                self.root.update()
                
                # Generate output filename with correct extension
                output_name = sanitize_filename(group_name) + "_merged" + extension
                output_path = files[0]['path'].parent / output_name
                
                # Merge files with selected format and bitrate
                merge_audio_files(files, output_path, bitrate=bitrate, output_format=output_format)
                
                # Get merged metadata
                metadata = get_merged_metadata(files)
                
                # Add chapters
                chapters_data = []
                current_time_ms = 0
                
                for file_info in files:
                    title = file_info.get('title') or file_info['path'].name
                    duration_ms = int(file_info['duration'] * 1000)
                    
                    chapters_data.append({
                        'title': title,
                        'start_ms': current_time_ms,
                        'duration_ms': duration_ms
                    })
                    
                    current_time_ms += duration_ms
                
                # Add chapters and metadata to output file
                add_chapters_and_tags(output_path, chapters_data, metadata=metadata, output_format=output_format)
                
                self.status_label.config(text=f"Completed {idx+1}/{len(selected_groups)}")
                self.root.update()
            
            self.status_label.config(text=f"✓ Successfully merged {len(selected_groups)} album(s) to {format_label}")
            messagebox.showinfo("Success", f"Successfully merged {len(selected_groups)} album(s) to {format_label}!")
            
        except Exception as e:
            self.status_label.config(text="Error during merge")
            messagebox.showerror("Error", f"Error during merge:\n{str(e)}")
    
    def _get_selected_format(self):
        """Get the format value from the selected option."""
        selected_label = self.selected_format.get()
        return FORMAT_LOOKUP.get(selected_label, 'mp3')
    
    def _get_selected_bitrate(self):
        """Get the bitrate value from the selected option."""
        output_format = self._get_selected_format()
        options = BITRATE_OPTIONS.get(output_format, BITRATE_OPTIONS['mp3'])
        selected_label = self.selected_bitrate.get()
        
        for label, value in options:
            if label == selected_label:
                return value
        return None
    
    def run(self):
        """Start the application"""
        self.root.mainloop()