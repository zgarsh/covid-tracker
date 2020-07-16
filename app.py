import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Get data - covid info from NYT and zip code to county code (FIP) mapping from HUD
# HUD: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
# NYT: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv

zips_and_fips = pd.read_csv('zip-to-fips.csv')
og_data = pd.read_csv('nyt-covid-7-14.csv')
# Note that ~30% of counties are missing from NYT covid data!
og_data['fullname'] = og_data['county'] + ' County, ' + og_data['state']

# create list of county and state names for input dropdown
all_fullnames = []
for name in og_data['fullname'].unique():
    dict_entry = {'label': name, 'value': name}
    all_fullnames.append(dict_entry)


def get_county_data_from_name(fullname):
    my_data = og_data[og_data.fullname == fullname]
    
    county_name = my_data['county'].unique()
    
    if len(county_name) > 1:
        raise ValueError('something is wrong - found more than one matching county')
    
    my_filtered_data = my_data[['date', 'cases', 'deaths']]
    
    
    return my_filtered_data


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app.layout = html.Div(children=[
    html.H2(children='COVID-19 cases reported to date'),

    # html.Div(children='''
    #     Enter your county.
    # '''),

    dcc.Dropdown(
        id='input',
        options= all_fullnames,
        multi=False
    ),

    html.Div(id='output-graph'),

    html.Div(children='''
        Data courtesy of The New York Times, based on reports from state and local health agencies. 
    '''),

    dcc.Link('NYT Covid tracking page', href='https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html.')
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_value(input_data):
    
    result = get_county_data_from_name(input_data)
    # county_name = result['county']
    # county_data = result['data'] 

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {
                    'x': result.date,
                    'y': result.cases,
                    'type': 'line',
                    'name': input_data
                },
            ],
            'layout': {
                'title': input_data
            }
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True)