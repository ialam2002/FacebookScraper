
"""
Tab for configuring scraping parameters and starting scraping jobs.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext

class ScrapingTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_scraping_tab()

    def build_scraping_tab(self):
        frame = self.frame
        header = ctk.CTkLabel(frame, text="Scraping Parameters", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(pady=(0, 15))

        urls_label = ctk.CTkLabel(frame, text="Profile URLs (one per line or comma-separated):")
        urls_label.pack(anchor="w", padx=10, pady=(0, 5))

        self.app.profile_urls_text = scrolledtext.ScrolledText(frame, height=8, wrap="word", font=("Consolas", 10))
        self.app.profile_urls_text.pack(fill="x", padx=10, pady=(0, 15))

        params_frame = ctk.CTkFrame(frame)
        params_frame.pack(fill="x", padx=10, pady=10)

        depth_label = ctk.CTkLabel(params_frame, text="Depth:")
        depth_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.app.depth_spinbox = ctk.CTkEntry(params_frame, width=50)
        self.app.depth_spinbox.insert(0, "0")
        self.app.depth_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Cap toggle
        self.app.cap_enabled_var = ctk.BooleanVar(value=False)
        cap_checkbox = ctk.CTkCheckBox(params_frame, text="Enable Max Friends Cap", variable=self.app.cap_enabled_var)
        cap_checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        friends_label = ctk.CTkLabel(params_frame, text="Max Friends per Profile:")
        friends_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.app.max_friends_spinbox = ctk.CTkEntry(params_frame, width=50)
        self.app.max_friends_spinbox.insert(0, "200")
        self.app.max_friends_spinbox.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        output_label = ctk.CTkLabel(frame, text="Output File (Optional - leave blank to save in memory only):")
        output_label.pack(anchor="w", padx=10, pady=(10, 5))

        output_frame = ctk.CTkFrame(frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=10, pady=5)

        self.app.output_file_entry = ctk.CTkEntry(output_frame)
        self.app.output_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_btn = ctk.CTkButton(output_frame, text="Browse", width=80, command=self.app.browse_output_file)
        browse_btn.pack(side="left")

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=15)

        self.app.start_button = ctk.CTkButton(button_frame, text="Start Scraping", command=self.app.start_scraping)
        self.app.start_button.pack(side="left", padx=5)

        self.app.stop_button = ctk.CTkButton(button_frame, text="Stop Scraping", command=self.app.stop_scraping, state="disabled")
        self.app.stop_button.pack(side="left", padx=5)

        self.app.progress_label = ctk.CTkLabel(frame, text="Ready", text_color="gray")
        self.app.progress_label.pack(pady=(5, 0))

        self.app.progress_bar = ctk.CTkProgressBar(frame, orientation="horizontal", mode="determinate")
        self.app.progress_bar.set(0)
        self.app.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
