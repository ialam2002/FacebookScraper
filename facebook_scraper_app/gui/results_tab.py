
"""
Tab for displaying and exporting scraping results.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, Canvas, Scrollbar, Entry, StringVar, Frame, Label

class ResultsTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_results_tab()

    def build_results_tab(self):
        frame = self.frame

        # Top control bar (search + buttons)
        top_bar = ctk.CTkFrame(frame)
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        # Search/filter box (left side of top bar)
        search_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        search_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(search_frame, text="Search/Filter:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(5, 2))
        self.search_var = StringVar()
        self.search_var.trace_add('write', self.on_search_update)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=220)
        self.search_entry.pack(side="left", padx=2)

        # Buttons (right side of top bar)
        buttons_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        buttons_frame.pack(side="left", padx=(0, 0))
        clear_btn = ctk.CTkButton(buttons_frame, text="Clear Results", command=self.app.clear_results, width=120)
        clear_btn.pack(side="left", padx=5)
        export_btn = ctk.CTkButton(buttons_frame, text="Export JSON", command=self.app.export_results, width=120)
        export_btn.pack(side="left", padx=5)
        export_excel_btn = ctk.CTkButton(buttons_frame, text="Export Excel", command=self.export_to_excel, width=120)
        export_excel_btn.pack(side="left", padx=5)
        load_btn = ctk.CTkButton(buttons_frame, text="Load JSON", command=self.app.load_from_json, width=120)
        load_btn.pack(side="left", padx=5)

        # Results display area (full width below top bar)
        results_area = ctk.CTkFrame(frame, fg_color="#222222")
        results_area.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        # Scrollable area for collapsible results
        results_canvas = Canvas(results_area, borderwidth=0, highlightthickness=0, bg="#222222")
        self.results_scrollable_frame = ctk.CTkFrame(results_canvas)
        self.results_scrollable_frame_id = results_canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        vscroll = Scrollbar(results_area, orient="vertical", command=results_canvas.yview)
        results_canvas.configure(yscrollcommand=vscroll.set)
        results_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vscroll.pack(side="right", fill="y")

        def _on_frame_configure(event):
            results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        self.results_scrollable_frame.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event): 
            results_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event): 
            results_canvas.unbind_all("<MouseWheel>")
        results_canvas.bind("<Enter>", _bind_mousewheel)
        results_canvas.bind("<Leave>", _unbind_mousewheel)

        self.collapsible_sections = []

        # Internal use label
        internal_label = ctk.CTkLabel(frame, text="FOR INTERNAL USE ONLY", 
                                    font=ctk.CTkFont(size=14, weight="bold"), 
                                    text_color="#ff6b6b")
        internal_label.pack(pady=(15, 5))

    def export_to_excel(self):
        # Merge profiles before export, grouped by person
        from gui.merge_utils import merge_profiles
        merged = merge_profiles(getattr(self.app, 'network_data', None), getattr(self.app, 'person_to_profiles', None))
        if not merged:
            from tkinter import messagebox
            messagebox.showwarning("No Data", "No network data to export.")
            return
        # Use the main profile URL as the key for each merged profile
        network_data = {}
        for person_id, data in merged.items():
            main_url = None
            # Find the profile_url with the most friends
            if 'profile_urls' in data and data['profile_urls']:
                max_friends = -1
                for url in data['profile_urls']:
                    friends_count = len(getattr(self.app, 'network_data', {}).get(url, {}).get('friends', []))
                    if friends_count > max_friends:
                        main_url = url
                        max_friends = friends_count
            if not main_url:
                main_url = data['profile_urls'][0] if 'profile_urls' in data and data['profile_urls'] else person_id
            network_data[main_url] = {**data, 'main_profile_url': main_url}

        import openpyxl
        from openpyxl.utils import get_column_letter
        from tkinter import filedialog, messagebox
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Excel File"
        )
        if not file_path:
            return
        wb = openpyxl.Workbook()
        # Remove the default sheet
        wb.remove(wb.active)

        # Single combined sheet for all friends
        ws_all = wb.create_sheet(title="All Friends")
        ws_all.append(["Main Profile Name", "Main Profile URL", "Friend Name", "Friend Profile URL"])
        for main_url, data in network_data.items():
            main_name = data.get('profile_name', main_url)
            for friend in data.get('friends', []):
                ws_all.append([
                    main_name,
                    main_url,
                    friend.get('name', ''),
                    friend.get('url', '')
                ])
        # Auto-size columns
        for col in ws_all.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            ws_all.column_dimensions[col_letter].width = min(max_length + 2, 50)

        # --- Add Likes Data as a Second Sheet if Available ---
        likes_data = None
        try:
            # Try to get likes data from PostScraperTab (if loaded)
            if hasattr(self.app, 'post_scraper_tab') and hasattr(self.app.post_scraper_tab, 'loaded_json_results'):
                likes_data = self.app.post_scraper_tab.loaded_json_results
        except Exception:
            likes_data = None
        if likes_data:
            ws_likes = wb.create_sheet(title="Post Likes")
            ws_likes.append(["Scraped Profile Name", "Scraped Profile URL", "Liker Name", "Liker Profile URL"])
            deduped = set()
            for profile in likes_data:
                scraped_name = profile.get('profile_name', 'Unknown')
                scraped_url = profile.get('profile_url', '')
                for post in profile.get('post_likes', []):
                    for liker in post.get('liked_by', []):
                        liker_name = liker.get('name', '')
                        liker_url = liker.get('profile_url', '')
                        key = (scraped_name, scraped_url, liker_name, liker_url)
                        if key not in deduped:
                            ws_likes.append([scraped_name, scraped_url, liker_name, liker_url])
                            deduped.add(key)
            # Auto-size columns
            for col in ws_likes.columns:
                max_length = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                ws_likes.column_dimensions[col_letter].width = min(max_length + 2, 50)

        # --- Custom Sheet: Mutuals Matrix ---
        # Redefined Mutuals Matrix: Columns: Main Profile Name A, Main Profile Name B, mutual friend name
        # Helper to normalize URLs (strip trailing slashes and unwanted query/fragment while preserving essential parameters)
        def normalize_url(url):
            if not url:
                return url
            
            import re
            
            # Remove fragment (everything after #)
            url = url.split('#', 1)[0]
            
            # Handle profile.php URLs - preserve the id parameter
            if '/profile.php' in url:
                match = re.match(r'(https?://[^/]+/profile\.php)\?.*?id=([^&]+)', url)
                if match:
                    base_url, profile_id = match.groups()
                    return f"{base_url}?id={profile_id}"
                else:
                    # If no id parameter found, return as is
                    return url.split('?', 1)[0]
            else:
                # Handle regular username URLs - remove all query parameters
                url = url.split('?', 1)[0]
                url = url.rstrip('/')
                if url.endswith('/friends'):
                    url = url[:-8]  # remove '/friends'
                return url
        ws_matrix = wb.create_sheet(title="Mutuals Matrix")
        ws_matrix.append([
            "Main Profile Name A",
            "Main Profile Name B",
            "Mutual Friend Name",
            "Are A and B Direct Friends?",
            "Is Mutual Friend Direct Friend of Both?"
        ])
        # Build a lookup for main profiles
        main_urls = list(network_data.keys())
        url_to_name = {url: data.get('profile_name', url) for url, data in network_data.items()}
        # For each unique unordered pair (A, B), A != B
        for i, main_url in enumerate(main_urls):
            main_name = url_to_name[main_url]
            norm_main_url = normalize_url(main_url)
            for j in range(i + 1, len(main_urls)):
                other_url = main_urls[j]
                other_name = url_to_name[other_url]
                norm_other_url = normalize_url(other_url)
                # Find mutual friends between A and B (normalized)
                a_friends = {normalize_url(f.get('url')) for f in network_data[main_url].get('friends', []) if f.get('url')}
                b_friends = {normalize_url(f.get('url')) for f in network_data[other_url].get('friends', []) if f.get('url')}
                mutual_friend_urls = a_friends & b_friends
                # Indicator: Are A and B direct friends?
                a_to_b = norm_other_url in a_friends
                b_to_a = norm_main_url in b_friends
                direct_friends = "Yes" if a_to_b or b_to_a else "No"
                # Concise debug output for direct friendship
                # Add a row for each mutual friend
                for mf_url in mutual_friend_urls:
                    # Try to get the name from either profile's friends list (using original, not normalized, for name lookup)
                    mf_name = None
                    for f in network_data[main_url].get('friends', []):
                        if normalize_url(f.get('url')) == mf_url:
                            mf_name = f.get('name', f.get('url'))
                            break
                    if not mf_name:
                        for f in network_data[other_url].get('friends', []):
                            if normalize_url(f.get('url')) == mf_url:
                                mf_name = f.get('name', f.get('url'))
                                break
                    # Indicator: Is mutual friend a direct friend of both?
                    is_direct_friend_of_both = "Yes" if (mf_url in a_friends and mf_url in b_friends) else "No"
                    ws_matrix.append([
                        main_name,
                        other_name,
                        mf_name or mf_url,
                        "",  # Leave Are A and B Direct Friends? blank for mutual friend rows
                        is_direct_friend_of_both
                    ])
                # Also add a row for the main profiles themselves (mutual friend blank)
                ws_matrix.append([
                    main_name,
                    other_name,
                    "",
                    direct_friends,
                    ""
                ])

        # Save after all sheets are created
        try:
            wb.save(file_path)
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save Excel file: {e}")
        import openpyxl
        from openpyxl.utils import get_column_letter
        from tkinter import filedialog, messagebox
        network_data = getattr(self.app, 'network_data', None)
        if not network_data:
            messagebox.showwarning("No Data", "No network data to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Excel File"
        )
        if not file_path:
            return
        wb = openpyxl.Workbook()
        # Remove the default sheet
        wb.remove(wb.active)
        for profile_url, data in network_data.items():
            ws = wb.create_sheet(title=data['profile_name'][:31])  # Excel sheet names max 31 chars
            ws.append(["#", "Name", "Profile URL", "Has Profile Pic", "Profile Pic URL"])
            for i, friend in enumerate(data.get('friends', []), 1):
                ws.append([
                    i,
                    friend.get('name', 'N/A'),
                    friend.get('url', 'N/A'),
                    "Yes" if friend.get('profile_pic') else "No",
                    friend.get('profile_pic', '')
                ])
            # Auto-size columns
            for col in ws.columns:
                max_length = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                ws.column_dimensions[col_letter].width = min(max_length + 2, 50)
        try:
            wb.save(file_path)
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save Excel file: {e}")

    def clear_collapsible_sections(self):
        for section in getattr(self, 'collapsible_sections', []):
            try:
                section['frame'].destroy()
            except Exception:
                pass
        self.collapsible_sections = []
        
    def create_table_header(self, parent, columns):
        """Create a header row for the Excel-like table."""
        header_frame = ctk.CTkFrame(parent, fg_color="#1a1a2e")
        header_frame.pack(fill="x", padx=2, pady=2)

        # Use fixed widths that are larger to fit content better
        column_widths = [60, 200, 350, 120]  # Increased widths for better visibility
        
        for i, col in enumerate(columns):
            width = column_widths[i] if i < len(column_widths) else 150
            cell = ctk.CTkLabel(
                header_frame, 
                text=col, 
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width,
                anchor="w",
                fg_color="#1a1a2e",
                corner_radius=0
            )
            cell.pack(side="left", padx=1, pady=1)

    def create_table_row(self, parent, row_data, index):
        """Create a data row for the Excel-like table."""
        row_frame = ctk.CTkFrame(parent, fg_color="#2d2d44" if index % 2 == 0 else "#252538")
        row_frame.pack(fill="x", padx=2, pady=0)

        # Use fixed widths that match the header for consistency
        column_widths = [60, 200, 350, 120]  # Increased widths for better visibility
        
        # Index cell
        index_cell = ctk.CTkLabel(
            row_frame,
            text=str(index),
            width=column_widths[0],
            anchor="w",
            fg_color="transparent",
            corner_radius=0
        )
        index_cell.pack(side="left", padx=1, pady=1)

        # Name cell
        name_cell = ctk.CTkLabel(
            row_frame,
            text=row_data.get('name', 'N/A'),
            width=column_widths[1],
            anchor="w",
            fg_color="transparent",
            corner_radius=0
        )
        name_cell.pack(side="left", padx=1, pady=1)

        # URL cell - don't truncate since we have horizontal scrolling now
        url = row_data.get('url', 'N/A')
        url_cell = ctk.CTkLabel(
            row_frame,
            text=url,
            width=column_widths[2],
            anchor="w",
            fg_color="transparent",
            corner_radius=0
        )
        url_cell.pack(side="left", padx=1, pady=1)

        # Profile Pic status
        has_pic = "Yes" if row_data.get('profile_pic') else "No"
        pic_cell = ctk.CTkLabel(
            row_frame,
            text=has_pic,
            width=column_widths[3],
            anchor="w",
            fg_color="transparent",
            corner_radius=0
        )
        pic_cell.pack(side="left", padx=1, pady=1)

    def display_results(self, network_data):
        from gui.merge_utils import merge_profiles
        merged = merge_profiles(network_data, getattr(self.app, 'person_to_profiles', None))
        # Use the main profile URL as the key for each merged profile
        merged_data = {}
        for person_id, data in merged.items():
            main_url = None
            if 'profile_urls' in data and data['profile_urls']:
                max_friends = -1
                for url in data['profile_urls']:
                    friends_count = len(network_data.get(url, {}).get('friends', []))
                    if friends_count > max_friends:
                        main_url = url
                        max_friends = friends_count
            if not main_url:
                main_url = data['profile_urls'][0] if 'profile_urls' in data and data['profile_urls'] else person_id
            merged_data[main_url] = {**data, 'main_profile_url': main_url}
        self.clear_collapsible_sections()
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for main_url, data in merged_data.items():
            if search_term and search_term not in data['profile_name'].lower():
                continue
            section = self.create_collapsible_section(data, main_url)
            self.collapsible_sections.append(section)


    def create_collapsible_section(self, data, main_url):
        section_frame = ctk.CTkFrame(self.results_scrollable_frame, fg_color="#222", corner_radius=8, width=1100)
        section_frame.pack(fill="x", pady=4, padx=4, anchor="n")

        # Header with expand/collapse button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent", width=1100)
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
        # Show main profile name (never a URL) and URL in header
        name = data.get('profile_name', '').strip() or 'Profile'
        # If name looks like a URL, fallback to 'Profile' or person_id
        import re
        if re.match(r'https?://', name):
            name = data.get('person_id', 'Profile')
            if re.match(r'https?://', name):
                name = 'Profile'
        url = data.get('main_profile_url', main_url)
        ctk.CTkLabel(header_frame, text=f"{name}", font=ctk.CTkFont(size=14, weight="bold"), cursor="hand2", text_color="#00bfff").pack(side="left")
        if url and url != 'N/A':
            def open_url(event, url=url):
                import webbrowser
                webbrowser.open(url)
            label = ctk.CTkLabel(header_frame, text=f"  [Open Profile]  ", text_color="#1a0dab", cursor="hand2")
            label.pack(side="left")
            label.bind("<Button-1>", open_url)
        ctk.CTkLabel(header_frame, text=f"(depth {data['depth']})", text_color="#aaa").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text=f"{len(data['friends'])} friends", text_color="#aaa").pack(side="left", padx=8)

        # Details (hidden by default)
        details_frame = ctk.CTkFrame(section_frame, fg_color="#333", corner_radius=6, width=1100)
        
        # Table container with both horizontal and vertical scrolling
        table_container = ctk.CTkFrame(details_frame, fg_color="#333")
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create outer frame for both scrollbars
        outer_frame = Frame(table_container, bg="#333")
        outer_frame.pack(fill="both", expand=True)
        
        # Create a canvas for scrolling
        table_canvas = Canvas(outer_frame, borderwidth=0, highlightthickness=0, bg="#333")
        table_frame = ctk.CTkFrame(table_canvas, fg_color="#333")
        
        # Add both vertical and horizontal scrollbars
        v_scrollbar = Scrollbar(outer_frame, orient="vertical", command=table_canvas.yview)
        h_scrollbar = Scrollbar(outer_frame, orient="horizontal", command=table_canvas.xview)
        table_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Set up the layout with both scrollbars
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        table_canvas.pack(side="left", fill="both", expand=True)
        
        # Fixed width for the table frame (wider to fit all columns comfortably)
        canvas_frame = table_canvas.create_window((0, 0), window=table_frame, anchor="nw")
        
        # Configure scrolling region to include full width and height
        def _on_table_frame_configure(event):
            # Update the scrollregion to encompass the entire table
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
        
        table_frame.bind("<Configure>", _on_table_frame_configure)
        
        # Create table header
        self.create_table_header(table_frame, ["#", "Name", "Profile URL", "Has Profile Pic"])
        
        # Create table rows (limiting to max 100 rows at a time for performance)
        friends_to_display = data['friends'][:100]  # Limit to first 100 for performance
        remaining_count = max(0, len(data['friends']) - 100)
        
        for i, friend in enumerate(friends_to_display, 1):
            self.create_table_row(table_frame, friend, i)
            
        # Show message if there are more friends than displayed
        if remaining_count > 0:
            more_frame = ctk.CTkFrame(table_frame, fg_color="#333366")
            more_frame.pack(fill="x", padx=2, pady=5)
            ctk.CTkLabel(
                more_frame,
                text=f"+ {remaining_count} more friends (limited display for performance)",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color="#ccccff"
            ).pack(pady=3)
            
        # Set a fixed height for the table container (increased for better visibility)
        table_container.configure(height=300)

        # Start collapsed
        details_frame.forget()

        return {'frame': section_frame, 'header': header_frame, 'details': details_frame, 'expand_btn': expand_btn}

    def on_search_update(self, *args):
        # Add a small delay to prevent excessive updates during typing
        if hasattr(self, '_search_after_id'):
            self.frame.after_cancel(self._search_after_id)
        
        def delayed_search():
            # Re-display results with filter
            if hasattr(self.app, 'network_data') and self.app.network_data:
                self.display_results(self.app.network_data)
        
        # Schedule search after 300ms
        self._search_after_id = self.frame.after(300, delayed_search)

