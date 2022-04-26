from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import io


# DATA

df = pd.read_csv("data/year-cumulative-taxonomy_x2.csv")  # keep this for drop down menu

layout = html.Div(
    children=[
        dbc.NavbarSimple(  ###FIRST NAVBAR
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
                            children="Select one or more of your interests of viral species or genus or family",
                        ),
                    ],
                    style={},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            multi=True,
                            id="pandas-dropdown-1",
                            value="All Species",
                            options=[
                                {"label": i, "value": i}
                                for i in list(df.Taxonomy.unique())
                            ],
                        )
                    ],
                ),
                dbc.Label("Sequence Type"),
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
            ]
        ),
        dcc.Graph(id="box-1"),
        dbc.Label("Parameters"),
        dbc.RadioItems(
            className="body",
            id="radio1",
            options=[
                {"label": "Cumulative", "value": "cumulative"},
                {"label": "One-Year", "value": "one-year"},
            ],
            value="cumulative",
            labelStyle={"display": "inline-flex"},
            inline=True,
        ),
        dbc.Button("Download CSV", size="sm", color="info", id="btn_csv"),
        dcc.Download(id="download-species-year"),
        dcc.Store(id="df-species-year", storage_type="local"),
        dcc.Graph(id="graph-year"),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="graph-country")], lg=6),
                dbc.Col(
                    [dcc.Graph(id="graph-host")],
                    lg=6,
                ),
            ]
        ),
        dcc.Graph(id="graph-isolation_source"),
    ],
)


@callback(
    Output("box-1", "figure"),
    [Input(component_id="radio2", component_property="value")],
    Input("pandas-dropdown-1", "value"),
)
def card(prot_nuc, selected_family):
    df_1 = pd.read_csv("data/descriptive-taxonomy_x2.csv")
    if str(prot_nuc) == "protein":
        df_1.rename(
            columns={"Count_x": "Count"},
            inplace=True,
        )
    else:
        df_1 = pd.read_csv("data/year-cumulative-taxonomy_x2.csv")
        df_1.rename(
            columns={"Count_y": "Count"},
            inplace=True,
        )
    if type(selected_family) != str:
        filtered_df_1 = df_1[df_1["Taxonomy"].isin(selected_family)]
    else:
        filtered_df_1 = df_1[df_1["Taxonomy"] == selected_family]
    box_1 = go.Figure(
        go.Indicator(
            mode="number",
            value=filtered_df_1["Count"].sum(),
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    box_1.update_layout(
        height=300,  # Added parameter
        template={
            "data": {
                "indicator": [
                    {
                        "title": {
                            "text": "Number of " + str(prot_nuc) + " sequences found:"
                        },
                        "mode": "number",
                    }
                ]
            }
        },
    )
    return box_1


### FIGURE 1


@callback(
    Output("graph-year", "figure"),
    Output("df-species-year", "data"),
    [Input(component_id="radio2", component_property="value")],
    Input("pandas-dropdown-1", "value"),
    [Input(component_id="radio1", component_property="value")],
)
def update_figure(hey, selected_family, value):
    if str(hey) == "protein":
        df = pd.read_csv("data/year-cumulative-taxonomy_x2.csv")
        df.rename(
            columns={"Cumulative_Count_x": "Cumulative_Count", "Count_x": "Count"},
            inplace=True,
        )
    else:
        df = pd.read_csv("data/year-cumulative-taxonomy_x2.csv")
        df.rename(
            columns={"Cumulative_Count_y": "Cumulative_Count", "Count_y": "Count"},
            inplace=True,
        )
    if value == "cumulative":
        if type(selected_family) != str:
            filtered_df = df[df["Taxonomy"].isin(selected_family)]
        else:
            filtered_df = df[df["Taxonomy"] == selected_family]

        fig = px.line(
            filtered_df,
            x="Collection_Date",
            y="Cumulative_Count",
            color="Taxonomy",
            symbol="Taxonomy",
            labels={
                "Collection_Date": "Collection Date",
                "Cumulative_Count": "Cumulative number of protein sequences",
                "Taxonomy": "Taxonomy",
            },
        )

        fig.update_layout(
            title=("Timeline of reported viral sequences for " + str(selected_family)),
            transition_duration=500,
        )
        fig.update_yaxes(
            automargin=True
        )  # fixes the overlapping of y-axis title and ticks
        filtered_df = filtered_df.to_dict()  # make it JSON serializable
        return fig, filtered_df
    else:
        if type(selected_family) != str:
            filtered_df = df[df["Taxonomy"].isin(selected_family)]
        else:
            filtered_df = df[df["Taxonomy"] == selected_family]

        fig = px.line(
            filtered_df,
            x="Collection_Date",
            y="Count",
            color="Taxonomy",
            symbol="Taxonomy",
            labels={
                "Collection_Date": "Collection Date",
                "Count": "Annual protein sequences",
                "Taxonomy": "Taxonomy",
            },
        )

        fig.update_layout(transition_duration=500)
        filtered_df = filtered_df.to_dict()  # make it JSON serializable
        return fig, filtered_df


@callback(
    Output("graph-country", "figure"),
    Input("pandas-dropdown-1", "value"),
    prevent_initial_call=False,
)
def figure_2(selected_family):
    if type(selected_family) != str:
        filtered_df_2 = df_2[df_2["Taxonomy"].isin(selected_family)].sort_values(
            by="Count", ascending=False
        )[0:10]
    else:
        filtered_df_2 = df_2[df_2["Taxonomy"] == selected_family].sort_values(
            by="Count", ascending=False
        )[0:10]

    fig_2 = px.bar(
        filtered_df_2,
        x="Count",
        y="Country",
        color="Country",
        orientation="h",
        labels={
            "Count": "Cumulative number of protein sequences",
        },
    )

    fig_2.update_layout(
        title=("Top 10 Countries reported viral sequences for " + str(selected_family)),
        transition_duration=500,
        showlegend=False,
    )

    return fig_2


@callback(
    Output("graph-host", "figure"),
    Input("pandas-dropdown-1", "value"),
    prevent_initial_call=False,
)
def figure_3(selected_family):
    if type(selected_family) != str:
        filtered_df_3 = df_3[df_3["Taxonomy"].isin(selected_family)].sort_values(
            by="Count", ascending=False
        )[0:10]
    else:
        filtered_df_3 = df_3[df_3["Taxonomy"] == selected_family].sort_values(
            by="Count", ascending=False
        )[0:10]

    fig_3 = px.bar(
        filtered_df_3,
        x="Count",
        y="Host",
        color="Host",
        orientation="h",
        labels={"Count": "Cumulative number of protein sequences"},
    )

    fig_3.update_layout(
        title=("Top 10 Hosts for " + str(selected_family)),
        transition_duration=500,
        showlegend=False,
    )
    fig_3.update_xaxes(autorange="reversed")
    fig_3.update_yaxes(side="right")
    return fig_3


@callback(
    Output("graph-isolation_source", "figure"),
    Input("pandas-dropdown-1", "value"),
    prevent_initial_call=False,
)
def figure_4(selected_family):
    if type(selected_family) != str:
        filtered_df_4 = df_4[df_4["Taxonomy"].isin(selected_family)].sort_values(
            by="Count", ascending=False
        )[0:10]
    else:
        filtered_df_4 = df_4[df_4["Taxonomy"] == selected_family][0:10]

    fig_4 = px.pie(
        filtered_df_4,
        values=filtered_df_4["Count"],
        names=filtered_df_4["Isolation_Source"],
        hole=0.3,
    )

    fig_4.update_layout(
        title=("Top 10 Isolation Source for " + str(selected_family)),
        transition_duration=500,
        showlegend=False,
    )
    fig_4.update_traces(textposition="inside", textinfo="percent+label")
    return fig_4


###DOWNLOADS

# Figure 1
@callback(
    Output("download-species-year", "data"),
    Input("btn_csv", "n_clicks"),
    State("df-species-year", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df_to_download = pd.DataFrame(data)
    return dcc.send_data_frame(
        df_to_download.to_csv, "species-year.csv", sep=";", index=False
    )
