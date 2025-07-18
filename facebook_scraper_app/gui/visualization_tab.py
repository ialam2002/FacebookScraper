
"""
Tab for configuring and displaying the network graph visualization.
"""
import customtkinter as ctk

class VisualizationTab:
    def export_plotly_pdf(self):
        import tkinter.filedialog as filedialog
        import tkinter.messagebox as messagebox
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Export Graph as PDF"
            )
            if file_path:
                # Ensure the graph is generated before exporting
                if not hasattr(self.graph_visualizer, '_last_fig') or self.graph_visualizer._last_fig is None:
                    messagebox.showerror("Error", "Please generate the graph before exporting to PDF.")
                    return
                try:
                    import kaleido  # noqa: F401
                except ImportError:
                    messagebox.showerror("Error", "The 'kaleido' package is required for PDF export. Please install it with 'pip install -U kaleido'.")
                    return
                self.graph_visualizer.export_pdf(file_path)
                messagebox.showinfo("Exported", f"Graph exported as PDF to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    def __init__(self, parent, app):
        from gui.visualization import GraphVisualizer
        self.app = app
        self.graph_visualizer = GraphVisualizer()
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_visualization_tab()

    def build_visualization_tab(self):
        frame = self.frame
        controls_frame = ctk.CTkFrame(frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 10))

        layout_label = ctk.CTkLabel(controls_frame, text="Layout:")
        layout_label.pack(side="left", padx=5)

        self.app.layout_var = ctk.StringVar(value="Random")
        layouts = ["Spring", "Kamada-Kawai", "Circular", "Random", "Shell", "Spectral"]
        layout_menu = ctk.CTkOptionMenu(controls_frame, values=layouts, variable=self.app.layout_var)
        layout_menu.pack(side="left", padx=5)

        self.app.mutual_friends_only_var = ctk.BooleanVar(value=False)
        mutual_checkbox = ctk.CTkCheckBox(controls_frame, text="Show mutual friends only", variable=self.app.mutual_friends_only_var)
        mutual_checkbox.pack(side="left", padx=15)

        params_frame = ctk.CTkFrame(frame, fg_color="transparent")
        params_frame.pack(fill="x", pady=5)

        node_size_label = ctk.CTkLabel(params_frame, text="Node Size:")
        node_size_label.pack(side="left", padx=5)
        self.app.node_size_var = ctk.IntVar(value=15)
        node_size_spin = ctk.CTkEntry(params_frame, width=40, textvariable=self.app.node_size_var)
        node_size_spin.pack(side="left", padx=5)

        # Removed base node size control for simplification

        edge_width_label = ctk.CTkLabel(params_frame, text="Edge Width:")
        edge_width_label.pack(side="left", padx=5)
        self.app.edge_width_var = ctk.IntVar(value=1)
        edge_width_spin = ctk.CTkEntry(params_frame, width=30, textvariable=self.app.edge_width_var)
        edge_width_spin.pack(side="left", padx=5)

        color_label = ctk.CTkLabel(params_frame, text="Color Scheme:")
        color_label.pack(side="left", padx=5)
        self.app.color_scheme_var = ctk.StringVar(value="YlGnBu")
        color_schemes = ["YlGnBu", "Plasma", "Viridis", "Rainbow", "Jet"]
        color_menu = ctk.CTkOptionMenu(params_frame, values=color_schemes, variable=self.app.color_scheme_var)
        color_menu.pack(side="left", padx=5)

        action_frame = ctk.CTkFrame(frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)

        gen_btn = ctk.CTkButton(action_frame, text="Generate Graph", command=self.app.generate_plotly_graph)
        gen_btn.pack(side="left", padx=5)


        save_btn = ctk.CTkButton(action_frame, text="Save as HTML", command=self.app.save_plotly_graph)
        save_btn.pack(side="left", padx=5)

        pdf_btn = ctk.CTkButton(action_frame, text="Export as PDF", command=self.export_plotly_pdf)
        pdf_btn.pack(side="left", padx=5)

        open_btn = ctk.CTkButton(action_frame, text="Open in Browser", command=self.app.open_plotly_in_browser)
        open_btn.pack(side="left", padx=5)

        self.app.visualization_frame = ctk.CTkFrame(frame, border_width=1)
        self.app.visualization_frame.pack(fill="both", expand=True, pady=10)

        self.app.info_label = ctk.CTkLabel(
            self.app.visualization_frame,
            text="Graph visualization will be generated as an interactive HTML file.\n"
                 "Configure the parameters above and click 'Generate Graph' to create the visualization.",
            wraplength=500,
            justify="center"
        )
        self.app.info_label.pack(expand=True, padx=10, pady=10)

        self.app.stats_label = ctk.CTkLabel(
            self.app.visualization_frame,
            text="No graph data available",
            text_color="gray"
        )
        self.app.stats_label.pack(pady=5)
