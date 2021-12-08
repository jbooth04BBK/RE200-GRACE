import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from common_routines import *

# get list of graphml file in folder including sub folder
##### start defining app data

dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                          project_path="Z:\\Projects\\Research\\0200-GRACE")

analytics_files = get_files_by_extension(gml_project_path, '.csv', suffix="_analytics_summary")

default_analytic_plot_types = analytic_plot_types[0]

dd_centralities = centralities
default_centrality = dd_centralities[0]

max_elements = 10000

# end of global definitions #######################################

def controls_table(controls):
    # return html.Div(children=[control[1] for control in controls])

    table_rows = []

    for control in controls:

        table_row = []
        if len(control[0]) > 0:
            cell = html.Td(children=control[0], colSpan='1')
            table_row.append(cell)
            cell = html.Td(children=control[1], colSpan='1')
            table_row.append(cell)
            cell = html.Td(colSpan='3')
            table_row.append(cell)
        else:
            cell = html.Td(children=control[1], colSpan='5')
            table_row.append(cell)

        table_rows.append(html.Tr(table_row))

    table = html.Table(id="page_controls", className='controls-table', children=
    # Header
    [html.Tr([html.Th(html.Td(children="Controls", colSpan='5'))])] + table_rows
                       )

    return html.Div(children=table)


### Start DASH app
app = dash.Dash(__name__)

controls = [["Select an analytics file:",
    dcc.Dropdown(
        id="dropdown-files",
        options=[{"label": x, "value": x} for x in analytics_files],
        value=analytics_files[0],
    )
             ]]

controls.append(["Select a plot type:",
    dcc.Dropdown(
        id="dropdown-plot-types",
        options=[{"label": x, "value": x} for x in analytic_plot_types],
        value= default_analytic_plot_types
    )
                ])

controls.append(["Select a centrality algorithm:",
    dcc.Dropdown(
        id="dropdown-centrality",
        options=[{"label": x, "value": x} for x in dd_centralities],
        value=default_centrality
    )
                ])

controls.append(["",
    dcc.Graph(id='plot-analytics'),
                ])

app.layout = html.Div([
    html.H1("Graph Analytics plot"),
    html.H3(f"File Browser: {gml_project_path}"),
    controls_table(controls),
    html.H5("Done")
                    ])


@app.callback(
                Output("plot-analytics", "figure"),
                Input("dropdown-files", "value"),
                Input("dropdown-plot-types", "value"),
                Input("dropdown-centrality", "value"),
                Input("plot-analytics", "clickData")
)
def process_selected_options(file_name, analytic_plot_type, centrality, plot_clickdata):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    centrality = centrality if centrality is not None else default_centrality

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

    ###############################################
    # What parameter values to I have to work with?
    ###############################################

    log_debug("file_name: {0}, analytic plot type: {1}, centrality: {2}".format(file_name, analytic_plot_type, centrality))

    analytics_file_name = file_name[2:len(file_name)]

    inpFilePath = os.path.join(gml_project_path, analytics_file_name)

    log_debug(f"Reading file: {inpFilePath}")
    df_all_analytic_data = pd.read_csv(inpFilePath)

    #############
    # Set up plot
    #############

    fig = plot_graph_analytics_summary(df_all_analytic_data, analytic_plot_type=analytic_plot_type, centrality=centrality)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)