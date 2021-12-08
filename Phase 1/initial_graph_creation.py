from common_routines import *

def add_demo_node(dt_graph, node_id, add_sample_attr, add_events=True, add_patients=True):
    dt_graph["graph"]["nodes"][node_id] = dict()
    dt_graph["graph"]["nodes"][node_id]["label"] = f"Node {node_id}"
    dt_graph["graph"]["nodes"][node_id]["type"] = "Patient"
    if add_events:
        dt_graph["graph"]["nodes"][node_id]["events"] = random.randint(1, 100)
    if add_patients:
        dt_graph["graph"]["nodes"][node_id]["patients"] = random.randint(1, 10)

    if add_sample_attr:
        dt_graph["graph"]["nodes"][node_id]["nodeSampleAttributeInteger"] = random.randint(1, 1000)
        dt_graph["graph"]["nodes"][node_id]["nodeSampleAttributeBoolean"] = random.randint(0, 1)
        dt_graph["graph"]["nodes"][node_id]["nodeSampleAttributeFloat"] = round((
                random.randint(1, 1000000) / 10000), 4)
        dt_graph["graph"]["nodes"][node_id][
            "nodeSampleAttributeString"] = "Here is a random string: {0:,.2f}".format(
            random.randint(1, 1000000) / 100)


def add_demo_edge(dt_graph, edge_id, source, target, add_sample_attr, add_events=True, add_patients=True):
    dt_graph["graph"]["edges"][edge_id] = dict()
    dt_graph["graph"]["edges"][edge_id]["source"] = source
    dt_graph["graph"]["edges"][edge_id]["target"] = target
    dt_graph["graph"]["edges"][edge_id]["label"] = f"Edge from node {source} to node {target}"
    dt_graph["graph"]["edges"][edge_id]["type"] = "Patient has Patient"

    if (edge_id % 2) == 0:
        dt_graph["graph"]["edges"][edge_id]["highlight"] = 1

    if add_events:
        dt_graph["graph"]["edges"][edge_id]["events"] = random.randint(1, 100)
    if add_patients:
        dt_graph["graph"]["edges"][edge_id]["patients"] = random.randint(1, 10)

    if add_sample_attr:
        dt_graph["graph"]["edges"][edge_id]["edgeSampleAttributeInteger"] = random.randint(1, 1000)
        dt_graph["graph"]["edges"][edge_id]["edgeSampleAttributeBoolean"] = random.randint(0, 1)
        dt_graph["graph"]["edges"][edge_id]["edgeSampleAttributeFloat"] = round(
            (random.randint(1, 1000000) / 10000), 4)
        dt_graph["graph"]["edges"][edge_id][
            "edgeSampleAttributeString"] = "Here is a random string: {0:,.2f}".format(
            random.randint(1, 1000000) / 100)


def create_demo_dt_graph(label="Graph Label", directed=0, id=1, comment=None, num_nodes=3, add_sample_attr=True,
                         add_events=True, add_patients=True):
    '''

    :param label: String
    :param directed: 0/1
    :param id: Integer
    :param comment: String
    :param num_nodes: Integer
    :param add_sample_attr: True/False
    :return: dictionary contianing all grpah details

    '''

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    dt_graph = dict()

    dt_graph["graph"] = dict()
    if comment is not None:
        dt_graph["graph"]["comment"] = comment
    dt_graph["graph"]["directed"] = directed
    dt_graph["graph"]["id"] = id
    dt_graph["graph"]["label"] = label

    if num_nodes > 0:

        dt_graph["graph"]["nodes"] = dict()
        dt_graph["graph"]["edges"] = dict()

        edge_id = 0

        for node_id in range(1, (num_nodes + 1)):

            add_demo_node(dt_graph, node_id, add_sample_attr, add_events, add_patients)

            if node_id > 1:
                source = node_id - 1
                target = node_id
                edge_id += 1

                add_demo_edge(dt_graph, edge_id, source, target, add_sample_attr, add_events, add_patients)

        # Put in final link
        source = node_id
        target = 1
        edge_id += 1

        add_demo_edge(dt_graph, edge_id, source, target, add_sample_attr)

        assign_colour_size(dt_graph)

    return dt_graph


def create_networkx_graph(dt_graph):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    G = None

    if "graph" in dt_graph:

        if "directed" in dt_graph["graph"] and dt_graph["graph"]["directed"] == 1:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        # graph attributes
        for graph_key in dt_graph["graph"]:

            if graph_key not in ["nodes", "edges"]:
                G.graph[graph_key] = dt_graph["graph"][graph_key]

        # nodes
        if "nodes" in dt_graph["graph"]:

            list_nodes = []

            for node_id in dt_graph["graph"]["nodes"]:

                dict_attbs = dict()
                att_key = "label"
                if att_key in dt_graph["graph"]["nodes"][node_id]:
                    dict_attbs[att_key] = dt_graph["graph"]["nodes"][node_id][att_key]
                #     label = dt_graph["graph"]["nodes"][node_id][att_key]
                # else:
                #     label = node_id

                for att_key in dt_graph["graph"]["nodes"][node_id]:

                    if att_key not in ["label", ]:
                        dict_attbs[att_key] = dt_graph["graph"]["nodes"][node_id][att_key]

                # list_nodes.append((label,dict_attbs))
                list_nodes.append((node_id, dict_attbs))

            G.add_nodes_from(list_nodes)

        # edges
        # If there are no nodes then there can't be any edges
        # (2, 3, {'weight': 3.1415})
        # Or should edges create nodes?
        if "edges" in dt_graph["graph"]:

            list_edges = []

            for edge_id in dt_graph["graph"]["edges"]:

                # source = dt_graph["graph"]["nodes"][edge_id[0]]["label"]
                # target = dt_graph["graph"]["nodes"][edge_id[1]]["label"]

                source = dt_graph["graph"]["edges"][edge_id]["source"]
                target = dt_graph["graph"]["edges"][edge_id]["target"]

                dict_attbs = dict()
                if "label" in dt_graph["graph"]["edges"][edge_id]:
                    att_key = "label"
                    dict_attbs[att_key] = dt_graph["graph"]["edges"][edge_id][att_key]

                for att_key in dt_graph["graph"]["edges"][edge_id]:

                    if att_key not in ["label", "source", "target"]:
                        dict_attbs[att_key] = dt_graph["graph"]["edges"][edge_id][att_key]

                list_edges.append((source, target, dict_attbs))

            G.add_edges_from(list_edges)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return G


def plot_graph(G, outFilePath=None, with_labels=False, font_weight='normal', node_color=None, node_size=None,
               edge_color=None, edge_size=None, show_plot=False):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    subax1 = plt.subplot(111)  # nrows = 1, ncols = 1, index = 1

    sample_color = "#ff43a4"
    if node_color is None:
        node_color = sample_color

    if node_size is None:
        d = dict(G.degree)
        node_size = [v * 100 for v in d.values()]

    sample_color = "#000000"
    if edge_color is None:
        edge_color = sample_color

    if edge_size is None:
        edges = G.edges
        edge_size = [G[u][v]['weight'] for u, v in edges]

    nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_color, node_size=node_size,
            edge_color=edge_color, width=edge_size)

    if show_plot:
        plt.show()
    else:
        plotFilePath = outFilePath.replace(".gml", "_matplotlib.png")
        plt.savefig(plotFilePath, dpi=1200)

    if outFilePath is not None:
        nx.write_gml(G, outFilePath)
        outFilePath = outFilePath.replace(".gml", ".graphml")
        try:
            nx.write_graphml_lxml(G, outFilePath)
        except:
            pass
        outFilePath = outFilePath.replace(".graphml", ".gexf")
        nx.write_gexf(G, outFilePath)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def plot_multiple_graphs(project, dex_project_path, csv_project_path, gml_project_path, sub_project, stage=1, show_plot=False):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    with_labels = False
    font_weight = "normal"

    if stage == 6:

        rdvs = []
        rdvs.append(("demographics", "caboodle"))
        rdvs.append(("hospital_admissions", "caboodle"))
        rdvs.append(("medication_orders", "caboodle"))

        incl_node_types = None
        output_stage = (stage*10)+1
        dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path, sub_project,
                                          incl_node_types, output_stage)

        # Create a GML file for dt_graph, read in GML file and plot
        outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{output_stage}_graph.gml")

        G = nx.read_gml(outFilePath)

        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax1 = plt.subplot(231)  # nrows = 2, ncols = 3, index = 1
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        size_method = "events"
        dt_graph = assign_colour_size(dt_graph, size_method=size_method)
        G = nx.read_gml(outFilePath)
        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax2 = plt.subplot(232)
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        size_method = "patients"
        dt_graph = assign_colour_size(dt_graph, size_method=size_method)
        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax3 = plt.subplot(233)
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        # Simpler graphs
        incl_node_types = []
        output_stage = (stage*10)+2
        incl_node_types.append("patient")
        # incl_node_types.append("hospital admission")
        incl_node_types.append("drug")
        incl_node_types.append("pharmaceutical class")

        dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path, sub_project,
                                          incl_node_types=incl_node_types, stage=output_stage)

        # Create a GML file for dt_graph, read in GML file and plot
        outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{output_stage}_graph.gml")

        G = nx.read_gml(outFilePath)

        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax4 = plt.subplot(234)
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        size_method = "events"
        dt_graph = assign_colour_size(dt_graph, size_method=size_method)
        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax5 = plt.subplot(235)
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        size_method = "patients"
        dt_graph = assign_colour_size(dt_graph, size_method=size_method)
        node_colors = get_node_colors(dt_graph)
        node_sizes = get_node_sizes(dt_graph)

        log_debug("Create plot")
        subax6 = plt.subplot(236)
        nx.draw(G, with_labels=with_labels, font_weight=font_weight, node_color=node_colors, node_size=node_sizes)

        if show_plot:
            plt.show()
        else:
            plotFilePath = os.path.join(dex_project_path, f"{sub_project}_demo_{stage}_matplotlib.png")
            plt.savefig(plotFilePath, dpi=1200)

    elif stage == 7:

        for graph_num in range(0,4):

            rdvs = []
            rdvs.append(("demographics", "caboodle"))
            rdvs.append(("hospital_admissions", "caboodle"))
            rdvs.append(("medication_orders", "caboodle"))

            if graph_num in [0,2, ]:
                incl_node_types = None
            else:
                incl_node_types = []
                incl_node_types.append("patient")
                incl_node_types.append("drug")
                incl_node_types.append("pharmaceutical class")

            if graph_num in [0, 1, ]:
                highlight_patients = None
            else:
                highlight_patient = get_first_project_id(dex_project_path, sub_project)
                highlight_patients = []
                highlight_patients.append(highlight_patient)

            output_stage = (stage * 10) + graph_num
            dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path,
                                              sub_project, incl_node_types, stage=output_stage,
                                              highlight_patients=highlight_patients,
                                              output_yaml=False, output_excel=False, output_graphml=True)

            # Path to GML file
            outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{output_stage}_graph.gml")

            G = nx.read_gml(outFilePath)

            node_colors = get_node_colors(dt_graph)
            node_sizes = get_node_sizes(dt_graph)
            edge_colors = get_edge_colors(dt_graph)
            edge_sizes = get_edge_sizes(dt_graph)

            plot_graph(G, outFilePath, with_labels=with_labels, font_weight=font_weight, node_color=node_colors,
                       node_size=node_sizes, edge_color=edge_colors, edge_size=edge_sizes)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def main():

    '''
    '''

    log_debug("Started!")

    # Ignore python script name - check project paths
    dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                project_path = "Z:\\Projects\\Research\\0200-GRACE")

    if dex_project_path is not None:

        phase = "demo"

        # Ignore python script name - get list of stages to run
        run_stages = get_stages(sys.argv[1:], default=[4,5,6,7,8,9,10,11,12 ])

        log_debug(f"Phase: {phase}, stages: {run_stages}")

        # Stage 1 - Very simple coloured graph
        # Stage 2 - Very simple coloured graph - with export files
        # stage 3 - All RDV data into dictionary, create graph from dictionary and plot, save to gml file
        # stage 4 - All RDV data into dictionary, save to gml file create graph from gml file and plot
        # stage 5 - Selected RDV data into dictionary and highlighted patint, save to gml file create graph from gml file and plot
        # Stage 6 - multiple graphs - All RDV vs Selected RDV plots show node size based on events, patients and combined
        # Stage 7 - multiple graphs - All RDV vs Selected RDV with no highlighted and highlighted patient
        # Stage 8 - add in time tree - just files
        # stage 9 - time tree simpler graph - just files
        # stage 10 - tree graph single type of node (drug) - just files
        # stage 11 - Homogeneous graph - drugs
        # stage 12 - Homogeneous graph - drugs and days i.e which drugs precede which other drugs

        for stage in run_stages:

            log_debug(f"Stage: {stage}")

            if stage in [1,2,]:

                size_method = "patients"
                dt_graph = create_demo_dt_graph(label="This is a sample graph", directed=1, id=42, comment="Hello I am a graph",
                                                num_nodes=10)

                if stage == 1:

                    G = create_networkx_graph(dt_graph)

                    node_colors = ['#009900', '#009933', '#009966', '#009999', '#0099cc', '#0099ff', '#00cc00', '#00cc33',
                                   '#00cc66', '#00cc99']

                    outFilePath = os.path.join(gml_project_path, f"initial_demo_{stage}_nxgraph.gml")
                    plot_graph(G, outFilePath, with_labels=True, node_color=node_colors)

                elif stage == 2:

                    # Output yaml file of dictionary
                    outFilePath = os.path.join(gml_project_path, f"initial_demo_{stage}_{size_method}_graph.yaml")
                    create_yaml_file(dt_graph, outFilePath)

                    outFilePath = os.path.join(gml_project_path, f"initial_demo_{stage}_{size_method}_graph.xlsx")
                    create_excel_file(dt_graph, outFilePath)

                    outFilePath_graphml = os.path.join(gml_project_path, f"initial_demo_{stage}_graph.graphml")
                    create_graphml_file(dt_graph, outFilePath_graphml)

                    outFilePath = os.path.join(gml_project_path, f"initial_demo_{stage}_graph.gml")
                    create_gml_file(dt_graph, outFilePath=outFilePath)

                    G = nx.read_gml(outFilePath)

                    outFilePath = None # os.path.join(gml_project_path, f"initial_demo_{stage}_nxgraph.gml")
                    node_colors = get_node_colors(dt_graph)
                    node_sizes = get_node_sizes(dt_graph)
                    edge_colors = get_edge_colors(dt_graph)
                    edge_sizes = get_edge_sizes(dt_graph)
                    plot_graph(G, outFilePath, with_labels=True, node_color=node_colors, node_size=node_sizes,
                               edge_color=edge_colors, edge_size=edge_sizes)

            elif stage in [3,4,5,8,9,10,]:

                sub_project = "sp01"

                rdvs = []
                rdvs.append(("demographics", "caboodle"))
                rdvs.append(("hospital_admissions", "caboodle"))
                rdvs.append(("medication_orders", "caboodle"))

                incl_node_types = None
                highlight_patients = None
                if stage in [5,9,]:
                    incl_node_types = []
                    incl_node_types.append("patient")
                    incl_node_types.append("drug")
                    incl_node_types.append("pharmaceutical class")

                    highlight_patient = get_first_project_id(dex_project_path, sub_project)
                    highlight_patients = []
                    highlight_patients.append(highlight_patient)

                if stage in [10,]:
                    incl_node_types = []
                    incl_node_types.append("drug")

                    highlight_patient = get_first_project_id(dex_project_path, sub_project)
                    highlight_patients = []
                    highlight_patients.append(highlight_patient)

                if stage in [8,9,10,]:
                    time_tree_grad = "day"
                else:
                    time_tree_grad = None

                method = "heterogeneous"

                dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path, sub_project,
                                                  incl_node_types, stage=stage, highlight_patients=highlight_patients,
                                                  time_tree_grad=time_tree_grad, output_yaml=True, output_excel=True,
                                                  output_graphml=True)

                # size_method = "events"
                # dt_graph = assign_colour_size(dt_graph, size_method=size_method)

                if stage == 3:
                    # Create a graph directly from dt_graph, plot and save
                    G = create_networkx_graph(dt_graph)

                    outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{stage}_nxgraph.gml")
                    node_colors = get_node_colors(dt_graph)
                    node_sizes = get_node_sizes(dt_graph)
                    edge_sizes = get_edge_sizes(dt_graph)
                    plot_graph(G, outFilePath, with_labels=False, node_color=node_colors, node_size=node_sizes, edge_size=edge_sizes)

                elif stage in [4, 5, ]:

                    # Path to GML file
                    outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{stage}_graph.gml")

                    G = nx.read_gml(outFilePath)

                    outFilePath = os.path.join(gml_project_path, f"{sub_project}_demo_{stage}_nxgraph.gml")
                    node_colors = get_node_colors(dt_graph)
                    node_sizes = get_node_sizes(dt_graph)
                    edge_colors = get_edge_colors(dt_graph)
                    edge_sizes = get_edge_sizes(dt_graph)
                    plot_graph(G, outFilePath, with_labels=False, node_color=node_colors, node_size=node_sizes,
                               edge_color=edge_colors, edge_size=edge_sizes)

                else:

                    if highlight_patients is not None:
                        for patient_id in highlight_patients:
                            # NB size of nodes based on events as only one patient
                            dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path,
                                                              gml_project_path, sub_project,
                                                              incl_node_types, stage=stage, size_method="events",
                                                              highlight_patients=None,
                                                              time_tree_grad=time_tree_grad, output_yaml=True,
                                                              output_excel=True,
                                                              output_graphml=True, method=method, inc_params=True,
                                                              sel_patient=patient_id)

                    pause = True

            elif stage in [6, 7, ]:

                sub_project = "sp01"

                plot_multiple_graphs(project, dex_project_path, csv_project_path, gml_project_path, sub_project, stage=stage)

            elif stage in [11, 12, ]:

                sub_project = "sp01"

                rdvs = []
                rdvs.append(("medication_orders", "caboodle"))

                incl_node_types = None
                highlight_patients = None
                if stage in [11,12,]:
                    incl_node_types = []
                    incl_node_types.append("drug")

                    highlight_patient = get_first_project_id(dex_project_path, sub_project)
                    highlight_patients = []
                    highlight_patients.append(highlight_patient)

                if stage in [12,]:
                    time_tree_grad = "day"
                else:
                    time_tree_grad = None

                method = "homogeneous"

                dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path, sub_project,
                                                  incl_node_types, stage=stage, highlight_patients=highlight_patients,
                                                  time_tree_grad=time_tree_grad, output_yaml=True, output_excel=True,
                                                  output_graphml=True, method=method, inc_params=True)

                if highlight_patients is not None:
                    for patient_id in highlight_patients:
                        # NB size of nodes based on events as only one patient
                        dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path,
                                                          gml_project_path, sub_project,
                                                          incl_node_types, stage=stage, size_method="events",
                                                          highlight_patients=None,
                                                          time_tree_grad=time_tree_grad, output_yaml=True,
                                                          output_excel=True,
                                                          output_graphml=True, method=method, inc_params=True,
                                                          sel_patient=patient_id)

    log_debug("Done!")

if __name__ == "__main__":
    main()
