from common_routines import *


def create_dots_test_analytics_dt_graph(project, sub_project, phase, output_folder, stage=1, directed=1, method="homogeneous",
                                        random_create=False, num_nodes=10, num_patients=10, highlight=0):
    '''

    '''

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    dt_patients = dict()
    dt_periods = dict()
    dt_drugs = dict()
    activities = []

    size_method = "patients"

    if random_create and num_nodes > 0 and num_patients> 0:
        pass
    else:
        # Create a fixed graph

        for patient_id in range (1,6):
            project_id = f"PR-000{patient_id}"
            hospital_no = f"999{patient_id}"
            dt_patients[project_id] = dict()
            dt_patients[project_id]['hospital_no'] = hospital_no
            dt_patients[project_id]['instances'] = dict()
            dt_patients[project_id]['instances']['total'] = 1
            dt_patients[project_id]['edges'] = dict()

        dt_drugs["Drug 1"] = ("Pharm Subclass 1", "Pharm Class 1")
        dt_drugs["Drug 2"] = ("Pharm Subclass 1", "Pharm Class 1")
        dt_drugs["Drug 3"] = ("Pharm Subclass 2", "Pharm Class 1")
        dt_drugs["Drug 4"] = ("Pharm Subclass 2", "Pharm Class 1")
        dt_drugs["Drug 5"] = ("Pharm Subclass 3", "Pharm Class 2")
        dt_drugs["Drug 6"] = ("Pharm Subclass 3", "Pharm Class 2")
        dt_drugs["Drug 7"] = ("Pharm Subclass 4", "Pharm Class 2")
        dt_drugs["Drug 8"] = ("Pharm Subclass 4", "Pharm Class 2")
        dt_drugs["Drug 9"] = ("Pharm Subclass 5", "Pharm Class 3")
        dt_drugs["Drug 10"] = ("Pharm Subclass 6", "Pharm Class 3")
        dt_drugs["Drug 11"] = ("Pharm Subclass 5", "Pharm Class 3")
        dt_drugs["Drug 12"] = ("Pharm Subclass 6", "Pharm Class 3")

        activities.append(("PR-0001", "Period 1", "Drug 1"))
        activities.append(("PR-0001", "Period 1", "Drug 3"))
        activities.append(("PR-0001", "Period 1", "Drug 5"))
        activities.append(("PR-0001", "Period 1", "Drug 7"))
        activities.append(("PR-0001", "Period 1", "Drug 10"))
        activities.append(("PR-0001", "Period 2", "Drug 1"))
        activities.append(("PR-0001", "Period 2", "Drug 2"))
        activities.append(("PR-0001", "Period 2", "Drug 4"))
        activities.append(("PR-0001", "Period 2", "Drug 6"))
        activities.append(("PR-0001", "Period 2", "Drug 8"))
        activities.append(("PR-0001", "Period 2", "Drug 9"))
        activities.append(("PR-0002", "Period 1", "Drug 1"))
        activities.append(("PR-0002", "Period 1", "Drug 3"))
        activities.append(("PR-0002", "Period 1", "Drug 5"))
        activities.append(("PR-0002", "Period 1", "Drug 7"))
        activities.append(("PR-0002", "Period 2", "Drug 1"))
        activities.append(("PR-0002", "Period 2", "Drug 3"))
        activities.append(("PR-0002", "Period 2", "Drug 5"))
        activities.append(("PR-0002", "Period 2", "Drug 7"))
        activities.append(("PR-0002", "Period 2", "Drug 9"))
        activities.append(("PR-0003", "Period 1", "Drug 1"))
        activities.append(("PR-0003", "Period 1", "Drug 2"))
        activities.append(("PR-0003", "Period 1", "Drug 4"))
        activities.append(("PR-0003", "Period 1", "Drug 6"))
        activities.append(("PR-0003", "Period 2", "Drug 1"))
        activities.append(("PR-0003", "Period 2", "Drug 2"))
        activities.append(("PR-0003", "Period 2", "Drug 3"))
        activities.append(("PR-0003", "Period 2", "Drug 4"))
        activities.append(("PR-0003", "Period 2", "Drug 6"))
        activities.append(("PR-0003", "Period 2", "Drug 8"))
        activities.append(("PR-0004", "Period 1", "Drug 11"))
        activities.append(("PR-0004", "Period 1", "Drug 12"))
        activities.append(("PR-0005", "Period 1", "Drug 11"))
        activities.append(("PR-0005", "Period 1", "Drug 12"))
        activities.append(("PR-0005", "Period 1", "Drug 3"))
        activities.append(("PR-0005", "Period 2", "Drug 1"))
        activities.append(("PR-0005", "Period 2", "Drug 11"))

    if len(dt_patients) > 0:

        if len(activities) > 0:

            dt_graph = create_graph_structure(project, sub_project, directed, method)

            # need a reverse lookup - for patient with project id which is its node? Also for edges same drug classification
            dt_nodes = dict()
            dt_edges = dict()

            node_id = accumulator()
            edge_id = accumulator()

            node_type = "drug"
            prev_node_type = "drug"

            cnt_patient_id = ""
            cnt_period = ""
            prev_activities = None

            for activity in activities:

                patient_id = activity[0]
                period = activity[1]
                drug_name = activity[2]

                node_label = f"Drug: {drug_name}"
                label = node_label

                parameters = {"Pharmaceutical subclass": dt_drugs[drug_name][0],
                              "Pharmaceutical class": dt_drugs[drug_name][1]}

                drug_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight,
                                         parameters=parameters)

                # Now add edges
                if patient_id != cnt_patient_id or period != cnt_period:
                    cnt_patient_id = patient_id
                    cnt_period = period
                    prev_activities = [None, ]

                for prev_activity in prev_activities:

                    if prev_activity is not None:

                        prev_drug_name = prev_activity[2]
                        prev_node_label = f"Drug: {prev_drug_name}"

                        prev_drug_node = add_rdv_node(dt_graph, dt_nodes, None, None, prev_node_label, prev_node_type,
                                                      accumulate=False)

                        label = f"{prev_node_label} comedication with {node_label}"
                        edge_type = f"{prev_node_type} comedication with {node_type}"

                        add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_drug_node, drug_node, label,
                                     edge_type, highlight=highlight)

                        # Add in reverse edge as linkage is reversable
                        if directed == 1:
                            label = f"{node_label} comedication with {prev_node_label}"
                            edge_type = f"{node_type} comedication with {prev_node_type}"

                            # NB reverse nodes
                            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, drug_node, prev_drug_node,
                                         label, edge_type, highlight=highlight)

                prev_activities.append(activity)

            assign_colour_size(dt_graph)

            # Output yaml file of dictionary
            outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_graph.yaml")
            create_yaml_file(dt_graph, outFilePath)

            # Create a excel file
            outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_graph.xlsx")
            create_excel_file(dt_graph, outFilePath, dt_nodes, dt_edges, dt_patients, dt_periods)

            outFilePath_graphml = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_graph.graphml")
            create_graphml_file(dt_graph, outFilePath_graphml)


def main():

    '''
    '''

    log_debug("Started!")

    # Ignore python script name - check project paths
    dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                project_path = "Z:\\Projects\\Research\\0200-GRACE")

    if dex_project_path is not None:

        phase = "analytics"

        # Ignore python script name - get list of stages to run
        run_stages = get_stages(sys.argv[1:], default=[1,2,3,4,5,6,7,8,])

        log_debug(f"Phase: {phase}, stages: {run_stages}")

        # Stage 1 - 10 patients, homogeneous graph of drug - create graph
        # Stage 2 - process graph analytics from graphML file created in stage 1

        for stage in run_stages:

            log_debug(f"Stage: {stage}")

            if stage in [1,2,3,4,5,6,7,8, ]:

                if stage in [1, 2, ]:
                    sub_project = "sp01"
                elif stage in [3, 4,]:
                    sub_project = "sp02"
                elif stage in [5, 6,]:
                    sub_project = "sp03"
                elif stage in [7, 8,]:
                    sub_project = "test01"

                if stage in [1,3,5,]:
                    rdvs = []
                    rdvs.append(("dots", "caboodle"))

                    incl_node_types = []
                    incl_node_types.append("drug")
                    time_tree_grad = "day"

                    # Select first patient to highlight
                    highlight_patient = get_first_project_id(dex_project_path, sub_project)
                    highlight_patients = []
                    highlight_patients.append(highlight_patient)

                    size_method = "combined" # events=days so the more 1 patient on 10 days as important as 10 patients on 1 day.
                    method = "homogeneous"

                    dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path,
                                                      sub_project, incl_node_types, stage=stage,size_method=size_method,
                                                      highlight_patients=highlight_patients, time_tree_grad=time_tree_grad,
                                                      output_yaml=True, output_excel=True, output_graphml=True, method=method,
                                                      directed=1, phase=phase, inc_params=True)

                    if highlight_patients is not None:
                        size_method = "events"  # NB size of nodes based on events as only one patient
                        for patient_id in highlight_patients:

                            dt_graph = create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path,
                                                              gml_project_path, sub_project,
                                                              incl_node_types, stage=stage, size_method=size_method,
                                                              highlight_patients=None,
                                                              time_tree_grad=time_tree_grad, output_yaml=True,
                                                              output_excel=True,
                                                              output_graphml=True, method=method, inc_params=True,
                                                              sel_patient=patient_id)

                elif stage in [7,]:

                    method = "homogeneous"

                    create_dots_test_analytics_dt_graph(project, sub_project, phase, gml_project_path, stage=stage,
                                                        directed=1, method=method, random_create=False,
                                                        num_nodes=10, num_patients=10, highlight=0)

                elif stage in [2,4,6,8]:

                    # Using the file created in previous stage
                    G = get_graph_graphml(project, phase, dex_project_path, csv_project_path, gml_project_path, sub_project, stage=stage-1)
                    dt_graph_analytics = process_graph_analytics(G)

                    # Output dictionary as a yaml file
                    outFilePath = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage-1}_graph_analytics.yaml")
                    create_yaml_file(dt_graph_analytics, outFilePath)

                    # Output dictionary as a json file
                    outFilePath = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage-1}_graph_analytics.json")
                    create_json_file(dt_graph_analytics, outFilePath)

    log_debug("Done!")

if __name__ == "__main__":
    main()
