# RE200-GRACE

[Introduction](#introduction)

[Phase 1](#phase-1)

[Code General](#code-general)

## Introduction
The GOSH DRE/CIRP project for John Booth's PhD.

### What is my PhD trying to achieve?
To create a timely way to compare patient’s progress using routinely collected EPR data. The current EPR is extraordinary at giving clinicians a wealth of data on a particular patient in one interface, but how do you compare your patient to others?

Could we build a recommendation system similar to Amazon or Netflix where we graph the interaction between patients and events to be able to ‘recommend’ a prospective event?

Currently it is envisaged that the PhD will be split into 3 broad phases:

- Phase 1 - What are graphs?
    - Analytics
    - Types
        - Knowledge
        - Property
        - Semantic
    - Databases
- Phase 2 - What are graphs good for in clinical informatics?
    - Using EPR data.
- Phase 3 - How do you communicate graphs?
    - To a non-data scientist i.e. a clinicians.

## Phase 1

Understanding the fundamentals of graph analytics with emphasis on example EPR data- [ReadMe](Phase%201/README.md) - 

## Code General
### Packages used:
Anaconda base installation plus:
- colour==0.1.5
- dash==2.0.0
- dash-core-components==2.0.0
- dash-html-components==2.0.0
- dash-table==5.0.0
- matplotlib==3.4.3
- networkx==2.6.3
- numpy==1.21.3
- pandas==1.3.4
- plotly==5.3.1
- PyYAML==5.4.1
- XlsxWriter==3.0.1

### Project path
The default path for the project is: "Z:\Projects\Research\0200-GRACE"

If the path does not exist then the default is the current directory that the code is running in. This path can be overridden by a command line parameter:

    Python Initial_rdv_visualisation.py  -path "H:\Projects\Research\0200-GRACE"

Sub folders are created:
        dex_project_path = project_path + "\\DataExtraction"
        csv_project_path = dex_project_path + "\\CSVs"
        gml_project_path = dex_project_path + "\\GMLs"

### Stages
Stages are used to run chunks of code during development to explorer different aspects of the phase in development.
Any script that uses stages the required list of stages to run can be passed in as an argument:

    Python Initial_rdv_visualisation.py –stages 1 2 3

If no argument is passed then stage 1 will be run.

### Output file creation:
- f"{sub_project}_{phase]_{stage}_{file type}.{extension}"

