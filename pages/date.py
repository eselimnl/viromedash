from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df_prot = pd.read_csv("data/year_species_aa.csv")
df_nt = pd.read_csv("data/year_species_nt.csv")


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
        html.H6("Specify the time interval to plot viral species"),
        # RANGE SLIDER
        dcc.RangeSlider(
            df_prot[
                "Collection_Date"
            ].min(),  # min year in overall dataset, not in the selected species
            2022,  # max year is always 2022
            id="date-range-slider",
            marks=None,
            value=[df_prot["Collection_Date"].min(), 2022],
            step=1,
            tooltip={"placement": "bottom", "always_visible": True},
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
                        dbc.Label("Select how many species to be shown"),
                        dcc.Dropdown(["5", "10", "20"], "10", id="numberofspecies"),
                    ],
                    lg=6,
                ),
            ]
        ),
        dcc.Graph(id="date-species-graph"),
        dbc.Button("Download CSV", size="sm", color="info", id="btn_csv_date"),
        dcc.Store(id="df-date", storage_type="local"),
        dcc.Download(id="download-date-data"),
    ]
)

### GRAPH


@callback(
    Output("date-species-graph", "figure"),
    Output("df-date", "data"),
    [Input(component_id="radio2", component_property="value"),
        Input(component_id="numberofspecies", component_property="value"),
        Input("date-range-slider", "value"),
    ],
)
def update_figure(analysis_type, speciesnumber, time):
    if analysis_type == "protein":
        df = pd.read_csv("data/year_species_aa.csv")
    else: 
        df = pd.read_csv("data/year_species_nt.csv")
    df = df.loc[df["Collection_Date"].between(time[0], time[1])]
    df_stored = (
        df.groupby(by=["Species"])[["Species", "Count"]]
        .sum("Count")
        .reset_index()
        .sort_values("Count", ascending=False)[0 : int(speciesnumber)]
    )

    fig = px.bar(
        df_stored,
        x="Species",
        y="Count",
        color="Species",
        labels={"Species": "Species", "Count": "Count"},
    )

    fig.update_layout(
        title=("Reported viral sequences for"),
        transition_duration=500,
        showlegend=False,
    )
    fig.update_yaxes(automargin=True)  # fixes the overlapping of y-axis title and ticks
    # filtered_df = filtered_df.to_dict()  # make it JSON serializable
    df_store = df.to_dict()
    return fig, df_store

###DOWNLOADS

# Figure 1
@callback(
    Output("download-date-data", "data"),
    Input("btn_csv_date", "n_clicks"),
    State("df-date", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df_to_download = pd.DataFrame(data)
    return dcc.send_data_frame(
        df_to_download.to_csv, "date.csv", sep=";", index=False
    )