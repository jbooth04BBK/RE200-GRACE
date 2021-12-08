# from dredataengineering.sql_routines import *

import pandas as pd
import numpy as np
import os
import csv
import sys
import io
import time
import inspect
import re

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import random
import yaml
import json
from colour import Color
import math
from datetime import date, datetime, timedelta

pd.options.mode.chained_assignment = None  # default='warn'

project = "RE0200"

age_groups = ["00to02", "03to05", "06to11", "12to17", "18to20"]

graph_measures = ["number_of_nodes", "number_of_edges", "non_edges", "density", "transitivity", "average_clustering",
                  "diameter", "radius", "center"]

centralities = []
centralities.append('harmonic_centrality')
centralities.append('eigenvector_centrality')
centralities.append('pagerank')
centralities.append('authorities')
centralities.append('degree_centrality')
centralities.append('betweenness_centrality')
centralities.append('closeness_centrality')
centralities.append('hubs')

analytic_plot_types = ["graph", "centralities"]

######################## dre_engineering ##################
# Required by log_debug
dre_run_start_time = None
dre_run_step_time = None

def log_debug(statement, inc_profiling=True):

    global dre_run_start_time, dre_run_step_time

    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    if dre_run_start_time is None:
        dre_run_start_time = now
        execution_time = 0
        total_execution_time = 0
    else:
        execution_time = int((now - dre_run_step_time).total_seconds() * 1000)
        total_execution_time = math.ceil((now - dre_run_start_time).total_seconds())

    if inc_profiling:
        print("{0} {1} {2}: {3}".format(date_time, str(total_execution_time).rjust(5), str(execution_time).rjust(5), statement))
    else:
        print("{0}: {1}".format(date_time, statement))

    # Update dre_run_step_time
    dre_run_step_time = now


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def return_date(date_string, date_format=None, str_format=None, adj_2digit_years=False):

    if date_format is None:
        POSSIBLE_DATE_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y%m%d', '%d/%m/%Y %H:%M:%S',
                                 '%d/%m/%Y %H:%M', '%d/%m/%Y', '%d/%m/%y', '%d-%b-%Y', '%d-%b-%y']
    else:
        POSSIBLE_DATE_FORMATS = [date_format]

    parsed_date = None

    if date_string is not None:

        # Check if the last 2 characters are '.0'
        if date_string[-2:] == ".0":
            date_string = date_string[:len(date_string)-2]

        for date_format in POSSIBLE_DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                if adj_2digit_years and date_format.find("%y") >= 0 and parsed_date.year > 2050:
                        parsed_date = parsed_date.replace(year=parsed_date.year - 100)
                break
            except ValueError:
                pass

    if str_format is not None and parsed_date is not None:
        return parsed_date.strftime(str_format)
    else:
        return parsed_date


def accumulator():
    sum = 0
    def addition(n):
         nonlocal sum
         sum += n
         return sum
    return addition

############# end of dre_engineering ################################
def check_project_path(args, project_path=None):

    dex_project_path = None
    csv_project_path = None
    gml_project_path = None

    found_path = False

    if len(args) >= 2:

        for arg_num, arg in enumerate(args):

            if found_path:
                project_path = arg
                break
            else:
                if arg.lower() == "-path":
                    found_path = True

    if project_path is None:
        project_path = os.curdir

    # Check path exists
    if os.path.exists(project_path):
        log_debug(f"Project path: {project_path}")
        # Check for other paths
        dex_project_path = project_path + "\\DataExtraction"
        csv_project_path = dex_project_path + "\\CSVs"
        gml_project_path = dex_project_path + "\\GMLs"
        gwk_project_path = gml_project_path + "\\Working"
        paths = [dex_project_path, csv_project_path, gml_project_path, gwk_project_path]
        for path in paths:
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except OSError as error:
                    log_debug(f"Error creating folder: {path}, error: {error}")
                    found_path = False
                    break
    else:
        log_debug(f"Project path not found: {project_path}")
        found_path = False

    return dex_project_path, csv_project_path, gml_project_path




def get_stages(args, default=None):
    # look for a list of stages from arguments passed to main script
    if default is None:
        default = [1, ]

    if len(args) >= 2:
        found_stages = False
        stages = []

        for arg_num, arg in enumerate(args):

            if found_stages:
                if isInt(arg):
                    stages.append(int(arg))
                else:
                    break
            else:
                if arg.lower() == "-stages":
                    found_stages = True

        if len(stages) == 0:
            stages = default
        else:
            # sort into numeric order
            stages.sort()
    else:
        stages = default

    return stages


def get_files_by_extension(root_path, extension=".csv", prefix=None, suffix=None, include_subfolders=True, include_root=False):

    sel_files = []

    for path, subdirs, files in os.walk(root_path):

        for item in files:

            if include_subfolders or (not include_subfolders and path.lower() == root_path.lower()):

                filename, file_extension = os.path.splitext(item)

                if file_extension.lower() == extension.lower():
                    if prefix is None and suffix is None:
                        sel_files.append(os.path.join(path, item))
                    elif prefix is not None and suffix is None:
                        if filename[:len(prefix)].lower() == prefix.lower():
                            sel_files.append(os.path.join(path, item))
                    elif prefix is None and suffix is not None:
                        if filename[-len(suffix):].lower() == suffix.lower():
                            sel_files.append(os.path.join(path, item))
                    else:
                        if filename[:len(prefix)].lower() == prefix.lower() and filename[-len(suffix):].lower() == suffix.lower():
                            sel_files.append(os.path.join(path, item))

    if len(sel_files) > 0:
        sel_files.sort(key=os.path.getmtime, reverse=True)
        if not include_root:
            sel_files = [file_name.replace(root_path, '.') for file_name in sel_files]

    return sel_files


def xml_safe(value):

    if isinstance(value, str):
        value = value.replace("&", "&amp;")
        value = value.replace('"', "&quot;")
        value = value.replace("'", "&apos;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")

    return value


def get_first_project_id(dex_project_path, sub_project):

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"

    patient_list_file_name = f"{file_name_prefix}patient_list.csv"
    plist_filepath = os.path.join(dex_project_path, patient_list_file_name)

    df_patient_list = pd.read_csv(plist_filepath)

    return df_patient_list['project_id'][0]


def plot_graph(G, layout="random", title="", max_nodes=100, seed=1, element_type=None, element_id=None,
                 dt_graph_analytics=dict(), show_centrality=None):

    log_debug(f"Create Graph - layout: {layout}")

    if layout == "fruchterman_reingold":
        pos = nx.fruchterman_reingold_layout(G, seed=seed)
    elif layout == "shell":
        pos = nx.shell_layout(G)
    elif layout == "spring":
        if element_type is not None and element_type.lower() == "node":
            fixed_positions = {element_id: (0, 0)}  # dict with one positions set at centre of plot
            fixed_nodes = fixed_positions.keys()
            pos = nx.spring_layout(G, seed=seed, pos=fixed_positions, fixed=fixed_nodes)
        else:
            pos = nx.spring_layout(G, seed=seed)
    # elif layout == "bipartite":
    #     pos = nx.bipartite_layout(G)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    # elif layout == "rescale":
    #     pos = nx.rescale_layout(G)
    # elif layout == "rescale_dict":
    #     pos = nx.rescale_dict_layout(G)
    elif layout == "spectral":
        pos = nx.spectral_layout(G)
    # elif layout == "planar":
    #     pos = nx.planar_layout(G)
    elif layout == "spiral":
        pos = nx.spiral_layout(G)
    # elif layout == "multipartite":
    #     pos = nx.multipartite_layout(G)

    else:
        pos = nx.random_layout(G, seed=seed)
    traces = []

    number_of_nodes = nx.number_of_nodes(G)
    number_of_edges = nx.number_of_edges(G)

    # Create Nodes
    # Select nodes to show.
    all_nodes = []
    selected_nodes = []
    selected_edges = []

    for node_num, node in enumerate(G.nodes()):
        all_nodes.append((node, G.nodes[node]['size']))

    sorted_nodes = sorted(all_nodes, key=lambda x: x[1], reverse=True)

    log_debug("Create Nodes")

    # Add nodes as a scatter trace
    # position, color, Size and text for Node Points
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    node_text = []
    for node_num, node_tuple in enumerate(sorted_nodes):
        node = node_tuple[0]
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        if show_centrality is not None and len(show_centrality) > 0:
            node_color.append(dt_graph_analytics['nodes'][node]['centralities'][show_centrality]['score'])
        else:
            if element_type is not None and element_type.lower() == "node" and node == element_id:
                # Highlight selected node
                node_color.append("#fff700")
            else:
                node_color.append(G.nodes[node]['color'])
        node_size.append(G.nodes[node]['size'])

        text = '{0}: {1}<br>{2}<br>patients: {3}, events: {4}'.format("Node", node, G.nodes[node]['label'],G.nodes[node]['patients'],G.nodes[node]['events'])

        # Are there more parameters that I want to add?
        for att_key in G.nodes[node]:
            if att_key not in ["id", "type", "highlight", "label", "color", "size", "patients", "events"]:
                value = G.nodes[node][att_key]
                text += f"<br>{att_key}: {value}"

        node_text.append(text)

        selected_nodes.append(node)

        if max_nodes is not None and node_num >= max_nodes:
            break

    # Create Edges
    # Add edges as disconnected lines in a single trace and nodes as a scatter trace

    log_debug("Create Edges")

    head_fraction = 0.90
    tail_fraction = 0.88

    hover_x = []
    hover_y = []
    hover_text = []

    for edge in G.edges():

        if edge[0] in selected_nodes and edge[1] in selected_nodes:

            selected_edges.append(edge)

            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_trace = go.Scatter(
                x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                mode='lines',
                hoverinfo='none',
                line=dict(
                    width=G.edges[edge]['weight'],
                    color = '#888' if G.edges[edge]['highlight'] == 0 else '#d30000')
            )

            traces.append(edge_trace)

            hover_x.append(pos[edge[0]][0] + ((pos[edge[1]][0] - pos[edge[0]][0]) * head_fraction))
            hover_y.append(pos[edge[0]][1] + ((pos[edge[1]][1] - pos[edge[0]][1]) * head_fraction))

            text = '{0}: {1}<br>{2}<br>patients: {3}, events: {4}'.format("Edge", edge, G.edges[edge]['label'],G.edges[edge]['patients'],G.edges[edge]['events'])

            # Are there more parameters that I want to add?
            for att_key in G.edges[edge]:
                if att_key not in ["id", "type", "label", "weight", "color", "highlight", "patients", "events"]:
                    value = G.edges[edge][att_key]
                    text += f"<br>{att_key}: {value}"

            hover_text.append(text)

    log_debug("Create Hover Nodes")

    hover_trace = go.Scatter(
        x=hover_x, y=hover_y,
        mode='markers',
        hoverinfo='text',
        text=hover_text,
        marker=dict(
            color="#000000",
            size=5),
        opacity=0
    )

    traces.append(hover_trace)

    # Nodes added last as looks better

    log_debug("Plot Nodes")

    if show_centrality is not None and len(show_centrality):
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=True,
                color=node_color,
                colorbar=dict(
                    thickness=15,
                    title=show_centrality,
                    xanchor='left',
                    titleside='right'
                ),
                size=node_size,
                line=dict(color='black', width=1))
        )
    else:
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(color='black', width=1))
        )

    traces.append(node_trace)

    # Create Network Graph
    #
    # Arrow heads have to be added as an annotation

    log_debug("Create Graph")

    fig = go.Figure(data=traces,
                   layout=go.Layout(
                       title=title,
                       titlefont_size=16,
                       title_font_color="hotpink",
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       annotations=[

                            # partial length arrows
                            dict(ax=(pos[edge[0]][0] + ((pos[edge[1]][0] - pos[edge[0]][0]) * tail_fraction)), ay=(pos[edge[0]][1] + ((pos[edge[1]][1] - pos[edge[0]][1]) * tail_fraction)),
                                 axref='x', ayref='y',  # tail of arrow
                                 x=(pos[edge[0]][0] + ((pos[edge[1]][0] - pos[edge[0]][0]) * head_fraction)), y=(pos[edge[0]][1] + ((pos[edge[1]][1] - pos[edge[0]][1]) * head_fraction)),
                                 xref='x', yref='y',  # head of arrow
                                 showarrow=True,
                                 arrowhead=1,
                                 arrowsize=2,
                                 arrowwidth=1,
                                 opacity=1
                                 )
                           for edge in selected_edges # G.edges

                       ],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=750,
                       width=1250,
                       plot_bgcolor='#ffffff' # '#e6e9f5'
                   )
                )

    log_debug("Graph complete")

    return fig


def plot_graph_analytics_summary(df_all_analytic_data, analytic_plot_type="graph", centrality="harmonic_centrality"):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    if analytic_plot_type == analytic_plot_types[0]: # Graph

        number_of_plots = len(graph_measures) * 2
        max_col = 2
        max_row = math.ceil(number_of_plots / max_col)

        fig = make_subplots(rows=max_row, cols=max_col, shared_yaxes=True,
                            subplot_titles=("Selected Patient", "All Patients"))

        cnt_row = 1
        cnt_col = 1

        # Only want labels to appear once in the legend
        label_legend = set()

        for graph_measure in graph_measures:

            log_debug(f"Graph measure: {graph_measure}")

            for patient_pass in range(1,3):

                log_debug(f"Patient pass: {patient_pass}")

                # filter records
                df_measure = df_all_analytic_data.query('patient_pass == @patient_pass & measure == @graph_measure')
                # order by label, max_day_of_admission, position
                df_measure.sort_values(['max_day_of_admission'], ascending=[True], inplace=True, ignore_index=True)

                number_rows = len(df_measure.index)
                x_pos = []
                y_pos = []

                # Create a trace for current measure
                for index, row in df_measure.iterrows():
                    sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(index + 1, number_rows))
                    sys.stdout.flush()

                    max_day_of_admission = int(row['max_day_of_admission'])
                    score = row['score']

                    x_pos.append(max_day_of_admission)
                    y_pos.append((score))

                print()

                trace = {
                    "mode": "lines+markers+text",
                    "type": "scatter",
                    "x": x_pos,
                    "y": y_pos,
                }

                fig.append_trace(trace, row=cnt_row, col=cnt_col)

                if cnt_row == max_row:
                    fig.update_xaxes(title_text="Days of stay", row=cnt_row, col=cnt_col)

                if cnt_col == 1:
                    fig.update_yaxes(title_text=graph_measure, row=cnt_row, col=cnt_col)

                cnt_col += 1

                if cnt_col > max_col:
                    cnt_col = 1
                    cnt_row += 1


        fig.update_layout(coloraxis=dict(colorscale='Viridis', showscale=False), showlegend=False,
                          title_text=f"Graph Analytics Comparison")


    elif analytic_plot_type == analytic_plot_types[1]:  # Centralities

        log_debug(f"Centrality: {centrality}")

        max_position = 30 # need to get this number from the data?

        # list of "N" colors between "start_color" and "end_color"
        start_color = "#ff0000"  # red
        end_color = "#ee82ee"  # violet
        N = df_all_analytic_data['label_id'].max()
        colorscale = [x.hex for x in list(Color(start_color).range_to(Color(end_color), N))]

        max_row = 1
        max_col = 2

        fig = make_subplots(rows=max_row, cols=max_col, shared_yaxes=True, subplot_titles=("Selected Patient", "All Patients"))

        cnt_row = 1
        cnt_col = 1

        # Only want labels to appear once in the legend
        label_legend = set()

        for patient_pass in range(1,3):

            log_debug(f"Patient pass: {patient_pass}")

            # filter records
            df_centrality = df_all_analytic_data.query('patient_pass == @patient_pass & measure == @centrality')
            # order by label, max_day_of_admission, position
            df_centrality.sort_values(['label', 'max_day_of_admission', 'position'], ascending=[True, True, True],
                                      inplace=True, ignore_index=True)

            # Create a trace for each drug
            traces = []
            number_rows = len(df_centrality.index)
            cnt_label_id = None
            cnt_label = None

            for index, row in df_centrality.iterrows():
                sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(index + 1, number_rows))
                sys.stdout.flush()

                label_id = row['label_id']
                label = row['label']
                max_day_of_admission = int(row['max_day_of_admission'])
                position = int(row['position'])
                patients = int(row['patients'])
                events = int(row['events'])

                if position <= max_position:

                    if cnt_label is not None and label != cnt_label:

                        name = f" {cnt_label_id}: {cnt_label}" if cnt_label_id < 10 else f"{cnt_label_id}: {cnt_label}"
                        if name not in label_legend:
                            label_legend.add(name)
                            showlegend = True
                        else:
                            showlegend = False

                        trace = {
                            "mode": "lines+markers+text",
                            "name": name,
                            "showlegend": showlegend,
                            "legendrank": cnt_label_id,
                            "type": "scatter",
                            "x": x_pos,
                            "y": y_pos,
                            "marker": {"size": size, "color": colorscale[cnt_label_id]},
                            "line": {"color": colorscale[cnt_label_id]},
                            "text": text,
                        }

                        traces.append(trace)

                    if cnt_label is None or label != cnt_label:
                        cnt_label_id = label_id
                        cnt_label = label
                        x_pos = []
                        y_pos = []
                        size = []
                        text = []

                    x_pos.append(max_day_of_admission)
                    y_pos.append((max_position - position))
                    text.append(f"{cnt_label_id}")

                    if patient_pass == 1:
                        size.append(10 + int(events))
                    else:
                        size.append(10 + int(patients / 5) + int(events / 30))

            print()

            # Don't forget the last one:
            name = f" {cnt_label_id}: {cnt_label}" if cnt_label_id < 10 else f"{cnt_label_id}: {cnt_label}"
            if name not in label_legend:
                label_legend.add(name)
                showlegend = True
            else:
                showlegend = False

            trace = {
                "mode": "lines+markers+text",
                "name": name,
                "showlegend": showlegend,
                "legendrank": cnt_label_id,
                "type": "scatter",
                "x": x_pos,
                "y": y_pos,
                "marker": {"size": size, "color": colorscale[cnt_label_id]},
                "line": {"color": colorscale[cnt_label_id]},
                "text": text,
            }

            traces.append(trace)

            layout = {
                "title": {"text": f"{centrality}: Bump chart - {'All Patients' if patient_pass == 2 else 'Selected Patient'}"},
                "xaxis": {
                    "type": "linear",
                    "range": [0, 13],
                    "autorange": True
                },
                "yaxis": {
                    "type": "linear",
                    "range": [0, max_position],
                    "autorange": True
                },
                "autosize": True
            }

            for trace in traces:
                fig.append_trace(trace, row=cnt_row, col=cnt_col)

            cnt_col += 1

            if cnt_col > max_col:
                cnt_col = 1
                cnt_row += 1

            # fig = go.Figure(data=traces, layout=layout)

        fig.update_layout(coloraxis=dict(colorscale='Viridis', showscale=False), showlegend=True,
                          legend={'traceorder': 'normal'}, title_text=f"{centrality}: Bump chart")

        fig.update_xaxes(title_text="Days of stay")

    pause = True

    fig.update_layout(height=1000, width=2000)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return fig


def get_graph_graphml(project, phase, dex_project_path, csv_project_path, gml_project_path, sub_project, stage=1,
                            incl_shortest_paths=True):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    inpFilePath_graphml = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage}_graph.graphml")

    log_debug(f"Reading file: {inpFilePath_graphml}")
    G = nx.read_graphml(inpFilePath_graphml)

    return G


def process_graph_analytics(G, weight_key='patients', incl_centralities=True, incl_shortest_paths=True,
                            inc_attribute_assortivity=True, inc_error_logging=False):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    # Need a dictionary of zero values in case an error occurs
    node_zero_values = dict()
    for node_num, source_node in enumerate(G.nodes()):
        node_zero_values[source_node] = 0

    dt_graph_analytics = dict()
    dt_graph_analytics['graph'] = dict()
    # what sort of graph is it?

    dt_graph_analytics['graph']['nx_info'] = nx.info(G)
    log_debug(dt_graph_analytics['graph']['nx_info'])

    dt_graph_analytics['graph']['number_of_nodes'] = nx.number_of_nodes(G)
    dt_graph_analytics['graph']['number_of_edges'] = nx.number_of_edges(G)
    dt_graph_analytics['graph']['non_edges'] = len(list(nx.non_edges(G)))
    dt_graph_analytics['graph']['density'] = nx.density(G)
    # dt_graph_analytics['graph']['degree_histogram'] = nx.degree_histogram(G)
    dt_graph_analytics['graph']['transitivity'] = nx.transitivity(G)
    dt_graph_analytics['graph']['average_clustering'] = nx.average_clustering(G)

    try:
        dt_graph_analytics['graph']['eccentricity'] = nx.eccentricity(G)
        dt_graph_analytics['graph']['diameter'] = nx.diameter(G, e=dt_graph_analytics['graph']['eccentricity'])
        dt_graph_analytics['graph']['radius'] = nx.radius(G, e=dt_graph_analytics['graph']['eccentricity'])
        dt_graph_analytics['graph']['center'] = nx.center(G, e=dt_graph_analytics['graph']['eccentricity'])
    except Exception as e:
        dt_graph_analytics['graph']['eccentricity'] = []
        dt_graph_analytics['graph']['diameter'] = 0
        dt_graph_analytics['graph']['radius'] = 0
        dt_graph_analytics['graph']['center'] = []
        function_name = "nx.eccentricity"
        if inc_error_logging:
            log_debug(f"Function: {function_name}, error occurred: {e}")
        dt_graph_analytics['graph']['eccentricity'] = []

    ##############
    # Centralities
    ##############
    if incl_centralities:

        log_debug(f"Record node centralities - weight = {weight_key}")

        dt_node_harmonic_centrality = nx.harmonic_centrality(G)

        try:
            dt_node_eigenvector_centrality = nx.eigenvector_centrality(G, weight=weight_key)
        except Exception as e:
            function_name = "nx.eigenvector_centrality"
            if inc_error_logging:
                log_debug(f"Function: {function_name}, error occurred: {e}")
            dt_node_eigenvector_centrality = node_zero_values

        dt_node_pagerank = nx.pagerank(G, weight=weight_key)

        dt_node_degree_centrality = nx.degree_centrality(G)
        dt_node_betweenness_centrality = nx.betweenness_centrality(G, weight=weight_key)
        dt_node_closeness_centrality = nx.closeness_centrality(G)

        dt_node_hubs, dt_node_authorities = nx.hits(G)

    #######################
    # Attribute assortivity
    #######################
    if inc_attribute_assortivity:
        # create a dictionary of parameters and there values
        attributes = dict()
        attributes_count = dict()
        for node_id in G.nodes():
            # what parameters does each node have and what are their unique values:
            for att_key in G.nodes[node_id]:
                if att_key not in ["id", "type", "highlight", "label", "color", "size", "patients", "events"]:
                    value = G.nodes[node_id][att_key]
                    if att_key not in attributes:
                        attributes[att_key] = dict()
                        attributes_count[att_key] = 0
                        attributes[att_key][value] = 0
                    else:
                        if value not in attributes[att_key]:
                            count = attributes_count[att_key] + 1
                            attributes[att_key][value] = count
                            attributes_count[att_key] = count

        if len(attributes) > 0:

            dt_graph_analytics['graph']['attributes'] = dict()

            for att_key in attributes:
                log_debug(f"Attribute assortivity: {att_key}")
                dt_graph_analytics['graph']['attributes'][att_key] = dict()
                # Create mapping tables
                matrix = nx.attribute_mixing_matrix(G, att_key, mapping=attributes[att_key])
                dt_graph_analytics['graph']['attributes'][att_key]['assortativity_coefficient'] = float(
                    nx.attribute_assortativity_coefficient(G, att_key))
                dt_graph_analytics['graph']['attributes'][att_key]['attribute_mixing_matrix'] = dict()
                for value_num, value in enumerate(attributes[att_key]):
                    dt_graph_analytics['graph']['attributes'][att_key]['attribute_mixing_matrix'][value] = matrix[value_num,:].tolist()

                pause = True

    log_debug(f"Analyisng nodes: {dt_graph_analytics['graph']['number_of_nodes']}")
    dt_graph_analytics['nodes'] = dict()

    all_nodes = []

    for node_num, source_node in enumerate(G.nodes()):

        if not incl_shortest_paths:
            sys.stdout.write(
                "\r \rProcessing rows: {0} of {1}".format(node_num + 1, dt_graph_analytics['graph']['number_of_nodes']))
            sys.stdout.flush()

        dt_graph_analytics['nodes'][source_node] = dict()
        for att_id in G.nodes[source_node]:
            value = G.nodes[source_node][att_id]
            dt_graph_analytics['nodes'][source_node][att_id] = value

        dt_graph_analytics['nodes'][source_node]['degree'] = nx.degree(G, source_node)
        dt_graph_analytics['nodes'][source_node]['out_neighbors'] = len(G[source_node])
        dt_graph_analytics['nodes'][source_node]['all_neighbors'] = len(list(nx.all_neighbors(G, source_node)))

        # dt_graph_analytics['nodes'][source_node]['clustering'] = nx.clustering(nx.graph(G), source_node)
        dt_graph_analytics['nodes'][source_node]['clustering'] = nx.clustering(G, source_node)

        if incl_centralities:

            dt_graph_analytics['nodes'][source_node]['centralities'] = dict()
            for centrality in centralities:
                dt_graph_analytics['nodes'][source_node]['centralities'][centrality] = dict()

            dt_graph_analytics['nodes'][source_node]['centralities']['harmonic_centrality']['score'] = dt_node_harmonic_centrality[
                source_node]
            dt_graph_analytics['nodes'][source_node]['centralities']['eigenvector_centrality']['score'] = dt_node_eigenvector_centrality[
                source_node]
            dt_graph_analytics['nodes'][source_node]['centralities']['pagerank']['score'] = dt_node_pagerank[source_node]
            dt_graph_analytics['nodes'][source_node]['centralities']['authorities']['score'] = dt_node_authorities[source_node]

            dt_graph_analytics['nodes'][source_node]['centralities']['degree_centrality']['score'] = dt_node_degree_centrality[source_node]
            dt_graph_analytics['nodes'][source_node]['centralities']['betweenness_centrality']['score'] = dt_node_betweenness_centrality[
                source_node]

            dt_graph_analytics['nodes'][source_node]['centralities']['closeness_centrality']['score'] = dt_node_closeness_centrality[
                source_node]
            dt_graph_analytics['nodes'][source_node]['centralities']['hubs']['score'] = dt_node_hubs[source_node]

            all_nodes.append((source_node,
                              dt_node_harmonic_centrality[source_node],
                              dt_node_eigenvector_centrality[source_node],
                              dt_node_pagerank[source_node],
                              dt_node_authorities[source_node],
                              dt_node_degree_centrality[source_node],
                              dt_node_betweenness_centrality[source_node],
                              dt_node_closeness_centrality[source_node],
                              dt_node_hubs[source_node]
                              ))

        if incl_shortest_paths:

            # calculate shortest path to all other nodes
            dt_graph_analytics['nodes'][source_node]['shortest_path'] = dict()
            for target_node_num, target_node in enumerate(G.nodes()):
                sys.stdout.write(
                    "\r \rProcessing rows: {0} of {1} of {2}".format(target_node_num + 1, node_num + 1,
                                                              dt_graph_analytics['graph']['number_of_nodes']))
                sys.stdout.flush()

                if source_node != target_node:
                    try:
                        dt_graph_analytics['nodes'][source_node]['shortest_path'][target_node] = nx.shortest_path(G,
                                                                                                                  source_node,
                                                                                                                  target_node,
                                                                                                                  weight=weight_key)
                    except Exception as e:
                        function_name = "nx.shortest_path"
                        if inc_error_logging:
                            log_debug(f"Function: {function_name}, error occurred: {e}")
                        dt_graph_analytics['nodes'][source_node]['shortest_path'][target_node] = []

    print()

    #############################
    # Assign centrality positions
    #############################
    if incl_centralities:

        dt_graph_analytics['graph']['centralities'] = dict()
        for sort_column in range(1, 9):
            log_debug(f"Assign centrality positions: {sort_column}")
            dt_graph_analytics['graph']['centralities'][centralities[sort_column - 1]] = dict()
            sorted_nodes = sorted(all_nodes, key=lambda x: x[sort_column], reverse=True)
            for node_num, source_node in enumerate(sorted_nodes):
                dt_graph_analytics['nodes'][source_node[0]]['centralities'][centralities[sort_column - 1]]['pos'] = node_num + 1
                dt_graph_analytics['graph']['centralities'][centralities[sort_column - 1]][str(node_num + 1)] = dict()
                dt_graph_analytics['graph']['centralities'][centralities[sort_column - 1]][str(node_num + 1)]['node'] = source_node[0]
                dt_graph_analytics['graph']['centralities'][centralities[sort_column - 1]][str(node_num + 1)]['score'] = source_node[sort_column]

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    # Plot clustering vs degree for nodes

    return dt_graph_analytics


def create_excel_file(dt_graph, outFilePath, dt_nodes=None, dt_edges=None, dt_patients=None, dt_periods=None):
    '''

    dt_graph["graph"]
    dt_graph["graph"]["_node_atts"]
    dt_graph["graph"]["_node_atts"][att_id]
    dt_graph["graph"]["_edge_atts"]
    dt_graph["graph"]["_edge_atts"][att_id]
    dt_graph["graph"]["_node_types"]
    dt_graph["graph"]["_node_types"][type_id]
    dt_graph["graph"]["_edge_types"]
    dt_graph["graph"]["_edge_types"][type_id]
    dt_graph["graph"]["edges"]
    dt_graph["graph"]["nodes"]
    dt_graph["graph"]["nodes"][node_id]
    dt_graph["graph"]["edges"]
    dt_graph["graph"]["edges"][edge_id]

    sheet 1 - graph - list attributes
    sheet 2 - attributes, both node and edge
    sheet 3 - nodes
    sheet 4 - edges

    Node_patients
    dt_nodes[node_label]
    dt_nodes[node_label]([node_id],[patient_list]) - list of patient_ids

    dt_edges[(source,target)]
    dt_edges[(source,target)][edge_id],[patient_list]) - list of patient_ids

    dt_patients["hospital_no"]
    dt_patients["instance"]
    dt_patients["instances"]["total"]
    dt_patients["instances"][instance_id][0] = start_datetime
    dt_patients["instances"][instance_id][1] = end_datetime
    dt_patients["edges"]
    dt_patients["edges"][edge_id]
    dt_patients["edges"][edge_id]["events"]

    :param dt_graph:
    :param outFilePath:
    :return:
    '''

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    if "graph" in dt_graph:
        # graph attributes
        # print id, label and directed first if exist

        # create excel file
        writer = pd.ExcelWriter(outFilePath, engine='xlsxwriter')

        graph_cols = ["key", "value"]
        graph_output = []

        att_key = "id"
        if att_key in dt_graph["graph"]:
            output_row = []
            output_row.append(att_key)
            output_row.append(dt_graph["graph"][att_key])
            graph_output.append(output_row)

        att_key = "label"
        if att_key in dt_graph["graph"]:
            output_row = []
            output_row.append(att_key)
            output_row.append(dt_graph["graph"][att_key])
            graph_output.append(output_row)

        att_key = "directed"
        if att_key in dt_graph["graph"]:
            output_row = []
            output_row.append(att_key)
            output_row.append(dt_graph["graph"][att_key])
            graph_output.append(output_row)

        for graph_key in dt_graph["graph"]:

            if graph_key not in ["id", "label", "directed", "nodes", "edges", "_graph_atts", "_node_atts", "_edge_atts"]:
                output_row = []
                output_row.append(graph_key)
                output_row.append(dt_graph["graph"][graph_key])
                graph_output.append(output_row)

        df = pd.DataFrame.from_records(graph_output, columns=graph_cols)
        df.to_excel(writer, sheet_name='Graph', index=False)

        # Attributes
        att_cols = ["source", "id", "name", "type"]
        att_output = []

        for att_type in ["_graph_atts", "_node_atts", "_edge_atts"]:

            if att_type == "_graph_atts":
                source = "graph"
            elif att_type == "_node_atts":
                source = "node"
            else:
                source = "edge"

            if att_type in dt_graph["graph"]:

                for att_id in dt_graph["graph"][att_type]:
                    name = dt_graph["graph"][att_type][att_id]["name"]
                    type = dt_graph["graph"][att_type][att_id]["type"]
                    output_row = []
                    output_row.append(source)
                    output_row.append(att_id)
                    output_row.append(name)
                    output_row.append(type)
                    # output_row att line
                    att_output.append(output_row)

        df = pd.DataFrame.from_records(att_output, columns=att_cols)
        df.to_excel(writer, sheet_name='Attributes', index=False)

        # nodes
        node_cols = ["id", "label"]
        node_output = []

        if "nodes" in dt_graph["graph"]:

            # get list of columns - have to check every node
            for node_id in dt_graph["graph"]["nodes"]:
                for att_key in dt_graph["graph"]["nodes"][node_id]:
                    if att_key not in ["label", ]:
                        if att_key not in node_cols:
                            node_cols.append(att_key)

            for node_id in dt_graph["graph"]["nodes"]:

                output_row = []
                output_row.append(node_id)

                for att_key in node_cols:

                    if att_key != "id":
                        if att_key in dt_graph["graph"]["nodes"][node_id]:
                            output_row.append(dt_graph["graph"]["nodes"][node_id][att_key])
                        else:
                            output_row.append("")

                # output_row node line
                node_output.append(output_row)

        df = pd.DataFrame.from_records(node_output, columns=node_cols)
        df.to_excel(writer, sheet_name='Nodes', index=False)

        # edges
        edge_cols = ["id", "source", "target", "label"]
        edge_output = []

        if "edges" in dt_graph["graph"]:

            for edge_id in dt_graph["graph"]["edges"]:
                for att_key in dt_graph["graph"]["edges"][edge_id]:
                    if att_key not in ["label", "source", "target", ]:
                        if att_key not in edge_cols:
                            edge_cols.append(att_key)

            for edge_id in dt_graph["graph"]["edges"]:

                output_row = []
                output_row.append(edge_id)

                for att_key in edge_cols:

                    if att_key != "id":
                        if att_key in dt_graph["graph"]["edges"][edge_id]:
                            output_row.append(dt_graph["graph"]["edges"][edge_id][att_key])
                        else:
                            output_row.append("")

                # output_row edge line
                edge_output.append(output_row)

        df = pd.DataFrame.from_records(edge_output, columns=edge_cols)
        df.to_excel(writer, sheet_name='Edges', index=False)

        if dt_nodes is not None:

            # Node_patients
            #     dt_nodes[node_label]
            #     dt_nodes[node_label]([node_id],[patient_list]) - list of patient_ids

            node_patient_cols = ["node_label", "node_id", "project_id"]
            node_patient_output = []

            for node_label in dt_nodes:

                patient_list = dt_nodes[node_label][1]
                for patient_id in patient_list:
                    output_row = []
                    output_row.append(node_label)
                    output_row.append(dt_nodes[node_label][0])
                    output_row.append(patient_id)

                    # output_row patient line
                    node_patient_output.append(output_row)

            df = pd.DataFrame.from_records(node_patient_output, columns=node_patient_cols)
            df.to_excel(writer, sheet_name='Node Patients', index=False)

        if dt_edges is not None:

            #     dt_edges[(source,target)]
            #     dt_edges[(source,target)][edge_id],[patient_list]) - list of patient_ids

            edge_patient_cols = ["source", "target", "edge_id", "project_id"]
            edge_patient_output = []

            for edge_tuple in dt_edges:

                patient_list = dt_edges[edge_tuple][1]
                for patient_id in patient_list:
                    output_row = []
                    output_row.append(edge_tuple[0])
                    output_row.append(edge_tuple[1])
                    output_row.append(dt_edges[edge_tuple][0])
                    output_row.append(patient_id)

                    # output_row patient line
                    edge_patient_output.append(output_row)

            df = pd.DataFrame.from_records(edge_patient_output, columns=edge_patient_cols)
            df.to_excel(writer, sheet_name='Edge Patients', index=False)

        if dt_patients is not None:

            # patients
            #     dt_patients["hospital_no"]
            #     dt_patients["instance"]
            #     dt_patients["instances"]["total"]
            #     dt_patients["instances"][instance_id][0] = start_datetime
            #     dt_patients["instances"][instance_id][1] = end_datetime
            #     dt_patients["edges"]
            #     dt_patients["edges"][edge_id]
            #     dt_patients["edges"][edge_id]["events"]

            patient_cols = ["project_id", "instance", "start_datetime", "end_datetime"]
            patient_output = []

            patient_edge_cols = ["project_id", "edge_id", "events"]
            patient_edge_output = []

            for patient_id in dt_patients:

                total_events = dt_patients[patient_id]['instances']['total']
                for instance_id in range(1, total_events + 1):
                    if instance_id in dt_patients[patient_id]['instances']:
                        start_datetime = dt_patients[patient_id]['instances'][instance_id][0]
                        end_datetime = dt_patients[patient_id]['instances'][instance_id][1]

                        output_row = []
                        output_row.append(patient_id)
                        output_row.append(instance_id)
                        output_row.append(start_datetime)
                        output_row.append(end_datetime)

                    else:

                        output_row = []
                        output_row.append(patient_id)
                        output_row.append(instance_id)
                        output_row.append(None)
                        output_row.append(None)

                    # output_row patient line
                    patient_output.append(output_row)

                for edge_id in dt_patients[patient_id]['edges']:
                    output_row = []
                    output_row.append(patient_id)
                    output_row.append(edge_id)
                    output_row.append(dt_patients[patient_id]['edges'][edge_id]['events'])

                    # output_row patient edge line
                    patient_edge_output.append(output_row)

            df = pd.DataFrame.from_records(patient_output, columns=patient_cols)
            df.to_excel(writer, sheet_name='Patients', index=False)

            df = pd.DataFrame.from_records(patient_edge_output, columns=patient_edge_cols)
            df.to_excel(writer, sheet_name='Patient Edges', index=False)

        if dt_periods is not None and len(dt_periods) > 0:

            # periods
            #     dt_periods[patient_id]
            #     dt_periods[patient_id][node_type]
            #     dt_periods[patient_id][node_type][time_node_label]
            #     list of tuples: (node_id, node_label)

            period_cols = ["project_id", "node_type", "time_node_label", "node_id", "node_label"]
            period_output = []

            for patient_id in dt_periods:

                for node_type in dt_periods[patient_id]:

                    for time_node_label in dt_periods[patient_id][node_type]:

                        node_list = dt_periods[patient_id][node_type][time_node_label]

                        for node in node_list:
                            node_id = node[0]
                            node_label = node[1]

                            output_row = []
                            output_row.append(patient_id)
                            output_row.append(node_type)
                            output_row.append(time_node_label)
                            output_row.append(node_id)
                            output_row.append(node_label)

                            # output_row period line
                            period_output.append(output_row)

            df = pd.DataFrame.from_records(period_output, columns=period_cols)
            df.to_excel(writer, sheet_name='Patient Periods', index=False)

        writer.close()

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def create_yaml_file(dt_graph, outFilePath):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    with open(outFilePath, 'w') as outfile:
        yaml.dump(dt_graph, outfile, default_flow_style=False, width=255, sort_keys=False)

    log_debug("YAML file created: {0}".format(outFilePath))

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def create_json_file(dt_graph, outFilePath):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    with open(outFilePath, 'w') as outfile:
        json.dump(dt_graph, outfile)

    log_debug("JSON file created: {0}".format(outFilePath))

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))



def output_graphml_attribute(att_key, element_id, source, dt_attributes, dt_graph, tab, output, wFile):
    if att_key == "_node_colour":
        rev_att_key = "color"
    elif att_key == "_node_size":
        rev_att_key = "size"
    elif att_key == "_edge_colour":
        rev_att_key = "color"
    elif att_key == "_edge_size":
        rev_att_key = "weight"
    else:
        rev_att_key = att_key

    att_id = dt_attributes[f"_{source[:len(source) - 1]}_atts"][rev_att_key]
    value = dt_graph["graph"][source][element_id][att_key]
    # if att_key == "_node_size":
    #     # currently between 50 and a 1000, need to scale from 5 - 100
    #     value = int(value / 10)

    # start and close node attribute tab
    output += tab + tab + tab + f'<data key="{att_id}">{value}</data>\n'
    wFile.writelines(output)
    output = ''

    return output


def create_graphml_file(dt_graph, outFilePath):
    '''
    Create a graphML file from a graph dictionary

    No concept of a label?
    Edges can have an id separate from defintion of source and target, also can have their own directed property

    :param dt_graph: dictionary containg graph details
    :param outFilePath: full path including full file name to GML file
    :return: None
    '''
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    tab = "  "  # 2 spaces
    with open(outFilePath, "w", encoding="ascii") as wFile:

        output = ''
        output += '<?xml version="1.0" encoding="UTF-8"?>\n'
        ###################
        # start graphml tag
        ###################
        output += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n'
        output += tab + 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        output += tab + 'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n'
        output += tab + tab + 'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n'
        wFile.writelines(output)
        output = ''

        if "graph" in dt_graph:

            # graph attributes

            att_key = "id"
            id = dt_graph["graph"][att_key] if att_key in dt_graph["graph"] else "42"

            att_key = "label"
            label = dt_graph["graph"][att_key] if att_key in dt_graph["graph"] else "Graph Label Default"

            att_key = "directed"
            directed = dt_graph["graph"][att_key] if att_key in dt_graph["graph"] else 0
            edgedefault = "undirected" if directed == 0 else "directed"

            ###########################
            # Add Attribute definitions
            ###########################

            dt_attributes = dict()

            for att_type in ["_graph_atts", "_node_atts", "_edge_atts"]:

                dt_attributes[att_type] = dict()

                # Add default parameters
                if att_type == "_graph_atts":

                    source = "graph"
                    # No Defaults
                    pass

                elif att_type == "_node_atts":

                    source = "node"

                    att_id = "DN1"
                    name = "color"
                    type = "string"
                    dt_attributes[att_type][name] = att_id
                    # start node attribute tab
                    output += tab + f'<key id="{att_id}" for="{source}" attr.name="{name}" attr.type="{type}">\n'
                    wFile.writelines(output)
                    output = ''

                    # Defaults will go here

                    # complete node attribute tab
                    output += tab + f'</key>\n'
                    wFile.writelines(output)
                    output = ''

                    att_id = "DN2"
                    name = "size"
                    type = "int"
                    dt_attributes[att_type][name] = att_id

                    # start node attribute tab
                    output += tab + f'<key id="{att_id}" for="{source}" attr.name="{name}" attr.type="{type}">\n'
                    wFile.writelines(output)
                    output = ''

                    # Defaults will go here

                    # complete node attribute tab
                    output += tab + f'</key>\n'
                    wFile.writelines(output)
                    output = ''


                else:
                    source = "edge"

                    att_id = "DE1"
                    name = "color"
                    type = "string"
                    dt_attributes[att_type][name] = att_id

                    # start node attribute tab
                    output += tab + f'<key id="{att_id}" for="{source}" attr.name="{name}" attr.type="{type}">\n'
                    wFile.writelines(output)
                    output = ''

                    # Defaults will go here

                    # complete node attribute tab
                    output += tab + f'</key>\n'
                    wFile.writelines(output)
                    output = ''

                    att_id = "DE2"
                    name = "weight"
                    type = "int"
                    dt_attributes[att_type][name] = att_id

                    # start node attribute tab
                    output += tab + f'<key id="{att_id}" for="{source}" attr.name="{name}" attr.type="{type}">\n'
                    wFile.writelines(output)
                    output = ''

                    # Defaults will go here

                    # complete node attribute tab
                    output += tab + f'</key>\n'
                    wFile.writelines(output)
                    output = ''

                if att_type in dt_graph["graph"]:

                    # check for _node_colour and _node_size

                    for att_id in dt_graph["graph"][att_type]:
                        name = dt_graph["graph"][att_type][att_id]["name"]
                        type = dt_graph["graph"][att_type][att_id]["type"]

                        # start node attribute tab
                        output += tab + f'<key id="{att_id}" for="{source}" attr.name="{name}" attr.type="{type}">\n'
                        wFile.writelines(output)
                        output = ''

                        # Defaults will go here

                        # complete node attribute tab
                        output += tab + f'</key>\n'
                        wFile.writelines(output)
                        output = ''

                        dt_attributes[att_type][name] = att_id

            #################
            # start graph tab
            #################
            output += tab + f'<graph id="{id}" edgedefault="{edgedefault}">\n'
            wFile.writelines(output)
            output = ''

            # Graph parameters
            for att_key in dt_graph["graph"]:

                # system parameters begining with _ should not be output
                if att_key not in ["id", "nodes", "edges", ] and att_key[:1] != "_":
                    att_id = dt_attributes["_graph_atts"][att_key]
                    value = xml_safe(dt_graph["graph"][att_key])
                    # start and close node attribute tab
                    output += tab + tab + tab + f'<data key="{att_id}">{value}</data>\n'
                    wFile.writelines(output)
                    output = ''

            # Nodes
            if "nodes" in dt_graph["graph"]:

                for node_id in dt_graph["graph"]["nodes"]:

                    att_key = "label"
                    label = dt_graph["graph"]["nodes"][node_id][att_key] if att_key in dt_graph["graph"]["nodes"][
                        node_id] else "Node Label Default"

                    # start node tab
                    output += tab + tab + f'<node id="{node_id}">\n'
                    wFile.writelines(output)
                    output = ''

                    # Default parameters
                    att_key = "_node_colour"
                    if att_key in dt_graph["graph"]["nodes"][node_id]:
                        output = output_graphml_attribute(att_key, node_id, "nodes", dt_attributes, dt_graph, tab,
                                                          output, wFile)
                    att_key = "_node_size"
                    if att_key in dt_graph["graph"]["nodes"][node_id]:
                        output = output_graphml_attribute(att_key, node_id, "nodes", dt_attributes, dt_graph, tab,
                                                          output, wFile)

                    # Parameters
                    for att_key in dt_graph["graph"]["nodes"][node_id]:

                        # system parameters begining with _ should not be output
                        if att_key[:1] != "_":
                            att_id = dt_attributes["_node_atts"][att_key]
                            value = xml_safe(dt_graph["graph"]["nodes"][node_id][att_key])
                            # start and close node attribute tab
                            output += tab + tab + tab + f'<data key="{att_id}">{value}</data>\n'
                            wFile.writelines(output)
                            output = ''

                    # complete node tab
                    output += tab + tab + f'</node>\n'
                    wFile.writelines(output)
                    output = ''

                # edges
                # If there are no nodes then there can't be any edges
                # Nodes are defined so any properties can be defined.
                if "edges" in dt_graph["graph"]:

                    for edge_id in dt_graph["graph"]["edges"]:

                        att_key = "source"
                        source = dt_graph["graph"]["edges"][edge_id][att_key]

                        att_key = "target"
                        target = dt_graph["graph"]["edges"][edge_id][att_key]

                        # start edge tab
                        output += tab + tab + f'<edge id="{edge_id}" source="{source}" target="{target}" '
                        att_key = "directed"
                        if att_key in dt_graph["graph"]["edges"][edge_id]:
                            directed = "true" if dt_graph["graph"]["edges"][edge_id][att_key] == 1 else "false"
                            output += f'directed="{target}" '

                        output += f'>\n'
                        wFile.writelines(output)
                        output = ''

                        # Default parameters
                        att_key = "_edge_colour"
                        if att_key in dt_graph["graph"]["edges"][edge_id]:
                            output = output_graphml_attribute(att_key, edge_id, "edges", dt_attributes, dt_graph, tab,
                                                              output, wFile)
                        att_key = "_edge_size"
                        if att_key in dt_graph["graph"]["edges"][edge_id]:
                            output = output_graphml_attribute(att_key, edge_id, "edges", dt_attributes, dt_graph, tab,
                                                              output, wFile)

                        # Parameters
                        for att_key in dt_graph["graph"]["edges"][edge_id]:

                            # system parameters begining with _ should not be output
                            if att_key not in ["source", "target", ] and att_key[:1] != "_":
                                att_id = dt_attributes["_edge_atts"][att_key]
                                value = xml_safe(dt_graph["graph"]["edges"][edge_id][att_key])
                                # start and close node attribute tab
                                output += tab + tab + tab + f'<data key="{att_id}">{value}</data>\n'
                                wFile.writelines(output)
                                output = ''

                        # complete edge tab
                        output += tab + tab + f'</edge>\n'
                        wFile.writelines(output)
                        output = ''

            ####################
            # complete graph tab
            ####################
            output += tab + '</graph>\n'
            wFile.writelines(output)
            output = ''

        ######################
        # Complete graphml tag
        ######################
        output += '</graphml>\n'

        wFile.writelines(output)
        output = ''

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def create_gml_file(dt_graph, outFilePath):
    '''
    Create a GML file from a graph dictionary

    :param dt_graph: dictionary containg graph details
    :param outFilePath: full path including full file name to GML file
    :return: None
    '''
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    tab = "  "  # 2 spaces
    with open(outFilePath, "w", encoding="ascii") as wFile:

        wFile.writelines("graph [\n")

        if "graph" in dt_graph:
            # graph attributes
            # print id, label and directed first if exist

            att_key = "id"
            if att_key in dt_graph["graph"]:
                wFile.writelines(
                    tab + '{0} {1}\n'.format(att_key, dt_graph["graph"][att_key]))

            att_key = "label"
            if att_key in dt_graph["graph"]:
                wFile.writelines(
                    tab + '{0} "{1}"\n'.format(att_key, dt_graph["graph"][att_key]))

            att_key = "directed"
            if att_key in dt_graph["graph"]:
                wFile.writelines(
                    tab + '{0} {1}\n'.format(att_key, dt_graph["graph"][att_key]))

            for graph_key in dt_graph["graph"]:

                if graph_key not in ["id", "label", "directed", "nodes", "edges"] and graph_key[:1] != "_":
                    if isinstance(dt_graph["graph"][graph_key], str):
                        wFile.writelines(tab + '{0} "{1}"\n'.format(graph_key, dt_graph["graph"][graph_key]))
                    else:
                        wFile.writelines(tab + "{0} {1}\n".format(graph_key, dt_graph["graph"][graph_key]))

            # nodes
            if "nodes" in dt_graph["graph"]:

                for node_id in dt_graph["graph"]["nodes"]:

                    wFile.writelines(tab + "node [\n")

                    wFile.writelines(
                        tab + tab + 'id {0}\n'.format(node_id))

                    if "label" in dt_graph["graph"]["nodes"][node_id]:
                        att_key = "label"
                        wFile.writelines(
                            tab + tab + '{0} "{1}"\n'.format(att_key, dt_graph["graph"]["nodes"][node_id][att_key]))

                    for att_key in dt_graph["graph"]["nodes"][node_id]:

                        # system parameters begining with _ should not be output
                        if att_key not in ["label", ] and att_key[:1] != "_":
                            if isinstance(dt_graph["graph"]["nodes"][node_id][att_key], str):
                                wFile.writelines(tab + tab + '{0} "{1}"\n'.format(att_key,
                                                                                  dt_graph["graph"]["nodes"][node_id][
                                                                                      att_key]))
                            else:
                                wFile.writelines(tab + tab + "{0} {1}\n".format(att_key,
                                                                                dt_graph["graph"]["nodes"][node_id][
                                                                                    att_key]))

                    wFile.writelines(tab + "]\n")

                # edges
                # If there are no nodes then there can't be any edges
                # Or should edges create nodes?
                if "edges" in dt_graph["graph"]:

                    for edge_id in dt_graph["graph"]["edges"]:

                        wFile.writelines(tab + "edge [\n")

                        att_key = "id"
                        wFile.writelines(tab + tab + '{0} {1}\n'.format(att_key, edge_id))

                        att_key = "source"
                        source = dt_graph["graph"]["edges"][edge_id][att_key]

                        att_key = "target"
                        target = dt_graph["graph"]["edges"][edge_id][att_key]

                        wFile.writelines(tab + tab + 'source {0}\n'.format(source))
                        wFile.writelines(tab + tab + 'target {0}\n'.format(target))

                        att_key = "label"
                        if att_key in dt_graph["graph"]["edges"][edge_id]:
                            wFile.writelines(
                                tab + tab + '{0} "{1}"\n'.format(att_key, dt_graph["graph"]["edges"][edge_id][att_key]))

                        for att_key in dt_graph["graph"]["edges"][edge_id]:

                            # system parameters begining with _ should not be output
                            if att_key not in ["label", "source", "target", ] and att_key[:1] != "_":
                                if isinstance(dt_graph["graph"]["edges"][edge_id][att_key], str):
                                    wFile.writelines(tab + tab + '{0} "{1}"\n'.format(att_key,
                                                                                      dt_graph["graph"]["edges"][
                                                                                          edge_id][att_key]))
                                else:
                                    wFile.writelines(tab + tab + "{0} {1}\n".format(att_key,
                                                                                    dt_graph["graph"]["edges"][edge_id][
                                                                                        att_key]))

                        wFile.writelines(tab + "]\n")

        wFile.writelines("]\n")

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, accumulate=True, highlight=0,
                 parameters=None):
    '''

    :param dt_graph:
    :param dt_nodes:
    :param node_id:
    :param patient_id:
    :param label:
    :param node_type:
    :param accumulate: Set to False when checking a node exists rather than explicitly adding it.
    :param highlight:
    :return:
    '''

    if label not in dt_nodes:

        cnt_node = node_id(1)

        dt_graph["graph"]["nodes"][cnt_node] = dict()
        dt_graph["graph"]["nodes"][cnt_node]["label"] = label
        dt_graph["graph"]["nodes"][cnt_node]["type"] = node_type
        dt_graph["graph"]["nodes"][cnt_node]["events"] = 1
        dt_graph["graph"]["nodes"][cnt_node]["patients"] = 1
        dt_graph["graph"]["nodes"][cnt_node]["highlight"] = 0

        if parameters is not None:
            for parameter in parameters:
                dt_graph["graph"]["nodes"][cnt_node][parameter] = parameters[parameter]

        dt_nodes[label] = (cnt_node, [patient_id])

    else:

        cnt_node = dt_nodes[label][0]

        if accumulate:
            events = dt_graph["graph"]["nodes"][cnt_node]["events"]
            dt_graph["graph"]["nodes"][cnt_node]["events"] = events + 1

            patient_list = dt_nodes[label][1]
            if patient_id not in patient_list:
                patient_list.append(patient_id)
                patients = dt_graph["graph"]["nodes"][cnt_node]["patients"]
                dt_graph["graph"]["nodes"][cnt_node]["patients"] = patients + 1

    if highlight == 1:
        dt_graph["graph"]["nodes"][cnt_node]["highlight"] = highlight

    return cnt_node


def add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, source, target, label, edge_type, highlight=0,
                 parameters=None):
    # NB At present all edges are unique so potentially the same edge could be added more than once
    #    but it will have a different ID, should have a different label

    if (source, target, label) not in dt_edges:

        cnt_edge = edge_id(1)

        dt_graph["graph"]["edges"][cnt_edge] = dict()
        dt_graph["graph"]["edges"][cnt_edge]["source"] = source
        dt_graph["graph"]["edges"][cnt_edge]["target"] = target
        dt_graph["graph"]["edges"][cnt_edge]["label"] = label
        dt_graph["graph"]["edges"][cnt_edge]["events"] = 1
        dt_graph["graph"]["edges"][cnt_edge]["patients"] = 1
        dt_graph["graph"]["edges"][cnt_edge]["type"] = edge_type
        dt_graph["graph"]["edges"][cnt_edge]["highlight"] = 0

        if parameters is not None:
            for parameter in parameters:
                dt_graph["graph"]["edges"][cnt_edge][parameter] = parameters[parameter]

        if patient_id is not None:
            dt_edges[(source, target, label)] = (cnt_edge, [patient_id])

    else:

        cnt_edge = dt_edges[(source, target, label)][0]
        events = dt_graph["graph"]["edges"][cnt_edge]["events"]
        dt_graph["graph"]["edges"][cnt_edge]["events"] = events + 1

        if patient_id is not None:
            patient_list = dt_edges[(source, target, label)][1]
            if patient_id not in patient_list:
                patient_list.append(patient_id)
                patients = dt_graph["graph"]["edges"][cnt_edge]["patients"]
                dt_graph["graph"]["edges"][cnt_edge]["patients"] = patients + 1

    if patient_id is not None:
        # Record use of edge by patient
        if cnt_edge not in dt_patients[patient_id]["edges"]:
            dt_patients[patient_id]["edges"][cnt_edge] = dict()
            dt_patients[patient_id]["edges"][cnt_edge]["events"] = 1
        else:
            events = dt_patients[patient_id]["edges"][cnt_edge]["events"]
            dt_patients[patient_id]["edges"][cnt_edge]["events"] = events + 1

    if highlight == 1:
        dt_graph["graph"]["edges"][cnt_edge]["highlight"] = highlight

    return cnt_edge

def get_time_node_details(time_tree_grad, row, dt_patients, patient_id):

    time_node_label = None
    time_node_type = None
    time_node_value = None

    if time_tree_grad is not None and ('start_datetime_mo' in row or 'start_datetime' in row) and patient_id in dt_patients:

        if "day_of_admission" in row:
            # DOTs RDV
            time_node_value = int(row["day_of_admission"])
        else:

            if time_tree_grad == "day":
                if 'start_datetime_mo' in row:
                    event_start = return_date(row['start_datetime_mo']).date()
                else:
                    event_start = return_date(row['start_datetime']).date()

            # Get patient start_datetime - could be more than one
            total_events = dt_patients[patient_id]['instances']['total']
            for instance_id in range(1, total_events + 1):
                if time_tree_grad == "day":
                    start = dt_patients[patient_id]['instances'][instance_id][0].date()
                    end = dt_patients[patient_id]['instances'][instance_id][1].date()

                if start <= event_start <= end:
                    patient_start = start
                    break

            if time_tree_grad == "day":
                time_node_value = (event_start - patient_start).days

        time_node_label = f"{time_tree_grad}: {time_node_value}"
        time_node_type = "period"

        if time_node_label is None:
            pause = True

    return time_node_label, time_node_type, time_node_value


def add_rdv_period_node(time_tree_grad, row, dt_patients, highlight, dt_graph, dt_nodes, node_id, patient_id,
                        create_node=True):

    time_node_label, time_node_type, time_node_value = get_time_node_details(time_tree_grad, row, dt_patients, patient_id)

    time_node = None

    if time_tree_grad is not None:

        if create_node:
            parameters = {"value": time_node_value}
            time_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, time_node_label, time_node_type,
                                     highlight=highlight, parameters=parameters)

    return time_node, time_node_label, time_node_type


def add_demographics_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, prev_row, row, node_id, edge_id,
                              incl_node_types=None,
                              time_tree_grad=None, highlight_patients=None, inc_params=True):
    # project_id,hospital_no,birth_date,death_date,deceased_flag,sex,ethnicity_nat_code,ethnicity_local_code,ethnicity_name

    patient_id = row['project_id']

    if highlight_patients is not None and patient_id in highlight_patients:
        highlight = 1
    else:
        highlight = 0

    prev_node = None
    prev_node_label = None
    prev_node_type = None

    node_type = "patient"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Patient: {row['project_id']}"
        label = node_label

        parameters = None
        if inc_params:
            parameters = {"Sex": row['sex']}

        patient_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight)

        prev_node = patient_node
        prev_node_label = node_label
        prev_node_type = node_type

    node_type = "sex"
    if incl_node_types is None or node_type.lower() in incl_node_types:

        node_label = f"Sex: {row['sex']}"
        label = node_label
        sex_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight)

        if prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, sex_node, label, edge_type,
                         highlight=highlight)

    return dt_graph


def add_hospital_admissions_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, prev_row, row, node_id, edge_id,
                                     incl_node_types=None,
                                     time_tree_grad=None, highlight_patients=None, inc_params=True):
    # project_id,encounter_key,patient_class,hospital_service,admission_type,admission_source,disharge_disposition,
    # principal_problem,start_datetime,end_datetime

    patient_id = row['project_id']

    if highlight_patients is not None and patient_id in highlight_patients:
        highlight = 1
    else:
        highlight = 0

    prev_node = None
    prev_node_label = None
    prev_node_type = None

    # Pateint node should already exist - if it does do not add patients or events
    node_type = "patient"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Patient: {row['project_id']}"
        label = node_label
        patient_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, accumulate=False,
                                    highlight=highlight)

        prev_node = patient_node
        prev_node_label = node_label
        prev_node_type = node_type

    node_type = "hospital admission"
    if incl_node_types is None or node_type.lower() in incl_node_types:

        node_label = f"Hospital admission from: {row['start_datetime']} to: {row['end_datetime']}"
        label = f"Patient: {patient_id}: {node_label}"
        hospital_admission_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type,
                                               highlight=highlight)

        if prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, hospital_admission_node,
                         label, edge_type, highlight=highlight)

        prev_node = hospital_admission_node
        prev_node_label = node_label
        prev_node_type = node_type

    return dt_graph


def add_medication_orders_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, prev_row, row, node_id,
                                   edge_id, incl_node_types=None,
                                   time_tree_grad=None, highlight_patients=None, method="heterogeneous",
                                   inc_params=True):
    # row:
    # project_id,start_datetime,end_datetime,MedicationOrderKey,ordered_datetime,medication_order_id,sequence_number,
    # drug_code,drug_name,drug_gpi,drug_simple_generic_name,drug_therapeutic_class_name,drug_pharmaceutical_class_name,
    # drug_pharmaceutical_subclass_name,dose_amount,formulation_code,intended_frequency,quantity,dose,dose_range,
    # calculated_dose_range,dose_number,route_name,indication,indication_comments,response,medication_order_name,
    # medication_order_mode_name,medication_order_class_name,medication_order_source_name,disps_this_period,
    # admins_this_period,first_admin_datetime,encounter_key
    #
    # Added columns - from hospital admissions
    # start_datetime_ha, end_datetime_ha

    patient_id = row['project_id']

    if highlight_patients is not None and patient_id in highlight_patients:
        highlight = 1
    else:
        highlight = 0

    create_node = True if method == "heterogeneous" else False

    time_node, time_node_label, time_node_type = add_rdv_period_node(time_tree_grad, row, dt_patients, highlight,
                                                                     dt_graph, dt_nodes, node_id, patient_id,
                                                                     create_node=create_node)

    if time_node_label is None:
        pause = True

    prev_node = None
    prev_node_label = None
    prev_node_type = None

    # Pateint node should already exist - if it does do not add patients or events
    node_type = "patient"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Patient: {row['project_id']}"
        label = node_label
        patient_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, accumulate=False,
                                    highlight=highlight)

        prev_node = patient_node
        prev_node_label = node_label
        prev_node_type = node_type

    node_type = "hospital admission"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Hospital admission from: {row['start_datetime_ha']} to: {row['end_datetime_ha']}"
        label = f"Patient: {patient_id}: {node_label}"
        hospital_admission_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type,
                                               accumulate=False,
                                               highlight=highlight)

        prev_node = hospital_admission_node
        prev_node_label = node_label
        prev_node_type = node_type

    node_type = "Medication order"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Medication order: {row['MedicationOrderKey']}"
        label = f"Patient: {patient_id}: {node_label}"

        parameters = None
        if inc_params:
            parameters = {"Drug": row['drug_simple_generic_name'],
                          "Pharmaceutical subclass": row['drug_pharmaceutical_subclass_name'],
                          "Pharmaceutical class": row['drug_pharmaceutical_class_name']}

        medication_order_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type,
                                             highlight=highlight, parameters=parameters)

        if prev_node is not None:
            label = f"Patient: {patient_id}: {prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, medication_order_node, label,
                         edge_type, highlight=highlight)

            prev_node = medication_order_node
            prev_node_label = node_label
            prev_node_type = node_type

        if time_node is not None:
            label = f"{time_node_label} has {node_label}"
            edge_type = f"{time_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, time_node, medication_order_node, label,
                         edge_type, highlight=highlight)
            time_node = None
            time_node_label = None
            time_node_type = None

    node_type = "drug"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Drug: {row['drug_simple_generic_name']}"
        label = node_label

        parameters = None
        if inc_params:
            parameters = {"Pharmaceutical subclass": row['drug_pharmaceutical_subclass_name'],
                          "Pharmaceutical class": row['drug_pharmaceutical_class_name']}

        drug_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight,
                                 parameters=parameters)

        if method == "heterogeneous" and prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, drug_node, label, edge_type,
                         highlight=highlight)


        elif method == "homogeneous" and prev_row is not None:

            # is this the same patient?
            if patient_id == prev_row["project_id"]:
                prev_node_label = f"Drug: {prev_row['drug_simple_generic_name']}"
                prev_drug_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, prev_node_label, node_type,
                                              accumulate=False)

                # if using time tree then edges are created at the end after all the nodes are in place
                if time_tree_grad is None:
                    label = f"{prev_node_label} precedes {node_label}"
                    edge_type = f"{node_type} precedes {node_type}"
                    add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_drug_node, drug_node, label,
                                 edge_type, highlight=highlight)

        prev_node = drug_node
        prev_node_label = node_label
        prev_node_type = node_type

        if time_node_label is not None:
            if method == "heterogeneous":
                label = f"{time_node_label} has {node_label}"
                edge_type = f"{time_node_type} has {node_type}"
                add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, time_node, drug_node, label,
                             edge_type, highlight=highlight)
            else:
                # record by time period
                node_list = []
                if patient_id not in dt_periods:
                    dt_periods[patient_id] = dict()
                    dt_periods[patient_id][node_type] = dict()
                    dt_periods[patient_id][node_type][time_node_label] = node_list
                elif node_type not in dt_periods[patient_id]:
                    dt_periods[patient_id][node_type] = dict()
                    dt_periods[patient_id][node_type][time_node_label] = node_list
                elif time_node_label not in dt_periods[patient_id][node_type]:
                    dt_periods[patient_id][node_type][time_node_label] = node_list
                else:
                    node_list = dt_periods[patient_id][node_type][time_node_label]

                if (drug_node, node_label) not in node_list:
                    node_list.append((drug_node, node_label))
                    dt_periods[patient_id][node_type][time_node_label] = node_list

                if time_node_label is None:
                    pause = True

            time_node = None
            time_node_label = None
            time_node_type = None

    node_type = "Pharmaceutical subclass"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Pharmaceutical subclass: {row['drug_pharmaceutical_subclass_name']}"
        label = node_label

        parameters = None
        if inc_params:
            parameters = {"Pharmaceutical class": row['drug_pharmaceutical_class_name']}

        phsubclass_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight,
                                       parameters=parameters)

        if prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, phsubclass_node, label,
                         edge_type,
                         highlight=highlight)

        prev_node = phsubclass_node
        prev_node_label = node_label
        prev_node_type = node_type

        if time_node is not None:
            label = f"{time_node_label} has {node_label}"
            edge_type = f"{time_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, time_node, phsubclass_node, label,
                         edge_type, highlight=highlight)
            time_node = None
            time_node_label = None
            time_node_type = None

    node_type = "Pharmaceutical class"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Pharmaceutical class: {row['drug_pharmaceutical_class_name']}"
        label = node_label
        phclass_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight)

        if prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, phclass_node, label,
                         edge_type,
                         highlight=highlight)

        if time_node is not None:
            label = f"{time_node_label} has {node_label}"
            edge_type = f"{time_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, time_node, phclass_node, label,
                         edge_type, highlight=highlight)
            time_node = None
            time_node_label = None
            time_node_type = None

    return dt_graph


def add_dots_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, prev_row, row, node_id,
                                   edge_id, incl_node_types=None,
                                   time_tree_grad=None, highlight_patients=None, method="heterogeneous",
                                   inc_params=True, directed=1, index=0):
    # row:
    # project_id,start_datetime,end_datetime,MedicationOrderKey,ordered_datetime,medication_order_id,sequence_number,
    # drug_code,drug_name,drug_gpi,drug_simple_generic_name,drug_therapeutic_class_name,drug_pharmaceutical_class_name,
    # drug_pharmaceutical_subclass_name,dose_amount,formulation_code,intended_frequency,quantity,dose,dose_range,
    # calculated_dose_range,dose_number,route_name,indication,indication_comments,response,medication_order_name,
    # medication_order_mode_name,medication_order_class_name,medication_order_source_name,disps_this_period,
    # admins_this_period,first_admin_datetime,encounter_key
    #
    # Added columns - from hospital admissions
    # start_datetime_ha, end_datetime_ha

    patient_id = row['project_id']

    if highlight_patients is not None and patient_id in highlight_patients:
        highlight = 1
    else:
        highlight = 0

    # If heterogeneous create a time node, otherwise just get time details which
    # can be used as a parameter and/or used to create edges per time period
    create_node = True if method == "heterogeneous" else False

    time_node, time_node_label, time_node_type = add_rdv_period_node(time_tree_grad, row, dt_patients, highlight,
                                                                     dt_graph, dt_nodes, node_id, patient_id,
                                                                     create_node=create_node)

    prev_node = None
    prev_node_label = None
    prev_node_type = None

    # Pateint node should already exist - if it does do not add patients or events
    node_type = "patient"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Patient: {row['project_id']}"
        label = node_label
        patient_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, accumulate=False,
                                    highlight=highlight)

        prev_node = patient_node
        prev_node_label = node_label
        prev_node_type = node_type

    node_type = "drug"
    if incl_node_types is None or node_type.lower() in incl_node_types:
        node_label = f"Drug: {row['drug_simple_generic_name']}"
        label = node_label

        parameters = None
        if inc_params:
            parameters = {"Pharmaceutical subclass": row['drug_pharmaceutical_subclass_name'],
                          "Pharmaceutical class": row['drug_pharmaceutical_class_name']}

        accumulate = True if index == 0 else False
        drug_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, label, node_type, highlight=highlight,
                                 parameters=parameters, accumulate=accumulate)

        if method == "heterogeneous" and prev_node is not None:
            label = f"{prev_node_label} has {node_label}"
            edge_type = f"{prev_node_type} has {node_type}"
            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_node, drug_node, label, edge_type,
                         highlight=highlight)

        elif method == "homogeneous" and prev_row is not None:

            prev_node_label = f"Drug: {prev_row['drug_simple_generic_name']}"
            prev_drug_node = add_rdv_node(dt_graph, dt_nodes, node_id, patient_id, prev_node_label, node_type,
                                          accumulate=False)

            # # if using time tree then edges are created at the end after all the nodes are in place
            # if time_tree_grad is None:
            # label = f"{prev_node_label} comedication with {node_label} {time_node_label}"
            # edge_type = f"{prev_node_type} comedication with {node_type}  {time_node_type}"
            # Adding in time into label would create a multigraph, with out label events represent days in DOTs
            label = f"{prev_node_label} comedication with {node_label}"
            edge_type = f"{prev_node_type} comedication with {node_type}"

            add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, prev_drug_node, drug_node, label,
                         edge_type, highlight=highlight)

            # Add in reverse edge as linkage is reversable
            if directed == 1:
                # label = f"{node_label} comedication with {prev_node_label} {time_node_label}"
                # edge_type = f"{node_type} comedication with {prev_node_type} {time_node_type}"
                label = f"{node_label} comedication with {prev_node_label}"
                edge_type = f"{node_type} comedication with {prev_node_type}"

                # NB reverse nodes
                add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, drug_node, prev_drug_node, label,
                             edge_type, highlight=highlight)

        prev_node = drug_node
        prev_node_label = node_label
        prev_node_type = node_type

        if time_node_label is not None:
            if method == "heterogeneous":
                label = f"{time_node_label} has {node_label}"
                edge_type = f"{time_node_type} has {node_type}"
                add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id, time_node, drug_node, label,
                             edge_type, highlight=highlight)

            time_node = None
            time_node_label = None
            time_node_type = None

def create_graph_structure(project, sub_project, directed, method):

    # Create graph
    dt_graph = dict()
    dt_graph["graph"] = dict()
    dt_graph["graph"]["id"] = 1
    dt_graph["graph"]["label"] = "{0}{1}".format(project, "" if sub_project is None else f"_{sub_project}")
    dt_graph["graph"]["directed"] = directed
    dt_graph["graph"]["created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dt_graph["graph"]["method"] = method

    # Need to define any attributes used
    dt_graph["graph"]["_graph_atts"] = dict()
    graph_att_keys = [("G1", "label", "string"),
                      ("G2", "directed", "int"),
                      ("G3", "created", "string"),
                      ("G4", "method", "string")
                      ]
    for graph_att_key in graph_att_keys:
        graph_att_id = graph_att_key[0]
        dt_graph["graph"]["_graph_atts"][graph_att_id] = dict()
        dt_graph["graph"]["_graph_atts"][graph_att_id]["name"] = graph_att_key[1]
        dt_graph["graph"]["_graph_atts"][graph_att_id]["type"] = graph_att_key[2]

    dt_graph["graph"]["nodes"] = dict()
    dt_graph["graph"]["edges"] = dict()

    return dt_graph


def create_graph_from_rdvs(rdvs, project, dex_project_path, csv_project_path, gml_project_path, sub_project=None,
                           incl_node_types=None, stage=1, size_method="patients", highlight_patients=None,
                           output_yaml=False, output_excel=False, output_graphml=True, output_gml=True,
                           time_tree_grad=None, method="heterogeneous", inc_params=False, sel_patient=None, 
                           directed=1, phase="demo"):
    
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    dt_graph = create_graph_structure(project, sub_project, directed, method)

    # need a reverse lookup - for patient with project id which is its node? Also for edges same drug classification
    dt_nodes = dict()
    dt_edges = dict()
    dt_periods = dict()

    node_id = accumulator()
    edge_id = accumulator()

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"

    #########################
    # Patients - patient list
    #########################

    # Read patient list - create dictionary of patients
    # store start date - calculate all dates from this date/time
    # store all edges with number of events

    dt_patients = dict()

    patient_list_file_name = f"{file_name_prefix}patient_list.csv"
    inpfilepath = os.path.join(dex_project_path, patient_list_file_name)

    log_debug("Processing patient list, file: {0}".format(patient_list_file_name))
    df_patient_list = pd.read_csv(inpfilepath)

    # Iterate through df to create patient dictionary
    number_rows = len(df_patient_list.index)

    for index, row in df_patient_list.iterrows():
        sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(index + 1, number_rows))
        sys.stdout.flush()

        # NB could have the same patient with different start dates
        project_id = row['project_id']
        hospital_no = row['hospital_no']

        if sel_patient is None or project_id == sel_patient:

            if time_tree_grad is not None:
                start_datetime = return_date(row['start_datetime'])
                end_datetime = return_date(row['end_datetime'])

            if project_id not in dt_patients:
                dt_patients[project_id] = dict()
                dt_patients[project_id]['hospital_no'] = hospital_no
                dt_patients[project_id]['instances'] = dict()
                dt_patients[project_id]['instances']['total'] = 1
                dt_patients[project_id]['edges'] = dict()
            else:
                events = dt_patients[project_id]['instances']['total']
                dt_patients[project_id]['instances']['total'] = events + 1

            if time_tree_grad is not None:
                cnt_event = dt_patients[project_id]['instances']['total']
                dt_patients[project_id]['instances'][cnt_event] = (start_datetime, end_datetime)
    print()

    ######
    # RDVs
    ######

    for rdv, source in rdvs:

        file_name = f"{file_name_prefix}{source}_patient_{rdv}.csv"
        inpfilepath = os.path.join(csv_project_path, file_name)

        # load RDV into dataframe and pass to relevant function
        log_debug("Processing RDV: {0}, file: {1}".format(rdv, file_name))
        df_rdv = pd.read_csv(inpfilepath)

        if rdv == "medication_orders":
            # merge with hospital_admissions
            file_name = f"{file_name_prefix}{source}_patient_hospital_admissions.csv"
            inpfilepath = os.path.join(csv_project_path, file_name)
            df_ha_rdv = pd.read_csv(inpfilepath)
            # merge on project_id and encounterKey
            df_merge = pd.DataFrame.merge(df_rdv, df_ha_rdv, on=['project_id', 'encounter_key'], how='inner',
                                          suffixes=("_mo", "_ha"))
            df_rdv = df_merge

        elif rdv == "dots":
            df_rdv.sort_values(["project_id", "day_of_admission"], inplace=True)

        # Iterate through df to create nodes and edges
        number_rows = len(df_rdv.index)
        prev_row = None
        prev_rows = []
        cnt_patient_id = ""
        cnt_time_node_value = ""

        for row_num, row in df_rdv.iterrows():

            sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(row_num + 1, number_rows))
            sys.stdout.flush()

            patient_id = row['project_id']
            # What is the time period? Retruns None if time_tree_grad = None
            time_node_label, time_node_type, time_node_value = get_time_node_details(time_tree_grad, row, dt_patients,
                                                                                     patient_id)

            if sel_patient is None or patient_id == sel_patient:

                if method == "heterogeneous":

                    if rdv == "demographics":
                        add_demographics_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, None, row, node_id,
                                                  edge_id, incl_node_types,
                                                  time_tree_grad, highlight_patients)
                    elif rdv == "hospital_admissions":
                        add_hospital_admissions_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, None, row, node_id,
                                                         edge_id, incl_node_types,
                                                         time_tree_grad, highlight_patients)
                    elif rdv == "medication_orders":
                        add_medication_orders_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, None, row,
                                                       node_id, edge_id, incl_node_types,
                                                       time_tree_grad, highlight_patients, inc_params=inc_params)

                elif method == "homogeneous":

                    if rdv == "medication_orders":
                        add_medication_orders_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, prev_row,
                                                       row, node_id, edge_id, incl_node_types,
                                                       time_tree_grad, highlight_patients, method=method,
                                                       inc_params=inc_params)

                    elif rdv == "dots":
                        # If co-medications then need to keep track of all previous medications for this patient and period
                        if cnt_patient_id != patient_id or cnt_time_node_value != time_node_value:
                            cnt_patient_id = patient_id
                            cnt_time_node_value = time_node_value

                            prev_rows = [None, ]

                        for prev_row_num, prev_row in enumerate(prev_rows):
                            add_dots_to_graph(dt_graph, dt_nodes, dt_edges, dt_patients, dt_periods, prev_row,
                                                           row, node_id, edge_id, incl_node_types,
                                                           time_tree_grad, highlight_patients, method=method,
                                                           inc_params=inc_params, directed=directed, index=prev_row_num)

                        prev_rows.append(row)

                    prev_row = row

        print()

    if time_tree_grad is not None:

        log_debug("Processing time tree: {0}".format(method))

        if method == "heterogeneous":

            period_nodes = []

            for node_id in dt_graph["graph"]["nodes"]:

                # Check for a period node
                if dt_graph["graph"]["nodes"][node_id]["type"] == "period":
                    period_nodes.append((node_id, dt_graph["graph"]["nodes"][node_id]["label"],
                                         dt_graph["graph"]["nodes"][node_id]["value"]))

            # Add edges between period nodes
            node_type = "period"
            # Sort on Value to get correct order
            period_nodes = sorted(period_nodes, key=lambda x: x[2])

            for pn_num, period_node in enumerate(period_nodes):

                if pn_num > 0:
                    target_node = period_node[0]
                    node_label = period_node[1]
                    label = f"{source_label} has {node_label}"
                    edge_type = f"{node_type} has {node_type}"
                    add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id=None, source=source_node,
                                 target=target_node, label=label, edge_type=edge_type, highlight=False)

                source_node = period_node[0]
                source_label = period_node[1]

        elif method == "homogeneous":

            # process dt_periods adding required edges
            for patient_id in dt_periods:

                if highlight_patients is not None and patient_id in highlight_patients:
                    highlight = 1
                else:
                    highlight = 0

                for node_type in dt_periods[patient_id]:

                    prev_node_list = None
                    prev_time_node_label = None

                    for time_node_label in dt_periods[patient_id][node_type]:

                        node_list = dt_periods[patient_id][node_type][time_node_label]

                        if prev_node_list is not None:

                            for source in prev_node_list:

                                source_node = source[0]
                                source_label = source[1]

                                for target in node_list:
                                    target_node = target[0]
                                    target_label = target[1]

                                    label = f"{source_label} precedes {target_label}"
                                    edge_type = f"{node_type} precedes {node_type}"

                                    parameters = {"Period": f"{prev_time_node_label} to {time_node_label}"}

                                    add_rdv_edge(dt_graph, dt_edges, dt_patients, edge_id, patient_id=patient_id,
                                                 source=source_node,
                                                 target=target_node, label=label, edge_type=edge_type,
                                                 highlight=highlight,
                                                 parameters=parameters)

                        prev_node_list = node_list
                        prev_time_node_label = time_node_label

    # Output dictionary as a yaml file
    outFilePath = os.path.join(gml_project_path, f"{sub_project}_{phase}_{stage}_rawgraph.yaml")

    create_yaml_file(dt_graph, outFilePath)

    # Do some one off tasks so they don't need to be repeated
    # store max_events and max_patients, total events, total patients(?), total nodes, total edges
    # store parameters in graph
    # Add an initial colour and size so will work out of the box.
    #
    assign_colour_size(dt_graph, size_method=size_method)

    if sel_patient is None:
        output_folder = gml_project_path
    else:
        output_folder = gml_project_path + "\\" + sel_patient
        # create if doesn't exist
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
            log_debug(f"Created folder : {output_folder}")

    if output_yaml:
        # Output yaml file of dictionary
        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_graph.yaml")
        create_yaml_file(dt_graph, outFilePath)

        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_patients.yaml")
        create_yaml_file(dt_patients, outFilePath)

        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_nodes.yaml")
        create_yaml_file(dt_nodes, outFilePath)

        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_edges.yaml")
        create_yaml_file(dt_edges, outFilePath)

        if len(dt_periods) > 0:
            outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_periods.yaml")
            create_yaml_file(dt_periods, outFilePath)

    if output_excel:
        # Create a excel file
        outFilePath = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_{size_method}_graph.xlsx")
        create_excel_file(dt_graph, outFilePath, dt_nodes, dt_edges, dt_patients, dt_periods)

    if output_gml:
        # create more graph model files gml & graphML
        outFilePath_gml = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_graph.gml")
        create_gml_file(dt_graph, outFilePath_gml)

    if output_graphml:
        outFilePath_graphml = os.path.join(output_folder, f"{sub_project}_{phase}_{stage}_graph.graphml")
        create_graphml_file(dt_graph, outFilePath_graphml)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return dt_graph


def assign_colour_size(dt_graph, size_method="events"):
    # size method can be events, patients, combined

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    # Is this the first time?
    if "_node_max_events" not in dt_graph["graph"]:

        log_debug("Gathering initial graph data")

        # Nodes
        # find max events or patients
        node_max_counter = 0
        node_max_events = 0
        node_max_patients = 0
        total_nodes = 0
        node_att_keys = dict()

        for node_id in dt_graph["graph"]["nodes"]:

            total_nodes += 1

            if size_method in dt_graph["graph"]["nodes"][node_id]:
                if dt_graph["graph"]["nodes"][node_id][size_method] > node_max_counter:
                    node_max_counter = dt_graph["graph"]["nodes"][node_id][size_method]
            if "events" in dt_graph["graph"]["nodes"][node_id]:
                if dt_graph["graph"]["nodes"][node_id]["events"] > node_max_events:
                    node_max_events = dt_graph["graph"]["nodes"][node_id]["events"]
            if "patients" in dt_graph["graph"]["nodes"][node_id]:
                if dt_graph["graph"]["nodes"][node_id]["patients"] > node_max_patients:
                    node_max_patients = dt_graph["graph"]["nodes"][node_id]["patients"]

            # Check for attributes
            for node_att_key in dt_graph["graph"]["nodes"][node_id]:

                # system parameters begining with _ should not be output
                if node_att_key[:1] != "_":
                    if node_att_key not in node_att_keys:
                        value = dt_graph["graph"]["nodes"][node_id][node_att_key]
                        if isinstance(value, float):
                            node_att_type = "double"
                        elif isinstance(value, int):
                            node_att_type = "int"
                        elif isinstance(value, bool):
                            node_att_type = "boolean"
                        else:
                            node_att_type = "string"
                        node_att_id = "N{0}".format(len(node_att_keys) + 1)
                        node_att_keys[node_att_key] = (node_att_id, node_att_type)

        # Edges
        # find max events or patients
        edge_max_counter = 0
        edge_max_events = 0
        edge_max_patients = 0
        total_edges = 0
        edge_att_keys = dict()

        for edge_id in dt_graph["graph"]["edges"]:

            total_edges += 1

            if size_method in dt_graph["graph"]["edges"][edge_id]:
                if dt_graph["graph"]["edges"][edge_id][size_method] > edge_max_counter:
                    edge_max_counter = dt_graph["graph"]["edges"][edge_id][size_method]
            if "events" in dt_graph["graph"]["edges"][edge_id]:
                if dt_graph["graph"]["edges"][edge_id]["events"] > edge_max_events:
                    edge_max_events = dt_graph["graph"]["edges"][edge_id]["events"]
            if "patients" in dt_graph["graph"]["edges"][edge_id]:
                if dt_graph["graph"]["edges"][edge_id]["patients"] > edge_max_patients:
                    edge_max_patients = dt_graph["graph"]["edges"][edge_id]["patients"]

            # Check for attributes
            for edge_att_key in dt_graph["graph"]["edges"][edge_id]:

                # system parameters begining with _ should not be output
                if edge_att_key not in ["source", "target", ] and edge_att_key[:1] != "_":
                    if edge_att_key not in edge_att_keys:
                        value = dt_graph["graph"]["edges"][edge_id][edge_att_key]
                        if isinstance(value, float):
                            edge_att_type = "double"
                        elif isinstance(value, int):
                            edge_att_type = "int"
                        elif isinstance(value, bool):
                            edge_att_type = "boolean"
                        else:
                            edge_att_type = "string"
                        edge_att_id = "E{0}".format(len(edge_att_keys) + 1)
                        edge_att_keys[edge_att_key] = (edge_att_id, edge_att_type)

        # Store results at graph level
        dt_graph["graph"]["_node_max_events"] = node_max_events
        dt_graph["graph"]["_node_max_patients"] = node_max_patients
        dt_graph["graph"]["_node_total"] = total_nodes
        dt_graph["graph"]["_edge_max_events"] = edge_max_events
        dt_graph["graph"]["_edge_max_patients"] = edge_max_patients
        dt_graph["graph"]["_edge_total"] = total_edges
        if len(node_att_keys) > 0:
            dt_graph["graph"]["_node_atts"] = dict()
            for node_att_key in node_att_keys:
                node_att_id = node_att_keys[node_att_key][0]
                node_att_type = node_att_keys[node_att_key][1]
                dt_graph["graph"]["_node_atts"][node_att_id] = dict()
                dt_graph["graph"]["_node_atts"][node_att_id]["name"] = node_att_key
                dt_graph["graph"]["_node_atts"][node_att_id]["type"] = node_att_type
        if len(edge_att_keys) > 0:
            dt_graph["graph"]["_edge_atts"] = dict()
            for edge_att_key in edge_att_keys:
                edge_att_id = edge_att_keys[edge_att_key][0]
                edge_att_type = edge_att_keys[edge_att_key][1]
                dt_graph["graph"]["_edge_atts"][edge_att_id] = dict()
                dt_graph["graph"]["_edge_atts"][edge_att_id]["name"] = edge_att_key
                dt_graph["graph"]["_edge_atts"][edge_att_id]["type"] = edge_att_type

    else:
        node_max_counter = dt_graph["graph"]["_node_max_events"] if size_method == "events" else dt_graph["graph"][
            "_node_max_patients"]
        node_max_events = dt_graph["graph"]["_node_max_events"]
        node_max_patients = dt_graph["graph"]["_node_max_patients"]
        edge_max_counter = dt_graph["graph"]["_edge_max_events"] if size_method == "events" else dt_graph["graph"][
            "_edge_max_patients"]
        edge_max_events = dt_graph["graph"]["_edge_max_events"]
        edge_max_patients = dt_graph["graph"]["_edge_max_patients"]

    # Assign node colours and sizes
    log_debug("Assigning Node colour and size")

    min_size = 10
    max_size = 100

    for node in dt_graph["graph"]["nodes"]:

        if "type" in dt_graph["graph"]["nodes"][node]:

            if dt_graph["graph"]["nodes"][node]["type"].lower() == "patient":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#d30000"  # red
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "sex":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#fff200"  # Yellow
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "hospital admission":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#fc0fc0"  # pink
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "medication order":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#3bb143"  # green
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "drug":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#6693f5"  # cornflower
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "pharmaceutical subclass":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#0018f9"  # blue
            elif dt_graph["graph"]["nodes"][node]["type"].lower() == "pharmaceutical class":
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#000080"  # Navy
            else:
                dt_graph["graph"]["nodes"][node]["_node_colour"] = "#ff43a4"

            if size_method == "combined":
                if "events" in dt_graph["graph"]["nodes"][node] and "patients" in dt_graph["graph"]["nodes"][node]:
                    events = dt_graph["graph"]["nodes"][node]["events"]
                    patients = dt_graph["graph"]["nodes"][node]["patients"]
                    dt_graph["graph"]["nodes"][node]["_node_size"] = int(
                        ((min_size / 2) + int((events / node_max_events) * ((max_size - min_size) / 2))) + (
                                    (min_size / 2) + int((patients / node_max_patients) * ((max_size - min_size) / 2))))
            else:
                if size_method in dt_graph["graph"]["nodes"][node]:
                    counter = dt_graph["graph"]["nodes"][node][size_method]
                    dt_graph["graph"]["nodes"][node]["_node_size"] = min_size + int(
                        (counter / node_max_counter) * (max_size - min_size))

    # Assign node colours and sizes
    log_debug("Assigning Edge size")

    min_size = 1
    max_size = 50

    for edge in dt_graph["graph"]["edges"]:

        if "type" in dt_graph["graph"]["edges"][edge]:

            if "highlight" in dt_graph["graph"]["edges"][edge] and dt_graph["graph"]["edges"][edge]["highlight"] == 1:
                dt_graph["graph"]["edges"][edge]["_edge_colour"] = "#d30000"  # red
            else:
                dt_graph["graph"]["edges"][edge]["_edge_colour"] = "#000000"  # black

            if size_method == "combined":
                if "events" in dt_graph["graph"]["edges"][edge] and "patients" in dt_graph["graph"]["edges"][edge]:
                    events = dt_graph["graph"]["edges"][edge]["events"]
                    patients = dt_graph["graph"]["edges"][edge]["patients"]
                    dt_graph["graph"]["edges"][edge]["_edge_size"] = int(
                        ((min_size / 2) + (events / edge_max_events) * ((max_size - min_size) / 2)) + (
                                    (min_size / 2) + (patients / edge_max_patients) * ((max_size - min_size) / 2)))
            else:
                if size_method in dt_graph["graph"]["edges"][edge]:
                    counter = dt_graph["graph"]["edges"][edge][size_method]
                    dt_graph["graph"]["edges"][edge]["_edge_size"] = min_size + int(
                        (counter / edge_max_counter) * (max_size - min_size))

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return dt_graph


def get_node_colors(dt_graph):
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    node_colors = []

    # Assign colours
    for node in dt_graph["graph"]["nodes"]:

        if "_node_colour" in dt_graph["graph"]["nodes"][node]:
            node_colors.append(dt_graph["graph"]["nodes"][node]["_node_colour"])
        else:
            node_colors.append("#000000")  # Black

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return node_colors


def get_node_sizes(dt_graph):
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    node_sizes = []

    # Assign sizes
    for node in dt_graph["graph"]["nodes"]:

        if "_node_size" in dt_graph["graph"]["nodes"][node]:
            node_sizes.append(dt_graph["graph"]["nodes"][node]["_node_size"])
        else:
            node_sizes.append(50)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return node_sizes


def get_edge_colors(dt_graph):
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    edge_colors = []

    # Assign colours
    for edge in dt_graph["graph"]["edges"]:

        if "_edge_colour" in dt_graph["graph"]["edges"][edge]:
            edge_colors.append(dt_graph["graph"]["edges"][edge]["_edge_colour"])
        else:
            edge_colors.append("#000000")  # Black

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return edge_colors


def get_edge_sizes(dt_graph):
    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    edge_sizes = []

    # Assign sizes
    for edge in dt_graph["graph"]["edges"]:

        if "_edge_size" in dt_graph["graph"]["edges"][edge]:
            edge_sizes.append(dt_graph["graph"]["edges"][edge]["_edge_size"])
        else:
            edge_sizes.append(2)

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))

    return edge_sizes


