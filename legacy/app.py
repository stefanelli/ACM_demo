import base64
import json
import os
import time
from dash import Dash, html, dcc, Input, Output, State, no_update
import dash_ag_grid as dag
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from interpolation import cubic_spline, tenor_to_date
from constants import inv_name_map, resample_frequency, tab1_doc, tab2_doc

load_dotenv()
SERVER_HOSTNAME = os.getenv("SERVER_HOSTNAME")
HTTP_PATH = os.getenv("HTTP_PATH")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

DB_NAME = "default"
TABLE_NAME = "simple_data"

app = Dash(__name__)
app.title = "ACM"
server = app.server

df = pd.DataFrame({
        'Tenor':     ['ON', '1M' , '3M' , '6M' , '1Y' , '2Y' , '3Y' , '5Y' , '7Y' , '10Y', '15Y', '20Y', '30Y'],
        'Zero Rate': [4.43, 4.496, 4.448, 4.442, 4.087, 4.328, 4.321, 4.419, 4.502, 4.778, 5.085, 5.287, 4.589]
    })

table = dag.AgGrid(
    id='zero-table',
    rowData=df.to_dict('records'),
    columnDefs=[
        {
            "field": 'Tenor',
            "editable": False,
            'resizable': True,
        },
        {
            "field": 'Zero Rate',
            "type": 'numericColumn',
            "editable": True,
            'resizable': True,
        }],
    defaultColDef={
        'flex': 1,
        'minWidth': 100,
        'resizable': True,
        'editable': True,
    },
    dashGridOptions={
        'rowSelection': 'single',
        'animateRows': True,
        "undoRedoCellEditing": True,
        "undoRedoCellEditingLimit": 20,
    },
    style={'height': '600px', 'width': '25%'}
)


app.layout = html.Div([
    html.H1("ACM Demo"),
    dcc.Tabs(id="tabs-parent", value='tab-0', children=[
        dcc.Tab(label='Yield Curve GUI', value='tab-1', children=[
            tab1_doc,
            html.Div([
                html.H2("Yield curve marking GUI"),
                html.Div(id='table_container' , children=[
                    table,
                    html.Div(id="editing-grid"),
                ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px'}),
                html.Button('Reset', id='reset_button', n_clicks=0),
            ]),
        ]),
        dcc.Tab(label='Databricks Example', value='tab-2', children=[
            html.Div(id="Databricks", children=[
                html.H2("Databricks Example"),
                tab2_doc,
                dcc.Dropdown(list(inv_name_map.keys()), '', id='prod-dropdown'),
                dcc.Dropdown(resample_frequency, '', id='time-dropdown'),
                html.Button('Create plot', id='jobs-api-button', n_clicks=0),
                dcc.Loading(id="loading-1", children=[
                    html.Div(id="selection-plot",children="No graph loaded yet",),
                ], type="default"),
            ])
        ]),
    ]),
    ])

@app.callback(
    Output('table_container', 'children'),
    Input('reset_button','n_clicks'),
    prevent_initial_call=True,
)
def reset(_):
    return [table, html.Div(id="editing-grid"),]

@app.callback(
    Output('editing-grid', 'children'),
    Input('zero-table', 'cellValueChanged'),
    State('zero-table', 'rowData'),
)
def update(_, rows):
    updated_df = pd.DataFrame(rows)
    interpolated = cubic_spline(updated_df, np.linspace(0, 30, 1001))
    fig = px.line(interpolated, x='Tenor', y='Zero Rate', title='Yield Curve')
    fig.add_scatter(x=[tenor_to_date(tenor) for tenor in updated_df['Tenor']], y=updated_df['Zero Rate'], mode='markers' ,marker=dict(color='red', size=8))
    fig.update_layout(
        title='Interpolated Yield Curve with reference points',
        xaxis_title='Tenor',
        yaxis_title='Zero Rate',
        showlegend=False
    )
    result = dcc.Graph(figure=fig, responsive=True, style={'width': '70vh', 'height': '40vh'})
    return result


@app.callback(
    Output('selection-plot', 'children'),
    State('prod-dropdown', 'value'),
    State('time-dropdown', 'value'),
    Input("jobs-api-button", "n_clicks"),
    prevent_initial_callback=True,
)
def invoke_jobs_api(product, freq, n_clicks):
    # print(f"prod: {prod}, freq: {freq}, n_clicks: {n_clicks}")
    if n_clicks == 0:
        print("No button clicked yet")
        return no_update
    prod = inv_name_map[product]
    w = WorkspaceClient(host=f"https://{SERVER_HOSTNAME}", token=ACCESS_TOKEN)
    parameters_to_cluster = {'instrument': prod, 'resample_freq': freq}
    notebook_path = "/Workspace/Users/salvatore.stefanelli@gmail.com/ACM_demo"
    create_job = w.jobs.create(
        name=f"sdk-{time.time_ns()}",
        tasks=[
            jobs.Task(
                task_key="Run-Notebook",
                notebook_task=jobs.NotebookTask(
                notebook_path=notebook_path,
                base_parameters=parameters_to_cluster,
                ),
            )
        ]
    )
    w.jobs.run_now(create_job.job_id).result()

    fig_bytes = w.dbfs.read("/tmp/fig1.json")
    content = fig_bytes.data
    decoded_content = base64.b64decode(content).decode('utf-8')

    w.jobs.delete(job_id=create_job.job_id)

    fig_data = json.loads(decoded_content.replace('heatmapgl', 'heatmap')) # hack to workaround the deprecation of heatmapgl in Plotly 6.0

    fig = go.Figure(fig_data)


    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True)
