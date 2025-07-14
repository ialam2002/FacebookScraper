
"""
Tab for displaying and exporting scraping results.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, Canvas, Scrollbar, Entry, StringVar

class ResultsTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_results_tab()

    def build_results_tab(self):
        frame = self.frame

        # Search/filter box
        search_frame = ctk.CTkFrame(frame)
        search_frame.pack(fill="x", padx=5, pady=(5, 0))
        ctk.CTkLabel(search_frame, text="Search/Filter:").pack(side="left", padx=(5, 2))
        self.search_var = StringVar()
        self.search_var.trace_add('write', self.on_search_update)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300)
        self.search_entry.pack(side="left", padx=2)

        # Scrollable area for collapsible results
        # Use a valid Tkinter color for Canvas background
        results_canvas = Canvas(frame, borderwidth=0, highlightthickness=0, bg="#222222")
        self.results_scrollable_frame = ctk.CTkFrame(results_canvas)
        self.results_scrollable_frame_id = results_canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        vscroll = Scrollbar(frame, orient="vertical", command=results_canvas.yview)
        results_canvas.configure(yscrollcommand=vscroll.set)
        results_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vscroll.pack(side="right", fill="y")

        def _on_frame_configure(event):
            results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        self.results_scrollable_frame.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        results_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.collapsible_sections = []

        # Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        clear_btn = ctk.CTkButton(buttons_frame, text="Clear Results", command=self.app.clear_results)
        clear_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(buttons_frame, text="Export Results", command=self.app.export_results)
        export_btn.pack(side="left", padx=5)

        load_btn = ctk.CTkButton(buttons_frame, text="Load from JSON", command=self.app.load_from_json)
        load_btn.pack(side="left", padx=5)

    def clear_collapsible_sections(self):
        for section in getattr(self, 'collapsible_sections', []):
            section['frame'].destroy()
        self.collapsible_sections = []

    def display_results(self, network_data):
        self.clear_collapsible_sections()
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for profile_url, data in network_data.items():
            if search_term and search_term not in data['profile_name'].lower():
                continue
            section = self.create_collapsible_section(data, profile_url)
            self.collapsible_sections.append(section)

    def create_collapsible_section(self, data, profile_url):
        section_frame = ctk.CTkFrame(self.results_scrollable_frame, fg_color="#222", corner_radius=8)
        section_frame.pack(fill="x", pady=4, padx=4, anchor="n")

        # Header with expand/collapse button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        expanded = [False]

        def toggle():
            expanded[0] = not expanded[0]
            if expanded[0]:
                details_frame.pack(fill="x", padx=10, pady=4)
                expand_btn.configure(text="-", fg_color="#444")
            else:
                details_frame.forget()
                expand_btn.configure(text="+", fg_color="#222")

        expand_btn = ctk.CTkButton(header_frame, text="+", width=28, command=toggle)
        expand_btn.pack(side="left", padx=(2, 6), pady=2)
        ctk.CTkLabel(header_frame, text=f"{data['profile_name']} (depth {data['depth']})", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(header_frame, text=f"{len(data['friends'])} friends", text_color="#aaa").pack(side="left", padx=8)

        # Details (hidden by default)
        details_frame = ctk.CTkFrame(section_frame, fg_color="#333", corner_radius=6)
        for i, friend in enumerate(data['friends'][:5], 1):
            pic_info = f" [Profile Pic: {friend['profile_pic']}]" if friend.get('profile_pic') else ""
            ctk.CTkLabel(details_frame, text=f"{i}. {friend['name']} ({friend['url']}){pic_info}", anchor="w").pack(fill="x", padx=4, pady=1)
        if len(data['friends']) > 5:
            ctk.CTkLabel(details_frame, text=f"... and {len(data['friends']) - 5} more", text_color="#aaa").pack(anchor="w", padx=4, pady=1)

        # Start collapsed
        details_frame.forget()

        return {'frame': section_frame, 'header': header_frame, 'details': details_frame, 'expand_btn': expand_btn}

    def on_search_update(self, *args):
        # Re-display results with filter
        if hasattr(self.app, 'network_data') and self.app.network_data:
            self.display_results(self.app.network_data)

