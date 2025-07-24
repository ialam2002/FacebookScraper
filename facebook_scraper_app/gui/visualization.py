
"""
Graph visualization logic for Facebook network data using PyVis and NetworkX.
"""
import os
import json
import tempfile
import webbrowser
import networkx as nx
from pyvis.network import Network

class GraphVisualizer:
    def __init__(self):
        self.pyvis_html_path = None
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

        # Create PyVis network
        net = Network(height="100vh", width="100vw", bgcolor="#f0f0f0", font_color="black")
        net.barnes_hut()
        # Add nodes and edges
        for node, data in G.nodes(data=True):
            title = f"<b>{node}</b>"
            if data.get('url'):
                title += f"<br><a href='{data['url']}' target='_blank'>Open Profile</a>"
            if data.get('profile_pic'):
                title += f"<br><img src='{data['profile_pic']}' width='60'>"
            color = "#3b5998" if node in main_profiles else ("#43a047" if mutual_friend_map and node in mutual_friend_map else "#ff9800")
            net.add_node(node, label=node, title=title, color=color, shape="dot", size=node_size)
        # Determine if this is a mutual friends only graph
        is_mutual_only = mutual_friend_map is not None
        for source, target in G.edges():
            # If mutual only and both nodes are main profiles, make edge red
            if is_mutual_only and source in main_profiles and target in main_profiles:
                net.add_edge(source, target, width=edge_width, color='red')
            else:
                net.add_edge(source, target, width=edge_width)
        temp_dir = tempfile.mkdtemp()
        self.pyvis_html_path = os.path.join(temp_dir, "pyvis_graph.html")
        net.write_html(self.pyvis_html_path)
        # Inject legend and JS to disable physics after 20s into the HTML file
        legend_html = '''\
<div id="pyvis-legend" style="position:absolute;top:20px;right:20px;z-index:9999;background:rgba(255,255,255,0.95);border:1px solid #bbb;padding:12px 18px;border-radius:8px;box-shadow:0 2px 8px #aaa;font-size:15px;">
  <b>Legend</b><br>
  <div style="margin-top:6px;display:flex;align-items:center;"><span style="display:inline-block;width:18px;height:18px;background:#3b5998;border-radius:50%;margin-right:8px;border:2px solid #222;"></span>Main Profile</div>
  <div style="margin-top:4px;display:flex;align-items:center;"><span style="display:inline-block;width:18px;height:18px;background:#43a047;border-radius:50%;margin-right:8px;border:2px solid #222;"></span>Mutual Friend</div>
  <div style="margin-top:4px;display:flex;align-items:center;"><span style="display:inline-block;width:18px;height:18px;background:#ff9800;border-radius:50%;margin-right:8px;border:2px solid #222;"></span>Friend</div>
</div>
        '''
        js_disable_physics = '''<script type="text/javascript">
if (typeof network !== 'undefined') {
  network.once('stabilizationIterationsDone', function() {
    setTimeout(function() {
      network.setOptions({physics: false});
    }, 20000);
  });
}
</script>'''
        # Insert legend and JS before </body>
        with open(self.pyvis_html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        if '</body>' in html:
            html = html.replace('</body>', legend_html + '\n' + js_disable_physics + '\n</body>')
            with open(self.pyvis_html_path, 'w', encoding='utf-8') as f:
                f.write(html)
        return self.pyvis_html_path
    def save_graph(self, save_path):
        with open(self.pyvis_html_path, 'r', encoding='utf-8') as src, \
             open(save_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

    def open_in_browser(self):
        webbrowser.open(f"file://{os.path.abspath(self.pyvis_html_path)}")