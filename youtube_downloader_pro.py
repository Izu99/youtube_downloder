import customtkinter as ctk
import tkinter.filedialog as filedialog
import subprocess
import threading
import os
import re
import time
import queue
from PIL import Image
import urllib.request
import io
import json

class YouTubeDownloaderPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.progress_queue = queue.Queue()
        self._check_queue_for_updates()

        # --- App Configuration ---
        self.title("YouTube Downloader Pro")
        self.geometry("800x600")
        self.minsize(700, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Grid Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.title_label = ctk.CTkLabel(self.header_frame, text="YouTube Downloader Pro", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # --- Main Content Frame ---
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Section ---
        self.url_label = ctk.CTkLabel(self.main_content_frame, text="YouTube URL:", font=ctk.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.url_entry = ctk.CTkEntry(self.main_content_frame, placeholder_text="Enter YouTube URL")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="ew")

        self.type_label = ctk.CTkLabel(self.main_content_frame, text="Download Type:", font=ctk.CTkFont(weight="bold"))
        self.type_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.download_type_var = ctk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(self.main_content_frame, text="Video", variable=self.download_type_var, value="video")
        self.video_radio.grid(row=1, column=1, padx=(20, 0), pady=10, sticky="w")
        self.audio_radio = ctk.CTkRadioButton(self.main_content_frame, text="Audio (mp3)", variable=self.download_type_var, value="audio")
        self.audio_radio.grid(row=1, column=1, padx=(120, 0), pady=10, sticky="w")

        self.resolution_label = ctk.CTkLabel(self.main_content_frame, text="Resolution:", font=ctk.CTkFont(weight="bold"))
        self.resolution_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.resolution_options = ["best", "720p", "360p", "144p"]
        self.resolution_var = ctk.StringVar(value="720p")
        self.resolution_menu = ctk.CTkOptionMenu(self.main_content_frame, variable=self.resolution_var, values=self.resolution_options)
        self.resolution_menu.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.path_label = ctk.CTkLabel(self.main_content_frame, text="Download Path:", font=ctk.CTkFont(weight="bold"))
        self.path_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self.main_content_frame, placeholder_text="Select download directory")
        self.path_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.path_entry.insert(0, "/home/isuru/Downloads")
        self.browse_button = ctk.CTkButton(self.main_content_frame, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=3, column=2, padx=20, pady=10)

        # --- Download Button ---
        self.download_button = ctk.CTkButton(self.main_content_frame, text="Download", command=self.start_download, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_button.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        # --- Progress Section ---
        self.progress_bar = ctk.CTkProgressBar(self.main_content_frame)
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(self.main_content_frame, text="0%")
        self.progress_label.grid(row=5, column=2, padx=20, pady=10, sticky="e")

        # --- Output Console ---
        self.output_text = ctk.CTkTextbox(self.main_content_frame, wrap="word", height=150)
        self.output_text.grid(row=6, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(6, weight=1)
        self.update_output("Welcome to YouTube Downloader Pro!")

    # --- Thumbnail Feature Commented Out ---
    # def update_thumbnail(self, url):
    #     try:
    #         with urllib.request.urlopen(url) as response:
    #             image_data = response.read()
    #         image = Image.open(io.BytesIO(image_data))
    #         image.thumbnail((320, 180))
    #         self.thumbnail_image = ctk.CTkImage(light_image=image, dark_image=image, size=(320, 180))
    #         self.thumbnail_label.configure(image=self.thumbnail_image)
    #     except Exception as e:
    #         self.update_output(f"Error loading thumbnail: {e}", is_error=True)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, directory)

    def update_output(self, message, is_error=False):
        self.output_text.configure(state="normal")
        prefix = "ERROR: " if is_error else ""
        self.output_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {prefix}{message}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_progress(self, percentage, speed="N/A", eta="N/A"):
        self.progress_bar.set(percentage / 100)
        self.progress_label.configure(text=f"{int(percentage)}%")

    def _check_queue_for_updates(self):
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                self.update_progress(**progress_data)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue_for_updates)

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.update_output("Please enter a YouTube URL.", is_error=True)
            return
        
        self.download_button.configure(state="disabled", text="Downloading...")
        self.update_progress(0)
        
        download_thread = threading.Thread(target=self._execute_download, daemon=True)
        download_thread.start()

    def _execute_download(self):
        url = self.url_entry.get()
        download_type = self.download_type_var.get()
        resolution = self.resolution_var.get()
        download_path = self.path_entry.get()

        # --- Predict filename and handle existing files ---
        output_template = os.path.join(download_path, "%(title)s.%(ext)s")
        try:
            self.update_output("Determining filename...")
            get_filename_cmd = ["yt-dlp", "--get-filename", "-o", output_template, url]
            predicted_filename = subprocess.check_output(get_filename_cmd, text=True, encoding='utf-8').strip()

            if os.path.exists(predicted_filename):
                self.update_output(f'File "{os.path.basename(predicted_filename)}" already exists.')
                base, ext = os.path.splitext(predicted_filename)
                count = 1
                final_output_path = f"{base}_({count}){ext}"
                while os.path.exists(final_output_path):
                    count += 1
                    final_output_path = f"{base}_({count}){ext}"
                self.update_output(f'Will download as "{os.path.basename(final_output_path)}"')
            else:
                final_output_path = predicted_filename

        except subprocess.CalledProcessError as e:
            self.update_output(f"Could not determine filename. Download aborted. Error: {e}", is_error=True)
            self.download_button.configure(state="normal", text="Download")
            return

        # --- Build the final download command ---
        command = ["yt-dlp", "--no-warnings", "--progress", "--newline"]
        
        if download_type == "video":
            if resolution == "best":
                format_string = "bestvideo+bestaudio/best"
            else:
                res_height = resolution[:-1]
                format_string = f"bestvideo[height<={res_height}]+bestaudio/bestvideo+bestaudio"
            command.extend(["-f", format_string])
        elif download_type == "audio":
            command.extend(["-x", "--audio-format", "mp3"])

        command.extend(["-o", final_output_path, url])

        self.update_output(f"Starting download: {os.path.basename(final_output_path)}")
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

        for line in process.stdout:
            # Also print to console for debugging, and update the GUI
            print(line.strip())
            self.update_output(line.strip())
            progress_match = re.search(r"\[download\]\s+([\d\.]+)%", line)
            if progress_match:
                percentage = float(progress_match.group(1))
                self.progress_queue.put({'percentage': percentage})

        process.wait()

        if process.returncode == 0:
            self.update_output("Download completed successfully!")
            self.progress_queue.put({'percentage': 100})
        else:
            self.update_output("Download failed.", is_error=True)
            
        self.download_button.configure(state="normal", text="Download")
        # Reset progress bar for the next download
        time.sleep(1) # Give a moment before resetting
        self.progress_queue.put({'percentage': 0})

if __name__ == "__main__":
    app = YouTubeDownloaderPro()
    app.mainloop()