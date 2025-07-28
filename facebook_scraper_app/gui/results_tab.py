
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

        # More controlled mousewheel scrolling - only scrolls when mouse is over the canvas
        def _on_mousewheel(event):
            results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Only bind mousewheel when mouse enters the canvas, unbind when it leaves
        def _bind_mousewheel(event): 
            results_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event): 
            results_canvas.unbind_all("<MouseWheel>")
        
        # Set up mousewheel bindings
        results_canvas.bind("<Enter>", _bind_mousewheel)
        results_canvas.bind("<Leave>", _unbind_mousewheel)

        self.collapsible_sections = []

        # Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        clear_btn = ctk.CTkButton(buttons_frame, text="Clear Results", command=self.app.clear_results)
        clear_btn.pack(side="left", padx=5)


        export_btn = ctk.CTkButton(buttons_frame, text="Export Results to JSON", command=self.app.export_results)
        export_btn.pack(side="left", padx=5)

        export_excel_btn = ctk.CTkButton(buttons_frame, text="Export to Excel", command=self.export_to_excel)
        export_excel_btn.pack(side="left", padx=5)

        load_btn = ctk.CTkButton(buttons_frame, text="Load from JSON", command=self.app.load_from_json)
        load_btn.pack(side="left", padx=5)
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
        # Main people tabs (one per person)
        import re
        def sanitize_sheet_name(name):
            # Remove invalid characters for Excel sheet names: : \ / ? * [ ]
            name = re.sub(r'[:\\/?*\[\]]', '', name)
            # Remove leading/trailing whitespace and limit to 31 chars
            return name.strip()[:31] or 'Sheet'

        for profile_url, data in network_data.items():
            safe_title = sanitize_sheet_name(data['profile_name'])
            ws = wb.create_sheet(title=safe_title)
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

        # Sheet 1: Main People Only
        ws_main = wb.create_sheet(title="Main People Only")
        ws_main.append(["Name", "Profile URL", "Profile Pic", "Connected"])
        # For 'Connected', check if any other main person is in their friends
        main_urls = list(network_data.keys())
        for main_url, data in network_data.items():
            # Connected if any other main profile is in this person's friends
            connected = any(
                other_url != main_url and any(f.get('url') == other_url for f in data.get('friends', []))
                for other_url in main_urls
            )
            ws_main.append([
                data.get('profile_name', ''),
                main_url,
                data.get('profile_pic', ''),
                "Yes" if connected else "No"
            ])

        # Sheet 2: Main + Mutually Connected Friends
        ws_mutual = wb.create_sheet(title="Main+Mutual Friends")
        ws_mutual.append(["Main Name", "Main Profile URL", "Friend Name", "Friend Profile URL", "Mutual"])
        # For each main, list all friends, and mark if that friend is also a main
        for main_url, data in network_data.items():
            main_name = data.get('profile_name', '')
            for friend in data.get('friends', []):
                is_mutual = friend.get('url') in main_urls
                ws_mutual.append([
                    main_name,
                    main_url,
                    friend.get('name', ''),
                    friend.get('url', ''),
                    "Yes" if is_mutual else "No"
                ])

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

