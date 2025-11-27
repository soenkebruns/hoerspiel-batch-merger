import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .scanner import scan_mp3_folders
from .merger import merge_mp3_files
from .chapters import create_chapter_markers
from .utils import is_valid_mp3_file

class MP3AlbumMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Album Merger")
        self.create_widgets()

    def create_widgets(self):
        # Folder selection
        self.folder_label = tk.Label(self.root, text="Select Folder:")
        self.folder_label.pack(pady=5)

        self.folder_button = tk.Button(self.root, text="Browse...", command=self.select_folder)
        self.folder_button.pack()

        # Treeview with checkboxes
        self.tree = ttk.Treeview(self.root, selectmode='extended')
        self.tree.pack(expand=True, fill='both')
        self.tree.bind('<Double-1>', self.on_item_double_click)

        # Merge button
        self.merge_button = tk.Button(self.root, text="Merge MP3s", command=self.merge_mp3s)
        self.merge_button.pack(pady=5)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.populate_treeview()

    def populate_treeview(self):
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Scan for MP3 files
        mp3_files = scan_mp3_folders(self.folder_path)
        for file in mp3_files:
            self.tree.insert('', 'end', text=file, iid=file, open=False)

    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        print(f'You selected: {item}')  # Replace with actual action

    def merge_mp3s(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Please select MP3 files to merge.")
            return
        mp3s_to_merge = [self.tree.item(item)['text'] for item in selected_items]
        output_file = self.folder_path + '/merged_output.mp3'
        if merge_mp3_files(mp3s_to_merge, output_file):
            messagebox.showinfo("Success", "MP3 files merged successfully!")
        else:
            messagebox.showerror("Error", "Failed to merge MP3 files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3AlbumMergerApp(root)
    root.mainloop()