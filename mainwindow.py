import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from imagescompress import ImagesCompress


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compresser")
        self.root.resizable(False, False)

        self.min_size = tk.IntVar(value=0)
        self.max_size = tk.IntVar(value=5000)
        self.compress_quality = tk.IntVar(value=85)
        self.convert_mode = tk.IntVar(value=0)
        self.compress_mode = tk.IntVar(value=0)
        self.images_list = []
        self.folder = tk.StringVar()
        self.progress = False

        self.all_images_var = tk.StringVar(value='0')
        self.com_images_var = tk.StringVar(value='0')
        self.done_progress_var = tk.StringVar(value='0')
        self.images_skipped_var = tk.StringVar(value='0')
        self.files_compressed_var = tk.StringVar(value='0')
        self.memory_saved_var = tk.StringVar(value='   ')

        self.make_layout()

    def listImages(self, folder, minSize=0, maxSize=5000):
        imageList = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                frst_regex_res = re.match(
                    re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)|(.*webp$)|(.*tiff)', re.IGNORECASE), file)

                current_root = root.replace('\\', '/')

                if frst_regex_res:
                    file_size = round(os.stat(current_root + "/" + file).st_size / 1024, 3)

                    if (maxSize == 0 and minSize == 0) or (minSize <= file_size <= maxSize):
                        imageList.append([file, current_root, file_size])
        return imageList

    def make_layout(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Separator(main_frame, orient=tk.VERTICAL).grid(row=0, column=1, sticky='ns', padx=5)

        # Left column
        folder_frame = ttk.Frame(left_frame)
        folder_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(folder_frame, text="Folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_frame, textvariable=self.folder, width=25).grid(row=0, column=1, sticky="ew")
        ttk.Button(folder_frame, text="Browse...", command=self.browse_folder).grid(row=0, column=2)

        convert_frame = ttk.LabelFrame(left_frame, text="Convert")
        convert_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Radiobutton(convert_frame, text="None", variable=self.convert_mode, value=0).pack(anchor=tk.W)
        ttk.Radiobutton(convert_frame, text="Convert to webp", variable=self.convert_mode, value=2).pack(anchor=tk.W)
        ttk.Radiobutton(convert_frame, text="Convert to jpg", variable=self.convert_mode, value=1).pack(anchor=tk.W)

        size_frame = ttk.Frame(left_frame)
        size_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(size_frame, text="Size (kb):").grid(row=0, column=0)
        ttk.Label(size_frame, text="Min").grid(row=0, column=1)
        ttk.Entry(size_frame, textvariable=self.min_size, width=5).grid(row=0, column=2)
        ttk.Label(size_frame, text="Max").grid(row=0, column=3)
        ttk.Entry(size_frame, textvariable=self.max_size, width=5).grid(row=0, column=4)
        ttk.Button(size_frame, text="Filter", command=self.filter_images).grid(row=0, column=5, padx=5)

        quality_frame = ttk.Frame(left_frame)
        quality_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        ttk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.compress_quality, length=200).pack(side=tk.LEFT, fill=tk.X, expand=True)

        png_mode_frame = ttk.LabelFrame(left_frame, text="PNG compress mode")
        png_mode_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Radiobutton(png_mode_frame, text="P (8-bit pixels)", variable=self.compress_mode, value=0).pack(anchor=tk.W)
        ttk.Radiobutton(png_mode_frame, text="RGB (3x8-bit)", variable=self.compress_mode, value=1).pack(anchor=tk.W)

        self.go_button = ttk.Button(left_frame, text="GO!", command=self.start_compression)
        self.go_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Right column
        notebook = ttk.Notebook(right_frame)
        notebook.pack(expand=True, fill="both")

        info_tab = ttk.Frame(notebook, padding="10")
        output_tab = ttk.Frame(notebook, padding="10")

        notebook.add(info_tab, text="INFO")
        notebook.add(output_tab, text="OUTPUT")

        # Info Tab
        ttk.Label(info_tab, text="All images").grid(row=0, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.all_images_var, background='#28a745').grid(row=0, column=1, sticky="w")
        ttk.Label(info_tab, text="Images for compression").grid(row=1, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.com_images_var, background='#28a745').grid(row=1, column=1, sticky="w")
        ttk.Label(info_tab, text="Progress").grid(row=2, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.done_progress_var, background='#28a745').grid(row=2, column=1, sticky="w")
        ttk.Label(info_tab, text="Images skipped").grid(row=3, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.images_skipped_var, background='#28a745').grid(row=3, column=1, sticky="w")
        ttk.Label(info_tab, text="Files compressed:").grid(row=4, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.files_compressed_var, background='#28a745').grid(row=4, column=1, sticky="w")
        ttk.Label(info_tab, text="Saved:").grid(row=5, column=0, sticky="w")
        ttk.Label(info_tab, textvariable=self.memory_saved_var, background='#28a745').grid(row=5, column=1, sticky="w")

        # Output Tab
        self.output_text = tk.Text(output_tab, height=20, width=20)
        self.output_text.pack(fill="both", expand=True)


    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder.set(folder_path)
            self.update_image_list()

    def update_image_list(self):
        try:
            file_list = self.listImages(self.folder.get())
            self.images_list = file_list
            self.all_images_var.set(len(file_list))
            self.com_images_var.set(len(file_list))
        except Exception as e:
            self.log_output(f"Error listing files: {e}")
            self.images_list = []
            self.all_images_var.set(0)
            self.com_images_var.set(0)


    def filter_images(self):
        try:
            min_s = self.min_size.get()
            max_s = self.max_size.get()
            if self.folder.get() and max_s > min_s:
                self.images_list = self.listImages(self.folder.get(), min_s, max_s)
                self.com_images_var.set(len(self.images_list))
            else:
                messagebox.showerror("Error", "Incorrect folder or min or max file size")
        except Exception as e:
            self.log_output(f"Something wrong with filtering: {e}")

    def start_compression(self):
        if len(self.images_list):
            self.go_button.config(state=tk.DISABLED)
            self.done_progress_var.set('0')
            threading.Thread(target=self.run_comp, daemon=True).start()
        else:
            messagebox.showinfo("Info", "Click filter first!")

    def run_comp(self):
        self.progress = True
        compress = ImagesCompress(self.folder.get(),
                                  self.images_list,
                                  self.compress_quality.get(),
                                  self.compress_mode.get(),
                                  self.convert_mode.get())

        result = compress.compress_files(self.progress_update)

        self.root.after(0, self.update_ui_after_compression, result)


    def progress_update(self):
        self.root.after(0, self.increment_progress)

    def increment_progress(self):
        val = int(self.done_progress_var.get())
        val += 1
        self.done_progress_var.set(str(val))


    def update_ui_after_compression(self, result):
        self.images_skipped_var.set(result['files_counter'] - result['compress_counter'])
        self.files_compressed_var.set(result['compress_counter'])
        self.memory_saved_var.set(
            f'{result["weight_before"]} -> {result["weight_after"]} : {int(result["weight_before"]) - int(result["weight_after"])} kb')
        self.go_button.config(state=tk.NORMAL)
        self.progress = False
        self.log_output("Compression finished.")


    def log_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)


    def show_window(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.show_window()
