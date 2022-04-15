# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, Input, Output, html, dcc, State, dash_table
from dash.exceptions import PreventUpdate
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import dash_bio as dashbio
from dash_bio.utils import protein_reader
from Bio import Entrez, SeqIO

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv("data/year-cumulative-taxonomy_x2.csv")  # keep this for drop down menu
df_2 = pd.read_csv("data/country-cumulative-taxonomy.csv")
df_3 = pd.read_csv("data/host-taxonomy.csv")
df_4 = pd.read_csv("data/isolation_source-taxonomy.csv")


#############################################
##                 LAYOUT                  ##
##                SECTION                  ##
#############################################

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

page_2_layout = html.Div(
    children=[
        html.H1(children="METAViz: Sequence Metadata Visualizer"),
        html.Div(
            className="body mid",
            children="A web application to visualize metadata of a given list of sequences.",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Link("Go to METAViz", href="/"),
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
            ],
            style={"background-color": "rgb(249, 249, 249)"},
        ),
        dcc.Graph(id="graph-isolation_source"),
    ],
)

page_1_layout = html.Div(
    [
        html.H1(children="METAViz: Sequence Metadata Visualizer"),
        html.Div(
            className="body mid",
            children="A web application to visualize metadata of a given list of sequences.",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Link(
                            "Go to an application of a METAViz: NCBI Virus Catalogue",
                            href="/page-2",
                        ),
                        html.H6(
                            children="Upload an accession list (.txt or .csv) or a fasta file to visualize sequence metadata",
                        ),
                    ],
                    style={},
                ),
                dcc.RadioItems(
                    className="body",
                    id="radio2",
                    options=[
                        {"label": "Nucleotide", "value": "nucleotide"},
                        {"label": "Protein", "value": "protein"},
                    ],
                    value="protein",
                    labelStyle={"display": "inline-flex"},
                ),
            ]
        ),
        dcc.Store(id="stored-data", storage_type="local"),
        dcc.Store(id="df-stored", storage_type="local"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "50%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Don't allow multiple files to be uploaded
            multiple=True,
        ),
        html.Div(id="output-data-upload"),
        html.Div(id="process-outputs"),
    ]
)

# Update the index
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page-2":
        return page_2_layout
    else:
        return page_1_layout
    # You could also return a 404 "URL not found" page here


@app.callback(
    Output("box-1", "figure"),
    [Input(component_id="radio2", component_property="value")],
    Input("pandas-dropdown-1", "value"),
)
def card(prot_nuc, selected_family):
    df_1 = pd.read_csv("data/descriptive-taxonomy_x2.csv")
    if str(prot_nuc) == "Protein":
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
                        "title": {"text": "Number of " + str(prot_nuc) + " sequences"},
                        "mode": "number",
                    }
                ]
            }
        },
    )
    return box_1


#############################################
##                 PAGE 2                  ##
##                SECTION                  ##
#############################################


def parse_contents(contents, filename, date):
    if contents and filename:
        contents, filename = contents[0], filename[0]

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            if "csv" in filename:
                # Assume that the user uploaded a CSV file
                ids = pd.read_csv(io.StringIO(decoded.decode("utf-8")), names=["ID"])[
                    "ID"
                ].tolist()
                # remove the version "." if exist
                ids = [i.split(".")[0] if type(i) == str else str(i) for i in ids]
            elif "txt" in filename:
                # Assume that the user uploaded an txt file
                ids = pd.read_csv(io.StringIO(decoded.decode("utf-8")), names=["ID"])[
                    "ID"
                ].tolist()
                ids = [i.split(".")[0] if type(i) == str else str(i) for i in ids]
            # ADD Fasta
            elif "fasta" in filename:
                ids = []
                for seq_record in SeqIO.parse(
                    io.StringIO(decoded.decode("utf-8")), "fasta"
                ):
                    ids.append(seq_record.id)
            else:
                # Assume that it is something similar to csv (especially ncbi seq)
                ids = pd.read_csv(io.StringIO(decoded.decode("utf-8")), names=["ID"])[
                    "ID"
                ].tolist()
                ids = [i.split(".")[0] if type(i) == str else str(i) for i in ids]
        except Exception as e:
            print(e)
            return html.Div(["There was an error processing this file."])

        return ids, html.Div([html.Button(id="submit-button", children="Create Graph")])
    else:
        return [{}]


@app.callback(
    [Output("output-data-upload", "children"), Output("stored-data", "data")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
    prevent_initial_call=True,
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if not list_of_contents:
        raise PreventUpdate

    if list_of_contents is not None:
        ids, element = parse_contents(list_of_contents, list_of_names, list_of_dates)

        children = [element]

        return children, ids


##############DATA PROCESSING################


def data_processing(ids, molecule_type):
    Entrez.email = "eselimnl@gmail.com"
    Entrez.tool = "viralcatalogue"
    Entrez.api_key = "075788ecc8b13ce90ce89db8a7f18810d609"
    handle = Entrez.efetch(
        db=molecule_type, id=ids, rettype="gb", retmode="xml"
    )  # db to set protein or nucleotide from user input
    response = Entrez.read(handle)
    handle.close()

    def extract_countries(entry):  # Parse the entries to get the country
        sources = [
            feature
            for feature in entry["GBSeq_feature-table"]
            if feature["GBFeature_key"] == "source"
        ]

        for source in sources:
            qualifiers = [
                qual
                for qual in source["GBFeature_quals"]
                if qual["GBQualifier_name"] == "country"
            ]

            for qualifier in qualifiers:
                yield qualifier["GBQualifier_value"]

    countries = []
    for entry in response:
        accession = entry["GBSeq_primary-accession"]
        for country in extract_countries(entry):
            if ":" in country:
                countries.append([accession, country.split(":").pop(0)])
            else:
                countries.append([accession, country])
    df_countries = pd.DataFrame(countries, columns=["Accessions", "Countries"])
    grouped_countries = (
        df_countries.groupby(["Countries"]).size().reset_index(name="Count")
    )

    def extract_host(entry):  # Parse the entries to get the host
        sources = [
            feature
            for feature in entry["GBSeq_feature-table"]
            if feature["GBFeature_key"] == "source"
        ]

        for source in sources:
            qualifiers = [
                qual
                for qual in source["GBFeature_quals"]
                if qual["GBQualifier_name"] == "host"
            ]

            for qualifier in qualifiers:
                yield qualifier["GBQualifier_value"]

    hosts = []
    for entry in response:
        accession = entry["GBSeq_primary-accession"]
        for host in extract_host(entry):
            if ";" in host:  # removes latter attributes if found
                hosts.append([accession, host.split(";").pop(0)])
            elif "," in host:
                hosts.append([accession, host.split(",").pop(0)])
            else:
                hosts.append([accession, host])
    df_hosts = pd.DataFrame(hosts, columns=["Accessions", "Hosts"])
    grouped_hosts = df_hosts.groupby(["Hosts"]).size().reset_index(name="Count")

    def extract_date(entry):  # Parse the entries to get the collection date
        sources = [
            feature
            for feature in entry["GBSeq_feature-table"]
            if feature["GBFeature_key"] == "source"
        ]

        for source in sources:
            qualifiers = [
                qual
                for qual in source["GBFeature_quals"]
                if qual["GBQualifier_name"] == "collection_date"
            ]

            for qualifier in qualifiers:
                yield qualifier["GBQualifier_value"]

    dates = []
    for entry in response:
        accession = entry["GBSeq_primary-accession"]
        for date in extract_date(entry):
            dates.append([accession, str(date)])

    df_dates = pd.DataFrame(dates, columns=["Accessions", "Dates"])
    df_dates["Dates"] = pd.to_datetime(
        df_dates["Dates"], errors="coerce"
    ).dt.year  # parses only years
    grouped_dates = df_dates.groupby(["Dates"]).size().reset_index(name="Count")

    df = (
        pd.merge(
            pd.merge(df_countries, df_hosts, on="Accessions", how="outer"),
            df_dates,
            on="Accessions",
        )
        .fillna("Unknown")
        .to_dict()
    )  # outer to include "unknowns"
    return grouped_countries, grouped_hosts, grouped_dates, df


@app.callback(
    [Output("df-stored", "data"), Output("process-outputs", "children")],
    Input("submit-button", "n_clicks"),
    State(component_id="radio2", component_property="value"),
    State("stored-data", "data"),
)
def processed_data(n, molecule_type, ids):
    if n is None:
        raise PreventUpdate
    else:
        a, b, c, d = data_processing(ids, molecule_type)
        df = pd.DataFrame(d)
        c.sort_values("Dates", inplace=True)
        c["Cumsum"] = c["Count"].cumsum()

        sc_fig_1 = px.line(
            c,
            x="Dates",
            y="Count",
            markers=True,
            labels={
                "Dates": "Collection Date",
                "Count": "Per year number of sequences",
            },
            hover_name="Dates",
            hover_data=["Count"],  # lets tweak the hover values
        )

        sc_fig_1.update_layout(
            title=("Figure 1. Timeline of reported sequences"),
            transition_duration=500,
            paper_bgcolor="rgb(248, 248, 255)",
            plot_bgcolor="rgb(248, 248, 255)",
        )
        sc_fig_1_2 = px.line(
            c,
            x="Dates",
            y="Cumsum",
            markers=True,
            labels={
                "Dates": "Collection Date",
                "Cumsum": "Cumulative number of sequences",
            },
        )

        sc_fig_1_2.update_layout(
            title=("Figure 2. Timeline of reported sequences"),
            transition_duration=500,
            paper_bgcolor="rgb(248, 248, 255)",
            plot_bgcolor="rgb(248, 248, 255)",
        )

        list_countries = a.Countries.to_list()
        new_strings_countries = (
            []
        )  # replace gaps " " with "_", otherwise we recieve an error with multiple words
        for string in list_countries:
            new_string = string.replace(" ", "_")
            new_strings_countries.append(new_string)
        sc_fig_2 = px.bar(
            a[0:10].sort_values(by="Count", ascending=True),
            x="Count",
            y=new_strings_countries[0:10],
            color="Countries",
            orientation="h",
            labels={"Count": "Total number", "y": "Countries"},
            hover_name=new_strings_countries[0:10],
            hover_data=["Count"],  # lets tweak the hover values
        )

        sc_fig_2.update_layout(
            title=("Figure 3. Top 10 Countries"),
            transition_duration=500,
            showlegend=False,
            paper_bgcolor="rgb(249, 249, 249)",
            plot_bgcolor="rgb(249, 249, 249)",
        )
        list_hosts = b.Hosts.to_list()
        new_strings_hosts = []
        for string in list_hosts:
            new_string = string.replace(" ", "_")
            new_strings_hosts.append(new_string)
        sc_fig_3 = px.bar(
            b[0:10].sort_values(by="Count", ascending=True),
            x="Count",
            color="Hosts",
            y=new_strings_hosts[0:10],
            orientation="h",
            labels={"Count": "Total number", "y": "Hosts"},
            hover_name=new_strings_hosts[0:10],
            hover_data=["Count"],  # lets tweak the hover values
        )

        sc_fig_3.update_layout(
            title=("Figure 4. Top 10 Hosts"),
            transition_duration=500,
            showlegend=False,
            paper_bgcolor="rgb(253, 250, 237)",
            plot_bgcolor="rgb(253, 250, 237)",
        )

        # print(graphs)
        return d, html.Div(
            [
                html.Button("Download CSV", id="btn_csv"),
                dcc.Download(id="download-dataframe-csv"),
                dash_table.DataTable(
                    df.to_dict("records"),
                    [{"name": i, "id": i} for i in df.columns],
                    filter_action="native",
                    page_action="native",
                    page_size=10,
                    style_table={
                        "height": 300,
                        "overflowY": "scroll",
                    },  # vertical scroll
                    style_data={
                        "width": "150px",
                        "minWidth": "150px",
                        "maxWidth": "150px",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                    },
                    css=[
                        {
                            "selector": "table",
                            "rule": "table-layout: fixed",  # note - this does not work with fixed_rows
                        }
                    ],
                ),
                html.Div(
                    [
                        html.Div([dcc.Graph(figure=sc_fig_1)], className="six columns"),
                        html.Div(
                            [dcc.Graph(figure=sc_fig_1_2)], className="six columns"
                        ),
                    ],
                    className="row",
                    style={"background-color": "rgb(249, 249, 249)"},
                ),
                dcc.Graph(figure=sc_fig_2),
                dcc.Graph(figure=sc_fig_3),
            ]
        )


# download stored-df


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("df-stored", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df_to_download = pd.DataFrame(data)
    return dcc.send_data_frame(
        df_to_download.to_csv, "metaframe.csv", sep=";", index=False
    )


#############################################
##               PAGE-2  GRAPH             ##
##                SECTION                  ##
#############################################


#############################################
##               PAGE-1  GRAPH             ##
##                SECTION                  ##
#############################################


@app.callback(
    Output("graph-year", "figure"),
    [Input(component_id="radio2", component_property="value")],
    Input("pandas-dropdown-1", "value"),
    [Input(component_id="radio1", component_property="value")],
)
def update_figure(hey, selected_family, value):
    if str(hey) == "Protein":
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
            "Count": "Cumulative number of protein sequences",
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
        labels={"Count": "Cumulative number of protein sequences"},
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
        paper_bgcolor="rgb(207, 226, 243)",
        plot_bgcolor="rgb(207, 226, 243)",
    )
    return fig_4


if __name__ == "__main__":
    app.run_server(debug=True)
