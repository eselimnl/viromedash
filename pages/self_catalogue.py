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
import dash_bio as dashbio
from dash_bio.utils import protein_reader
from Bio import Entrez, SeqIO

layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("HOME", href="/")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Filters", header=True),
                        dbc.DropdownMenuItem("Species/Genus/Family", href="/species"),
                        dbc.DropdownMenuItem("Page 3", href="#"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Filters",
                ),
            ],
            brand="METAViz",
            brand_href="/",
            color="info",
            dark=True,
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H6(
                            children="Upload an accession list (.txt or .csv) or a fasta file to visualize sequence metadata",
                        ),
                    ],
                    style={},
                ),
                dbc.RadioItems(
                    className="body",
                    id="radio2",
                    options=[
                        {"label": "Nucleotide", "value": "nucleotide"},
                        {"label": "Protein", "value": "protein"},
                    ],
                    value="protein",
                    labelStyle={"display": "inline-flex"},
                ),
                dbc.Button(
                    "Download Sample Input",
                    href="/static/sample_data.txt",
                    download="sample_list.txt",
                    external_link=True,
                    color="info",
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

        return ids, html.Div(
            [
                html.Button(id="submit-button", children="Create Graph"),
                dbc.Spinner(html.Div(id="loading-output")),
            ]
        )
    else:
        return [{}]


# LOADING
@callback(
    Output("loading-output", "children"),
    [Input("submit-button", "n_clicks")],
    State("df-stored", "data"),
)
def load_output(n, data):
    if n is None:
        return f"Output not reloaded yet"


@callback(
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
    Entrez.max_tries = 10
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


@callback(
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
            title=("Figure 1. Timeline of reported sequences"), transition_duration=500
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
            title=("Figure 2. Timeline of reported sequences"), transition_duration=500
        )
        a.sort_values(by="Count", ascending=False, inplace=True)
        list_countries = a.Countries.to_list()
        new_strings_countries = (
            []
        )  # replace gaps " " with "_", otherwise we recieve an error with multiple words

        for string in list_countries:
            new_string = string.replace(" ", "_")
            new_strings_countries.append(new_string)
        sc_fig_2 = px.bar(
            a[0:10],
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
        )
        sc_fig_2.update_yaxes(categoryorder="total ascending")

        b.sort_values(by="Count", ascending=False, inplace=True)
        list_hosts = b.Hosts.to_list()
        new_strings_hosts = []
        for string in list_hosts:
            new_string = string.replace(" ", "_")
            new_strings_hosts.append(new_string)
        sc_fig_3 = px.bar(
            b[0:10],
            x="Count",
            color="Hosts",
            y=new_strings_hosts[0:10],
            orientation="h",
            labels={"Count": "Total number", "y": "Hosts"},
            hover_name=new_strings_hosts[0:10],
            hover_data=["Count"],  # lets tweak the hover values
        )

        sc_fig_3.update_layout(
            title=("Figure 4. Top 10 Hosts"), transition_duration=500, showlegend=False
        )
        sc_fig_3.update_yaxes(categoryorder="total ascending")

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
                ),
                dcc.Graph(figure=sc_fig_2),
                dcc.Graph(figure=sc_fig_3),
            ]
        )


# download stored-df


@callback(
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
