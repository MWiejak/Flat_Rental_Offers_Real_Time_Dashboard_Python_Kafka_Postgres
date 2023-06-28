from dash import Dash, html, dcc, callback, Output, Input, no_update
from time import sleep
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import webbrowser
from connect import connect

# Create PostgreSQL database connection using connect.py script:
print("Establishing connection to PostgreSQL server...")

try:    
    sleep(10)
    conn = connect()
    cursor = conn.cursor()
    print("Connection established!")
    
except Exception as e:
    print("Error while trying to establish PostgreSQL server connection")
    print(str(e))

cursor.execute("SELECT * FROM flats;")
data = cursor.fetchall()
cursor.close()

df = pd.DataFrame(data, columns=["url","location","date","size","price"])

# df = pd.read_csv('./data.csv')
# df = df[df['size'] != -1]

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(

    children=[
        dbc.NavbarSimple(brand='Olx Data Visualization', color='dark', dark=True),
        html.Div(
            className='container mt-5 mb-5',
            children=[
                html.Div(id='summary-table-container'),
                dcc.Dropdown(
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': loc, 'value': loc} for loc in df.location.unique()],
                    value='All',
                    id='dropdown-selection',
                    className='mb-2',
                    style={'background-color': '#dcebf7'}
                ),
                dbc.Card([dcc.Graph(id='graph-content')], className='mb-2'),
                html.Div(
                    className='row',
                    children=[
                        dbc.Card([dcc.Graph(id='histogram-ads-count')], className='col-sm-6'),
                        dbc.Card([dcc.Graph(id='histogram-price-dist')], className='col-sm-6')
                    ]
                ),
                html.Div(id='scatter-redirect')
            ]
        )
    ]
)

@callback(
    Output('summary-table-container', 'children'),
    Input('dropdown-selection', 'value')
)

def update_summary_table(value):
    dff = df if value == 'All' else df[df.location == value]

    table = dbc.Table.from_dataframe(
        pd.DataFrame({
            'Total Advertisements': [len(dff.index)],
            'Min Size': [dff['size'].min()],
            'Max Size': [dff['size'].max()],
            'Min Price': [dff['price'].min()],
            'Max Price': [dff['price'].max()]
        }),
        striped=True,
        bordered=True,
        hover=True,
        id='summary-table'
    )

    return table

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df if value =='All' else df[df.location==value]
    fig = px.scatter(dff, x='size', y='price', title="Housing price vs size", custom_data='url')
    fig.update_layout(xaxis=dict(title='Size(sq.m)'), yaxis=dict(title='Price(zlotys)'))
    return fig

@app.callback(
    Output('scatter-redirect', 'children'),
    Input('graph-content', 'clickData')
)

def redirect_to_url(clickData):
    if clickData is not None:
        url = clickData['points'][0]['customdata'][0].strip()
        webbrowser.open_new_tab(url)
    return no_update

@callback(
    Output('histogram-ads-count', 'figure'),
    Input('dropdown-selection', 'value')
)

def update_hist_ads_count(value):
    dff = df if value =='All' else df[df.location==value]
    fig = px.histogram(dff, x='date', nbins=20, title='Number of ads per day')
    fig.update_layout(xaxis=dict(title='date'), yaxis=dict(title='Number of posts'))
    fig.update_traces(marker_color='red')
    return fig

@callback(
    Output('histogram-price-dist', 'figure'),
    Input('dropdown-selection', 'value')
)

def update_hist_price_dist(value):
    dff = df if value =='All' else df[df.location==value]
    fig = px.histogram(dff, x='price',  title='Price distribution')
    fig.update_layout(xaxis=dict(title='Amount(zlotys)'), yaxis=dict(title='Price range frequency'))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)