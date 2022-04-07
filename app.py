# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, Input, Output
import plotly.express as px
import pandas as pd
from dash import html
from dash import dcc
import pandas as pd
import plotly.graph_objects as go

app = Dash(__name__)
server = app.server
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv("data/year-cumulative-taxonomy.csv")
df_1 = pd.read_csv("data/descriptive-taxonomy.csv")
df_2 = pd.read_csv("data/country-cumulative-taxonomy.csv")
df_3 = pd.read_csv("data/host-taxonomy.csv")
df_4 = pd.read_csv("data/isolation_source-taxonomy.csv")

app.layout = html.Div(
    children=[
        html.H1(children="NCBI Virus Visualizer"),
        html.Div(
            className="body mid",
            children="""
        A web application to explore more about virus of interest.
    """,
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
                            value=df.Taxonomy[0],
                            options=[
                                {"label": i, "value": i}
                                for i in list(df.Taxonomy.unique())
                            ],
                        )
                    ],
                ),
                dcc.RadioItems(
                    className="body",
                    id="radio2",
                    options=[
                        {"label": "Nucleotide", "value": "Nucleotide"},
                        {"label": "Protein", "value": "Protein"},
                    ],
                    value="Protein",
                    labelStyle={"display": "inline-flex"},
                ),
            ]
        ),
        dcc.Graph(id="box-1"),
        dcc.RadioItems(
            className="body",
            id="radio1",
            options=[
                {"label": "Cumulative", "value": "cumulative"},
                {"label": "One-Year", "value": "one-year"},
            ],
            value="cumulative",
            labelStyle={"display": "inline-flex"},
        ),
        dcc.Graph(id="graph-year"),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="graph-country")],
                    style={"display": "inline-block"},
                ),
                html.Div(
                    [dcc.Graph(id="graph-host")],
                    style={"display": "inline-block", "float": "right"},
                ),
            ]
        ),
        dcc.Graph(id="graph-isolation_source"),
    ],
)


@app.callback(Output("box-1", "figure"), Input("pandas-dropdown-1", "value"))
def card(selected_family):
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
                        "title": {"text": "Number of protein sequences"},
                        "mode": "number",
                    }
                ]
            }
        },
    )
    return box_1


@app.callback(
    Output("graph-year", "figure"),
    Input("pandas-dropdown-1", "value"),
    [Input(component_id="radio1", component_property="value")],
)
def update_figure(selected_family, value):
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
                "Cumulative_Count": "Cumulative protein sequences",
                "Taxonomy": "Taxonomy",
            },
        )

        fig.update_layout(
            title=("Timeline of reported viral sequences for " + str(selected_family)),
            transition_duration=500,
            paper_bgcolor="rgb(248, 248, 255)",
            plot_bgcolor="rgb(248, 248, 255)",
        )

        return fig
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

        return fig


@app.callback(
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
            "Count": "Cumulative protein sequences",
        },
    )

    fig_2.update_layout(
        title=("Top 10 Countries reported viral sequences for " + str(selected_family)),
        transition_duration=500,
        showlegend=False,
        paper_bgcolor="rgb(249, 249, 249)",
        plot_bgcolor="rgb(249, 249, 249)",
    )

    return fig_2


@app.callback(
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
        labels={
            "Count": "Cumulative protein sequences",
        },
    )

    fig_3.update_layout(
        title=("Top 10 Hosts for " + str(selected_family)),
        transition_duration=500,
        showlegend=False,
        paper_bgcolor="rgb(249, 249, 249)",
        plot_bgcolor="rgb(249, 249, 249)",
    )
    fig_3.update_xaxes(autorange="reversed")
    fig_3.update_yaxes(side="right")
    return fig_3


@app.callback(
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
        paper_bgcolor="rgb(249, 249, 249)",
        plot_bgcolor="rgb(249, 249, 249)",
    )
    return fig_4


if __name__ == "__main__":
    app.run_server(debug=True)
