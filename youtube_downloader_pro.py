import customtkinter as ctk
import tkinter.filedialog as filedialog
import subprocess
import threading
import os
import re
import time
import queue
from PIL import Image, ImageTk
import urllib.request
import io
import json

class YouTubeDownloaderPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.progress_queue = queue.Queue()
        self._check_queue_for_updates() # Start checking the queue periodically

        # --- App Configuration ---
        self.title("Enhanced YouTube Downloader Pro")
        self.geometry("900x700")
        self.minsize(800, 600)
        ctk.set_appearance_mode("dark") # Dark theme
        ctk.set_default_color_theme("green") # Green accent color

        # --- Grid Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Main content area

        # --- Header Frame ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=15)
        self.header_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.header_frame, text="🚀 YouTube Downloader Pro", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(15, 5))

        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Download your favorite videos and audios with ease!", font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 15))

        # --- Main Content Frame ---
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_rowconfigure(7, weight=1) # Output frame should expand

        # --- Thumbnail Preview ---
        self.thumbnail_label = ctk.CTkLabel(self.main_content_frame, text="")
        self.thumbnail_label.grid(row=0, column=2, rowspan=4, padx=15, pady=10, sticky="nsew")

        # --- Input Section ---
        # URL Input
        self.url_label = ctk.CTkLabel(self.main_content_frame, text="🔗 YouTube URL:", font=ctk.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.main_content_frame, placeholder_text="Enter YouTube URL here", corner_radius=10)
        self.url_entry.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        self.url_entry.bind("<FocusOut>", self.on_url_focus_out)

        # Download Type
        self.type_label = ctk.CTkLabel(self.main_content_frame, text="📥 Download Type:", font=ctk.CTkFont(weight="bold"))
        self.type_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.download_type_var = ctk.StringVar(value="video") # Default to video
        self.video_radio = ctk.CTkRadioButton(self.main_content_frame, text="Video", variable=self.download_type_var, value="video", corner_radius=5, command=self.on_url_focus_out)
        self.video_radio.grid(row=1, column=1, padx=(15, 5), pady=10, sticky="w")
        self.audio_radio = ctk.CTkRadioButton(self.main_content_frame, text="Audio", variable=self.download_type_var, value="audio", corner_radius=5, command=self.on_url_focus_out)
        self.audio_radio.grid(row=1, column=1, padx=(5, 15), pady=10, sticky="e")

        # Resolution (for video)
        self.resolution_label = ctk.CTkLabel(self.main_content_frame, text="📺 Resolution:", font=ctk.CTkFont(weight="bold"))
        self.resolution_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.resolution_options = ["best"]
        self.resolution_var = ctk.StringVar(value="best") # Default to best
        self.resolution_menu = ctk.CTkOptionMenu(self.main_content_frame, variable=self.resolution_var, values=self.resolution_options, corner_radius=10)
        self.resolution_menu.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        # Download Path
        self.path_label = ctk.CTkLabel(self.main_content_frame, text="📁 Download Path:", font=ctk.CTkFont(weight="bold"))
        self.path_label.grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self.main_content_frame, placeholder_text="Select download directory", corner_radius=10)
        self.path_entry.grid(row=3, column=1, padx=15, pady=10, sticky="ew")
        # Set default download path from memory
        default_download_path = "/home/isuru/Downloads"
        self.path_entry.insert(0, default_download_path)

        self.browse_button = ctk.CTkButton(self.main_content_frame, text="Browse", command=self.browse_path, corner_radius=10, hover=True)
        self.browse_button.grid(row=3, column=2, padx=15, pady=10, sticky="e")

        # Download Button
        self.download_button = ctk.CTkButton(self.main_content_frame, text="🚀 Start Download", command=self.start_download, corner_radius=10, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_button.grid(row=4, column=0, columnspan=3, padx=15, pady=20, sticky="ew")

        # --- Progress Section ---
        self.progress_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=15)
        self.progress_frame.grid(row=5, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, corner_radius=10, height=20)
        self.progress_bar.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%", font=ctk.CTkFont(weight="bold"))
        self.progress_label.grid(row=0, column=1, padx=15, pady=10, sticky="e")

        self.speed_label = ctk.CTkLabel(self.progress_frame, text="Speed: N/A", font=ctk.CTkFont(size=12))
        self.speed_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        self.eta_label = ctk.CTkLabel(self.progress_frame, text="ETA: N/A", font=ctk.CTkFont(size=12))
        self.eta_label.grid(row=1, column=1, padx=15, pady=(0, 10), sticky="e")

        # --- Output Frame ---
        self.output_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=15)
        self.output_frame.grid(row=6, column=0, columnspan=3, padx=15, pady=10, sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)

        self.output_text = ctk.CTkTextbox(self.output_frame, wrap="word", corner_radius=10)
        self.output_text.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.output_text.insert("end", f"[{time.strftime('%H:%M:%S')}] ✨ Welcome to YouTube Downloader Pro!\n")
        self.output_text.configure(state="disabled") # Make it read-only

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="Version 1.0 | Ready", font=ctk.CTkFont(size=12), anchor="e")
        self.status_bar.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

    def on_url_focus_out(self, event=None):
        url = self.url_entry.get()
        if url and re.match(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%?]{11})', url):
            self._get_resolutions()

    def _get_resolutions(self):
        url = self.url_entry.get()
        if not url:
            return

        self.update_output("Fetching video data and resolutions...")
        try:
            # Get video info in JSON format
            command = ["yt-dlp", "--dump-json", url]
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            video_info = json.loads(process.stdout)

            # Update thumbnail
            if video_info.get('thumbnail'):
                self.update_thumbnail(video_info['thumbnail'])

            # Extract and sort resolutions
            resolutions = set()
            for f in video_info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f'{f["height"]}p')
            
            sorted_resolutions = sorted(list(resolutions), key=lambda x: int(x[:-1]), reverse=True)
            
            # Add "best" option and update dropdown
            final_resolutions = ["best"] + sorted_resolutions
            self.resolution_menu.configure(values=final_resolutions)
            self.resolution_var.set(final_resolutions[0])
            self.update_output("Available resolutions updated.")

        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            self.update_output(f"Error fetching video data or resolutions: {e}", is_error=True)
            self.resolution_menu.configure(values=["best"])
            self.resolution_var.set("best")

    def update_thumbnail(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                image_data = response.read()
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((320, 180)) # Resize for preview
            self.thumbnail_image = ImageTk.PhotoImage(image)
            self.thumbnail_label.configure(image=self.thumbnail_image)
        except Exception as e:
            self.update_output(f"Error loading thumbnail: {e}", is_error=True)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, directory)

    def update_output(self, message, is_error=False):
        self.output_text.configure(state="normal")
        prefix = "❌ ERROR: " if is_error else "✅ "
        self.output_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {prefix}{message}\n")
        self.output_text.see("end") # Scroll to the end
        self.output_text.configure(state="disabled")

    def update_progress(self, percentage, speed="N/A", eta="N/A"):
        self.progress_bar.set(percentage / 100)
        self.progress_label.configure(text=f"{int(percentage)}%")
        self.speed_label.configure(text=f"Speed: {speed}")
        self.eta_label.configure(text=f"ETA: {eta}")

    def _check_queue_for_updates(self):
        try:
            while True:
                percentage, speed, eta = self.progress_queue.get_nowait()
                self.update_progress(percentage, speed, eta)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue_for_updates) # Check every 100ms

    def start_download(self):
        url = self.url_entry.get()
        download_type = self.download_type_var.get()
        resolution = self.resolution_var.get()
        download_path = self.path_entry.get()

        if not url or not re.match(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%?]{11})', url):
            self.update_output("Please enter a valid YouTube URL.", is_error=True)
            return
        if not download_path:
            self.update_output("Please select a download path.", is_error=True)
            return

        self.update_output(f"Starting download for: {url}")
        self.update_output(f"Type: {download_type}, Resolution: {resolution}, Path: {download_path}")
        self.download_button.configure(state="disabled", text="Downloading...")
        self.update_progress(0, "N/A", "N/A") # Reset progress

        # Run download in a separate thread to keep UI responsive
        download_thread = threading.Thread(target=self._execute_download, args=(url, download_type, resolution, download_path), daemon=True)
        download_thread.start()

    def _execute_download(self, url, download_type, resolution, download_path):
        try:
            # Construct the yt-dlp command
            command = ["yt-dlp", "--get-filename", "-o", os.path.join(download_path, "%(title)s.%(ext)s"), url]
            try:
                process = subprocess.run(command, capture_output=True, text=True, check=True)
                filename = process.stdout.strip()
                if os.path.exists(filename):
                    # Simple dialog for user confirmation
                    # In a real-world scenario, you'd want a more robust dialog system
                    # that doesn't block the main thread like this.
                    # For this example, we'll use a simple text-based confirmation.
                    self.update_output(f'File "{os.path.basename(filename)}" already exists. Download again?')
                    # This is a placeholder for a proper dialog
                    # In a real customtkinter app, you would create a Toplevel window for this.
                    # For now, we will proceed with renaming.
                    base, ext = os.path.splitext(filename)
                    count = 1
                    while os.path.exists(f"{base}_({count}){ext}"):
                        count += 1
                    new_filename = f"{base}_({count}){ext}"
                    self.update_output(f"Downloading as \"{os.path.basename(new_filename)}\"")
                    command.extend(["-o", new_filename])

            except subprocess.CalledProcessError as e:
                self.update_output(f"Error getting filename: {e.stderr}", is_error=True)
                return

            command = ["yt-dlp"]

            if download_type == "video":
                # Clean resolution string for yt-dlp
                res_val = resolution.split(" ")[0].replace("(", "").replace("p)", "")
                if res_val == "best":
                    command.extend(["-f", "bestvideo+bestaudio/best"])
                else:
                    command.extend(["-f", f"bestvideo[height<={res_val}]+bestaudio/best[height<={res_val}]"])
            elif download_type == "audio":
                command.extend(["-x", "--audio-format", "mp3"])

            command.extend(["-o", os.path.join(download_path, "%(title)s.%(ext)s"), url])

            self.update_output(f"Executing command: {' '.join(command)}")

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', errors='replace')
            for line in process.stdout:
                self.update_output(line.strip())
                # Debug: Print raw yt-dlp output line
                print(f"[DEBUG] YT-DLP Raw: {line.strip()}")

                progress_match = re.search(r"(\d+\.?\d*)%\s+of\s+.*?\s+at\s+(\d+\.?\d*[KMGTPEZY]?iB/s)\s+ETA\s+(.*)", line)
                if progress_match:
                    try:
                        percentage = float(progress_match.group(1))
                        speed = progress_match.group(2)
                        eta = progress_match.group(3)
                        self.progress_queue.put((percentage, speed, eta))
                        # Debug: Confirm data put into queue
                        print(f"[DEBUG] Put to queue: {percentage}%, {speed}, {eta}")
                    except ValueError:
                        print(f"[DEBUG] ValueError parsing progress: {progress_match.group(1)}")
                elif re.search(r"100%", line) and "of" in line:
                    self.progress_queue.put((100, "N/A", "00:00")) # Ensure 100% is shown
                    print("[DEBUG] Put 100% to queue")

            process.stdout.close() # Explicitly close stdout
            process.wait()

            if process.returncode == 0:
                self.update_output("Download completed successfully! 🎉")
            else:
                self.update_output(f"Download failed with error code: {process.returncode} ❌", is_error=True)

        except Exception as e:
            self.update_output(f"An unexpected error occurred: {e} 🚨", is_error=True)
        finally:
            self.download_button.configure(state="normal", text="🚀 Start Download")
            self.status_bar.configure(text="Version 1.0 | Ready")

if __name__ == "__main__":
    app = YouTubeDownloaderPro()
    app.mainloop()
