'''

pip install
networkx
matplotlib
scipy
dash
plotly
colour
x pygraphviz

'''
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

import os


def scatter_nodes(pos, labels=None, color=None, size=20, opacity=1):
    # pos is the dict of node positions
    # labels is a list  of labels of len(pos), to be displayed when hovering the mouse over the nodes
    # color is the color for nodes. When it is set as None the Plotly default color is used
    # size is the size of the dots representing the nodes
    #opacity is a value between [0,1] defining the node color opacity

    # Simple answer: just need to define color as a list of colors which are automatically indexed with the nodes.

    L=len(pos)
    trace = go.Scatter(x=[], y=[],  mode='markers', marker=go.Scatter.marker(size=[]))
    for k in range(L):
        trace['x'].append(pos[k][0])
        trace['y'].append(pos[k][1])
    attrib=dict(name='', text=labels , hoverinfo='text', opacity=opacity) # a dict of Plotly node attributes
    trace=dict(trace, **attrib)# concatenate the dict trace and attrib
    trace['marker']['size']=size
    trace['marker']['color']=color
    return trace

# Plotly figure
def networkGraph(EGDE_VAR):

    # edges = [[EGDE_VAR, 'B'], ['B', 'C'], ['B', 'D']]
    # G = nx.Graph()
    # G.add_edges_from(edges)
    stage = 2
    gml_project_path = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs"
    # file_name = f"initial_demo_{stage}_graph.gml"
    # file_name = "sp01_demo_70_graph.gml"
    # file_name = "sp01_demo_70_graph.graphml"
    file_name = "sp01_demo_12_graph.graphml"
    outFilePath = os.path.join(gml_project_path, file_name)
    G = nx.read_graphml(outFilePath)

    if EGDE_VAR == "A":
        pos = nx.fruchterman_reingold_layout(G)
    elif EGDE_VAR == "B":
        pos = nx.shell_layout(G)
    else:
        pos = nx.spring_layout(G)

    # edges trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(color='black', width=1),
        hoverinfo='none',
        showlegend=False,
        mode='lines')

    # nodes trace
    node_x = []
    node_y = []
    text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y, text=text,
        mode='markers+text',
        showlegend=False,
        hoverinfo='none',
        marker=dict(
            color='pink',
            size=50,
            line=dict(color='black', width=1)))

    # layout
    layout = dict(plot_bgcolor='white',
                  paper_bgcolor='white',
                  margin=dict(t=10, b=10, l=10, r=10, pad=0),
                  xaxis=dict(linecolor='black',
                             showgrid=False,
                             showticklabels=False,
                             mirror=True),
                  yaxis=dict(linecolor='black',
                             showgrid=False,
                             showticklabels=False,
                             mirror=True),
                  height=1000)

    # figure
    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

    return fig

# Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Dash Networkx'

app.layout = html.Div([
        html.I('Write your EDGE_VAR'),
        html.Br(),
        dcc.Input(id='EGDE_VAR', type='text', value='K', debounce=True),
        dcc.Graph(id='my-graph'),
    ]
)

@app.callback(
    Output('my-graph', 'figure'),
    [Input('EGDE_VAR', 'value')],
)
def update_output(EGDE_VAR):
    return networkGraph(EGDE_VAR)

if __name__ == '__main__':
    app.run_server(debug=True)
