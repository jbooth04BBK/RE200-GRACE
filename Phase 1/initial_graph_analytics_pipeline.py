from common_routines import *


def extract_patient_list(project, csv_project_path, sub_project, phase, output_folder, stage=1, sel_patient=None):
    '''

    '''

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"
    source = "caboodle"
    rdv = "dots"

    file_name = f"{file_name_prefix}{source}_patient_{rdv}.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)

    # load RDV into dataframe and pass to relevant function
    log_debug("Processing RDV: {0}, file: {1}".format(rdv, file_name))
    df_rdv = pd.read_csv(inpfilepath)

    # sp03_caboodle_patient_dots.csv
    # project_id,sex,age_group_at_admission,drug_simple_generic_name,drug_pharmaceutical_class_name,drug_pharmaceutical_subclass_name,day_of_admission

    # WHat is the age_group of the selected patient
    temp = df_rdv.loc[df_rdv['project_id'] == sel_patient, 'age_group_at_admission'].drop_duplicates().values.tolist()
    selected_age_group = temp[0]

    patient_list = df_rdv.loc[df_rdv['age_group_at_admission'] == selected_age_group, 'project_id'].drop_duplicates().values.tolist()
    patient_list.remove(sel_patient)

    log_debug("Patients found: {0}".format(len(patient_list)))

    return patient_list


def create_graphs(project, csv_project_path, sub_project, phase, output_folder, stage=1, sel_patient=None,
                  patient_list=None, output_working_files=True):


    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    centrality_summary = []
    dt_labels = dict()
    label_id = accumulator()

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"
    source = "caboodle"
    rdv = "dots"
    directed = 1
    method = "homogeneous"
    size_method = "combined"
    highlight_patients = None
    incl_node_types = []
    incl_node_types.append("drug")
    time_tree_grad = "day"
    inc_params = True

    file_name = f"{file_name_prefix}{source}_patient_{rdv}.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)

    # load RDV into dataframe and pass to relevant function
    log_debug("Processing RDV: {0}, file: {1}".format(rdv, file_name))
    df_orig = pd.read_csv(inpfilepath)
    # Make sure in correct order
    df_rdv = df_orig.sort_values(["project_id", "day_of_admission", "drug_simple_generic_name"], ignore_index=True)

    # Iterate through df to create nodes and edges
    number_rows = len(df_rdv.index)

    for patient_pass in range(1,3):

        # pass 1 - selected patient
        # pass 2 - patient_list

        log_debug("Patient pass: {0}".format(patient_pass))

        # Define dt_patients
        dt_patients = dict()
        if patient_pass == 1:
            project_id = sel_patient
            dt_patients[project_id] = dict()
            dt_patients[project_id]['instances'] = dict()
            dt_patients[project_id]['instances']['total'] = 1
            dt_patients[project_id]['edges'] = dict()
        else:
            for project_id in patient_list:
                dt_patients[project_id] = dict()
                dt_patients[project_id]['instances'] = dict()
                dt_patients[project_id]['instances']['total'] = 1
                dt_patients[project_id]['edges'] = dict()

        for max_day_of_admission in range(0,14):

            log_debug("Max day of admission: {0}".format(max_day_of_admission))

            # Create graph
            dt_graph = create_graph_structure(project, sub_project, directed, method)

            # need a reverse lookup - for patient with project id which is its node? Also for edges same drug classification
            dt_nodes = dict()
            dt_edges = dict()
            dt_periods = dict()

            node_id = accumulator()
            edge_id = accumulator()

            prev_row = None
            prev_rows = []
            cnt_patient_id = ""
            cnt_day_of_admission = ""

            for row_num, row in df_rdv.iterrows():

                sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(row_num + 1, number_rows))
                sys.stdout.flush()

                patient_id = row['project_id']
                day_of_admission = row['day_of_admission']
                drug_simple_generic_name = row['drug_simple_generic_name']

                if patient_pass == 1 and sel_patient is not None and patient_id == sel_patient:
                    include_patient = True
                elif patient_pass == 2 and patient_list is not None and patient_id in patient_list:
                    include_patient = True
                else:
                    include_patient = False

                if include_patient and day_of_admission <= max_day_of_admission:

                    # log_debug(f"{row_num}: {patient_id}, {day_of_admission}, {drug_simple_generic_name}")

                    # If co-medications then need to keep track of all previous medications for this patient and period
                    if cnt_patient_id != patient_id or cnt_day_of_admission != day_of_admission:
                        cnt_patient_id = patient_id
                        cnt_day_of_admission = day_of_admission

                        prev_rows = [None, ]

                    for prev_row_num, prev_row in enumerate(prev_rows):
                        add_dots_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, prev_row,
                                                       row, node_id, edge_id, incl_node_types,
                                                       time_tree_grad, highlight_patients, method=method,
                                                       inc_params=inc_params, directed=directed, index=prev_row_num)

                    prev_rows.append(row)
                    prev_row = row

            print()

            # Graph complete
            if output_working_files:
                # Output dictionary as a yaml file
                outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{patient_pass}_{max_day_of_admission}_rawgraph.yaml")
                create_yaml_file(dt_graph, outFilePath)

            # Do some one off tasks so they don't need to be repeated
            # store max_events and max_patients, total events, total patients(?), total nodes, total edges
            # store parameters in graph
            # Add an initial colour and size so will work out of the box.
            #
            assign_colour_size(dt_graph, size_method=size_method)

            if output_working_files:
                outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{patient_pass}_{max_day_of_admission}_{size_method}_graph.xlsx")
                create_excel_file(dt_graph, outFilePath, dt_nodes, dt_edges, dt_patients, dt_periods)

            # This file is required for analytics
            outFilePath_graphml = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{patient_pass}_{max_day_of_admission}_graph.graphml")
            create_graphml_file(dt_graph, outFilePath_graphml)

            log_debug("Graph complete")

            # Using the file created in previous stage - NB graphML file not created from a graph but my defined dictionary
            log_debug(f"Reading file: {outFilePath_graphml}")
            G = nx.read_graphml(outFilePath_graphml)

            dt_graph_analytics = process_graph_analytics(G, weight_key='patients', incl_centralities=True, incl_shortest_paths=False,
                            inc_attribute_assortivity=False, inc_error_logging=False)

            if output_working_files:
                # Output dictionary as a yaml file
                outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{patient_pass}_{max_day_of_admission}_graph_analytics.yaml")
                create_yaml_file(dt_graph_analytics, outFilePath)

            # Output dictionary as a json file - required by graphML file for plotting
            outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{patient_pass}_{max_day_of_admission}_graph_analytics.json")
            create_json_file(dt_graph_analytics, outFilePath)

            log_debug("Record Graph Summary")

            position = 0
            node_id = ""
            cnt_label_id = 0
            label = ""
            patients = 0
            events = 0

            for graph_measure in graph_measures:

                if graph_measure == "center":
                    score = len(dt_graph_analytics["graph"][graph_measure])
                else:
                    score = dt_graph_analytics["graph"][graph_measure]

                row = []
                row.append(patient_pass)
                row.append(max_day_of_admission)
                row.append(graph_measure)
                row.append(position)
                row.append(node_id)
                row.append(score)
                row.append(cnt_label_id)
                row.append(label)
                row.append(patients)
                row.append(events)

                centrality_summary.append(row)


            log_debug("Record Centrality Summary")

            # Record in summary file
            for centrality in dt_graph_analytics["graph"]["centralities"]:

                for position in dt_graph_analytics["graph"]["centralities"][centrality]:

                    node_id = dt_graph_analytics["graph"]["centralities"][centrality][position]["node"]
                    score = dt_graph_analytics["graph"]["centralities"][centrality][position]["score"]
                    label = dt_graph_analytics["nodes"][node_id]["label"]
                    patients = dt_graph_analytics["nodes"][node_id]["patients"]
                    events = dt_graph_analytics["nodes"][node_id]["events"]

                    if label in dt_labels:
                        cnt_label_id = dt_labels[label]
                    else:
                        cnt_label_id = label_id(1)
                        dt_labels[label] = cnt_label_id

                    row = []
                    row.append(patient_pass)
                    row.append(max_day_of_admission)
                    row.append(centrality)
                    row.append(position)
                    row.append(node_id)
                    row.append(score)
                    row.append(cnt_label_id)
                    row.append(label)
                    row.append(patients)
                    row.append(events)

                    centrality_summary.append(row)

            log_debug("Analytics Complete")

        df = pd.DataFrame(centrality_summary,
                          columns=['patient_pass', 'max_day_of_admission', 'measure', 'position', 'node_id', 'score',
                                   'label_id', 'label', 'patients', 'events'])

        # Output dictionary as a json file
        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_analytics_summary.csv")
        log_debug(f"Output Centrality Summary: {outFilePath}")
        df.to_csv(outFilePath, encoding='utf-8', index=False)

        log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def main():

    '''
    '''

    log_debug("Started!")

    # Ignore python script name - check project paths
    dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                project_path = "Z:\\Projects\\Research\\0200-GRACE")

    if dex_project_path is not None:

        phase = "pipeline"

        # Ignore python script name - get list of stages to run
        run_stages = get_stages(sys.argv[1:], default=[1, 2, ])

        log_debug(f"Phase: {phase}, stages: {run_stages}")

        # Stage 1 - identify patients - Create graphs and analytics
        # Stage 2 - example plot of changes in centrality positions

        for stage in run_stages:

            log_debug(f"Stage: {stage}")

            if stage in [1, 2,]:

                sub_project = "sp03"

                # Select first patient to highlight
                sel_patient = get_first_project_id(dex_project_path, sub_project)

                output_folder = gml_project_path + "\\Working"

                if stage in [1, ]:

                    patient_list = extract_patient_list(project, csv_project_path, sub_project, phase, csv_project_path, stage=stage,
                                             sel_patient=sel_patient)

                    create_graphs(project, csv_project_path, sub_project, phase, output_folder=output_folder, stage=stage,
                                     sel_patient=sel_patient, patient_list=patient_list, output_working_files=False)

                elif stage in [2, ]:

                    analytic_plot_type = analytic_plot_types[0] # graph
                    # analytic_plot_type = analytic_plot_types[1] # centralities

                    # centrality = centralities[0] # 'harmonic_centrality'
                    # centrality = centralities[1] # 'eigenvector_centrality'
                    # centrality = centralities[2] # 'pagerank'
                    # centrality = centralities[3] # 'authorities'
                    # centrality = centralities[4] # 'degree_centrality')
                    # centrality = centralities[5]  # 'betweenness_centrality'
                    centrality = centralities[6] # 'closeness_centrality'
                    # centrality = centralities[7] # 'hubs'

                    # Read CSV file
                    inFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage-1}_analytics_summary.csv")
                    df_all_analytic_data = pd.read_csv(inFilePath)

                    fig = plot_graph_analytics_summary(df_all_analytic_data, analytic_plot_type=analytic_plot_type, centrality=centrality)

                    inFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage-1}_analytics_summary.html")
                    fig.write_html(inFilePath, auto_open=True)

    log_debug("Done!")

if __name__ == "__main__":
    main()
