import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

class MP3AlbumMerger:
    def __init__(self, master):
        self.master = master
        master.title("MP3 Album Merger")

        # Instructions label
        self.label = tk.Label(master, text="Select MP3 files to merge:")
        self.label.pack()

        # Listbox to display selected files
        self.file_list = tk.Listbox(master, selectmode=tk.MULTIPLE, width=50, height=10)
        self.file_list.pack()

        # Buttons
        self.add_files_button = tk.Button(master, text="Add MP3 Files", command=self.add_files)
        self.add_files_button.pack()

        self.merge_button = tk.Button(master, text="Merge MP3s", command=self.merge_files)
        self.merge_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        for file in files:
            self.file_list.insert(tk.END, file)

    def merge_files(self):
        files = self.file_list.get(0, tk.END)
        if not files:
            messagebox.showwarning("Warning", "No files selected!")
            return

        output_file = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 Files", "*.mp3")])
        if not output_file:
            return

        # Here would be the logic to merge the MP3 files using a suitable library, e.g., pydub
        # This is a placeholder for demonstration purposes.
        with open(output_file, 'wb') as outfile:
            for fname in files:
                with open(fname, 'rb') as infile:
                    outfile.write(infile.read())

        messagebox.showinfo("Success", "Files merged successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3AlbumMerger(root)
    root.mainloop()