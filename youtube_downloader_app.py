import customtkinter as ctk
import tkinter.filedialog as filedialog
import subprocess
import threading
import os
import re
import json
from PIL import Image, ImageTk
import time

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎬 YouTube Downloader Pro")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Initialize variables
        self.is_downloading = False
        self.download_start_time = 0
        
        # Create UI
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Apply modern styling
        self.apply_modern_styling()

    def create_header(self):
        """Create the header section with title and description"""
        self.header_frame = ctk.CTkFrame(self, corner_radius=15, height=80)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🎬 YouTube Downloader Pro",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(15, 5))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Download videos and audio from YouTube with ease",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 15))

    def create_main_content(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Input section
        self.create_input_section()
        
        # Progress section
        self.create_progress_section()
        
        # Download button
        self.create_download_button()
        
        # Output section
        self.create_output_section()

    def create_input_section(self):
        """Create the input section with URL, type, resolution, and path"""
        self.input_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # URL Input with icon
        self.url_label = ctk.CTkLabel(
            self.input_frame, 
            text="🔗 YouTube URL:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.url_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=40,
            font=ctk.CTkFont(size=12),
            corner_radius=10
        )
        self.url_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        # Download Type with modern radio buttons
        self.type_label = ctk.CTkLabel(
            self.input_frame, 
            text="📥 Download Type:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.type_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        self.type_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.type_frame.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        self.download_type_var = ctk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="🎥 Video", 
            variable=self.download_type_var, 
            value="video",
            font=ctk.CTkFont(size=12)
        )
        self.video_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.audio_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="🎵 Audio", 
            variable=self.download_type_var, 
            value="audio",
            font=ctk.CTkFont(size=12)
        )
        self.audio_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Resolution with modern option menu
        self.resolution_label = ctk.CTkLabel(
            self.input_frame, 
            text="📺 Resolution:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.resolution_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")
        
        self.resolution_options = ["best", "2160p (4K)", "1440p (2K)", "1080p (FHD)", "720p (HD)", "480p", "360p"]
        self.resolution_var = ctk.StringVar(value="720p (HD)")
        self.resolution_menu = ctk.CTkOptionMenu(
            self.input_frame, 
            variable=self.resolution_var, 
            values=self.resolution_options,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        self.resolution_menu.grid(row=2, column=1, padx=15, pady=15, sticky="ew")

        # Download Path with browse button
        self.path_label = ctk.CTkLabel(
            self.input_frame, 
            text="📁 Download Path:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.path_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")
        
        self.path_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.path_frame.grid(row=3, column=1, padx=15, pady=15, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_entry = ctk.CTkEntry(
            self.path_frame, 
            placeholder_text="Select download directory",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=10
        )
        self.path_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Set default download path
        default_download_path = "/home/isuru/Downloads"
        self.path_entry.insert(0, default_download_path)

        self.browse_button = ctk.CTkButton(
            self.path_frame, 
            text="📂 Browse", 
            command=self.browse_path,
            width=100,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.browse_button.grid(row=0, column=1, sticky="e")

    def create_progress_section(self):
        """Create the progress section with progress bar and stats"""
        self.progress_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.progress_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        # Progress info
        self.progress_info_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.progress_info_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_status_label = ctk.CTkLabel(
            self.progress_info_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_percentage_label = ctk.CTkLabel(
            self.progress_info_frame,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff88"
        )
        self.progress_percentage_label.grid(row=0, column=2, sticky="e")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=20,
            corner_radius=10,
            progress_color="#00ff88"
        )
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)
        
        # Speed and time info
        self.stats_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.stats_frame.grid_columnconfigure(1, weight=1)
        
        self.speed_label = ctk.CTkLabel(
            self.stats_frame,
            text="Speed: --",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.speed_label.grid(row=0, column=0, sticky="w")
        
        self.eta_label = ctk.CTkLabel(
            self.stats_frame,
            text="ETA: --",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.eta_label.grid(row=0, column=2, sticky="e")

    def create_download_button(self):
        """Create the download button with modern styling"""
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="⬇️ Start Download",
            command=self.start_download,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            hover_color="#00cc66"
        )
        self.download_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    def create_output_section(self):
        """Create the output section with scrollable text"""
        self.output_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.output_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)

        self.output_label = ctk.CTkLabel(
            self.output_frame,
            text="📋 Download Log",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.output_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10
        )
        self.output_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.output_text.insert("end", "🚀 YouTube Downloader Pro is ready!\n")
        self.output_text.insert("end", "💡 Enter a YouTube URL and click 'Start Download' to begin.\n")
        self.output_text.configure(state="disabled")

    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = ctk.CTkFrame(self, corner_radius=10, height=35)
        self.status_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=7, sticky="w")
        
        self.version_label = ctk.CTkLabel(
            self.status_frame,
            text="v2.0 Pro",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.version_label.grid(row=0, column=2, padx=15, pady=7, sticky="e")

    def apply_modern_styling(self):
        """Apply modern styling effects"""
        # Add subtle animations and effects
        self.animate_progress_bar()

    def animate_progress_bar(self):
        """Animate progress bar when not downloading"""
        if not self.is_downloading:
            current_time = time.time()
            wave = (1 + abs(((current_time * 2) % 2) - 1)) * 0.05
            self.progress_bar.configure(progress_color=f"#{int(0x00):02x}{int(0xff * (0.5 + wave)):02x}{int(0x88):02x}")
        
        # Schedule next animation frame
        self.after(100, self.animate_progress_bar)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, directory)

    def update_output(self, message):
        self.output_text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert("end", f"[{timestamp}] {message}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_progress(self, percentage, speed="--", eta="--"):
        self.progress_bar.set(percentage / 100)
        self.progress_percentage_label.configure(text=f"{int(percentage)}%")
        self.speed_label.configure(text=f"Speed: {speed}")
        self.eta_label.configure(text=f"ETA: {eta}")
        
        # Update progress status
        if percentage == 0:
            self.progress_status_label.configure(text="Initializing...")
        elif percentage < 100:
            self.progress_status_label.configure(text="Downloading...")
        else:
            self.progress_status_label.configure(text="Completed!")

    def update_status(self, message):
        self.status_label.configure(text=message)

    def start_download(self):
        url = self.url_entry.get().strip()
        download_type = self.download_type_var.get()
        resolution = self.resolution_var.get()
        download_path = self.path_entry.get().strip()

        if not url:
            self.update_output("❌ Error: Please enter a YouTube URL.")
            return
        if not download_path:
            self.update_output("❌ Error: Please select a download path.")
            return

        self.is_downloading = True
        self.download_start_time = time.time()
        self.update_output(f"🚀 Starting download for: {url}")
        self.update_output(f"📋 Type: {download_type}, Resolution: {resolution}")
        self.update_output(f"📁 Path: {download_path}")
        
        self.download_button.configure(state="disabled", text="⏳ Downloading...")
        self.update_status("Downloading...")
        
        # Run download in a separate thread
        download_thread = threading.Thread(
            target=self._execute_download, 
            args=(url, download_type, resolution, download_path)
        )
        download_thread.daemon = True
        download_thread.start()

    def _execute_download(self, url, download_type, resolution, download_path):
        try:
            # Construct the yt-dlp command
            command = ["yt-dlp", "--newline"]

            if download_type == "video":
                # Clean resolution format
                if resolution == "best":
                    command.extend(["-f", "bestvideo+bestaudio/best"])
                else:
                    res_num = resolution.split()[0].replace('p', '')
                    command.extend(["-f", f"bestvideo[height<={res_num}]+bestaudio/best[height<={res_num}]"])
            elif download_type == "audio":
                command.extend(["-x", "--audio-format", "mp3", "--audio-quality", "192"])

            command.extend(["-o", os.path.join(download_path, "%(title)s.%(ext)s")])
            command.append(url)

            self.update_output(f"🔧 Executing: {' '.join(command)}")

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.update_output(line)
                    
                    # Parse progress from yt-dlp output
                    progress_match = re.search(r"\b(\d+\.?\d*)%", line)
                    if progress_match:
                        try:
                            percentage = float(progress_match.group(1))
                            
                            # Extract speed and ETA
                            speed = "--"
                            eta = "--"
                            
                            speed_match = re.search(r"at\s+([0-9.]+[A-Za-z/]+)", line)
                            if speed_match:
                                speed = speed_match.group(1)
                            
                            eta_match = re.search(r"ETA\s+([0-9:]+)", line)
                            if eta_match:
                                eta = eta_match.group(1)
                            
                            self.after(0, self.update_progress, percentage, speed, eta)
                        except ValueError:
                            pass
            
            process.wait()

            if process.returncode == 0:
                self.after(0, self.update_progress, 100, "--", "--")
                self.update_output("✅ Download completed successfully!")
                self.update_status("Download completed")
            else:
                self.update_output(f"❌ Download failed with error code: {process.returncode}")
                self.update_status("Download failed")

        except Exception as e:
            self.update_output(f"❌ An error occurred: {e}")
            self.update_status("Error occurred")
        finally:
            self.is_downloading = False
            self.download_button.configure(state="normal", text="⬇️ Start Download")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
