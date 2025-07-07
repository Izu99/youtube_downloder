#!/home/isuru/.gemini/projects/venv/bin/python
# YouTube Video and Audio Downloader GUI with Progress Bar

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import json
import os
import re
from pathlib import Path

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Style configuration for dark theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure dark theme colors
        self.style.configure('TFrame', background='#1a1a1a')
        self.style.configure('TLabel', background='#1a1a1a', foreground='#ffffff', font=('Arial', 10))
        self.style.configure('TButton', background='#333333', foreground='#ffffff', font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', background='#2d2d2d', foreground='#ffffff', insertcolor='#ffffff')
        self.style.configure('TCombobox', background='#2d2d2d', foreground='#ffffff')
        self.style.configure('Horizontal.TProgressbar', background='#4CAF50', troughcolor='#333333')
        
        # Map styles for hover effects
        self.style.map('TButton',
                      background=[('active', '#4CAF50'), ('pressed', '#45a049')])
        
        self.setup_ui()
        self.download_path = os.path.expanduser('~/Downloads')
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🎬 YouTube Downloader Pro", 
                              font=('Arial', 24, 'bold'), 
                              bg='#1a1a1a', fg='#4CAF50')
        title_label.pack(pady=(0, 20))
        
        # URL input section
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(url_frame, text="📎 YouTube URL:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.url_entry = ttk.Entry(url_frame, font=('Arial', 11), width=70)
        self.url_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Options section
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Download type
        type_frame = ttk.Frame(options_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="📥 Download Type:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value="video")
        ttk.Radiobutton(type_frame, text="🎥 Video", variable=self.type_var, value="video").pack(side=tk.LEFT, padx=(20, 10))
        ttk.Radiobutton(type_frame, text="🎵 Audio", variable=self.type_var, value="audio").pack(side=tk.LEFT)
        
        # Resolution selection
        resolution_frame = ttk.Frame(options_frame)
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="📺 Resolution:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.resolution_var = tk.StringVar(value="720p")
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, 
                                       values=["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"],
                                       width=10, state="readonly")
        resolution_combo.pack(side=tk.LEFT, padx=(20, 0))
        
        # Download path
        path_frame = ttk.Frame(options_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="📁 Download Path:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_entry = ttk.Entry(path_input_frame, font=('Arial', 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.path_entry.insert(0, self.download_path)
        
        browse_btn = ttk.Button(path_input_frame, text="📂 Browse", command=self.browse_path, width=10)
        browse_btn.pack(side=tk.RIGHT)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(20, 15))
        
        self.progress_label = tk.Label(progress_frame, text="Ready to download", 
                                      font=('Arial', 11), bg='#1a1a1a', fg='#cccccc')
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400, height=20)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.percentage_label = tk.Label(progress_frame, text="0%", 
                                        font=('Arial', 10, 'bold'), bg='#1a1a1a', fg='#4CAF50')
        self.percentage_label.pack(anchor=tk.E, pady=(5, 0))
        
        # Download button
        self.download_btn = ttk.Button(main_frame, text="⬇️ Start Download", 
                                      command=self.start_download, 
                                      style='TButton')
        self.download_btn.pack(pady=(20, 0))
        
        # Status/Info section
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        ttk.Label(info_frame, text="📋 Status:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Create scrollable text area
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.status_text = tk.Text(text_frame, height=10, bg='#2d2d2d', fg='#ffffff', 
                                  font=('Consolas', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_message("Welcome to YouTube Downloader Pro! 🎉")
        self.log_message("Enter a YouTube URL and click 'Start Download' to begin.")
        
    def browse_path(self):
        folder_path = filedialog.askdirectory(initialdir=self.download_path)
        if folder_path:
            self.download_path = folder_path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
    
    def log_message(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, percentage, status_text):
        self.progress_bar['value'] = percentage
        self.percentage_label.config(text=f"{percentage:.1f}%")
        self.progress_label.config(text=status_text)
        self.root.update_idletasks()
    
    def parse_progress(self, line):
        # Parse yt-dlp progress output
        if '[download]' in line and '%' in line:
            # Extract percentage
            match = re.search(r'(\d+\.?\d*)%', line)
            if match:
                percentage = float(match.group(1))
                
                # Extract speed and ETA if available
                speed_match = re.search(r'at\s+([0-9.]+[A-Za-z/]+)', line)
                eta_match = re.search(r'ETA\s+([0-9:]+)', line)
                
                status = f"Downloading... {percentage:.1f}%"
                if speed_match:
                    status += f" at {speed_match.group(1)}"
                if eta_match:
                    status += f" (ETA: {eta_match.group(1)})"
                
                return percentage, status
        return None, None
    
    def get_video_info(self, url):
        """Get video information using yt-dlp"""
        try:
            command = [
                '/home/isuru/.gemini/projects/venv/bin/yt-dlp',
                '--dump-json',
                url
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"yt-dlp error: {result.stderr}")
            return json.loads(result.stdout)
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def download_video(self, url, resolution, download_path):
        """Download video with progress tracking"""
        try:
            self.log_message(f"🔍 Getting video information...")
            data = self.get_video_info(url)
            title = data['title']
            
            self.log_message(f"📹 Title: {title}")
            self.log_message(f"🎯 Target resolution: {resolution}")
            
            # Build download command
            command = [
                '/home/isuru/.gemini/projects/venv/bin/yt-dlp',
                '-f', f'best[height<={resolution[:-1]}]',
                '-o', os.path.join(download_path, '%(title)s.%(ext)s'),
                '--newline',  # Force newline for each progress update
                url
            ]
            
            self.log_message(f"⬇️ Starting download...")
            
            # Start download process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line:
                        percentage, status = self.parse_progress(line)
                        if percentage is not None:
                            self.update_progress(percentage, status)
                        else:
                            self.log_message(line)
            
            if process.returncode == 0:
                self.update_progress(100, "Download completed successfully! ✅")
                self.log_message(f"✅ Download completed successfully!")
                self.log_message(f"📁 File saved in: {download_path}")
            else:
                raise Exception("Download failed")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.update_progress(0, "Download failed ❌")
    
    def download_audio(self, url, download_path):
        """Download audio with progress tracking"""
        try:
            self.log_message(f"🔍 Getting audio information...")
            data = self.get_video_info(url)
            title = data['title']
            
            self.log_message(f"🎵 Title: {title}")
            
            # Build download command
            command = [
                '/home/isuru/.gemini/projects/venv/bin/yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '-o', os.path.join(download_path, '%(title)s.%(ext)s'),
                '--newline',
                url
            ]
            
            self.log_message(f"⬇️ Starting audio download...")
            
            # Start download process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line:
                        percentage, status = self.parse_progress(line)
                        if percentage is not None:
                            self.update_progress(percentage, status)
                        else:
                            self.log_message(line)
            
            if process.returncode == 0:
                self.update_progress(100, "Audio download completed successfully! ✅")
                self.log_message(f"✅ Audio download completed successfully!")
                self.log_message(f"📁 File saved in: {download_path}")
            else:
                raise Exception("Audio download failed")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.update_progress(0, "Audio download failed ❌")
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        download_path = self.path_entry.get().strip()
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except:
                messagebox.showerror("Error", "Invalid download path")
                return
        
        # Disable download button during download
        self.download_btn.config(state='disabled', text="⏳ Downloading...")
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.percentage_label.config(text="0%")
        self.progress_label.config(text="Preparing download...")
        
        # Clear status text
        self.status_text.delete(1.0, tk.END)
        
        # Start download in separate thread
        def download_thread():
            try:
                if self.type_var.get() == "video":
                    self.download_video(url, self.resolution_var.get(), download_path)
                else:
                    self.download_audio(url, download_path)
            finally:
                # Re-enable download button
                self.download_btn.config(state='normal', text="⬇️ Start Download")
        
        threading.Thread(target=download_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
