
"""
Graph visualization logic for Facebook network data using Plotly and NetworkX.
"""
import os
import json
import tempfile
import webbrowser
import networkx as nx
import plotly.graph_objects as go
from plotly.offline import plot

class GraphVisualizer:
    def __init__(self):
        self.plotly_html_path = None
        self.num_nodes = 0
        self.num_edges = 0
    
    def generate_network_graph(self, network_data, layout="spring", node_size=20, edge_width=1, color_scheme="YlGnBu", mutual_friend_map=None):
        G = nx.Graph()

        # Add all main profiles
        main_profiles = set()
        for profile_url, data in network_data.items():
            G.add_node(data['profile_name'], 
                     depth=data['depth'], 
                     url=profile_url,
                     profile_pic=data.get('profile_pic'))
            main_profiles.add(data['profile_name'])

        # Add friends and edges
        for profile_url, data in network_data.items():
            for friend in data['friends']:
                G.add_node(friend['name'], 
                         depth=data['depth'] + 1, 
                         url=friend['url'],
                         profile_pic=friend.get('profile_pic'))
                G.add_edge(data['profile_name'], friend['name'])

        # Add edges between main profiles if they are friends with each other
        main_profile_names = list(main_profiles)
        for i, name1 in enumerate(main_profile_names):
            for name2 in main_profile_names[i+1:]:
                # Check if name2 is in name1's friends or vice versa
                data1 = network_data.get(G.nodes[name1]['url'])
                data2 = network_data.get(G.nodes[name2]['url'])
                if data1 and any(f['name'] == name2 for f in data1['friends']):
                    G.add_edge(name1, name2)
                elif data2 and any(f['name'] == name1 for f in data2['friends']):
                    G.add_edge(name1, name2)

        self.num_nodes = len(G.nodes())
        self.num_edges = len(G.edges())

        layout_funcs = {
            "spring": nx.spring_layout,
            "Kamada-Kawai": nx.kamada_kawai_layout,
            "Circular": nx.circular_layout,
            "Random": nx.random_layout,
            "Shell": nx.shell_layout,
            "Spectral": nx.spectral_layout
        }

        layout_func = layout_funcs.get(layout, nx.spring_layout)
        pos = layout_func(G, seed=42) if layout in ["spring", "Random"] else layout_func(G)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=edge_width, color='rgba(150, 150, 150, 0.5)'),
            hoverinfo='none',
            mode='lines')

        node_x_main = []
        node_y_main = []
        node_text_main = []
        node_urls_main = []
        node_x_friend = []
        node_y_friend = []
        node_text_friend = []
        node_urls_friend = []
        node_x_mutual = []
        node_y_mutual = []
        node_text_mutual = []
        node_urls_mutual = []
        node_hover_mutual = []
        main_profile_names = set(main_profiles)
        mutual_keys = set(mutual_friend_map.keys()) if mutual_friend_map else set()
        for node in G.nodes():
            x, y = pos[node]
            url = G.nodes[node].get('url', '')
            if node in main_profile_names:
                node_x_main.append(x)
                node_y_main.append(y)
                node_text_main.append(node)
                node_urls_main.append(url)
            elif mutual_friend_map and (url in mutual_keys or node in mutual_keys):
                node_x_mutual.append(x)
                node_y_mutual.append(y)
                node_text_mutual.append(node)
                node_urls_mutual.append(url)
                # Tooltip: show which main profiles this mutual friend is connected to
                connected_profiles = mutual_friend_map.get(url) or mutual_friend_map.get(node) or []
                if connected_profiles:
                    hover = f"<b>{node}</b><br>Mutual Friend<br>Connected to:<br>" + "<br>".join(connected_profiles) + "<br>Click to open profile"
                else:
                    hover = f"<b>{node}</b><br>Mutual Friend<br>Click to open profile"
                node_hover_mutual.append(hover)
            else:
                node_x_friend.append(x)
                node_y_friend.append(y)
                node_text_friend.append(node)
                node_urls_friend.append(url)

        # Main profiles: blue, Mutual friends: green, Friends: orange
        node_trace_main = go.Scatter(
            x=node_x_main, y=node_y_main,
            mode='markers+text',
            name='Main Profile',
            text=node_text_main,
            textposition="top center",
            hoverinfo='text',
            hovertext=[f"<b>{name}</b><br>Main Profile<br>Click to open profile" for name in node_text_main],
            customdata=node_urls_main,
            marker=dict(
                size=node_size,
                color='royalblue',
                line=dict(width=2, color='DarkSlateGrey'),
                opacity=0.95),
            textfont=dict(
                family="Arial",
                size=12,
                color='black'
            )
        )
        node_trace_mutual = go.Scatter(
            x=node_x_mutual, y=node_y_mutual,
            mode='markers+text',
            name='Mutual Friend',
            text=node_text_mutual,
            textposition="top center",
            hoverinfo='text',
            hovertext=node_hover_mutual,
            customdata=node_urls_mutual,
            marker=dict(
                size=node_size,
                color='mediumseagreen',
                line=dict(width=2, color='DarkSlateGrey'),
                opacity=0.95),
            textfont=dict(
                family="Arial",
                size=12,
                color='black'
            )
        )
        node_trace_friend = go.Scatter(
            x=node_x_friend, y=node_y_friend,
            mode='markers+text',
            name='Friend',
            text=node_text_friend,
            textposition="top center",
            hoverinfo='text',
            hovertext=[f"<b>{name}</b><br>Friend<br>Click to open profile" for name in node_text_friend],
            customdata=node_urls_friend,
            marker=dict(
                size=node_size,
                color='orange',
                line=dict(width=1, color='DarkSlateGrey'),
                opacity=0.85),
            textfont=dict(
                family="Arial",
                size=12,
                color='black'
            )
        )

        fig = go.Figure(
            data=[edge_trace, node_trace_main, node_trace_mutual, node_trace_friend],
            layout=go.Layout(
                title=dict(
                    text=f"<b>Facebook Friends Network</b><br><sub>Layout: {layout}</sub>",
                    font=dict(size=18, family="Arial"),
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=True,
                legend=dict(
                    title="Node Type",
                    x=0.01,
                    y=0.99,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='black',
                    borderwidth=1
                ),
                hovermode='closest',
                margin=dict(b=20, l=20, r=20, t=60),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                clickmode='event+select',
                paper_bgcolor='rgba(240,240,240,1)',
                plot_bgcolor='rgba(255,255,255,1)',
                width=1200,
                height=800,
                autosize=True
            )
        )

        fig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    title='Depth',
                    thickness=15,
                    xanchor='left',
                    titleside='right'
                )
            )
        )

        temp_dir = tempfile.mkdtemp()
        self.plotly_html_path = os.path.join(temp_dir, "plotly_graph.html")
        self._last_fig = fig  # Store for PDF export

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Facebook Friends Network</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { margin: 0; padding: 0; }
                #graph { 
                    width: 100vw; 
                    height: 100vh; 
                    position: fixed;
                    top: 0;
                    left: 0;
                }
            </style>
        </head>
        <body>
            <div id="graph"></div>
            <script>
                var figure = %s;
                Plotly.newPlot('graph', figure.data, figure.layout);
                
                document.getElementById('graph').on('plotly_click', function(data){
                    var point = data.points[0];
                    if(point && point.customdata) {
                        window.open(point.customdata, '_blank');
                    }
                });
                
                window.addEventListener('resize', function() {
                    Plotly.Plots.resize(document.getElementById('graph'));
                });
            </script>
        </body>
        </html>
        """ % json.dumps(fig.to_plotly_json())
        
        with open(self.plotly_html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        return self.plotly_html_path
    def export_pdf(self, pdf_path):
        # Requires kaleido: pip install -U kaleido
        if hasattr(self, '_last_fig') and self._last_fig is not None:
            self._last_fig.write_image(pdf_path, format="pdf")
    
    def save_graph(self, save_path):
        with open(self.plotly_html_path, 'r', encoding='utf-8') as src, \
             open(save_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    def open_in_browser(self):
        webbrowser.open(f"file://{os.path.abspath(self.plotly_html_path)}")