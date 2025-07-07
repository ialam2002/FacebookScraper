import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from profile_search.search import FaceMatcher, ImageProcessor
from PIL import Image, ImageTk
import requests
import io
import csv
import os
import json

class SearchTab:
    def display_results(self, results):
        """
        Display search results in the results_container frame in the Search tab.
        Each result shows the name, profile URL, similarity score, and the profile picture if available.
        """
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()

        if not results:
            no_results = ctk.CTkLabel(
                self.results_container,
                text="No matching profiles found.",
                text_color="gray",
                fg_color="black"
            )
            no_results.pack(pady=20)
            return

        # Store image references to prevent garbage collection
        if not hasattr(self, '_profile_img_refs'):
            self._profile_img_refs = []
        self._profile_img_refs.clear()

        for idx, profile in enumerate(results, 1):
            # Create frame for each result (black background)
            result_frame = ctk.CTkFrame(self.results_container, fg_color="black", border_width=1, corner_radius=8)
            result_frame.pack(fill="x", padx=10, pady=8, expand=True)

            # Left frame for image
            left_frame = ctk.CTkFrame(result_frame, fg_color="black")
            left_frame.pack(side="left", padx=10, pady=10)

            # Try to load and display profile picture
            try:
                if profile.get('profile_pic'):
                    response = requests.get(profile['profile_pic'])
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((90, 90), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._profile_img_refs.append(photo)
                    img_label = ctk.CTkLabel(left_frame, image=photo, text="", width=90, height=90, fg_color="black")
                    img_label.pack(padx=5, pady=5)
                else:
                    placeholder = ctk.CTkLabel(left_frame, text="No\nImage", width=90, height=90, fg_color="black", text_color="white")
                    placeholder.pack(padx=5, pady=5)
            except Exception as e:
                print(f"Error loading profile image: {e}")
                placeholder = ctk.CTkLabel(left_frame, text="No\nImage", width=90, height=90, fg_color="black", text_color="white")
                placeholder.pack(padx=5, pady=5)

            # Right frame for text info and button
            info_frame = ctk.CTkFrame(result_frame, fg_color="black")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            # Profile name and URL
            name_label = ctk.CTkLabel(
                info_frame, 
                text=f"Name: {profile.get('name', 'Unknown')}", 
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="black",
                text_color="white"
            )
            name_label.pack(anchor="w", pady=2)

            url = profile.get('url', 'N/A')
            url_label = ctk.CTkLabel(
                info_frame,
                text=f"Profile URL: {url}",
                text_color="#1a0dab" if url != 'N/A' else "gray",
                cursor="hand2" if url != 'N/A' else "arrow",
                fg_color="black"
            )
            url_label.pack(anchor="w", pady=2)
            if url != 'N/A':
                url_label.bind("<Button-1>", lambda e, url=url: self.app.open_url(url))

            # Similarity score (distance)
            distance = profile.get('distance', float('inf'))
            if distance != float('inf'):
                # Lower distance = better match. Show as "Match Score: 1 - distance" for user clarity
                match_score = max(0.0, 1.0 - distance)
                score_text = f"Match Score: {match_score:.2f} (Distance: {distance:.2f})"
            else:
                score_text = "Match Score: N/A"
            score_label = ctk.CTkLabel(
                info_frame,
                text=score_text,
                font=ctk.CTkFont(size=13),
                fg_color="black",
                text_color="white"
            )
            score_label.pack(anchor="w", pady=2)

            # Add to Scraper button
            add_button = ctk.CTkButton(
                info_frame,
                text="Add to Scraper",
                command=lambda url=url: self.app.add_to_scraper(url),
                width=140
            )
            add_button.pack(anchor="w", pady=8)

        # Update status
        self.search_status.configure(text=f"Found {len(results)} result(s).", text_color="green")
    def __init__(self, parent, app):
        self.app = app  # Reference to main app for controller access
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_search_tab()

    def build_search_tab(self):
        frame = self.frame
        # Search parameters frame
        params_frame = ctk.CTkFrame(frame)
        params_frame.pack(fill="x", padx=10, pady=10)

        # Name entry
        name_label = ctk.CTkLabel(params_frame, text="Full Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(params_frame, width=300)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Image upload
        image_label = ctk.CTkLabel(params_frame, text="Reference Image:")
        image_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        image_btn_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        image_btn_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.image_path_entry = ctk.CTkEntry(image_btn_frame)
        self.image_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_img_btn = ctk.CTkButton(
            image_btn_frame, 
            text="Browse", 
            width=80, 
            command=self.browse_image
        )
        browse_img_btn.pack(side="left")

        # Batch upload
        batch_label = ctk.CTkLabel(
            params_frame,
            text="Or upload Excel/CSV/JSON (columns: name, folder, image_name).\nIf folder is blank, image_name is treated as a URL."
        )
        batch_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        batch_btn_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        batch_btn_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.batch_path_entry = ctk.CTkEntry(batch_btn_frame)
        self.batch_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_batch_btn = ctk.CTkButton(
            batch_btn_frame,
            text="Browse",
            width=80,
            command=self.browse_batch_file
        )
        browse_batch_btn.pack(side="left")

        # Search button
        search_btn = ctk.CTkButton(
            frame, 
            text="Search Profiles", 
            command=self.start_search
        )
        search_btn.pack(pady=10)

        # Stop Search button
        self.stop_search_button = ctk.CTkButton(
            frame,
            text="Stop Search",
            command=self.stop_search,
            state="disabled"
        )
        self.stop_search_button.pack(pady=5)

        # Results frame
        results_frame = ctk.CTkFrame(frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Use a single scrollable frame for results
        self.results_container = ctk.CTkScrollableFrame(results_frame)
        self.results_container.pack(fill="both", expand=True)

        # Status label
        self.search_status = ctk.CTkLabel(frame, text="Ready", text_color="gray")
        self.search_status.pack(pady=5)

        # Progress bar
        self.search_progress = ctk.CTkProgressBar(frame, mode="determinate")
        self.search_progress.set(0)
        self.search_progress.pack(fill="x", padx=10, pady=(0, 10))

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Reference Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file_path:
            self.image_path_entry.delete(0, "end")
            self.image_path_entry.insert(0, file_path)

    def browse_batch_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Excel/CSV/JSON files", "*.xlsx *.csv *.json"), ("All files", "*.*")]
        )
        if file_path:
            self.batch_path_entry.delete(0, "end")
            self.batch_path_entry.insert(0, file_path)
            self.name_entry.configure(state="disabled")

    def start_search(self):
        if not self.app.scraper_controller.logged_in:
            messagebox.showerror("Error", "Please login first in the Configuration tab")
            return
        name = self.name_entry.get().strip()
        image_path = self.image_path_entry.get().strip()
        batch_path = self.batch_path_entry.get().strip()
        if not (name and image_path) and not batch_path:
            messagebox.showerror("Error", "Please provide either name and image OR a batch file")
            return
        self.search_status.configure(text="Starting search...", text_color="gray")
        self.search_progress.set(0)
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.search_active = True
        self.stop_search_button.configure(state="normal")
        threading.Thread(
            target=self.run_search,
            args=(name, image_path, batch_path),
            daemon=True
        ).start()

    def run_search(self, name, image_path, batch_path):
        try:
            matcher = FaceMatcher(
                self.app.email_entry.get(),
                self.app.password_entry.get(),
                driver=getattr(self.app.scraper_controller.scraper, 'driver', None)
            )
            if batch_path:
                self.process_batch_file(matcher, batch_path)
            else:
                target_img = ImageProcessor.load_image(image_path)
                self.app.after(0, lambda: self.search_status.configure(
                    text=f"Searching for {name}...", 
                    text_color="gray"
                ))
                matches = []
                if self.search_active:
                    matches = matcher.find_matches(target_img, name)
                if self.search_active:
                    self.app.after(0, lambda: self.display_results(matches))
                else:
                    self.app.after(0, lambda: self.search_status.configure(text="Search stopped by user.", text_color="orange"))
        except Exception as e:
            self.app.after(0, lambda: self.search_status.configure(
                text=f"Error: {str(e)}", 
                text_color="red"
            ))
            self.app.after(0, lambda e=e: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        finally:
            self.search_active = False
            self.app.after(0, lambda: self.search_progress.set(0))
            self.app.after(0, lambda: self.stop_search_button.configure(state="disabled"))

    def stop_search(self):
        self.search_active = False
        self.search_status.configure(text="Search stopped by user.", text_color="orange")
        self.stop_search_button.configure(state="disabled")

    def process_batch_file(self, matcher, batch_path):
        import pandas as pd
        try:
            if not os.path.exists(batch_path):
                self.app.after(0, lambda: messagebox.showerror("Error", f"Batch file not found: {batch_path}"))
                return
            batch_data = []
            if batch_path.lower().endswith('.json'):
                with open(batch_path, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
            elif batch_path.lower().endswith('.csv'):
                with open(batch_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get('name') or row.get('Name')
                        folder = row.get('folder') or row.get('Folder') or ''
                        image_name = row.get('image') or row.get('Image') or row.get('image_name') or row.get('Image Name') or ''
                        if name and image_name:
                            batch_data.append({'name': name, 'folder': folder, 'image_name': image_name})
            elif batch_path.lower().endswith('.xlsx'):
                df = pd.read_excel(batch_path)
                for _, row in df.iterrows():
                    name = row.get('name') or row.get('Name')
                    folder = row.get('folder') or row.get('Folder') or ''
                    image_name = row.get('image') or row.get('Image') or row.get('image_name') or row.get('Image Name') or ''
                    if pd.isna(name) or pd.isna(image_name):
                        continue
                    batch_data.append({'name': name, 'folder': folder, 'image_name': image_name})
            else:
                self.app.after(0, lambda: messagebox.showerror("Error", "Only JSON, CSV, or Excel batch files are supported."))
                return
            all_matches = []
            for entry in batch_data:
                if not self.search_active:
                    break
                name = entry.get('name')
                folder = entry.get('folder', '')
                image_name = entry.get('image_name', '')
                if not name or not image_name:
                    continue
                # If folder is blank, treat image_name as URL
                if not folder.strip():
                    image_path = image_name
                else:
                    image_path = os.path.join(folder, image_name)
                self.app.after(0, lambda n=name: self.search_status.configure(
                    text=f"Searching for {n}... (batch)", text_color="gray"))
                try:
                    target_img = matcher.ImageProcessor.load_image(image_path) if hasattr(matcher, 'ImageProcessor') else ImageProcessor.load_image(image_path)
                    matches = matcher.find_matches(target_img, name)
                    for m in matches:
                        m['batch_name'] = name
                    all_matches.extend(matches)
                except Exception as e:
                    print(f"Batch entry error for {name}: {e}")
            if self.search_active:
                self.app.after(0, lambda: self.display_results(all_matches))
            else:
                self.app.after(0, lambda: self.search_status.configure(text="Batch search stopped by user.", text_color="orange"))
        except Exception as e:
            self.app.after(0, lambda: self.search_status.configure(
                text=f"Batch error: {str(e)}", text_color="red"))
            self.app.after(0, lambda e=e: messagebox.showerror("Error", f"Batch search failed: {str(e)}"))
        finally:
            self.search_active = False
            self.app.after(0, lambda: self.search_progress.set(0))
            self.app.after(0, lambda: self.stop_search_button.configure(state="disabled"))

    def display_results(self, results):
        # Actual display logic is here; do NOT call self.app.display_results to avoid recursion
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()

        if not results:
            no_results = ctk.CTkLabel(
                self.results_container,
                text="No matching profiles found.",
                text_color="gray",
                fg_color="black"
            )
            no_results.pack(pady=20)
            return

        # Store image references to prevent garbage collection
        if not hasattr(self, '_profile_img_refs'):
            self._profile_img_refs = []
        self._profile_img_refs.clear()

        for idx, profile in enumerate(results, 1):
            # Create frame for each result (black background)
            result_frame = ctk.CTkFrame(self.results_container, fg_color="black", border_width=1, corner_radius=8)
            result_frame.pack(fill="x", padx=10, pady=8, expand=True)

            # Left frame for image
            left_frame = ctk.CTkFrame(result_frame, fg_color="black")
            left_frame.pack(side="left", padx=10, pady=10)

            # Try to load and display profile picture
            try:
                if profile.get('profile_pic'):
                    response = requests.get(profile['profile_pic'])
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((90, 90), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._profile_img_refs.append(photo)
                    img_label = ctk.CTkLabel(left_frame, image=photo, text="", width=90, height=90, fg_color="black")
                    img_label.pack(padx=5, pady=5)
                else:
                    placeholder = ctk.CTkLabel(left_frame, text="No\nImage", width=90, height=90, fg_color="black", text_color="white")
                    placeholder.pack(padx=5, pady=5)
            except Exception as e:
                print(f"Error loading profile image: {e}")
                placeholder = ctk.CTkLabel(left_frame, text="No\nImage", width=90, height=90, fg_color="black", text_color="white")
                placeholder.pack(padx=5, pady=5)

            # Right frame for text info and button
            info_frame = ctk.CTkFrame(result_frame, fg_color="black")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            # Profile name and URL
            name_label = ctk.CTkLabel(
                info_frame, 
                text=f"Name: {profile.get('name', 'Unknown')}", 
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="black",
                text_color="white"
            )
            name_label.pack(anchor="w", pady=2)

            url = profile.get('url', 'N/A')
            url_label = ctk.CTkLabel(
                info_frame,
                text=f"Profile URL: {url}",
                text_color="#1a0dab" if url != 'N/A' else "gray",
                cursor="hand2" if url != 'N/A' else "arrow",
                fg_color="black"
            )
            url_label.pack(anchor="w", pady=2)
            if url != 'N/A':
                url_label.bind("<Button-1>", lambda e, url=url: self.app.open_url(url))

            # Similarity score (distance)
            distance = profile.get('distance', float('inf'))
            if distance != float('inf'):
                # Lower distance = better match. Show as "Match Score: 1 - distance" for user clarity
                match_score = max(0.0, 1.0 - distance)
                score_text = f"Match Score: {match_score:.2f} (Distance: {distance:.2f})"
            else:
                score_text = "Match Score: N/A"
            score_label = ctk.CTkLabel(
                info_frame,
                text=score_text,
                font=ctk.CTkFont(size=13),
                fg_color="black",
                text_color="white"
            )
            score_label.pack(anchor="w", pady=2)

            # Add to Scraper button
            add_button = ctk.CTkButton(
                info_frame,
                text="Add to Scraper",
                command=lambda url=url: self.app.add_to_scraper(url),
                width=140
            )
            add_button.pack(anchor="w", pady=8)

        # Update status
        self.search_status.configure(text=f"Found {len(results)} result(s).", text_color="green")
