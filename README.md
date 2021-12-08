# RE200-GRACE
## Introduction
The GOSH DRE/CIRP project for John Booth's PhD.

###What is my PhD trying to achieve?
To create a timely way to compare patient’s progress using routinely collected EPR data. The current EPR is extraordinary at giving clinicians a wealth of data on a particular patient in one interface, but how do you compare your patient to others?

Could we build a recommendation system similar to Amazon or Netflix where we graph the interaction between patients and events to be able to ‘recommend’ a prospective event?

###What is this Phase 1 trying to achieve?
Understanding the fundamentals of graph analytics with emphasis on example EPR data.
- A better understanding on how Graph Creation and Analytics works.
- Key differences between labelled property graph and a semantic graph.
- A deep dive literature review based on terms derived from the initial sprints

##General
###Packages used:
- Anaconda base installation
- Networkx
- Matplotlib
- Plotly
- Dash
- Colour

###Project path
The default path for the project is: "Z:\Projects\Research\0200-GRACE"

If the path does not exist then the default is the current directory that the code is running in. This path can be overridden by a command line parameter:

    Python Initial_rdv_visualisation.py  -path "H:\Projects\Research\0200-GRACE"

Sub folders are created:
        dex_project_path = project_path + "\\DataExtraction"
        csv_project_path = dex_project_path + "\\CSVs"
        gml_project_path = dex_project_path + "\\GMLs"

###Stages
Stages are used to run chunks of code during development to explorer different aspects of the phase in development.
Any script that uses stages the required list of stages to run can be passed in as an argument:

    Python Initial_rdv_visualisation.py –stages 1 2 3

If no argument is passed then stage 1 will be run.

###Output file creation:
- f"{sub_project}_{phase]_{stage}_{file type}.{extension}"

##Main scripts
###Initial_rdv_visualisation.py
Creates dummy RDV's if the required RDV's doen't exist.
- phase = "check_rdvs"
- Stage 1 – sub_project = “sp01”
- Stage 2 – sub_project = “sp02”
- Stage 3 – sub_project = “sp03”
- check_rdvs()
- create_rdv_visualisation()

###Initial_graph_creation.py
Creates initial set of graphML files used in initial_graphml_plot.
- phase = "demo"
- Stage 1 - Very simple coloured graph
- Stage 2 - Very simple coloured graph - with export files
- stage 3 - All RDV data into dictionary, create graph from dictionary and plot, save to gml file
- stage 4 - All RDV data into dictionary, save to gml file create graph from gml file and plot
- stage 5 - Selected RDV data into dictionary and highlighted patint, save to gml file create graph from gml file and plot
- Stage 6 - multiple graphs - All RDV vs Selected RDV plots show node size based on events, patients and combined
- Stage 7 - multiple graphs - All RDV vs Selected RDV with no highlighted and highlighted patient
- Stage 8 - add in time tree - just files
- stage 9 - time tree simpler graph - just files
- stage 10 - tree graph single type of node (drug) - just files
- stage 11 - Homogeneous graph - drugs
- stage 12 - Homogeneous graph - drugs and days i.e which drugs precede which other drugs

###Initial_graph_analytics.py
Creates initial set of graph analytics stored in JSON files used in initial_graphml_plot.
- Phase = “analytics”
- Stage 1, 3, and 5 – create_graph_from_rdvs() for sub_projects sp01, sp02 and sp03
- Stage 7 - create_dots_test_analytics_dt_graph() creates graph of test data, stored in files with sub_project = ‘test01’.
- Stage 2, 4, 6, and 8 – process_graph_analytics for sub projects sp01, sp02, sp03 and test01. Results saved in both YAML and JSON file formats.

###initial_graphml_plot.py (20 minutes)
- Dash framework
- networkX.read_graphml(): creates graph from selected graphML file.
- Options:
    - Select a graphML file from a pre-populated list of files from a defined folder structured, ordered in date of creation order with most recent file first.
    - Select a layout algorithm
    - Select a centrality algorithm
    - Select an action on click
        - Node table
        - Node neighbourhood – out
        - Node neighbourhood – all
        - Node shortest path
    - Select a node

###Initial_graph_analytics_pipeline.py
Creates a summary analytics file from the sp03 DOTs RDV.
- phase = "pipeline"
- Stage 1 – create_graphs()
- Stage 2 – plot_graph_analytics_summary() - example plot of changes in centrality positions.

###Initial_graph_analytics_plot.py
- Dash framework
- Options:
    - Select an Analytics file from a pre-populated list of files *._analytics_summary.csv
    - Select a plot type:
        - Graph
        - Centralities
    - Select a centrality algorithm

