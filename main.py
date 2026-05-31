import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading  # Running the download in a thread keeps the GUI from freezing

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python Downloader with Progress Tracker")
        self.geometry("550x450")
        self.resizable(False, False)
        
        self.save_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.format_var = ctk.StringVar(value="mp4")
        self.create_widgets()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="YouTube Downloader", font=("Arial", 20, "bold"))
        title_label.pack(pady=15)

        # Folder Selection
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(pady=5, fill="x", padx=30)
        self.path_label = ctk.CTkLabel(folder_frame, text=f"Save to: {self.save_path}", wraplength=350, anchor="w")
        self.path_label.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        browse_btn = ctk.CTkButton(folder_frame, text="Browse", width=80, command=self.browse_folder)
        browse_btn.pack(side="right", padx=10, pady=10)

        # Format Selection
        format_frame = ctk.CTkFrame(self)
        format_frame.pack(pady=5, fill="x", padx=30)
        mp4_radio = ctk.CTkRadioButton(format_frame, text="Video (MP4)", variable=self.format_var, value="mp4")
        mp4_radio.pack(side="left", padx=50, pady=10)
        m4a_radio = ctk.CTkRadioButton(format_frame, text="Audio (M4A)", variable=self.format_var, value="m4a")
        m4a_radio.pack(side="left", padx=50, pady=10)

        # URL Input
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste YouTube URL here...", width=490)
        self.url_entry.pack(pady=15)

        # --- Real-Time Statistics Panel ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(pady=5, fill="x", padx=40)
        
        self.size_label = ctk.CTkLabel(self.stats_frame, text="File Size: --", font=("Arial", 12))
        self.size_label.pack(anchor="w")
        
        self.speed_label = ctk.CTkLabel(self.stats_frame, text="Speed: --", font=("Arial", 12))
        self.speed_label.pack(anchor="w")
        
        self.eta_label = ctk.CTkLabel(self.stats_frame, text="Time Remaining: --", font=("Arial", 12))
        self.eta_label.pack(anchor="w")

        # Action Button
        self.download_btn = ctk.CTkButton(self, text="Download Now", font=("Arial", 14, "bold"), height=40, command=self.start_download_thread)
        self.download_btn.pack(pady=15)

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.save_path)
        if selected_dir:
            self.save_path = selected_dir
            self.path_label.configure(text=f"Save to: {self.save_path}")

    # This hook functions automatically intercept updates sent by yt-dlp
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # 1. Total/Estimated File Size
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            size_mb = total_bytes / (1024 * 1024)
            self.size_label.configure(text=f"File Size: {size_mb:.2f} MB")
            
            # 2. Download Speed
            speed = d.get('speed', 0)
            if speed:
                speed_mb = speed / (1024 * 1024)
                self.speed_label.configure(text=f"Speed: {speed_mb:.2f} MB/s")
            else:
                self.speed_label.configure(text="Speed: Calculating...")

            # 3. Time Remaining (ETA)
            eta = d.get('eta')
            if eta is not None:
                minutes, seconds = divmod(eta, 60)
                if minutes > 0:
                    self.eta_label.configure(text=f"Time Remaining: {minutes}m {seconds}s")
                else:
                    self.eta_label.configure(text=f"Time Remaining: {seconds}s")
            else:
                self.eta_label.configure(text="Time Remaining: Calculating...")
                
        elif d['status'] == 'finished':
            self.speed_label.configure(text="Speed: Finished")
            self.eta_label.configure(text="Time Remaining: 0s")

    def start_download_thread(self):
        # We start the download in a secondary background thread so the 
        # application interface remains smooth and responsive while updating data.
        download_thread = threading.Thread(target=self.run_download)
        download_thread.start()

    def run_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste a valid YouTube URL.")
            return

        self.download_btn.configure(state="disabled")
        
        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],  # Connects code to the live statistics function
        }

        if self.format_var.get() == "m4a":
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
        else:
            ydl_opts['format'] = 'best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "File downloaded successfully!")
            self.url_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Clear text values and restore the button functionality
            self.size_label.configure(text="File Size: --")
            self.speed_label.configure(text="Speed: --")
            self.eta_label.configure(text="Time Remaining: --")
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()