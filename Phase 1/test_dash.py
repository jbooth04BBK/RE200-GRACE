import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os
import json

def create_graph():
    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    return fig

def read_csv():

    df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

    return df

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

# Dash app
app = dash.Dash(__name__)

colors = {
    'background': '#D6FBDF',
    'text': '#467651'
}

fig = create_graph()
df = read_csv()
current_directory = os.getcwd()

app.layout = html.Div([

    html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash', className="app-header--title")
        ]
    ),

    html.Div(
        children=html.Div([
            html.H5('Overview'),
            # html.H5(current_directory),
            # html.Img(src='/assets/DRIVE_Logo.png'),
            html.Div('''
               This is an example of a simple Dash app with
               local, customized CSS.
           ''')
        ])
    ),

    html.Div([
        html.Button('Button 1', id='btn-1'),
        html.Button('Button 2', id='btn-2'),
        html.Button('Button 3', id='btn-3'),
        html.Div(id='container')
    ]),

    html.Div(style={'backgroundColor': colors['background']}, children=[

        html.H1(children='Dash Test',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        html.Div(children='''
            Dash: A web application framework for your data.
        ''', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        html.H4(children='US Agriculture Exports (2011)',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        generate_table(df)

    ]),

    html.Div(children=[
        html.Div(children=[
            html.Label('Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value='MTL'
            ),

            html.Br(),
            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value=['MTL', 'SF'],
                multi=True
            ),

            html.Br(),
            html.Label('Radio Items'),
            dcc.RadioItems(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value='MTL'
            ),
        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Checkboxes'),
            dcc.Checklist(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value=['MTL', 'SF']
            ),

            html.Br(),
            html.Label('Text Input'),
            dcc.Input(value='HTML', type='text'),

            html.Br(),
            html.Label('Slider'),
            dcc.Slider(
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
                value=5,
            ),

        ], style={'padding': 10, 'flex': 1})

    ], style={'display': 'flex', 'flex-direction': 'row'})

])

@app.callback(Output('container', 'children'),
              Input('btn-1', 'n_clicks'),
              Input('btn-2', 'n_clicks'),
              Input('btn-3', 'n_clicks'))
def display(btn1, btn2, btn3):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    ctx_msg = json.dumps({
        'states': ctx.states,
        'triggered': ctx.triggered,
        'inputs': ctx.inputs
    }, indent=2)

    return html.Div([
        html.Table([
            html.Tr([html.Th('Button 1'),
                     html.Th('Button 2'),
                     html.Th('Button 3'),
                     html.Th('Most Recent Click')]),
            html.Tr([html.Td(btn1 or 0),
                     html.Td(btn2 or 0),
                     html.Td(btn3 or 0),
                     html.Td(button_id)])
        ]),
        html.Pre(ctx_msg)
    ])


if __name__ == '__main__':
    app.run_server(debug=True)

