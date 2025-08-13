
"""
Tab for configuring and displaying the network graph visualization.
"""
import customtkinter as ctk

class VisualizationTab:

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

        self.app.mutual_friends_only_var = ctk.BooleanVar(value=True)
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

        gen_btn = ctk.CTkButton(action_frame, text="Generate Graph", command=self.app.generate_pyvis_graph)
        gen_btn.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(action_frame, text="Save as HTML", command=self.app.save_pyvis_graph)
        save_btn.pack(side="left", padx=5)

        open_btn = ctk.CTkButton(action_frame, text="Open in Browser", command=self.app.open_pyvis_in_browser)
        open_btn.pack(side="left", padx=5)

        self.app.visualization_frame = ctk.CTkFrame(frame, border_width=1)
        self.app.visualization_frame.pack(fill="both", expand=True, pady=10)

        self.app.info_label = ctk.CTkLabel(
            self.app.visualization_frame,
            text="Graph visualization will be generated as an interactive HTML file using PyVis.\n"
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

        # Internal use label
        internal_label = ctk.CTkLabel(frame, text="FOR INTERNAL USE ONLY", 
                                    font=ctk.CTkFont(size=14, weight="bold"), 
                                    text_color="#ff6b6b")
        internal_label.pack(pady=(15, 5))
