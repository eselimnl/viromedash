from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df_host_species = pd.read_csv("data/host-species.csv")
df_host_species_nt = pd.read_csv("data/host-species.csv")

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
        html.Div(
            [
                html.H6(
                    children="Select your interest of host",
                ),
            ],
            style={},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="host_dropdown",
                    multi=False,  # inhibit multi selection
                    value="Homo sapiens",
                    options=[
                        {"label": i, "value": i}
                        for i in list(df_host_species.Host.unique())
                    ],
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Specify the sequence type"),
                        dbc.RadioItems(
                            className="body",
                            id="radio2",
                            options=[
                                {"label": "Nucleotide", "value": "nucleotide"},
                                {"label": "Protein", "value": "protein"},
                            ],
                            value="protein",
                            labelStyle={"display": "inline-flex"},
                            inline=True,
                        ),
                    ],
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("Select how many species to be shown in the figure"),
                        dcc.Dropdown(["5", "10", "20"], "10", id="numberofspecies2"),
                    ],
                    lg=6,
                ),
            ]
        ),
        dcc.Graph(id="host-graph"),
        dbc.Button("Download CSV", size="sm", color="info", id="btn_csv_host"),
        dcc.Store(id="df-host", storage_type="local"),
        dcc.Download(id="download-host-data"),
    ]
)


### GRAPH


@callback(
    Output("host-graph", "figure"),
    Output("df-host", "data"),
    # Output("df", "data"),
    [   Input(component_id="radio2", component_property="value"),
        Input(component_id="numberofspecies2", component_property="value"),
        Input(component_id="host_dropdown", component_property="value"),
    ],
)
def update_figure(analysis_type,numberofspecies2, selected_host):
    if analysis_type=="protein":
        df = pd.read_csv("data/host-species.csv")
    else:
        df = pd.read_csv("data/host-species-nt.csv")
    if type(selected_host) != str:

        df = df[df["Host"].isin(selected_host)].sort_values("Count", ascending=False)[
            0 : int(numberofspecies2)
        ]

    else:
        df = df[df["Host"] == selected_host].sort_values("Count", ascending=False)[
            0 : int(numberofspecies2)
        ]

    fig = px.bar(
        df,
        x="Species",
        y="Count",
        color="Species",
        labels={"Species": "Species", "Count": "Count"},
    )

    fig.update_layout(
        title=("Reported viral sequences for " + str(selected_host)),
        transition_duration=500,
        showlegend=False,
    )
    fig.update_yaxes(automargin=True)  # fixes the overlapping of y-axis title and ticks
    fig.update_xaxes(automargin=True)
    # filtered_df = filtered_df.to_dict()  # make it JSON serializable
    df = df.to_dict()
    return fig,df

###DOWNLOADS

# Figure 1
@callback(
    Output("download-host-data", "data"),
    Input("btn_csv_host", "n_clicks"),
    State("df-host", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df_to_download = pd.DataFrame(data)
    return dcc.send_data_frame(
        df_to_download.to_csv, "host.csv", sep=";", index=False
    )