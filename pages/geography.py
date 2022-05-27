from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# DATA

df = pd.read_csv("data/geography_species_with_dates.csv").dropna(
    subset=["Region"]
)  # lets remove NA values

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
                html.Div(
                    [
                        html.H6(
                            children="Select your interest of a continent or country",
                        ),
                    ],
                    style={},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="geography_dropdown",
                            multi=False,  # inhibit multi selection
                            value="Europa",
                            options=[
                                {"label": i, "value": i}
                                for i in list(df.Region.unique())
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
                        dbc.Label("Select how many contries to be shown in the figure"),
                        dcc.Dropdown(["5", "10", "20"], "10", id="numberofcountries"),
                    ],
                    lg=6,
                ),
            ]
        ),
                dbc.Label("Specify the time interval to filter the sequences based on collection date"),
                # RANGE SLIDER
                dcc.RangeSlider(
                    df[
                        "Collection_Date"
                    ].min(),  # min year in overall dataset, not in the selected species
                    2022,  # max year is always 2022
                    id="linear-range-slider",
                    marks=None,
                    value=[df["Collection_Date"].min(), df["Collection_Date"].max()],
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                # GRAPH
                dcc.Graph(id="geography-graph"),
            ]
        ),
    ]
)


### GRAPH


@callback(
    Output("geography-graph", "figure"),
    # Output("df", "data"),
    [
        Input(component_id="geography_dropdown", component_property="value"),
        Input("linear-range-slider", "value"),
        Input(component_id="numberofcountries", component_property="value"),
    ],
)
def update_figure(selected_country, time, numberOfcoutry):
    df = pd.read_csv("data/geography_species_with_dates.csv").dropna(subset=["Region"])
    if type(selected_country) != str:

        df = df[df["Region"].isin(selected_country)]
        df = (
            df.loc[df["Collection_Date"].between(time[0], time[1])]
            .groupby(by=["Species", "Region"])[["Species", "Region", "Count"]]
            .sum("Count")
            .reset_index()
            .sort_values("Count", ascending=False)[0:int(numberOfcoutry)]
        )
    else:
        df = df[df["Region"] == selected_country]
        df = (
            df.loc[df["Collection_Date"].between(time[0], time[1])]
            .groupby(by=["Species", "Region"])[["Species", "Region", "Count"]]
            .sum("Count")
            .reset_index()
            .sort_values("Count", ascending=False)[0:int(numberOfcoutry)]
        )

    fig = px.bar(
        df,
        x="Species",
        y="Count",
        color="Species",
        labels={"Species": "Species", "Count": "Count"},
    )

    fig.update_layout(
        title=("Reported viral sequences for " + str(selected_country)),
        transition_duration=500,
        showlegend=False,
    )
    fig.update_yaxes(automargin=True)  # fixes the overlapping of y-axis title and ticks
    # filtered_df = filtered_df.to_dict()  # make it JSON serializable
    return fig
