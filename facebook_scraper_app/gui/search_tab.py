
"""
Tab for searching profiles and displaying face match results.
"""
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
        # --- Individual Search Section ---
        self.indiv_search_frame = ctk.CTkFrame(frame)
        self.indiv_search_frame.pack(fill="x", padx=10, pady=10)

        self.person_rows = []
        self.add_person_btn = ctk.CTkButton(
            self.indiv_search_frame,
            text="Add Person",
            command=self.add_person_row
        )
        self.add_person_row()  # Add initial row

        # --- Batch Upload Section ---
        self.batch_frame = ctk.CTkFrame(frame)
        self.batch_frame.pack(fill="x", padx=10, pady=(0, 10))

        batch_label = ctk.CTkLabel(
            self.batch_frame,
            text="Batch upload: Excel/CSV/JSON (columns: name, folder, image_name). If folder is blank, image_name is treated as a URL."
        )
        batch_label.pack(anchor="w", padx=5, pady=5)

        batch_btn_frame = ctk.CTkFrame(self.batch_frame, fg_color="transparent")
        batch_btn_frame.pack(fill="x", padx=5, pady=5)

        self.batch_path_entry = ctk.CTkEntry(batch_btn_frame)
        self.batch_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_batch_btn = ctk.CTkButton(
            batch_btn_frame,
            text="Browse",
            width=80,
            command=self.browse_batch_file
        )
        browse_batch_btn.pack(side="left")

        # --- Search and Stop Buttons ---
        search_btn = ctk.CTkButton(
            frame,
            text="Search Profiles",
            command=self.start_search
        )
        search_btn.pack(pady=10)

        self.stop_search_button = ctk.CTkButton(
            frame,
            text="Stop Search",
            command=self.stop_search,
            state="disabled"
        )
        self.stop_search_button.pack(pady=5)

        # --- Results Section ---
        results_frame = ctk.CTkFrame(frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results_container = ctk.CTkScrollableFrame(results_frame)
        self.results_container.pack(fill="both", expand=True)

        self.search_status = ctk.CTkLabel(frame, text="Ready", text_color="gray")
        self.search_status.pack(pady=5)

        self.search_progress = ctk.CTkProgressBar(frame, mode="determinate")
        self.search_progress.set(0)
        self.search_progress.pack(fill="x", padx=10, pady=(0, 10))

    def add_person_row(self):
        row_frame = ctk.CTkFrame(self.indiv_search_frame, fg_color="transparent")
        # Check if add_person_btn is packed
        if self.add_person_btn.winfo_manager():
            row_frame.pack(fill="x", pady=4, before=self.add_person_btn)
        else:
            row_frame.pack(fill="x", pady=4)

        try:
            name_entry = ctk.CTkEntry(row_frame, width=200, placeholder_text="Full Name")
        except TypeError:
            name_entry = ctk.CTkEntry(row_frame, width=200)
        name_entry.pack(side="left", padx=(0, 5))

        try:
            image_path_entry = ctk.CTkEntry(row_frame, width=200, placeholder_text="Image Path or URL")
        except TypeError:
            image_path_entry = ctk.CTkEntry(row_frame, width=200)
        image_path_entry.pack(side="left", padx=(0, 5))

        browse_btn = ctk.CTkButton(
            row_frame,
            text="Browse",
            width=80,
            command=lambda e=image_path_entry: self.browse_image_for_entry(e)
        )
        browse_btn.pack(side="left", padx=(0, 5))

        del_btn = ctk.CTkButton(
            row_frame,
            text="Delete",
            width=60,
            fg_color="#b22222",
            text_color="white",
            command=lambda: self.delete_person_row(row_frame)
        )
        del_btn.pack(side="left")

        self.person_rows.append((name_entry, image_path_entry, row_frame))

        # Always keep the add button at the bottom
        self.add_person_btn.pack_forget()
        self.add_person_btn.pack(anchor="w", pady=5)

    def delete_person_row(self, row_frame):
        # Remove from list and destroy the frame
        self.person_rows = [row for row in self.person_rows if row[2] != row_frame]
        row_frame.destroy()

    def browse_image_for_entry(self, entry):
        file_path = filedialog.askopenfilename(
            title="Select Reference Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file_path:
            entry.delete(0, "end")
            entry.insert(0, file_path)

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
        batch_path = self.batch_path_entry.get().strip()
        # Gather all individual person entries
        people = []
        for name_entry, image_entry, _ in self.person_rows:
            name = name_entry.get().strip()
            image_path = image_entry.get().strip()
            if name and image_path and name != "Full Name":
                people.append((name, image_path))
        if not people and not batch_path:
            messagebox.showerror("Error", "Please provide at least one person (name and image) or a batch file")
            return
        self.search_status.configure(text="Starting search...", text_color="gray")
        self.search_progress.set(0)
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.search_active = True
        self.stop_search_button.configure(state="normal")
        threading.Thread(
            target=self.run_search_multi,
            args=(people, batch_path),
            daemon=True
        ).start()

    def run_search_multi(self, people, batch_path):
        try:
            matcher = FaceMatcher(
                self.app.email_entry.get(),
                self.app.password_entry.get(),
                driver=getattr(self.app.scraper_controller.scraper, 'driver', None)
            )
            all_results = []
            if batch_path:
                self.process_batch_file(matcher, batch_path)
            else:
                for name, image_path in people:
                    if not self.search_active:
                        break
                    self.app.after(0, lambda n=name: self.search_status.configure(
                        text=f"Searching for {n}...", 
                        text_color="gray"
                    ))
                    matches = []
                    if self.search_active:
                        target_img = ImageProcessor.load_image(image_path)
                        matches = matcher.find_matches(target_img, name, top_k=5)
                    all_results.append((name, matches))
                    if self.search_active:
                        # Display all accumulated results so far
                        self.app.after(0, lambda results=list(all_results): self.display_results(results))
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

    def display_results(self, results_by_person):
        # Collapsible sections for each person, and filtering by match score
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()

        if not results_by_person:
            no_results = ctk.CTkLabel(
                self.results_container,
                text="No matching profiles found.",
                text_color="gray",
                fg_color="black"
            )
            no_results.pack(pady=20)
            return

        if not hasattr(self, '_profile_img_refs'):
            self._profile_img_refs = []
        self._profile_img_refs.clear()

        # Filtering UI
        filter_frame = ctk.CTkFrame(self.results_container, fg_color="black")
        filter_frame.pack(fill="x", padx=10, pady=(0, 8))
        filter_label = ctk.CTkLabel(filter_frame, text="Min. Match Score:", fg_color="black", text_color="white")
        filter_label.pack(side="left", padx=(0, 5))
        filter_var = ctk.DoubleVar(value=0.0)
        filter_entry = ctk.CTkEntry(filter_frame, width=60, textvariable=filter_var)
        filter_entry.pack(side="left")

        def refresh_results():
            min_score = filter_var.get()
            # Remove all person frames except filter_frame
            for widget in self.results_container.winfo_children():
                if widget != filter_frame:
                    widget.destroy()
            for person_name, results in results_by_person:
                # Collapsible section
                section_frame = ctk.CTkFrame(self.results_container, fg_color="#181818", border_width=1, corner_radius=8)
                section_frame.pack(fill="x", padx=10, pady=6, expand=True)
                # Header with expand/collapse
                header_frame = ctk.CTkFrame(section_frame, fg_color="#222")
                header_frame.pack(fill="x")
                expanded = ctk.BooleanVar(value=False)
                def toggle_section(var=expanded, frame=section_frame, content_widgets=[]):
                    if var.get():
                        for w in content_widgets:
                            w.pack(fill="x", padx=0, pady=0)
                    else:
                        for w in content_widgets:
                            w.pack_forget()
                header_label = ctk.CTkLabel(
                    header_frame,
                    text=f"Results for: {person_name}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color="#222",
                    text_color="#00ffcc"
                )
                header_label.pack(side="left", padx=10, pady=4)
                toggle_btn = ctk.CTkButton(
                    header_frame,
                    text="Show" if not expanded.get() else "Hide",
                    width=60,
                    command=lambda v=expanded, btn=None: v.set(not v.get())
                )
                toggle_btn.pack(side="right", padx=10)

                # Content widgets (results)
                content_widgets = []
                filtered_results = []
                for idx, profile in enumerate(results[:5], 1):
                    distance = profile.get('distance', float('inf'))
                    match_score = max(0.0, 1.0 - distance) if distance != float('inf') else 0.0
                    if match_score < filter_var.get():
                        continue
                    filtered_results.append(profile)
                    result_frame = ctk.CTkFrame(section_frame, fg_color="black", border_width=1, corner_radius=8)
                    # ...existing code for left_frame, image, info_frame, etc...
                    left_frame = ctk.CTkFrame(result_frame, fg_color="black")
                    left_frame.pack(side="left", padx=10, pady=10)
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
                    info_frame = ctk.CTkFrame(result_frame, fg_color="black")
                    info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
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
                    score_text = f"Match Score: {match_score:.2f} (Distance: {distance:.2f})" if distance != float('inf') else "Match Score: N/A"
                    score_label = ctk.CTkLabel(
                        info_frame,
                        text=score_text,
                        font=ctk.CTkFont(size=13),
                        fg_color="black",
                        text_color="white"
                    )
                    score_label.pack(anchor="w", pady=2)
                    add_button = ctk.CTkButton(
                        info_frame,
                        text="Add to Scraper",
                        command=lambda url=url: self.app.add_to_scraper(url),
                        width=140
                    )
                    add_button.pack(anchor="w", pady=8)
                    content_widgets.append(result_frame)
                # If no results after filtering
                if not filtered_results:
                    no_results = ctk.CTkLabel(
                        section_frame,
                        text="No matching profiles found.",
                        text_color="gray",
                        fg_color="black"
                    )
                    content_widgets.append(no_results)
                # Initially collapsed
                expanded.set(False)
                def on_toggle(var=expanded, btn=toggle_btn, cws=content_widgets):
                    if var.get():
                        btn.configure(text="Hide")
                        for w in cws:
                            w.pack(fill="x", padx=10, pady=4)
                    else:
                        btn.configure(text="Show")
                        for w in cws:
                            w.pack_forget()
                expanded.trace_add('write', lambda *args, v=expanded, b=toggle_btn, cws=content_widgets: on_toggle(v, b, cws))
                # Start collapsed
                on_toggle(expanded, toggle_btn, content_widgets)

        # Initial render
        refresh_results()

        # Update on filter change
        def on_filter_change(*args):
            refresh_results()
        filter_var.trace_add('write', on_filter_change)

        self.search_status.configure(text=f"Search complete. {len(results_by_person)} person(s) processed.", text_color="green")
