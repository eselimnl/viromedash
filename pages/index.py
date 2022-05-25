from operator import index
from dash import Dash, Input, Output, html, dcc, State, dash_table, callback
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template

layout = html.Div(
    [  ###NAVBAR
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
            brand="METAViz",
            brand_href="/",
            color="#2196f3",
            dark=True,
        ),
        html.Div(
            [
                html.H1(children="Viral Sequence Catalogue"),
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(
                                children="Visual catalogue for the viral sequences resources from"
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
                html.Div(
                    [
                        dcc.Link(
                            dbc.Button(
                                "Species/genus/family", color="info", outline=True
                            ),
                            href="/species",
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Host and environmental source",
                                color="info",
                                outline=True,
                            ),
                            href="/host",
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Country and geographic region",
                                color="info",
                                outline=True,
                            ),
                            href="/geography",
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Collection and release date",
                                color="info",
                                outline=True,
                            ),
                            href="/date",
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Baltimore Classification", color="info", outline=True
                            ),
                            href="/baltimore",
                        ),
                        dcc.Link(
                            dbc.Button("Self catalogue", color="info", outline=True),
                            href="/self-catalogue",
                        ),
                    ]
                ),
            ],
            className="mid_center",
        ),
    ]
)
