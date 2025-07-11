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

        # Instance variables for managing download process
        self.current_download_process = None
        self.current_download_file = None
        self.stop_flag = threading.Event()

        # --- Modern App Configuration ---
        self.title("YouTube Downloader Pro")
        self.geometry("800x650") # Slightly taller
        self.minsize(700, 550) # Slightly taller min size
        ctk.set_appearance_mode("dark")
        # ctk.set_default_color_theme("blue") # Removed as per user request

        # Modern color palette with neon blue accents
        self.colors = {
            "bg_primary": "#0F0F23",
            "bg_secondary": "#1A1A2E",
            "bg_tertiary": "#16213E",
            "accent": "#00D9FF",  # Neon blue
            "accent_hover": "#00B8E6",  # Darker neon blue
            "text_primary": "#FFFFFF",
            "text_secondary": "#B8B8D1",
            "success": "#00FFD4",  # Neon cyan
            "warning": "#FFB800",
            "error": "#FF3B30",
            "neon_glow": "#00FFFF"
        }

        # Configure the main window
        self.configure(fg_color=self.colors["bg_primary"])

        # --- Grid Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Modern Header ---
        self.header_frame = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=self.colors["bg_secondary"],
            height=60
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=" YouTube Downloader Pro", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.title_label.pack(pady=15)

        # --- Main Content Frame with Modern Design ---
        self.main_content_frame = ctk.CTkFrame(
            self, 
            corner_radius=20,
            fg_color=self.colors["bg_secondary"],
            border_width=1,
            border_color=self.colors["bg_tertiary"]
        )
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_rowconfigure(6, weight=1) # Output console row

        # --- Input Section ---
        # URL
        self.url_label = ctk.CTkLabel(
            self.main_content_frame, 
            text=" YouTube URL:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.url_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            self.main_content_frame, 
            placeholder_text="Paste your YouTube URL here...",
            height=35,
            corner_radius=10,
            border_width=2,
            border_color=self.colors["bg_tertiary"],
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=20, pady=(15, 8), sticky="ew")

        # Download Type with modern styling
        self.type_label = ctk.CTkLabel(
            self.main_content_frame, 
            text=" Download Type:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.type_label.grid(row=1, column=0, padx=20, pady=8, sticky="w")
        
        self.download_type_var = ctk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(
            self.main_content_frame, 
            text=" Video", 
            variable=self.download_type_var, 
            value="video",
            font=ctk.CTkFont(size=13, weight="bold"),
            radiobutton_width=18,
            radiobutton_height=18
        )
        self.video_radio.grid(row=1, column=1, padx=20, pady=8, sticky="w")
        
        self.audio_radio = ctk.CTkRadioButton(
            self.main_content_frame, 
            text=" Audio (MP3)", 
            variable=self.download_type_var, 
            value="audio",
            font=ctk.CTkFont(size=13, weight="bold"),
            radiobutton_width=18,
            radiobutton_height=18
        )
        self.audio_radio.grid(row=1, column=2, padx=20, pady=8, sticky="w")

        # Resolution with modern dropdown
        self.resolution_label = ctk.CTkLabel(
            self.main_content_frame, 
            text="⚙️ Resolution:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.resolution_label.grid(row=2, column=0, padx=20, pady=8, sticky="w")
        
        self.resolution_options = ["best", "720p", "360p", "144p"]
        self.resolution_var = ctk.StringVar(value="720p")
        self.resolution_menu = ctk.CTkOptionMenu(
            self.main_content_frame, 
            variable=self.resolution_var, 
            values=self.resolution_options,
            height=35,
            corner_radius=10,
            fg_color=self.colors["bg_tertiary"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_hover"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.resolution_menu.grid(row=2, column=1, columnspan=2, padx=20, pady=8, sticky="ew")

        # Download path with modern styling
        self.path_label = ctk.CTkLabel(
            self.main_content_frame, 
            text=" Download Path:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.path_label.grid(row=3, column=0, padx=20, pady=8, sticky="w")
        
        self.path_entry = ctk.CTkEntry(
            self.main_content_frame, 
            placeholder_text="Select download directory",
            height=35,
            corner_radius=10,
            border_width=2,
            border_color=self.colors["bg_tertiary"],
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=13)
        )
        self.path_entry.grid(row=3, column=1, padx=20, pady=8, sticky="ew")
        self.path_entry.insert(0, "/home/isuru/Downloads")
        
        self.browse_button = ctk.CTkButton(
            self.main_content_frame, 
            text=" Browse", 
            command=self.browse_path, 
            width=100,
            height=35,
            corner_radius=10,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["accent"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.browse_button.grid(row=3, column=2, padx=20, pady=8)

        # --- Download and Stop Buttons --- (New Row)
        self.button_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.download_button = ctk.CTkButton(
            self.button_frame, 
            text=" Download", 
            command=self.start_download, 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=12,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color=self.colors["text_primary"]
        )
        self.download_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.stop_button = ctk.CTkButton(
            self.button_frame, 
            text=" Stop", 
            command=self.stop_download, 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=12,
            fg_color=self.colors["error"],
            hover_color="#CC2929", # Darker red for hover
            text_color=self.colors["text_primary"],
            state="disabled" # Disabled by default
        )
        self.stop_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # --- Modern Progress Section --- (New Row)
        self.progress_section_frame = ctk.CTkFrame(
            self.main_content_frame,
            fg_color=self.colors["bg_tertiary"],
            corner_radius=15
        )
        self.progress_section_frame.grid(row=5, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="ew")
        self.progress_section_frame.grid_columnconfigure(0, weight=1) # Progress bar takes most space
        self.progress_section_frame.grid_columnconfigure(1, weight=0) # Percentage label

        # Progress Bar and Percentage
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_section_frame,
            height=12,
            corner_radius=6,
            fg_color=self.colors["bg_primary"],
            progress_color=self.colors["success"],
            border_width=1,
            border_color=self.colors["bg_secondary"]
        )
        self.progress_bar.grid(row=0, column=0, padx=(15, 5), pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self.progress_section_frame, 
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"],
            width=50
        )
        self.progress_label.grid(row=0, column=1, padx=(5, 15), pady=10)

        # Speed and ETA Display
        self.speed_eta_frame = ctk.CTkFrame(
            self.progress_section_frame,
            fg_color="transparent" # Transparent background within the section frame
        )
        self.speed_eta_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=(0, 10), sticky="ew")
        self.speed_eta_frame.grid_columnconfigure(1, weight=1)

        self.speed_icon_label = ctk.CTkLabel(
            self.speed_eta_frame,
            text="⚡",
            font=ctk.CTkFont(size=20),
            text_color=self.colors["neon_glow"],
            width=30
        )
        self.speed_icon_label.grid(row=0, column=0, padx=(15, 5), pady=0, sticky="w")

        self.speed_label = ctk.CTkLabel(
            self.speed_eta_frame,
            text="Download Speed:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.speed_label.grid(row=0, column=1, padx=5, pady=0, sticky="w")

        self.speed_value_label = ctk.CTkLabel(
            self.speed_eta_frame,
            text="0.00 MB/s",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["neon_glow"]
        )
        self.speed_value_label.grid(row=0, column=2, padx=(5, 15), pady=0, sticky="e")

        self.eta_label = ctk.CTkLabel(
            self.speed_eta_frame,
            text="ETA: N/A",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.eta_label.grid(row=1, column=0, columnspan=3, padx=(15, 15), pady=(0, 0), sticky="ew")

        # --- Modern Output Console --- (New Row)
        self.output_text = ctk.CTkTextbox(
            self.main_content_frame, 
            wrap="word",
            corner_radius=12,
            fg_color=self.colors["bg_primary"],
            border_width=2,
            border_color=self.colors["bg_tertiary"],
            font=ctk.CTkFont(size=12, family="Consolas"),
            text_color=self.colors["text_primary"]
        )
        self.output_text.grid(row=6, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")
        self.update_output(" Welcome to YouTube Downloader Pro - Modern Edition!")

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, directory)

    def update_output(self, message, is_error=False):
        self.output_text.configure(state="normal")
        
        # Enhanced logging with emojis and better formatting
        if is_error:
            prefix = "❌ ERROR: "
        elif "completed" in message.lower():
            prefix = "✅ SUCCESS: "
        elif "starting" in message.lower():
            prefix = " INFO: "
        else:
            prefix = "ℹ️  INFO: "
            
        timestamp = time.strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {prefix}{message}\n"
        
        self.output_text.insert("end", formatted_message)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_progress(self, percentage, speed="0.00 MB/s", eta="N/A"):
        self.progress_bar.set(percentage / 100)
        self.progress_label.configure(text=f"{int(percentage)}%")
        
        # Update speed display with neon glow effect
        self.speed_value_label.configure(text=speed)
        self.eta_label.configure(text=f"ETA: {eta}")
        
        # Update progress bar color based on percentage
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

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.update_output("Please enter a YouTube URL.", is_error=True)
            return
        
        # Disable download button, enable stop button
        self.download_button.configure(
            state="disabled", 
            text=" Downloading...",
            fg_color=self.colors["warning"]
        )
        self.stop_button.configure(state="normal")
        self.update_progress(0)
        self.stop_flag.clear() # Clear stop flag for new download
        
        download_thread = threading.Thread(target=self._execute_download, daemon=True)
        download_thread.start()

    def stop_download(self):
        self.stop_flag.set() # Set the stop flag
        if self.current_download_process:
            self.current_download_process.terminate() # Terminate the yt-dlp process
            self.update_output("Download process terminated.")
        
        if self.current_download_file and os.path.exists(self.current_download_file):
            try:
                os.remove(self.current_download_file)
                self.update_output(f"Partially downloaded file deleted: {os.path.basename(self.current_download_file)}")
            except Exception as e:
                self.update_output(f"Error deleting partial file: {e}", is_error=True)
        
        # Reset UI elements
        self.download_button.configure(
            state="normal", 
            text=" Download",
            fg_color=self.colors["accent"]
        )
        self.stop_button.configure(state="disabled")
        self.progress_queue.put({'percentage': 0, 'speed': "0.00 MB/s", 'eta': "N/A"})
        self.update_output("Download stopped and cleaned up.")

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
            
            self.current_download_file = final_output_path # Store for potential deletion

        except subprocess.CalledProcessError as e:
            self.update_output(f"Could not determine filename. Download aborted. Error: {e}", is_error=True)
            self.download_button.configure(
                state="normal", 
                text=" Download",
                fg_color=self.colors["accent"]
            )
            self.stop_button.configure(state="disabled")
            return

        # --- Build the final download command ---
        command = ["yt-dlp", "--no-warnings", "--progress", "--newline"]
        
        if download_type == "video":
            if resolution == "best":
                format_string = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                res_height = resolution[:-1]
                format_string = f"bestvideo[height<={res_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res_height}][ext=mp4]/best[height<={res_height}]"
            command.extend(["-f", format_string])
        elif download_type == "audio":
            command.extend(["-x", "--audio-format", "mp3"])

        command.extend(["-o", final_output_path, url])

        self.update_output(f"Starting download: {os.path.basename(final_output_path)}")
        
        self.current_download_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

        for line in self.current_download_process.stdout:
            if self.stop_flag.is_set(): # Check stop flag during download
                break

            # Also print to console for debugging, and update the GUI
            print(line.strip())
            self.update_output(line.strip())
            
            # Initialize with default values
            percentage = 0.0
            speed = "N/A"
            eta = "N/A"

            # Parse progress percentage, speed, and ETA
            progress_match = re.search(r"(\d+\.?\d*)%\s+of\s+.*?\s+at\s+([\d\.]+(?:K|M|G)?i?B/s)(?:\s+ETA\s+(.*))?", line)
            if progress_match:
                try:
                    percentage = float(progress_match.group(1))
                    speed = progress_match.group(2)
                    eta = progress_match.group(3) if progress_match.group(3) else "N/A"
                    
                    # Ensure consistent speed formatting
                    if "KiB/s" in speed:
                        speed = speed.replace("KiB/s", " KB/s")
                    elif "MiB/s" in speed:
                        speed = speed.replace("MiB/s", " MB/s")
                    elif "GiB/s" in speed:
                        speed = speed.replace("GiB/s", " GB/s")
                    elif "B/s" not in speed and "KB/s" not in speed and "MB/s" not in speed and "GB/s" not in speed:
                        speed = speed + " B/s"
                except (ValueError, IndexError) as e:
                    # Log parsing errors but don't crash
                    print(f"Error parsing progress line: {line.strip()} - {e}")
                    percentage = 0.0 # Reset to default on error
                    speed = "N/A"
                    eta = "N/A"
                
                self.progress_queue.put({'percentage': percentage, 'speed': speed, 'eta': eta})

        self.current_download_process.wait()

        if not self.stop_flag.is_set(): # Only show success/failure if not stopped by user
            if self.current_download_process.returncode == 0:
                self.update_output("Download completed successfully!")
                self.progress_queue.put({'percentage': 100, 'speed': "0.00 MB/s", 'eta': "00:00"})
            else:
                self.update_output("Download failed.", is_error=True)
            
        # Reset button to original state
        self.download_button.configure(
            state="normal", 
            text=" Download",
            fg_color=self.colors["accent"]
        )
        self.stop_button.configure(state="disabled")
        
        # Reset progress bar and speed for the next download
        time.sleep(1) # Give a moment before resetting
        self.progress_queue.put({'percentage': 0, 'speed': "0.00 MB/s", 'eta': "N/A"})
        
        self.current_download_process = None
        self.current_download_file = None

if __name__ == "__main__":
    app = YouTubeDownloaderPro()
    app.mainloop()