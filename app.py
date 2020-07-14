import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.logger.info('hillooo')

# Get data - covid info from NYT and zip code to county code (FIP) mapping from HUD
# HUD: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
# NYT: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv

zips_and_fips = pd.read_csv('zip-to-fips.csv')
og_data = pd.read_csv('nyt-covid-7-8.csv')
# Note that ~30% of counties are missing from NYT covid data!

def zip_to_fips(zipcode):
    
    # fip = zips_and_fips[zips_and_fips['ZIP'] == zipcode].iloc[0]['COUNTY']

    # fip = zips_and_fips.loc[zips_and_fips.ZIP == zipcode,'COUNTY'].values[0]
    
    if zipcode:
        zipcode = int(zipcode)
    

    fip = zips_and_fips.loc[zips_and_fips.ZIP == zipcode,'COUNTY'].values[0]
    print(fip)

    # fip = zips_and_fips[zips_and_fips.ZIP == zipcode].COUNTY.item()

    # zips_dict = zips_and_fips.set_index('ZIP').T.to_dict('list')

    # mydict = {
    #     '94022' : 6075,
    #     '94114' : 6075
    # }

    # return 6075
    return fip

def get_county_data(my_fips):
    my_data = og_data[og_data.fips == my_fips]
    
    county_name = my_data['county'].unique()
    
    if len(county_name) > 1:
        raise ValueError('something is wrong - found more than one matching county')
    
    my_filtered_data = my_data[['date', 'cases', 'deaths']]
    
    
    return {
        'county': county_name[0],
        'data': my_filtered_data
    }

def zip_to_data(zip_code):
    """Returns dict with two values: 'county' has the name of the county, 'data' has a df with
    date, cases to date, and deaths to date"""
    
    fips = zip_to_fips(zip_code)
    data = get_county_data(fips)
    
    return data

zip_code = 94114

result = zip_to_data(zip_code)
county_name = result['county']
county_data = result['data']





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


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='COVID-19 cases reported to date'),

    html.Div(children='''
        Enter your zip code.
    '''),

    dcc.Input(id='input', value='', type='text'),

    html.Div(id='output-graph'),

    # dcc.Graph(
    #     id='example-graph',
    #     figure={
    #         'data': [
    #             {
    #                 'x': county_data.index,
    #                 'y': county_data.cases,
    #                 'type': 'line',
    #                 'name': county_name
    #             },
    #         ],
    #         'layout': {
    #             'title': county_name + ' County'
    #         }
    #     }
    # )
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_value(input_data):
    
    result = zip_to_data(input_data)
    county_name = result['county']
    county_data = result['data'] 

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {
                    'x': county_data.date,
                    'y': county_data.cases,
                    'type': 'line',
                    'name': county_name
                },
            ],
            'layout': {
                'title': county_name + ' County'
            }
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True)