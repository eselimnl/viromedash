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

df = pd.read_csv("data/geography_species.csv").dropna(
    subset=["Geographical_Region"]
)  # lets remove NA values

layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("HOME", href="/")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Filters", header=True),
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
                    label="Filters",
                ),
            ],
            brand="METAViz",
            brand_href="/",
            color="#2196f3",
            dark=True,
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H6(
                            children="Select your interest of contry or continents",
                        ),
                    ],
                    style={},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="geography_dropdown",
                            multi=False,  # inhibit multi selection
                            value="Australia",
                            options=[
                                {"label": i, "value": i}
                                for i in list(df.Geographical_Region.unique())
                            ],
                        )
                    ]
                ),
                dcc.Graph(id="geography-graph"),
            ]
        ),
    ]
)


@callback(
    Output("geography-graph", "figure"),
    # Output("df", "data"),
    [Input(component_id="geography_dropdown", component_property="value")],
)
def update_figure(selected_country):
    df = pd.read_csv("data/geography_species.csv").dropna(
        subset=["Geographical_Region"]
    )
    if type(selected_country) != str:

        df = df[df["Geographical_Region"].isin(selected_country)].sort_values(
            "Count", ascending=False
        )[0:10]
    else:
        df = df[df["Geographical_Region"] == selected_country].sort_values(
            "Count", ascending=False
        )[0:10]

    fig = px.scatter(
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
