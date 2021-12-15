# RE200-GRACE

### What is this Phase 1 trying to achieve?
Understanding the fundamentals of graph analytics with emphasis on example EPR data.
- A better understanding on how Graph Creation and Analytics works.
- Key differences between labelled property graph and a semantic graph.
- A deep dive literature review based on terms derived from the initial sprints

[Project README](../README.md)

## Main scripts
### initial_rdv_visualisation.py
Creates dummy RDV's if the required RDV's doen't exist.
- phase = "check_rdvs"
- Stage 1 – sub_project = “sp01”
- Stage 2 – sub_project = “sp02”
- Stage 3 – sub_project = “sp03”
- check_rdvs()
- create_rdv_visualisation()

### initial_graph_creation.py
Creates initial set of graphML files used by initial_graphml_plot.
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

### initial_graph_analytics.py
Creates initial set of graph analytics stored in JSON files used by initial_grapml_plot.
- Phase = “analytics”
- Stage 1, 3, and 5 – create_graph_from_rdvs() for sub_projects sp01, sp02 and sp03
- Stage 7 - create_dots_test_analytics_dt_graph() creates graph of test data, stored in files with sub_project = ‘test01’.
- Stage 2, 4, 6, and 8 – process_graph_analytics for sub projects sp01, sp02, sp03 and test01. Results saved in both YAML and JSON file formats.

### initial_graphml_plot.py
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

### initial_graph_analytics_pipeline.py (20 minutes)
Creates a summary analytics file from the sp03 DOTs RDV.
- phase = "pipeline"
- Stage 1 – create_graphs()
- Stage 2 – plot_graph_analytics_summary() - example plot of changes in centrality positions.

### initial_graph_analytics_plot.py
- Dash framework
- Options:
    - Select an Analytics file from a pre-populated list of files *._analytics_summary.csv
    - Select a plot type:
        - Graph
        - Centralities
    - Select a centrality algorithm

