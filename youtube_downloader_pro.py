import customtkinter as ctk
import tkinter.filedialog as filedialog
import subprocess
import threading
import os
import re
import time
import queue
import shutil
import json
import platform

class YouTubeDownloaderPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.YTDLP_PATH = self._find_ytdlp()

        self.progress_queue = queue.Queue()
        self._check_queue_for_updates()

        self.current_download_process = None
        self.current_download_file = None
        self.downloaded_file_path = None
        self.stop_flag = threading.Event()

        self.title("🎬 YouTube Downloader Pro")
        self.geometry("1000x700")
        self.minsize(1000, 700)
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        self.colors = {
            "bg_primary": "#0F0F23",
            "bg_secondary": "#1A1A2E",
            "bg_tertiary": "#16213E",
            "accent": "#00D9FF",
            "accent_hover": "#00B8E6",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B8B8D1",
            "success": "#00FFD4",
            "warning": "#FFB800",
            "error": "#FF3B30",
            "neon_glow": "#00FFFF",
            "console_bg": "#0F0F23",
            "border_color": "#16213E",
            "download_active": "#00A8CC",
            "download_normal": "#00BFFF",
            "stop_normal": "#BF00FF",  # Neon purple
            "stop_hover": "#E600FF",   # Lighter neon purple
            "play_normal": "#00FF7F",  # Greenish neon
            "play_hover": "#00E66F",   # Lighter greenish neon
            "clear_normal": "#00FFFF", # Neon cyan
            "clear_hover": "#00E6E6",  # Lighter neon cyan
            "console_info": "#FFFFFF",
            "console_success": "#00FF7F",
            "console_error": "#FF4444",
            "console_warning": "#FFD700",
            "console_progress": "#00BFFF",
            "console_timestamp": "#9370DB",
            "console_icon": "#FFB6C1",
            "console_highlight": "#FF6347"
        }

        self.configure(fg_color=self.colors["bg_primary"])
        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=self.colors["bg_secondary"], height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 YouTube Downloader Pro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title_label.pack(pady=15)

        content_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=self.colors["bg_secondary"])
        content_frame.pack(fill="both", expand=True)
        content_frame.pack_propagate(False)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(4, weight=1)

        url_label = ctk.CTkLabel(content_frame, text="🔗 YouTube URL:", font=ctk.CTkFont(size=14, weight="bold"))
        url_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        self.url_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Paste your YouTube URL here...",
            height=35,
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border_color"],
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")

        settings_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["bg_tertiary"], corner_radius=12)
        settings_frame.grid(row=2, column=0, padx=(20, 10), pady=(0, 15), sticky="nsew")

        type_label = ctk.CTkLabel(settings_frame, text="📥 Download Type:", font=ctk.CTkFont(size=13, weight="bold"))
        type_label.pack(padx=15, pady=(15, 8), anchor="w")

        radio_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        radio_frame.pack(padx=15, pady=(0, 10), fill="x")

        self.download_type_var = ctk.StringVar(value="video")
        video_radio = ctk.CTkRadioButton(
            radio_frame, text="🎥 Video", variable=self.download_type_var, value="video",
            font=ctk.CTkFont(size=12), radiobutton_width=18, radiobutton_height=18,
            fg_color=self.colors["accent"]
        )
        video_radio.pack(side="left", padx=(0, 20))

        audio_radio = ctk.CTkRadioButton(
            radio_frame, text="🎵 Audio", variable=self.download_type_var, value="audio",
            font=ctk.CTkFont(size=12), radiobutton_width=18, radiobutton_height=18,
            fg_color=self.colors["accent"]
        )
        audio_radio.pack(side="left")

        resolution_label = ctk.CTkLabel(settings_frame, text="⚙️ Resolution:", font=ctk.CTkFont(size=13, weight="bold"))
        resolution_label.pack(padx=15, pady=(10, 8), anchor="w")

        self.resolution_options = ["Best Quality", "720p HD", "360p", "144p"]
        self.resolution_var = ctk.StringVar(value="720p HD")
        self.resolution_menu = ctk.CTkOptionMenu(
            settings_frame, variable=self.resolution_var, values=self.resolution_options,
            height=32, corner_radius=8, fg_color=self.colors["bg_primary"],
            button_color=self.colors["accent"], font=ctk.CTkFont(size=12),
            dropdown_fg_color=self.colors["bg_tertiary"],
            dropdown_hover_color=self.colors["accent_hover"],
            dropdown_text_color=self.colors["text_primary"]
        )
        self.resolution_menu.pack(padx=15, pady=(0, 10), fill="x")

        path_label = ctk.CTkLabel(settings_frame, text="📁 Download Path:", font=ctk.CTkFont(size=13, weight="bold"))
        path_label.pack(padx=15, pady=(10, 8), anchor="w")

        path_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        path_frame.pack(padx=15, pady=(0, 15), fill="x")

        self.path_entry = ctk.CTkEntry(
            path_frame, height=32, corner_radius=8, border_width=1,
            border_color=self.colors["border_color"], fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=11)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))

        browse_button = ctk.CTkButton(
            path_frame, text="📂", command=self.browse_path, width=40, height=32,
            corner_radius=8, fg_color=self.colors["bg_primary"], hover_color=self.colors["accent"],
            font=ctk.CTkFont(size=12)
        )
        browse_button.pack(side="right")

        progress_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["bg_tertiary"], corner_radius=12)
        progress_frame.grid(row=2, column=1, padx=(10, 20), pady=(0, 15), sticky="nsew")

        controls_label = ctk.CTkLabel(progress_frame, text="🎮 Controls:", font=ctk.CTkFont(size=13, weight="bold"))
        controls_label.pack(padx=15, pady=(15, 8), anchor="w")

        buttons_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        buttons_frame.pack(padx=15, pady=(0, 15), fill="x")

        self.download_button = ctk.CTkButton(
            buttons_frame, text="⬇️ Download", command=self.start_download,
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=10,
            fg_color=self.colors["bg_secondary"], # Match parent background
            border_width=2,
            border_color=self.colors["accent"], # Neon blue/cyan
            hover_color=self.colors["accent_hover"] # Keep existing hover for border effect
        )
        self.download_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.stop_button = ctk.CTkButton(
            buttons_frame, text="⏹️ Stop", command=self.stop_download,
            font=ctk.CTkFont(size=14, weight="bold"), height=40, width=80, corner_radius=10, # Set a fixed width for stop button
            fg_color=self.colors["bg_secondary"], # Match parent background
            border_width=2,
            border_color=self.colors["stop_normal"], # Neon purple
            hover_color=self.colors["stop_hover"], # Lighter neon purple on hover
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=(4, 0)) # Remove fill="x", expand=True

        

        progress_label = ctk.CTkLabel(progress_frame, text="📊 Progress:", font=ctk.CTkFont(size=13, weight="bold"))
        progress_label.pack(padx=15, pady=(15, 8), anchor="w")

        progress_bar_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_bar_frame.pack(padx=15, pady=(0, 10), fill="x")

        self.progress_bar = ctk.CTkProgressBar(
            progress_bar_frame, height=12, corner_radius=6,
            fg_color=self.colors["bg_primary"], progress_color=self.colors["success"]
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_bar_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["success"], width=40
        )
        self.progress_label.pack(side="right")

        speed_frame = ctk.CTkFrame(progress_frame, fg_color=self.colors["bg_primary"], corner_radius=8)
        speed_frame.pack(padx=15, pady=(0, 15), fill="x")

        speed_info_frame = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_info_frame.pack(fill="x", padx=10, pady=8)

        self.speed_value = ctk.CTkLabel(
            speed_info_frame, text="⚡ 0.00 MB/s", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["neon_glow"]
        )
        self.speed_value.pack(side="left")

        self.eta_label = ctk.CTkLabel(
            speed_info_frame, text="ETA: N/A", font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.eta_label.pack(side="right")

        console_header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        console_header_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="ew")

        console_label = ctk.CTkLabel(
            console_header_frame, 
            text="🖥️ Console Output:", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        console_label.pack(side="left")

        # Buttons for console actions
        console_buttons_frame = ctk.CTkFrame(console_header_frame, fg_color="transparent")
        console_buttons_frame.pack(side="right")

        self.clear_button = ctk.CTkButton(
            console_buttons_frame, text="🗑️ Clear", command=self.clear_console,
            font=ctk.CTkFont(size=11), height=25, width=60, corner_radius=6,
            fg_color=self.colors["bg_primary"], hover_color=self.colors["bg_secondary"],
            border_width=2, border_color=self.colors["clear_normal"]
        )
        self.clear_button.pack(side="left", padx=(0, 5))

        self.play_button = ctk.CTkButton(
            console_buttons_frame, text="▶️ Play", command=self.play_file,
            font=ctk.CTkFont(size=11), height=25, width=60, corner_radius=6,
            fg_color=self.colors["bg_primary"], hover_color=self.colors["bg_secondary"],
            border_width=2, border_color=self.colors["play_normal"],
            state="disabled" # Initially disabled
        )
        self.play_button.pack(side="right")

        console_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["console_bg"], corner_radius=10)
        console_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        console_frame.grid_propagate(False)

        self.output_text = ctk.CTkTextbox(
            console_frame, wrap="word", corner_radius=8, fg_color=self.colors["console_bg"],
            border_width=2, border_color=self.colors["border_color"],
            font=ctk.CTkFont(size=11, family="Consolas"), text_color=self.colors["console_info"]
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

        self._configure_text_tags()

        self.update_output("🎉 Welcome to YouTube Downloader Pro - Enhanced Edition!", msg_type="info")
        if self.YTDLP_PATH:
            self.update_output(f"✅ yt-dlp found at: {self.YTDLP_PATH}", msg_type="success")
        else:
            self.update_output("❌ yt-dlp not found! Please install it.", msg_type="error")

    def _configure_text_tags(self):
        self.output_text.tag_config("timestamp", foreground=self.colors["console_timestamp"])
        self.output_text.tag_config("icon", foreground=self.colors["console_icon"])
        self.output_text.tag_config("info", foreground=self.colors["console_info"])
        self.output_text.tag_config("success", foreground=self.colors["console_success"])
        self.output_text.tag_config("error", foreground=self.colors["console_error"])
        self.output_text.tag_config("warning", foreground=self.colors["console_warning"])
        self.output_text.tag_config("progress", foreground=self.colors["console_progress"])
        self.output_text.tag_config("highlight", foreground=self.colors["console_highlight"])

    def clear_console(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.update_output("🧹 Console cleared", msg_type="info")

    def _find_ytdlp(self):
        ytdlp_path = shutil.which("yt-dlp")
        if ytdlp_path:
            return ytdlp_path
        
        common_paths = [
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
            os.path.expanduser("~/.local/bin/yt-dlp"),
            "/home/isuru/.local/bin/yt-dlp",
            "/home/isuru/.gemini/projects/youtube_downloder/venv/bin/yt-dlp"
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, directory)

    def play_file(self):
        if not self.downloaded_file_path or not os.path.exists(self.downloaded_file_path):
            self.update_output("❌ No downloaded file found to play.", msg_type="error")
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.downloaded_file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.downloaded_file_path])
            else:  # Linux
                subprocess.run(["xdg-open", self.downloaded_file_path])
            
            self.update_output(f"🎬 Opening file: {os.path.basename(self.downloaded_file_path)}", msg_type="success")
        except Exception as e:
            self.update_output(f"❌ Error opening file: {e}", msg_type="error")

    def update_output(self, message, msg_type="info"):
        self.output_text.configure(state="normal")
        
        style_config = {
            "info": {"icon": "ℹ️", "color": "info"},
            "success": {"icon": "✅", "color": "success"},
            "error": {"icon": "❌", "color": "error"},
            "warning": {"icon": "⚠️", "color": "warning"},
            "progress": {"icon": "📊", "color": "progress"},
            "highlight": {"icon": "🔥", "color": "highlight"}
        }
        
        if msg_type == "info":
            message_lower = message.lower()
            if any(word in message_lower for word in ["completed", "success", "finished", "done"]):
                msg_type = "success"
            elif any(word in message_lower for word in ["error", "failed", "not found", "cannot", "unable"]):
                msg_type = "error"
            elif any(word in message_lower for word in ["warning", "already downloaded", "skip"]):
                msg_type = "warning"
            elif any(word in message_lower for word in ["download]", "downloading", "%", "progress"]):
                msg_type = "progress"
            elif any(word in message_lower for word in ["analyzing", "starting", "found"]):
                msg_type = "highlight"
        
        config = style_config.get(msg_type, style_config["info"])
        
        timestamp = time.strftime('%H:%M:%S')
        
        timestamp_start = self.output_text.index("end-1c")
        self.output_text.insert("end", f"[{timestamp}] ")
        timestamp_end = self.output_text.index("end-1c")
        self.output_text.tag_add("timestamp", timestamp_start, timestamp_end)
        
        icon_start = self.output_text.index("end-1c")
        self.output_text.insert("end", f"{config['icon']} ")
        icon_end = self.output_text.index("end-1c")
        self.output_text.tag_add("icon", icon_start, icon_end)
        
        message_start = self.output_text.index("end-1c")
        self.output_text.insert("end", f"{message}\n")
        message_end = self.output_text.index("end-1c")
        self.output_text.tag_add(config["color"], message_start, message_end)
        
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_progress(self, percentage, speed="0.00 MB/s", eta="N/A"):
        self.progress_bar.set(percentage / 100)
        self.progress_label.configure(text=f"{int(percentage)}%")
        self.speed_value.configure(text=f"⚡ {speed}")
        self.eta_label.configure(text=f"ETA: {eta}")
        
        if percentage < 30:
            self.progress_bar.configure(progress_color=self.colors["warning"])
        elif percentage < 70:
            self.progress_bar.configure(progress_color=self.colors["accent"])
        else:
            self.progress_bar.configure(progress_color=self.colors["success"])

    def _check_queue_for_updates(self):
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                self.update_progress(**progress_data)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue_for_updates)

    def _get_url_info(self, url):
        if not self.YTDLP_PATH:
            self.update_output("yt-dlp executable not found.", msg_type="error")
            return 'error', None
        try:
            command = [self.YTDLP_PATH, "--flat-playlist", "--dump-json", url]
            process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')

            if process.returncode != 0:
                command = [self.YTDLP_PATH, "--dump-json", url]
                process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
                info = json.loads(process.stdout)
                return 'video', info

            if process.stdout.strip():
                first_line = process.stdout.split('\n')[0]
                info = json.loads(first_line)
                if 'entries' in info:
                    return 'playlist', info
                else:
                    return 'video', info
            else:
                self.update_output("The URL is not a valid YouTube video or playlist.", msg_type="error")
                return 'error', None

        except Exception as e:
            self.update_output(f"An unexpected error occurred during URL info retrieval: {e}", msg_type="error")
            return 'error', None

    def start_download(self):
        if not self.YTDLP_PATH:
            self.update_output("yt-dlp not found! Please install it.", msg_type="error")
            return

        url = self.url_entry.get()
        if not url:
            self.update_output("Please enter a YouTube URL.", msg_type="error")
            return

        self.download_button.configure(
            state="disabled",
            text="⏳ Downloading...",
            fg_color=self.colors["bg_secondary"], # Match parent background
            border_color=self.colors["download_active"]
        )
        self.stop_button.configure(state="normal")
        self.play_button.configure(state="disabled")  # Disable play button during download
        self.update_progress(0)
        self.stop_flag.clear()

        self.update_output("🔍 Analyzing URL...", msg_type="highlight")
        analysis_thread = threading.Thread(target=self._analyze_and_download, args=(url,), daemon=True)
        analysis_thread.start()

    def _analyze_and_download(self, url):
        url_type, url_info = self._get_url_info(url)

        if url_type == 'error':
            self._reset_download_ui()
            return

        download_thread = threading.Thread(
            target=self._execute_download,
            args=(url, self.download_type_var.get(), self.resolution_var.get(), self.path_entry.get(), url_type, url_info),
            daemon=True
        )
        download_thread.start()

    def stop_download(self):
        self.stop_flag.set()
        if self.current_download_process:
            self.current_download_process.terminate()
            self.update_output("🛑 Download process terminated.", msg_type="warning")

        if self.current_download_file and os.path.exists(self.current_download_file):
            try:
                os.remove(self.current_download_file)
                self.update_output(f"🗑️ Partially downloaded file deleted: {os.path.basename(self.current_download_file)}", msg_type="info")
            except Exception as e:
                self.update_output(f"Error deleting partial file: {e}", msg_type="error")

        self._reset_download_ui()
        self.progress_queue.put({'percentage': 0, 'speed': "0.00 MB/s", 'eta': "N/A"})
        self.update_output("✅ Download stopped and cleaned up.", msg_type="success")

    def _reset_download_ui(self):
        self.download_button.configure(
            state="normal",
            text="⬇️ Download",
            fg_color=self.colors["bg_secondary"], # Match parent background
            border_color=self.colors["accent"], # Neon blue/cyan
            border_width=2
        )
        self.stop_button.configure(state="disabled")

    def _find_downloaded_file(self, download_path, video_title, is_audio=False):
        """Find the downloaded file in the specified directory"""
        try:
            # Clean the title for filename matching
            clean_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
            
            # Common extensions based on download type
            if is_audio:
                extensions = ['.mp3', '.m4a', '.webm', '.ogg']
            else:
                extensions = ['.mp4', '.webm', '.mkv', '.avi']
            
            # Search for files in the download directory
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path):
                    # Check if the file matches the title pattern and has correct extension
                    for ext in extensions:
                        if file.endswith(ext) and clean_title.lower() in file.lower():
                            return file_path
            
            # If exact match not found, try to find the most recent file with correct extension
            recent_files = []
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path):
                    for ext in extensions:
                        if file.endswith(ext):
                            recent_files.append((file_path, os.path.getmtime(file_path)))
            
            if recent_files:
                # Return the most recently modified file
                return max(recent_files, key=lambda x: x[1])[0]
                
        except Exception as e:
            self.update_output(f"Error finding downloaded file: {e}", msg_type="error")
        
        return None

    def _execute_download(self, url, download_type, resolution, download_path, url_type, url_info):
        command = [self.YTDLP_PATH, "--no-warnings", "--progress", "--newline", "--no-overwrites"]

        if url_type == 'playlist':
            playlist_title = url_info.get('title', 'Unknown Playlist').replace('/', '_').replace('\\', '_')
            playlist_folder = os.path.join(download_path, playlist_title)
            output_template = os.path.join(playlist_folder, "%(playlist_index)s - %(title)s.%(ext)s")
            self.update_output(f"📁 Detected playlist: {playlist_title}", msg_type="highlight")
            self.current_download_file = None
        else:
            output_template = os.path.join(download_path, "%(title)s.%(ext)s")
            self.current_download_file = None

        command.extend(["-o", output_template])

        resolution_map = {
            "Best Quality": "best",
            "720p HD": "720",
            "360p": "360",
            "144p": "144"
        }

        actual_resolution = resolution_map.get(resolution, "720")

        if download_type == "video":
            if actual_resolution == "best":
                format_string = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                format_string = f"bestvideo[height<={actual_resolution}][ext=mp4]+bestaudio[ext=m4a]/best[height<={actual_resolution}][ext=mp4]/best[height<={actual_resolution}]"
            command.extend(["-f", format_string])
        elif download_type == "audio":
            command.extend(["-x", "--audio-format", "mp3"])

        command.append(url)

        self.update_output(f"🚀 Starting download ({download_type} - {resolution})...", msg_type="highlight")

        try:
            self.current_download_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            video_title = None
            if url_type == 'video' and url_info:
                video_title = url_info.get('title', 'Unknown')

            for line in self.current_download_process.stdout:
                if self.stop_flag.is_set():
                    break

                if "[download]" in line and "%" in line:
                    self.update_output(line.strip(), msg_type="progress")
                elif "has already been downloaded" in line:
                    self.update_output(line.strip(), msg_type="warning")
                elif "Downloading video" in line:
                    self.update_output(line.strip(), msg_type="info")

                percentage = 0.0
                speed = "N/A"
                eta = "N/A"

                if "[download]" in line and "%" in line:
                    self.update_output(line.strip(), msg_type="progress")
                    
                    # Parse progress information
                    try:
                        # Extract percentage
                        percent_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                        if percent_match:
                            percentage = float(percent_match.group(1))
                        
                        # Extract speed
                        speed_match = re.search(r'(\d+(?:\.\d+)?(?:K|M|G)?i?B/s)', line)
                        if speed_match:
                            speed = speed_match.group(1)
                        
                        # Extract ETA
                        eta_match = re.search(r'ETA (\d+:\d+)', line)
                        if eta_match:
                            eta = eta_match.group(1)
                        
                        # Update progress in queue
                        self.progress_queue.put({
                            'percentage': percentage,
                            'speed': speed,
                            'eta': eta
                        })
                    except Exception as e:
                        self.update_output(f"Error parsing progress: {e}", msg_type="error")
                
                elif "has already been downloaded" in line:
                    self.update_output(line.strip(), msg_type="warning")
                elif "Downloading video" in line or "Downloading playlist" in line:
                    self.update_output(line.strip(), msg_type="info")
                elif "ERROR" in line or "error" in line.lower():
                    self.update_output(line.strip(), msg_type="error")
                elif line.strip():
                    self.update_output(line.strip(), msg_type="info")

            # Wait for process to complete
            self.current_download_process.wait()
            
            # Check for errors
            stderr_output = self.current_download_process.stderr.read()
            if stderr_output:
                self.update_output(f"Error output: {stderr_output}", msg_type="error")

            if self.current_download_process.returncode == 0 and not self.stop_flag.is_set():
                self.update_output("✅ Download completed successfully!", msg_type="success")
                self.progress_queue.put({'percentage': 100, 'speed': "0.00 MB/s", 'eta': "Complete"})
                
                # Try to find and set the downloaded file path
                if url_type == 'video' and url_info:
                    video_title = url_info.get('title', 'Unknown')
                    is_audio = download_type == "audio"
                    self.downloaded_file_path = self._find_downloaded_file(download_path, video_title, is_audio)
                    
                    if self.downloaded_file_path:
                        self.update_output(f"📁 File saved: {os.path.basename(self.downloaded_file_path)}", msg_type="success")
                        self.play_button.configure(state="normal")  # Enable play button
                    else:
                        self.update_output("⚠️ Download completed but file location could not be determined.", msg_type="warning")
                else:
                    self.update_output("📁 Playlist download completed!", msg_type="success")
                    
            elif self.stop_flag.is_set():
                self.update_output("🛑 Download cancelled by user.", msg_type="warning")
            else:
                self.update_output(f"❌ Download failed with return code: {self.current_download_process.returncode}", msg_type="error")

        except Exception as e:
            self.update_output(f"❌ Download error: {e}", msg_type="error")
        finally:
            self.current_download_process = None
            self.current_download_file = None
            self._reset_download_ui()

    def _find_downloaded_file(self, download_path, video_title, is_audio=False):
        """Find the downloaded file in the specified directory"""
        try:
            # Clean the title for filename matching
            clean_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
            
            # Common extensions based on download type
            if is_audio:
                extensions = ['.mp3', '.m4a', '.webm', '.ogg']
            else:
                extensions = ['.mp4', '.webm', '.mkv', '.avi']
            
            # Search for files in the download directory
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path):
                    # Check if the file matches the title pattern and has correct extension
                    for ext in extensions:
                        if file.endswith(ext) and clean_title.lower() in file.lower():
                            return file_path
            
            # If exact match not found, try to find the most recent file with correct extension
            recent_files = []
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path):
                    for ext in extensions:
                        if file.endswith(ext):
                            recent_files.append((file_path, os.path.getmtime(file_path)))
            
            if recent_files:
                # Return the most recently modified file
                return max(recent_files, key=lambda x: x[1])[0]
                
        except Exception as e:
            self.update_output(f"Error finding downloaded file: {e}", msg_type="error")
        
        return None

    def play_file(self):
        if not self.downloaded_file_path or not os.path.exists(self.downloaded_file_path):
            self.update_output("❌ No downloaded file found to play.", msg_type="error")
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.downloaded_file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.downloaded_file_path])
            else:  # Linux
                subprocess.run(["xdg-open", self.downloaded_file_path])
            
            self.update_output(f"🎬 Opening file: {os.path.basename(self.downloaded_file_path)}", msg_type="success")
        except Exception as e:
            self.update_output(f"❌ Error opening file: {e}", msg_type="error")


if __name__ == "__main__":
    app = YouTubeDownloaderPro()
    app.mainloop()
