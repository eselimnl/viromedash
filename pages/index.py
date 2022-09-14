from operator import index
from turtle import color, position
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template

layout = html.Div(
    [  ###NAVBAR
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("HOME", href="/")),
                dbc.NavItem(dbc.NavLink("USER MANUAL", href="https://viromedash.readthedocs.io")),
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
                html.H1(children="Global Virome Sequence Metadata Visualizer"),
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(
                                children="A visualizer for viral sequence metadata from the records in"
                            ),
                            lg=10,
                        ),
                        dbc.Col(
                            dbc.Badge(
                                "NCBI Virus",
                                className="ms-1",
                                color="#2196f3",
                                pill=True,
                                href="https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/",
                            ),
                            lg=2,
                        ),
                    ]
                ),
            ],
            className="mid_center",
        ),

dbc.Col([
     dbc.Row([
        dbc.CardGroup([
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Species/Genus/Family", className="card-title"),
                    html.P(
                        "Find out the number of reports over years, host-organisms, geographic locations and isolation-sources of a viral species/genus/family.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="success", className="mt-auto"
                    ), href="/species"),
                ]
            ), style={"height": "24rem"},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Host species", className="card-title"),
                    html.P(
                        "Find out the reported viral species infecting a host-organism.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="warning", className="mt-auto"
                    ),href="/host"),
                ]
            ), #color="danger", inverse=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Collection date", className="card-title"),
                    html.P(
                        "Find out the reported viral species in a specific time interval.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="danger", className="mt-auto"
                    ), href="/date"),
                ]
            ))
     ])
        ]),
         dbc.Row([
                dbc.CardGroup([
                   
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Country/continent", className="card-title"),
                    html.P(
                        "Find out the reported viral species in a country/continent.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="primary", className="mt-auto"
                    ), href="/geography"),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Baltimore Classification", className="card-title"),
                    html.P(
                        "Sunburst chart to abundance of reported viral sequences based on the Baltimore classification.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="secondary", className="mt-auto"),
                    href="/baltimore"),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Self catalogue", className="card-title"),
                    html.P(
                        "This tool helps you to find out/visualize the metadata of uploaded viral sequences.",
                        className="card-text",
                    ),
                    dcc.Link(
                    dbc.Button(
                        "Click here", color="light", className="mt-auto"
                    ), href="/self-catalogue"),
                ]
            ), style={"height": "24rem"},
        )])
    ])
  ]),
  html.Div(
            [
                 dbc.Row(html.H5(children="Last update: May 2022"))], style={"color":"red"}),
])
