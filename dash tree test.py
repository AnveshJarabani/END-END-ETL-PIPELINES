import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

# Define your tree
tree = {
    'name': 'Root',
    'children': [
        {
            'name': 'Child 1',
            'children': [
                {'name': 'Grandchild 1'},
                {'name': 'Grandchild 2'}
            ]
        },
        {
            'name': 'Child 2',
            'children': [
                {'name': 'Grandchild 3'},
                {'name': 'Grandchild 4'}
            ]
        }
    ]
}

# Convert the tree to a NetworkX graph
G = nx.DiGraph()

def add_nodes_edges(tree):
    G.add_node(tree['name'])
    if 'children' in tree:
        for child in tree['children']:
            G.add_edge(tree['name'], child['name'])
            add_nodes_edges(child)

add_nodes_edges(tree)

# Define the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    dcc.Graph(id='graph', figure=go.Figure())
])

# Define the callback
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    dash.dependencies.Input('graph', 'clickData'))
def update_figure(clickData):
    if clickData is None:
        # Initialize the plot with the root node at the center
        pos = nx.spring_layout(G)
    else:
        # Center the plot on the clicked node
        node = clickData['points'][0]['text']
        pos = nx.spring_layout(G, pos={node: (0, 0)})
    # Create the plotly figure
    nodes = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        marker=dict(size=50, color='lightblue'),
        text=list(G.nodes()),
        textposition='bottom center',
        hoverinfo='text',
        textfont=dict(color='black', size=18),
    )
    edge_x = []
    edge_y = []
    for src, dst in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    edges = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=3, color='gray'),
        hoverinfo='none',
    )
    layout = go.Layout(
        hovermode='closest',
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    return go.Figure(data=[edges, nodes], layout=layout)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)