
"""
Main GUI application for the Facebook Scraper.
Handles tab management, event routing, and main window logic.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import os
import json
import tempfile
import webbrowser
import threading
from gui.scraper_control import ScraperController
from gui.visualization import GraphVisualizer
from gui.config_tab import ConfigTab
from gui.search_tab import SearchTab
from gui.scraping_tab import ScrapingTab
from gui.results_tab import ResultsTab
from gui.visualization_tab import VisualizationTab
from profile_search.search import FaceMatcher, ImageProcessor
from PIL import Image, ImageTk
import requests
import io
import csv

class FacebookScraperApp(ctk.CTk):
    def display_results(self, results):
        # Forward results to the SearchTab's display_results method
        self.search_tab.display_results(results)


    def __init__(self):
        super().__init__()
        self.title("Facebook Friends Network Scraper")
        self.geometry("1200x800")

        self.scraper_controller = ScraperController()
        self.visualizer = GraphVisualizer()
        self.scraping_active = False
        self.network_data = None
        self.plotly_html_path = None

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.notebook.add("Configuration")
        self.notebook.add("Search")
        self.notebook.add("Scraping")
        self.notebook.add("Results")
        self.notebook.add("Visualization")

        # Instantiate tab classes
        self.config_tab = ConfigTab(self.notebook.tab("Configuration"), self)
        self.search_tab = SearchTab(self.notebook.tab("Search"), self)
        self.scraping_tab = ScrapingTab(self.notebook.tab("Scraping"), self)
        self.results_tab = ResultsTab(self.notebook.tab("Results"), self)
        self.visualization_tab = VisualizationTab(self.notebook.tab("Visualization"), self)

        # Ensure driver closes on window close
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

    def on_app_close(self):
        try:
            if hasattr(self, 'scraper_controller') and self.scraper_controller:
                self.scraper_controller.close()
        except Exception:
            pass
        self.destroy()
    def create_widgets(self):
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.notebook.add("Configuration")
        self.notebook.add("Search")
        self.notebook.add("Scraping")
        self.notebook.add("Results")
        self.notebook.add("Visualization")
        
        self.build_config_tab()
        self.build_search_tab()
        self.build_scraping_tab()
        self.build_results_tab()
        self.build_visualization_tab()
    
    def build_config_tab(self):
        tab = self.notebook.tab("Configuration")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header = ctk.CTkLabel(frame, text="Facebook Login", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(pady=(0, 15))
        
        email_label = ctk.CTkLabel(frame, text="Facebook Email:")
        email_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.email_entry = ctk.CTkEntry(frame, width=400)
        self.email_entry.pack(padx=10, pady=(0, 10))
        
        password_label = ctk.CTkLabel(frame, text="Facebook Password:")
        password_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.password_entry = ctk.CTkEntry(frame, width=400, show="*")
        self.password_entry.pack(padx=10, pady=(0, 15))
        
        login_btn = ctk.CTkButton(frame, text="Test Login", command=self.test_login)
        login_btn.pack(pady=10)
        
        self.config_status_label = ctk.CTkLabel(frame, text="Not logged in", text_color="gray")
        self.config_status_label.pack(pady=5)
    
    def build_scraping_tab(self):
        tab = self.notebook.tab("Scraping")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header = ctk.CTkLabel(frame, text="Scraping Parameters", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(pady=(0, 15))
        
        urls_label = ctk.CTkLabel(frame, text="Profile URLs (one per line or comma-separated):")
        urls_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.profile_urls_text = scrolledtext.ScrolledText(frame, height=8, wrap="word", font=("Consolas", 10))
        self.profile_urls_text.pack(fill="x", padx=10, pady=(0, 15))
        
        params_frame = ctk.CTkFrame(frame)
        params_frame.pack(fill="x", padx=10, pady=10)
        
        depth_label = ctk.CTkLabel(params_frame, text="Depth:")
        depth_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.depth_spinbox = ctk.CTkEntry(params_frame, width=50)
        self.depth_spinbox.insert(0, "0")
        self.depth_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        friends_label = ctk.CTkLabel(params_frame, text="Max Friends per Profile:")
        friends_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.max_friends_spinbox = ctk.CTkEntry(params_frame, width=50)
        self.max_friends_spinbox.insert(0, "200")
        self.max_friends_spinbox.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        output_label = ctk.CTkLabel(frame, text="Output File:")
        output_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        output_frame = ctk.CTkFrame(frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_file_entry = ctk.CTkEntry(output_frame)
        self.output_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_btn = ctk.CTkButton(output_frame, text="Browse", width=80, command=self.browse_output_file)
        browse_btn.pack(side="left")
        
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        self.start_button = ctk.CTkButton(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(button_frame, text="Stop Scraping", command=self.stop_scraping, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        self.progress_label = ctk.CTkLabel(frame, text="Ready", text_color="gray")
        self.progress_label.pack(pady=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(frame, orientation="horizontal", mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
    
    def build_results_tab(self):
        tab = self.notebook.tab("Results")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 10))
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        clear_btn = ctk.CTkButton(buttons_frame, text="Clear Results", command=self.clear_results)
        clear_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(buttons_frame, text="Export Results", command=self.export_results)
        export_btn.pack(side="left", padx=5)
        
        load_btn = ctk.CTkButton(buttons_frame, text="Load from JSON", command=self.load_from_json)
        load_btn.pack(side="left", padx=5)
        
        graph_btn = ctk.CTkButton(buttons_frame, text="Generate Graph", command=self.generate_plotly_graph)
        graph_btn.pack(side="left", padx=5)
    
    def build_visualization_tab(self):
        tab = self.notebook.tab("Visualization")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        controls_frame = ctk.CTkFrame(frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        layout_label = ctk.CTkLabel(controls_frame, text="Layout:")
        layout_label.pack(side="left", padx=5)
        
        self.layout_var = ctk.StringVar(value="spring")
        layouts = ["Spring", "Kamada-Kawai", "Circular", "Random", "Shell", "Spectral"]
        layout_menu = ctk.CTkOptionMenu(controls_frame, values=layouts, variable=self.layout_var)
        layout_menu.pack(side="left", padx=5)
        
        # Mutual friends only checkbox
        self.mutual_friends_only_var = ctk.BooleanVar(value=False)
        mutual_checkbox = ctk.CTkCheckBox(controls_frame, text="Show mutual friends only", variable=self.mutual_friends_only_var)
        mutual_checkbox.pack(side="left", padx=15)

        params_frame = ctk.CTkFrame(frame, fg_color="transparent")
        params_frame.pack(fill="x", pady=5)

        node_size_label = ctk.CTkLabel(params_frame, text="Node Size:")
        node_size_label.pack(side="left", padx=5)
        self.node_size_var = ctk.IntVar(value=15)
        node_size_spin = ctk.CTkEntry(params_frame, width=40, textvariable=self.node_size_var)
        node_size_spin.pack(side="left", padx=5)

        # Removed base node size control for simplification

        edge_width_label = ctk.CTkLabel(params_frame, text="Edge Width:")
        edge_width_label.pack(side="left", padx=5)
        self.edge_width_var = ctk.IntVar(value=1)
        edge_width_spin = ctk.CTkEntry(params_frame, width=30, textvariable=self.edge_width_var)
        edge_width_spin.pack(side="left", padx=5)

        color_label = ctk.CTkLabel(params_frame, text="Color Scheme:")
        color_label.pack(side="left", padx=5)
        self.color_scheme_var = ctk.StringVar(value="YlGnBu")
        color_schemes = ["YlGnBu", "Plasma", "Viridis", "Rainbow", "Jet"]
        color_menu = ctk.CTkOptionMenu(params_frame, values=color_schemes, variable=self.color_scheme_var)
        color_menu.pack(side="left", padx=5)
        
        action_frame = ctk.CTkFrame(frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        
        gen_btn = ctk.CTkButton(action_frame, text="Generate Graph", command=self.generate_plotly_graph)
        gen_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(action_frame, text="Save as HTML", command=self.save_plotly_graph)
        save_btn.pack(side="left", padx=5)
        
        open_btn = ctk.CTkButton(action_frame, text="Open in Browser", command=self.open_plotly_in_browser)
        open_btn.pack(side="left", padx=5)
        
        self.visualization_frame = ctk.CTkFrame(frame, border_width=1)
        self.visualization_frame.pack(fill="both", expand=True, pady=10)
        
        self.info_label = ctk.CTkLabel(
            self.visualization_frame,
            text="Graph visualization will be generated as an interactive HTML file.\n"
                 "Configure the parameters above and click 'Generate Graph' to create the visualization.",
            wraplength=500,
            justify="center"
        )
        self.info_label.pack(expand=True, padx=10, pady=10)
        
        self.stats_label = ctk.CTkLabel(
            self.visualization_frame,
            text="No graph data available",
            text_color="gray"
        )
        self.stats_label.pack(pady=5)
    
    def build_search_tab(self):
        tab = self.notebook.tab("Search")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        batch_label = ctk.CTkLabel(params_frame, text="Or upload Excel/CSV/JSON:")
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
    
    #search tab helper methods
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
        if not self.scraper_controller.logged_in:
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
        
        # Clear previous results
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
                self.email_entry.get(),
                self.password_entry.get(),
                driver=getattr(self.scraper_controller.scraper, 'driver', None)
            )
            
            if batch_path:
                # Handle batch processing
                self.process_batch_file(matcher, batch_path)
            else:
                # Handle single search
                target_img = ImageProcessor.load_image(image_path)
                
                self.after(0, lambda: self.search_status.configure(
                    text=f"Searching for {name}...", 
                    text_color="gray"
                ))
                
                matches = []
                if self.search_active:
                    matches = matcher.find_matches(target_img, name)
                if self.search_active:
                    self.after(0, lambda: self.display_results(matches))
                else:
                    self.after(0, lambda: self.search_status.configure(text="Search stopped by user.", text_color="orange"))
        except Exception as e:
            self.after(0, lambda: self.search_status.configure(
                text=f"Error: {str(e)}", 
                text_color="red"
            ))
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        finally:
            self.search_active = False
            self.after(0, lambda: self.search_progress.set(0))
            self.after(0, lambda: self.stop_search_button.configure(state="disabled"))

    def stop_search(self):
        self.search_active = False
        self.search_status.configure(text="Search stopped by user.", text_color="orange")
        self.stop_search_button.configure(state="disabled")
    
    def build_search_tab(self):
        tab = self.notebook.tab("Search")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        batch_label = ctk.CTkLabel(params_frame, text="Or upload Excel/CSV/JSON:")
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
    
    #search tab helper methods
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
        if not self.scraper_controller.logged_in:
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
        
        # Clear previous results
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
                self.email_entry.get(),
                self.password_entry.get(),
                driver=getattr(self.scraper_controller.scraper, 'driver', None)
            )
            
            if batch_path:
                # Handle batch processing
                self.process_batch_file(matcher, batch_path)
            else:
                # Handle single search
                target_img = ImageProcessor.load_image(image_path)
                
                self.after(0, lambda: self.search_status.configure(
                    text=f"Searching for {name}...", 
                    text_color="gray"
                ))
                
                matches = []
                if self.search_active:
                    matches = matcher.find_matches(target_img, name)
                if self.search_active:
                    self.after(0, lambda: self.display_results(matches))
                else:
                    self.after(0, lambda: self.search_status.configure(text="Search stopped by user.", text_color="orange"))
        except Exception as e:
            self.after(0, lambda: self.search_status.configure(
                text=f"Error: {str(e)}", 
                text_color="red"
            ))
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        finally:
            self.search_active = False
            self.after(0, lambda: self.search_progress.set(0))
            self.after(0, lambda: self.stop_search_button.configure(state="disabled"))

    def stop_search(self):
        self.search_active = False
        self.search_status.configure(text="Search stopped by user.", text_color="orange")
        self.stop_search_button.configure(state="disabled")
    
    def process_batch_file(self, matcher, batch_path):
        # Batch file can be JSON: [{"name": ..., "image": ...}], CSV: name,image, or Excel: name,image
        import pandas as pd
        try:
            if not os.path.exists(batch_path):
                self.after(0, lambda: messagebox.showerror("Error", f"Batch file not found: {batch_path}"))
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
                        image = row.get('image') or row.get('Image')
                        if name and image:
                            batch_data.append({'name': name, 'image': image})
            elif batch_path.lower().endswith('.xlsx'):
                df = pd.read_excel(batch_path)
                for _, row in df.iterrows():
                    name = row.get('name') or row.get('Name')
                    image = row.get('image') or row.get('Image')
                    if pd.isna(name) or pd.isna(image):
                        continue
                    batch_data.append({'name': name, 'image': image})
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Only JSON, CSV, or Excel batch files are supported."))
                return
            all_matches = []
            for entry in batch_data:
                if not self.search_active:
                    break
                name = entry.get('name')
                image_path = entry.get('image')
                if not name or not image_path:
                    continue
                self.after(0, lambda n=name: self.search_status.configure(
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
                self.after(0, lambda: self.display_results(all_matches))
            else:
                self.after(0, lambda: self.search_status.configure(text="Batch search stopped by user.", text_color="orange"))
        except Exception as e:
            self.after(0, lambda: self.search_status.configure(
                text=f"Batch error: {str(e)}", text_color="red"))
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Batch search failed: {str(e)}"))
        finally:
            self.search_active = False
            self.after(0, lambda: self.search_progress.set(0))
            self.after(0, lambda: self.stop_search_button.configure(state="disabled"))
    
    # Controller methods
    def browse_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.output_file_entry.delete(0, "end")
            self.output_file_entry.insert(0, path)
    
    def test_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not all([email, password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        try:
            if self.scraper_controller.login(email, password):
                self.config_status_label.configure(text="Login successful!", text_color="green")
            else:
                self.config_status_label.configure(text="Login failed", text_color="red")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            self.config_status_label.configure(text="Login failed", text_color="red")
    
    def start_scraping(self):
        if not self.scraper_controller.logged_in:
            messagebox.showerror("Error", "Please login first")
            return
            
        urls_text = self.profile_urls_text.get("1.0", "end").strip()
        if not urls_text:
            messagebox.showerror("Error", "Please enter at least one profile URL")
            return
            
        urls = []
        for line in urls_text.split('\n'):
            if ',' in line:
                urls.extend([url.strip() for url in line.split(',') if url.strip()])
            else:
                if line.strip():
                    urls.append(line.strip())
        
        depth = int(self.depth_spinbox.get())
        max_friends = int(self.max_friends_spinbox.get())
        output_file = self.output_file_entry.get()
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
            
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.scraping_active = True
        
        threading.Thread(
            target=self.run_scraping,
            args=(urls, depth, max_friends, output_file),
            daemon=True
        ).start()
    
    def run_scraping(self, urls, depth, max_friends, output_file):
        try:
            self.update_progress("Starting scraping...", 0)
            
            network = self.scraper_controller.scrape_friends_network(
                start_urls=urls,
                depth=depth,
                max_friends_per_profile=max_friends,
                output_file=output_file
            )
            
            if network:
                self.network_data = network
                self.update_results(network)
                self.update_progress("Scraping completed successfully!", 100)
                messagebox.showinfo("Success", "Scraping completed successfully!")
            else:
                self.update_progress("Scraping completed with no results", 100)
                messagebox.showinfo("Info", "Scraping completed but no data was collected")
                
        except Exception as e:
            self.update_progress(f"Error: {str(e)}", 0)
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
        finally:
            self.scraping_active = False
            self.after(0, self.reset_controls)
    
    def stop_scraping(self):
        self.scraping_active = False
        self.update_progress("Stopping... Please wait", 0)
        self.scraper_controller.close()
    
    def reset_controls(self):
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
    
    def update_progress(self, message, value):
        self.after(0, lambda: self.progress_label.configure(text=message))
        self.after(0, lambda: self.progress_bar.set(value/100))
    
    def update_results(self, network):
        self.results_text.delete("1.0", "end")
        
        for profile_url, data in network.items():
            self.results_text.insert("end", f"\n{data['profile_name']} (depth {data['depth']}) has {len(data['friends'])} connections:\n")
            for i, friend in enumerate(data['friends'][:5], 1):
                pic_info = f" [Profile Pic: {friend['profile_pic']}]" if friend.get('profile_pic') else ""
                self.results_text.insert("end", f"  {i}. {friend['name']} ({friend['url']}){pic_info}\n")
            if len(data['friends']) > 5:
                self.results_text.insert("end", f"  ... and {len(data['friends']) - 5} more\n")
    
    def clear_results(self):
        self.results_text.delete("1.0", "end")
    
    def export_results(self):
        import pandas as pd
        if not self.network_data:
            messagebox.showwarning("Warning", "No results to export")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.network_data, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.csv'):
                # Flatten network data for CSV
                rows = []
                for url, data in self.network_data.items():
                    for friend in data['friends']:
                        rows.append({
                            'profile_name': data['profile_name'],
                            'profile_url': url,
                            'profile_pic': data.get('profile_pic'),
                            'friend_name': friend['name'],
                            'friend_url': friend['url'],
                            'friend_pic': friend.get('profile_pic')
                        })
                pd.DataFrame(rows).to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                # Flatten network data for Excel
                rows = []
                for url, data in self.network_data.items():
                    for friend in data['friends']:
                        rows.append({
                            'profile_name': data['profile_name'],
                            'profile_url': url,
                            'profile_pic': data.get('profile_pic'),
                            'friend_name': friend['name'],
                            'friend_url': friend['url'],
                            'friend_pic': friend.get('profile_pic')
                        })
                pd.DataFrame(rows).to_excel(file_path, index=False)
            else:
                messagebox.showerror("Error", "Unsupported file type.")
                return
            messagebox.showinfo("Success", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {e}")
    
    def load_from_json(self):
        import pandas as pd
        file_path = filedialog.askopenfilename(
            title="Load Network Data",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.network_data = json.load(f)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                self.network_data = self._network_from_flat_df(df)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                self.network_data = self._network_from_flat_df(df)
            else:
                messagebox.showerror("Error", "Unsupported file type.")
                return
            self.update_results(self.network_data)
            messagebox.showinfo("Success", "Network data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load network data: {str(e)}")

    def _network_from_flat_df(self, df):
        # Convert a flat DataFrame (from CSV/Excel) to the nested network_data dict
        network = {}
        for _, row in df.iterrows():
            url = row['profile_url']
            if url not in network:
                network[url] = {
                    'profile_name': row['profile_name'],
                    'profile_pic': row.get('profile_pic'),
                    'depth': 0,
                    'friends': []
                }
            network[url]['friends'].append({
                'name': row['friend_name'],
                'url': row['friend_url'],
                'profile_pic': row.get('friend_pic')
            })
        return network
    
    def generate_plotly_graph(self):
        import networkx as nx
        if not self.network_data:
            messagebox.showwarning("Warning", "No network data available. Please scrape data first or load from JSON.")
            return

        self.configure(cursor="watch")
        self.stats_label.configure(text="Generating graph... Please wait", text_color="gray")
        self.update()

        try:
            network_data = self.network_data
            if self.mutual_friends_only_var.get():
                # Show only main profiles and friends who are connected to more than one profile (mutuals)
                main_profiles = [url for url, data in network_data.items() if data.get('depth', 0) == 0]
                if len(main_profiles) < 2:
                    messagebox.showwarning("Mutual Friends Only", "Mutual friends graph requires at least two main profiles (depth=0) in the data.")
                    return

                # Build a mapping from friend url/name to the set of main profiles they are connected to
                friend_to_profiles = {}
                for url in main_profiles:
                    for f in network_data[url].get('friends', []):
                        key = f.get('url') or f.get('name')
                        if not key:
                            continue
                        if key not in friend_to_profiles:
                            friend_to_profiles[key] = set()
                        friend_to_profiles[key].add(url)

                # Keep only friends connected to more than one main profile
                mutual_friend_keys = {k for k, v in friend_to_profiles.items() if len(v) > 1}

                # Build filtered network: keep only main profiles, mutual friends, and edges between main profiles
                filtered_network = {}
                # Add main profiles and their mutual friends
                for url in main_profiles:
                    data = network_data[url]
                    # Keep only mutual friends
                    filtered_friends = [f for f in data.get('friends', []) if (f.get('url') in mutual_friend_keys or f.get('name') in mutual_friend_keys)]
                    filtered_network[url] = {
                        'profile_name': data['profile_name'],
                        'profile_pic': data.get('profile_pic'),
                        'depth': data.get('depth', 0),
                        'friends': filtered_friends
                    }
                # Add mutual friends as nodes (with their info if available)
                for key in mutual_friend_keys:
                    # Try to find info from network_data
                    found = None
                    for url, data in network_data.items():
                        for f in data.get('friends', []):
                            if (f.get('url') == key or f.get('name') == key):
                                found = f
                                break
                        if found:
                            break
                    filtered_network[key] = {
                        'profile_name': found.get('name', 'Unknown') if found else key,
                        'profile_pic': found.get('profile_pic') if found else None,
                        'depth': 1,
                        'friends': []
                    }
                # Add edges between main profiles if they are friends with each other
                for i, url1 in enumerate(main_profiles):
                    for url2 in main_profiles[i+1:]:
                        # Check if url2 is in url1's friends
                        data1 = network_data[url1]
                        if any((f.get('url') == url2 or f.get('name') == network_data[url2]['profile_name']) for f in data1.get('friends', [])):
                            # Add url2 as a friend to url1 if not already present
                            if not any((f.get('url') == url2 or f.get('name') == network_data[url2]['profile_name']) for f in filtered_network[url1]['friends']):
                                filtered_network[url1]['friends'].append({
                                    'name': network_data[url2]['profile_name'],
                                    'url': url2,
                                    'profile_pic': network_data[url2].get('profile_pic')
                                })
                        # Check if url1 is in url2's friends
                        data2 = network_data[url2]
                        if any((f.get('url') == url1 or f.get('name') == network_data[url1]['profile_name']) for f in data2.get('friends', [])):
                            if not any((f.get('url') == url1 or f.get('name') == network_data[url1]['profile_name']) for f in filtered_network[url2]['friends']):
                                filtered_network[url2]['friends'].append({
                                    'name': network_data[url1]['profile_name'],
                                    'url': url1,
                                    'profile_pic': network_data[url1].get('profile_pic')
                                })
                network_data = filtered_network

            layout = self.layout_var.get()
            # Defensive: fallback to default values if entry is empty or invalid
            try:
                node_size = int(self.node_size_var.get())
            except Exception:
                node_size = 15
            base_node_size = None  # Not used anymore
            try:
                edge_width = int(self.edge_width_var.get())
            except Exception:
                edge_width = 1
            color_scheme = self.color_scheme_var.get() if hasattr(self, 'color_scheme_var') else "YlGnBu"

            self.plotly_html_path = self.visualizer.generate_network_graph(
                network_data,
                layout=layout,
                node_size=node_size,
                edge_width=edge_width,
                color_scheme=color_scheme
            )

            num_nodes = self.visualizer.num_nodes
            num_edges = self.visualizer.num_edges

            self.stats_label.configure(
                text=f"Graph generated with {num_nodes} nodes and {num_edges} edges\n"
                    f"Layout: {layout.replace('_', ' ').title()}\n"
                    f"Click on any node to open their Facebook profile"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Plotly graph: {str(e)}")
        finally:
            self.configure(cursor="")
            self.update()
    
    def save_plotly_graph(self):
        if not hasattr(self.visualizer, 'plotly_html_path') or not self.visualizer.plotly_html_path:
            messagebox.showwarning("Warning", "No graph to save. Please generate a graph first.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Plotly Graph",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )

        if save_path:
            try:
                self.visualizer.save_graph(save_path)
                messagebox.showinfo("Success", f"Graph saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {str(e)}")

    def open_plotly_in_browser(self):
        if hasattr(self.visualizer, 'plotly_html_path') and self.visualizer.plotly_html_path:
            self.visualizer.open_in_browser()
        else:
            messagebox.showwarning("Warning", "No graph to open. Please generate a graph first.")

    def add_to_scraper(self, url):
        """Add the profile URL to the scraping list (Scraping tab)"""
        if hasattr(self, 'profile_urls_text') and url:
            # Get current URLs, split by line or comma, and add if not present
            current_urls = self.profile_urls_text.get("1.0", "end-1c").strip()
            urls = set([u.strip() for u in current_urls.replace(',', '\n').split('\n') if u.strip()])
            if url not in urls:
                if current_urls:
                    self.profile_urls_text.insert("end", f"\n{url}")
                else:
                    self.profile_urls_text.insert("end", url)
                messagebox.showinfo("Success", "Profile added to scraping list!")
            else:
                messagebox.showinfo("Info", "Profile already in scraping list.")
            # Switch to Scraping tab
            if hasattr(self, 'notebook'):
                self.notebook.set("Scraping")

    def open_url(self, url):
        """Open the profile URL in default browser"""
        if url and url.startswith('http'):
            import webbrowser
            webbrowser.open(url)