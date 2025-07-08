
"""
Tab for displaying and exporting scraping results.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext

class ResultsTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_results_tab()

    def build_results_tab(self):
        frame = self.frame
        self.app.results_text = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 10))
        self.app.results_text.pack(fill="both", expand=True, padx=5, pady=5)

        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        clear_btn = ctk.CTkButton(buttons_frame, text="Clear Results", command=self.app.clear_results)
        clear_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(buttons_frame, text="Export Results", command=self.app.export_results)
        export_btn.pack(side="left", padx=5)

        load_btn = ctk.CTkButton(buttons_frame, text="Load from JSON", command=self.app.load_from_json)
        load_btn.pack(side="left", padx=5)

        graph_btn = ctk.CTkButton(buttons_frame, text="Generate Graph", command=self.app.generate_plotly_graph)
        graph_btn.pack(side="left", padx=5)
