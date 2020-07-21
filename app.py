import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)

server = app.server

# Get data - covid info from NYT and zip code to county code (FIP) mapping from HUD
# HUD: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
# NYT: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv

zips_and_fips = pd.read_csv('zip-to-fips.csv')
og_data = pd.read_csv('nyt-covid-data.csv')
# Note that ~30% of counties are missing from NYT covid data!

# Add new column to df with <county name> County, <state name>
og_data['fullname'] = og_data['county'] + ' County, ' + og_data['state']

# Add new column for daily case count diff
og_data['cases_diff'] = og_data['cases'].diff()

# create list of county and state name dicts for input dropdown
all_fullnames = []
for name in og_data['fullname'].unique():
    dict_entry = {'label': name, 'value': name}
    all_fullnames.append(dict_entry)


def get_county_data_from_name(fullname):
    """using fullname from input, pull data from og_data and return a new df with date, cases, deaths for that county"""
    my_data = og_data[og_data.fullname == fullname]
    
    my_filtered_data = my_data[['date', 'cases', 'deaths']].copy()
    
#     Add column for cases diff per day
    my_filtered_data['cases_diff'] = my_filtered_data['cases'].diff()
    
    return my_filtered_data


def get_more_details_from_name(fullname):
    """get date of most recent entry, number of cases as of that date"""
    my_data = og_data[og_data.fullname == fullname]

    most_recent_date = my_data['date'].max()
#     deaths = my_data[my_data.date == most_recent_date]['deaths'].item()
    cases = my_data[my_data.date == most_recent_date]['cases'].item()

    return(most_recent_date, cases)


app.layout = html.Div(children=[


    html.H6(children='Choose your county'),

    dcc.Dropdown(
        id='input',
        options= all_fullnames,
        multi=False
    ),

    html.Div(id='output-graph'),

    html.Div(id='last-updated'),

    html.Div(id='source',
        children=['Data courtesy of The New York Times, based on reports from state and local health agencies.']
    )

 ])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_value(input_data):
    
    result = get_county_data_from_name(input_data)

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {
                    'x': result.date,
                    'y': result.cases_diff,
                    'type': 'bar',
                    'name': 'Covid-19 cases in ' + input_data
                },
            ],
            'layout': {
                'title': 'Covid-19 cases in ' + input_data,
                'plot_bgcolor': 'light-gray',
                'paper_bgcolor': 'light-gray'
            }
        }
    )

@app.callback(
    Output(component_id='last-updated', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_other_values(input_data):

    most_recent_date, total_cases = get_more_details_from_name(input_data)

    text = 'last updated ' + most_recent_date 

    return text



if __name__ == '__main__':
    app.run_server(debug=True)