import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from common_routines import *

# get list of graphml file in folder including sub folder
##### start defining app data

dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                          project_path="Z:\\Projects\\Research\\0200-GRACE")

graphml_files = get_files_by_extension(gml_project_path, '.graphml')

networkx_layouts = [
    "spring",
    # "bipartite",
    "circular",
    "fruchterman_reingold",
    "kamada_kawai",
    "random",
    # "rescale",
    # "rescale_dict",
    "shell",
    "spectral",
    # "planar",
    "spiral",
    # "multipartite",
]

default_layout = networkx_layouts[0]

dd_centralities = ["Non selected"] + centralities
default_centrality = dd_centralities[0]

click_actions = [
    "Node table",
    "Node Neighborhood - out",
    "Node Neighborhood - all",
    "Node Shortest paths",
]

default_click_action = click_actions[0]

max_elements = 10000

# end of global definitions #######################################

def centrality_heading_link(centrality):

    if centrality == 'harmonic_centrality':
        link = "https://en.wikipedia.org/wiki/Centrality#Harmonic_centrality"
    elif centrality == 'eigenvector_centrality':
        link = "https://en.wikipedia.org/wiki/Centrality#Eigenvector_centrality"
    elif centrality == 'pagerank':
        link = "https://en.wikipedia.org/wiki/Centrality#PageRank_centrality"
    elif centrality == 'authorities':
        link = "https://en.wikipedia.org/wiki/Authority_distribution"
    elif centrality == 'degree_centrality':
        link = "https://en.wikipedia.org/wiki/Centrality#Degree_centrality"
    elif centrality == 'betweenness_centrality':
        link = "https://en.wikipedia.org/wiki/Centrality#Betweenness_centrality"
    elif centrality == 'closeness_centrality':
        link = "https://en.wikipedia.org/wiki/Closeness_centrality"
    elif centrality == 'hubs':
        link = "https://en.wikipedia.org/wiki/Centrality#Degree_centrality"

    else:
        link = "https://en.wikipedia.org/wiki/Centrality"

    return html.Td(children=html.A(centrality, href=link, target="_blank"), colSpan=2)

def centralities_headings(dt_graph_analytics, type, element_id=None):

    table_row = []

    if type == "graph":

        for col_num, centrality in enumerate(dt_graph_analytics["graph"]["centralities"]):
            table_row.append(centrality_heading_link(centrality))

    else:

        for col_num, centrality in enumerate(dt_graph_analytics["nodes"][element_id]["centralities"]):
            table_row.append(centrality_heading_link(centrality))

    return table_row

def graph_analytics_table(dt_graph_analytics, max_nodes=10, element_type=None, element_id=None, incl_shortest_paths=True):

    tables = []

    #############
    # Node tables
    #############

    number_of_nodes = dt_graph_analytics["graph"]["number_of_nodes"]

    if element_type is not None and element_type.lower() == "node":

        node_label = dt_graph_analytics["nodes"][element_id]["label"]
        heading_text = f"Node: {node_label}"
        table_rows = []
        attributes = ["patients", "events", "degree", "out_neighbors", "all_neighbors", "clustering"]
        for att_id in attributes:
            table_row = []
            value = dt_graph_analytics["nodes"][element_id][att_id]
            if att_id in ["clustering"]:
                cell = html.Td(children=html.A(att_id, href="https://en.wikipedia.org/wiki/Clustering_coefficient", target="_blank"), colSpan=3)
            else:
                cell = html.Td(children=att_id, colSpan=3)
            table_row.append(cell)
            if att_id in ["clustering"]:
                cell = html.Td(children="{:.3f}".format(value))
            else:
                cell = html.Td(children=value)
            table_row.append(cell)
            table_rows.append(html.Tr(table_row))

        table = html.Table(className='analytics-table', children=
        # Header
        [html.Tr([html.Th(
            html.Td(children=heading_text, colSpan=4))])] + table_rows
                           )

        tables.append(table)

        # Table of centrality position and score
        table_rows = []
        # heading row
        table_row = centralities_headings(dt_graph_analytics, "nodes", element_id=element_id)

        table_rows.append(html.Tr(table_row))

        table_row = []
        for centrality in dt_graph_analytics["nodes"][element_id]["centralities"]:
            pos = dt_graph_analytics["nodes"][element_id]["centralities"][centrality]['pos']
            pos_text = f"{pos} of {number_of_nodes}"
            score = dt_graph_analytics["nodes"][element_id]["centralities"][centrality]['score']
            cell = html.Td(children="{:.3f}".format(score))
            table_row.append(cell)
            cell = html.Td(children=pos_text)
            table_row.append(cell)
        table_rows.append(html.Tr(table_row))

        table = html.Table(className='analytics-table', children=
        # Header
        [html.Tr([html.Th(
            html.Td(children="Node Centralities", colSpan=4))])] + table_rows
                           )

        tables.append(table)

        # Table of shortest paths
        table_rows = []
        if incl_shortest_paths and "shortest_path" in dt_graph_analytics["nodes"][element_id]:

            for target_node_id in dt_graph_analytics["nodes"][element_id]["shortest_path"]:

                table_row = []
                # Don't include the target first as given as last element of list

                # Miss first and last?
                for step in range(0,10):

                    if step >= len(dt_graph_analytics["nodes"][element_id]["shortest_path"][target_node_id]):
                        node_name = "______"
                    else:
                        step_node_id = dt_graph_analytics["nodes"][element_id]["shortest_path"][target_node_id][step]
                        node_label = dt_graph_analytics["nodes"][step_node_id]['label']
                        node_name = node_label.split(":")[1].strip()
                    cell = html.Td(children=node_name)
                    table_row.append(cell)

                table_rows.append(html.Tr(table_row))

        table = html.Table(className='analytics-table', children=
        # Header
        [html.Tr([html.Th(
            html.Td(children="Node shortest paths", colSpan=4))])] + table_rows
                           )

        tables.append(table)

        pause = True

    ##############
    # Graph tables
    ##############

    ignore_attributes = []
    ignore_attributes.append("nx_info")
    ignore_attributes.append("number_of_nodes")
    ignore_attributes.append("number_of_edges")
    ignore_attributes.append("non_edges")
    ignore_attributes.append("eccentricity")
    ignore_attributes.append("diameter")
    ignore_attributes.append("radius")
    ignore_attributes.append("center")
    ignore_attributes.append("centralities")
    ignore_attributes.append("attributes")

    table_rows = []
    for att_id in dt_graph_analytics["graph"]:
        if att_id not in ignore_attributes:
            table_row = []
            value = dt_graph_analytics["graph"][att_id]
            if att_id == "density":
                cell = html.Td(children=html.A(att_id, href="https://en.wikipedia.org/wiki/Dense_graph", target="_blank"), colSpan=3)
            else:
                cell = html.Td(children=att_id, colSpan=3)
            table_row.append(cell)
            cell = html.Td(children="{:.3f}".format(value))
            table_row.append(cell)
            table_rows.append(html.Tr(table_row))

    table = html.Table(className='analytics-table',children=
        # Header
        [html.Tr([html.Th(html.Td(children=dt_graph_analytics["graph"]["nx_info"], colSpan=4))])] + table_rows
    )

    tables.append(table)

    ##############
    # Centralities
    ##############

    # Start new table
    table_rows = []
    # heading row
    table_row = centralities_headings(dt_graph_analytics, "graph")

    table_rows.append(html.Tr(table_row))

    # Top max_nodes positions for each centrality
    max_pos = number_of_nodes if number_of_nodes <= max_nodes else max_nodes
    for pos in range(1,max_pos + 1):
        table_row = []
        for centrality in dt_graph_analytics["graph"]["centralities"]:
            node_id = dt_graph_analytics["graph"]["centralities"][centrality][str(pos)]['node']
            node_label = dt_graph_analytics["nodes"][node_id]['label']
            node_name = node_label.split(":")[1].strip()
            score = dt_graph_analytics["graph"]["centralities"][centrality][str(pos)]['score']
            cell = html.Td(children=node_name)
            table_row.append(cell)
            cell = html.Td(children="{:.3f}".format(score))
            table_row.append(cell)
        table_rows.append(html.Tr(table_row))

    table = html.Table(id="table-centrality",className='analytics-table',children=
        # Header
        [html.Tr([html.Th(html.Td(children="Centrality table", colSpan=4))])] + table_rows
    )

    tables.append(table)

    ##############
    # Attributes
    ##############

    if "attributes" in dt_graph_analytics["graph"]:

        # Start new table - as a heading
        table_rows = []
        table = html.Table(id=f"table-attributes", className='analytics-table', children=
        # Header
        [html.Tr([html.Th(html.Td(children="Attributes", colSpan=4))])] + table_rows
                           )
        tables.append(table)

        for att_num, att_key in enumerate(dt_graph_analytics["graph"]["attributes"]):
            # Start new table
            table_rows = []

            ac_value = dt_graph_analytics["graph"]["attributes"][att_key]['assortativity_coefficient']
            link_text = "Assortativity coefficient"
            link = html.A(link_text, href="https://en.wikipedia.org/wiki/Assortativity", target="_blank")
            table_row = []
            table_row.append(html.Td(children=link))
            table_row.append(html.Td(children=f"{ac_value:.3f}"))
            table_rows.append(html.Tr(table_row))

            # heading row
            table_row = []
            cell = html.Td(children="")
            table_row.append(cell)
            for value_num, value in enumerate(dt_graph_analytics["graph"]["attributes"][att_key]['attribute_mixing_matrix']):
                cell = html.Td(children=value)
                table_row.append(cell)
            table_rows.append(html.Tr(table_row))

            for value_num, value in enumerate(dt_graph_analytics["graph"]["attributes"][att_key]['attribute_mixing_matrix']):
                table_row = []
                cell = html.Td(children=value)
                table_row.append(cell)
                for matrix_value in dt_graph_analytics["graph"]["attributes"][att_key]['attribute_mixing_matrix'][value]:
                    cell = html.Td(children="{:.3f}".format(matrix_value))
                    table_row.append(cell)
                table_rows.append(html.Tr(table_row))

            table = html.Table(id=f"table-attributes-{att_key}",className='analytics-table',children=
                # Header
                [html.Tr([html.Th(html.Td(children=att_key, colSpan=4))])] + table_rows
            )

            tables.append(table)

    return html.Div(children=tables)


def controls_table(controls):
    # return html.Div(children=[control[1] for control in controls])

    table_rows = []

    for control in controls:

        table_row = []
        cell = html.Td(children=control[0])
        table_row.append(cell)
        cell = html.Td(children=control[1])
        table_row.append(cell)

        table_rows.append(html.Tr(table_row))

    table = html.Table(id="page_controls", className='controls-table', children=
    # Header
    [html.Tr([html.Th(html.Td(children="Controls", colSpan=2))])] + table_rows
                       )

    return html.Div(children=table)



pause = True

### Start DASH app
app = dash.Dash(__name__)

controls = [["Select a graphML file:",
    dcc.Dropdown(
        id="dropdown-files",
        options=[{"label": x, "value": x} for x in graphml_files],
        value=graphml_files[0],
    )
             ]]

controls.append(["Select a layout algorithm:",
    dcc.Dropdown(
        id="dropdown-layouts",
        options=[{"label": x, "value": x} for x in networkx_layouts],
        value= default_layout
    )
])

controls.append(["Select a centrality algorithm:",
    dcc.Dropdown(
        id="dropdown-centrality",
        options=[{"label": x, "value": x} for x in dd_centralities],
        value=default_centrality
    )
])

controls.append(["Select an action on Click:",
    dcc.Dropdown(
        id="click-actions",
        options=[{"label": x, "value": x} for x in click_actions],
        value= default_click_action
    )
])

controls.append(["Select a node:",
    dcc.Dropdown(
            id='dropdown-nodes',
            )
])

controls.append(["Selected Node:",
    dcc.Input(
            id='selected-node', type='text', size='100',
            )
])

controls.append(["",
    dcc.Graph(id='plot-graphml'),
])

app.layout = html.Div([
    html.H1("graphML plot and analytics"),
    html.H3(f"File Browser: {gml_project_path}"),
    controls_table(controls),
    html.H3("Graph Analytics:"),
    html.Div(id="graph_analytics"),
    html.H5("Done")
    ]
)


@app.callback(
                Output("selected-node", "value"),
                Output("dropdown-nodes", "options"),
                Output("plot-graphml", "figure"),
                Output("graph_analytics", "children"),
                Input("dropdown-files", "value"),
                Input("dropdown-layouts", "value"),
                Input("dropdown-centrality", "value"),
                Input("dropdown-nodes", "value"),
                Input("plot-graphml", "clickData"),
                State("click-actions", "value")
)
def process_selected_options(file_name, layout, centrality, sel_node_id, plot_clickdata, click_action):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    centrality = centrality if centrality != default_centrality else None

    ##############################
    # Which control was triggered?
    ##############################
    ctx = dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    input_return = ctx.triggered[0]['prop_id'].split('.')[1]

    log_debug("Input id: {0}, return type: {1}".format(input_id, input_return))

    # If file changes then blank plot selection
    if input_id == "dropdown-files":
        plot_clickdata = None
        sel_node_id = None
    elif input_id == "dropdown-nodes":
        plot_clickdata = None

    if plot_clickdata is not None and "text" in plot_clickdata["points"][0]:
        element_type = plot_clickdata["points"][0]["text"].split("<br>")[0].split(":")[0].strip()
        element_id = plot_clickdata["points"][0]["text"].split("<br>")[0].split(":")[1].strip()
        # Currently not interested in edges!
        if element_type.lower() == "edge":
            # The nearest node will be the target node
            element_type = "node"
            target_node_id = element_id.split("'")[3]
            element_id = target_node_id
    elif plot_clickdata is not None and "text" not in plot_clickdata["points"][0]:
        log_debug("text missing in clickData: {0}".format(json.dumps(plot_clickdata, indent=2)))
        element_type = None
        element_id = None
    elif sel_node_id is not None and sel_node_id != '0':
        element_type = "node"
        element_id = sel_node_id
    else:
        element_type = None
        element_id = None

    ###############################################
    # What parameter values to I have to work with?
    ###############################################

    log_debug("file_name: {0}, layout: {1}, centrality: {2}, selected node: {3}, element_type: {4}, element_id: {5}".format(
        file_name, layout, centrality, sel_node_id, element_type, element_id))

    graphml_file_name = file_name[2:len(file_name)]
    # graph_analytics_file_name = f"{graphml_file_name[:-8]}_analytics.yaml"
    graph_analytics_file_name = f"{graphml_file_name[:-8]}_analytics.json"

    inpFilePath = os.path.join(gml_project_path, graphml_file_name)

    log_debug(f"Reading file: {inpFilePath}")
    G = nx.read_graphml(inpFilePath)

    # Now I need a list of node labels - G.nodes[node_id]['label']
    nodes_details = []
    nodes_details.append((":Non selected", '0'))
    element_label = ":Non selected"
    for node_id in G.nodes():
        nodes_details.append((G.nodes[node_id]['label'], node_id))
        if node_id == element_id:
            element_label = G.nodes[node_id]['label']

    nodes_details = sorted(nodes_details, key=lambda x: x[0])

    dropdown_nodes = [{'label': node[0], 'value': node[1]} for node in nodes_details]
    sel_node_label = ":Non selected"

    # What am I going to do now - depend on click_actions value

    log_debug(f"Click Action: {click_action}")

    if element_type is not None and element_type.lower() == "node" and click_action != "Node table":

        # click_actions = [
        #     "Node table",
        #     "Node Neighborhood - out",
        #     "Node Neighborhood - all",
        #     "Node Shortest paths",
        # ]

        inp_dict_file = os.path.join(gml_project_path, graph_analytics_file_name)
        if os.path.exists(inp_dict_file):
            log_debug(f"Reading file: {inp_dict_file}")
            with open(inp_dict_file, 'r', encoding='utf-8') as f_read:
                # dt_graph_analytics = yaml.load(f_read, Loader=yaml.FullLoader)
                dt_graph_analytics = json.load(f_read)
            log_debug(f"Reading file: Complete")

        if click_action == "Node Shortest paths" and "shortest_path" in dt_graph_analytics["nodes"][element_id]:

            PG = G.copy()

            # get a list of edges used in shortest paths
            log_debug(f"Shortest path: Get edge list")
            edge_list = []
            for target_node_id in dt_graph_analytics["nodes"][element_id]["shortest_path"]:
                prev_node_id = element_id
                for step_node_id in dt_graph_analytics["nodes"][element_id]["shortest_path"][target_node_id]:
                    if (prev_node_id, step_node_id) not in edge_list:
                        edge_list.append((prev_node_id, step_node_id))
                    prev_node_id = step_node_id

            # remove any edges that don't involve a shortest path
            log_debug(f"Shortest path: Get remove edge list")
            remove_edges = []
            for edge_id in PG.edges():
                source_node_id = edge_id[0]
                target_node_id = edge_id[1]
                if (source_node_id, target_node_id) not in edge_list:
                    remove_edges.append((source_node_id, target_node_id))

            log_debug(f"Shortest path: Remove edges")
            for edge_id in remove_edges:
                source_node_id = edge_id[0]
                target_node_id = edge_id[1]
                PG.remove_edge(source_node_id, target_node_id)

        else:
            if click_action == "Node Neighborhood - out":
                undirected = False
            else:
                undirected = True

            PG = nx.ego_graph(G, element_id, undirected=undirected)

            if click_action == "Node Neighborhood - out":
                # remove any edges that don't involve the centre
                remove_edges = []
                for edge_id in PG.edges():
                    source_node_id = edge_id[0]
                    target_node_id = edge_id[1]
                    if source_node_id != element_id:
                        remove_edges.append((source_node_id, target_node_id))

                for edge_id in remove_edges:
                    source_node_id = edge_id[0]
                    target_node_id = edge_id[1]
                    PG.remove_edge(source_node_id, target_node_id)

        # Show analytics for complete graph
        # dt_graph_analytics = process_graph_analytics(PG, incl_shortest_paths=False)

        #############
        # Set up plot
        #############
        number_of_nodes = nx.number_of_nodes(PG)
        number_of_edges = nx.number_of_edges(PG)

        number_of_elements = number_of_nodes + (number_of_edges * 3)
        est_max_nodes = int(number_of_nodes * (max_elements / number_of_elements))
        max_nodes = number_of_nodes if number_of_nodes <= est_max_nodes else est_max_nodes

        title = f'<br>{click_action} graph from graphML file: {file_name}, layout: {layout}, Nodes: {number_of_nodes}, Edges: {number_of_edges}, Max nodes: {max_nodes}<br>'
        fig = plot_graph(PG, layout=layout, title=title, max_nodes=max_nodes, seed=2, element_type=element_type,
                           element_id=element_id, dt_graph_analytics=dt_graph_analytics, show_centrality=centrality)

        pause = True

    else:
        # Is there an analytics file? test01_analytics_7_graph_analytics.yaml - f"{sub_project}_{phase}_{stage}_graph_analytics.yaml"
        # todo check date and time of files if graphml file newer then recreate analytics
        inp_dict_file = os.path.join(gml_project_path, graph_analytics_file_name)
        if os.path.exists(inp_dict_file):
            log_debug(f"Reading file: {inp_dict_file}")
            with open(inp_dict_file, 'r', encoding='utf-8') as f_read:
                # dt_graph_analytics = yaml.load(f_read, Loader=yaml.FullLoader)
                dt_graph_analytics = json.load(f_read)
            log_debug(f"Reading file: Complete")
        else:
            # Is this one of my files? test01_analytics_7_graph.graphml - f"{sub_project}_{phase}_{stage}_graph.graphml"
            # only done once as file will be there the next time
            name_split = graphml_file_name.split("_")
            if len(name_split) == 4:
                phase = name_split[1]
                sub_project = name_split[0]
                stage = int(name_split[2])
                dt_graph_analytics = process_graph_analytics(G)
                # Output dictionary as a yaml file - so there for next time
                # outFilePath = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage}_graph_analytics.yaml")
                # create_yaml_file(dt_graph_analytics, outFilePath)
                outFilePath = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage}_graph_analytics.json")
                create_json_file(dt_graph_analytics, outFilePath)

        #############
        # Set up plot
        #############
        number_of_nodes = nx.number_of_nodes(G)
        number_of_edges = nx.number_of_edges(G)

        number_of_elements = number_of_nodes + (number_of_edges * 3)
        est_max_nodes = int(number_of_nodes * (max_elements / number_of_elements))
        max_nodes = number_of_nodes if number_of_nodes <= est_max_nodes else est_max_nodes

        title = f'<br>Network graph from graphML file: {file_name}, layout: {layout}, Nodes: {number_of_nodes}, Edges: {number_of_edges}, Max nodes: {max_nodes}<br>'
        fig = plot_graph(G, layout=layout, title=title, max_nodes=max_nodes, seed=2, element_type=element_type,
                           element_id=element_id, dt_graph_analytics=dt_graph_analytics, show_centrality=centrality)

    ########################
    # Set up analytics table
    ########################
    graph_analytics_layout = graph_analytics_table(dt_graph_analytics, element_type=element_type, element_id=element_id,
                                                   max_nodes=max_nodes)

    return element_label, dropdown_nodes, fig, graph_analytics_layout


if __name__ == "__main__":
    app.run_server(debug=True)