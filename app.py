# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from operator import index
from dash import Dash, Input, Output, html, dcc
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc  # apply a bootstrap template
from dash_bootstrap_templates import load_figure_template
from pages import geography, index, species, self_catalogue, baltimore, host, date

# This loads the "cyborg" themed figure template from dash-bootstrap-templates library,
# adds it to plotly.io and makes it the default figure template.
load_figure_template("flatly")

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.FLATLY],
)
server = app.server
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")],
    className="container",
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/self-catalogue":
        return self_catalogue.layout
    if pathname == "/species":
        return species.layout
    if pathname == "/geography":
        return geography.layout
    if pathname == "/date":
        return date.layout
    if pathname == "/host":
        return host.layout
    if pathname == "/baltimore":
        return baltimore.layout
    else:
        return index.layout
    # You could also return a 404 "URL not found" page here


if __name__ == "__main__":
    app.run_server(debug=True)
