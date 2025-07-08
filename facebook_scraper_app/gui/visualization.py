
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
    
    def generate_network_graph(self, network_data, layout="spring", node_size=15, 
                             base_node_size=10, edge_width=1, color_scheme="YlGnBu"):
        G = nx.Graph()

        for profile_url, data in network_data.items():
            G.add_node(data['profile_name'], 
                     depth=data['depth'], 
                     url=profile_url,
                     profile_pic=data.get('profile_pic'))
            
            for friend in data['friends']:
                G.add_node(friend['name'], 
                         depth=data['depth'] + 1, 
                         url=friend['url'],
                         profile_pic=friend.get('profile_pic'))
                G.add_edge(data['profile_name'], friend['name'])

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

        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_sizes = []
        node_urls = []
        node_images = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            depth = G.nodes[node].get('depth', 1)
            node_color.append(depth)
            # node_size (param) is int, node_sizes (list) is for marker size
            node_sizes.append(base_node_size + (node_size * (3 - min(depth, 3))))
            node_urls.append(G.nodes[node].get('url', ''))
            node_images.append(G.nodes[node].get('profile_pic', ''))

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            hovertext=[f"<b>{name}</b><br>Click to open profile" for name in node_text],
            customdata=node_urls,
            marker=dict(
                showscale=True,
                colorscale=color_scheme,
                size=node_sizes,
                color=node_color,
                line=dict(width=1, color='DarkSlateGrey'),
                opacity=0.9),
            textfont=dict(
                family="Arial",
                size=12,
                color='black'
            ))

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"<b>Facebook Friends Network</b><br><sub>Layout: {layout}</sub>",
                    font=dict(size=18, family="Arial"),
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=False,
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
    
    def save_graph(self, save_path):
        with open(self.plotly_html_path, 'r', encoding='utf-8') as src, \
             open(save_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    def open_in_browser(self):
        webbrowser.open(f"file://{os.path.abspath(self.plotly_html_path)}")