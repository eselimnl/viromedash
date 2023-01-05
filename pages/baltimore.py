from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


df = pd.read_csv("data/sunburst_500.csv")

fig = px.sunburst(
    df,
    path=["baltimore", "Family", "Genus", "Species"],
    color="baltimore",
    hover_data=['Count'],
    maxdepth=10,
    width=1200,
    height=1200)


fig.update_layout(
    margin=dict(l=20, r=20, t=1, b=1))

layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("HOME", href="/")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("SEARCH", header=True),
                        dbc.DropdownMenuItem("Species/Genus/Family", href="/species"),
                        dbc.DropdownMenuItem(
                            "Host and environmental source", href="/host"
                        ),
                        dbc.DropdownMenuItem(
                            "Country and geographic region", href="/geography"
                        ),
                        dbc.DropdownMenuItem(
                            "Collection and release date", href="/date"
                        ),
                        dbc.DropdownMenuItem(
                            "Baltimore Classification", href="/baltimore"
                        ),
                        dbc.DropdownMenuItem(
                            "Make a self catalogue", href="/self-catalogue"
                        ),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="SEARCH",
                ),
            ],
            brand="VIROMEdash",
            brand_href="/",
            color="#2196f3",
            dark=True,
        ),
        dbc.Alert("Sunburst chart based on baltimore classification of viruses. Only includes the species that has at least reported over 500 sequences.", color="primary"),
        dbc.Button("Download CSV", size="sm", color="info", id="btn_csv_baltimore"),
        dcc.Graph(figure=fig),
        #dcc.Store(id="df-date", storage_type="local"),
        dcc.Download(id="download-baltimore-csv"),
    ]
)


### DOWNLOAD

@callback(
    Output("download-baltimore-csv", "data"),
    Input("btn_csv_baltimore", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "baltimore.csv")
