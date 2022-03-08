# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, Input, Output
import plotly.express as px
import pandas as pd
from dash import html
from dash import dcc
import pandas as pd


app = Dash(__name__)
server = app.server
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv('data/year-cumulative-taxonomy.csv')

app.layout = html.Div(className="h1",children=[
    html.H1(children='Catalog Visualizer'),
    html.Div(className="body",children='''
        Dash: A web application framework for your data.
    '''),
dcc.RadioItems(className="body", id ='radio1',
                               options =
                   [{'label': 'Cumulative', 'value': 'cumulative'},
                   {'label': 'One-Year',   'value': 'one-year'},],
                               value ='cumulative',
                             labelStyle ={'display': 'inline-flex'}                                     
                              ),
    dcc.Graph(
        id='graph-family'),
    html.Div([
    dcc.Dropdown(multi=True, id='pandas-dropdown-1', value=df.Taxonomy[0], options=[  
        {'label': i, 'value': i} for i in list(df.Taxonomy.unique())])
])
])

@app.callback(
    Output('graph-family', 'figure'),
    Input('pandas-dropdown-1', 'value'),
    [Input(component_id='radio1', component_property='value')]
)

def update_figure(selected_family, value):
    if value == 'cumulative':
        if type(selected_family)!=str:
            filtered_df = df[df['Taxonomy'].isin(selected_family) ]
        else:
            filtered_df = df[df['Taxonomy']==selected_family]

        fig = px.line(filtered_df, x="Collection_Date", y="Cumulative_Count", color='Taxonomy',symbol='Taxonomy', labels={
                     "Collection_Date": "Collection Date",
                     "Cumulative_Count": "Cumulative protein sequences",
                     "Taxonomy": "Taxonomy"
                 })

        fig.update_layout(transition_duration=500)

        return fig
    else:
        if type(selected_family)!=str:
            filtered_df = df[df['Taxonomy'].isin(selected_family) ]
        else:
            filtered_df = df[df['Taxonomy']==selected_family]

        fig = px.line(filtered_df, x="Collection_Date", y="Count", color='Taxonomy', symbol='Taxonomy', labels={
                     "Collection_Date": "Collection Date",
                     "Count": "Annual protein sequences",
                     "Taxonomy": "Taxonomy"
                 },)

        fig.update_layout(transition_duration=500)

        return fig       
if __name__ == '__main__':
    app.run_server(debug=True)