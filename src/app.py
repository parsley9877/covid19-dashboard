from dash import dcc
from dash import html
import dash
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import requests
import json
import os
from datetime import date
from datetime import datetime

import utils

base_data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/'
data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/01-01-2021.csv'
raw_link = data_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
df = pd.read_csv(raw_link)
df = utils.filter_unknown_states(df)


state_map = dcc.Graph(id='state_map', style={'width':'100%'})
map_div = html.Div(children=[state_map])


#Datepicker

dp = dcc.DatePickerSingle(
    min_date_allowed=date(2020, 4, 12),
    max_date_allowed=date(2022, 2, 23),
    month_format='MMM Do, YY',
    placeholder='MMM Do, YY',
    date=date(2020,12, 4),
    id='datepicker'
)

dp_div = html.Div(children=[html.A('Please pick a date  '), dp], className='dp-div')

# Dropdown

services = ['Confirmed', 'Deaths', 'Incident_Rate', 'Total_Test_Results', 'Case_Fatality_Ratio', 'Testing_Rate', 'Hospitalization_Rate']
red_scheme = ['Confirmed', 'Deaths', 'Incident_Rate', 'Case_Fatality_Ratio', 'Hospitalization_Rate']
blue_schemes = ['Testing_Rate', 'Total_Test_Results']
drop_down = dcc.Dropdown(services, 'Incident_Rate', id='dropdown')
dd_div = html.Div(children=[html.A('What to Visualize:  '), drop_down], className='dd-div')




# Title
header = html.Div(id='header', style={'backgroundColor':'#051833'}, children=[
            html.H1(children='COVID-19 Data Analysis Dashboard', className='main-title')
])

# Buttons

but1 = html.Div(id='but-1', children=html.A('Incidents Map', id='tab-1-nav', className='nav-buttons', href='tab1'))
but2 = html.Div(id='but-2', children=html.A('Data Analysis', id='tab-2-nav', href='tab2', className='nav-buttons'))
but3 = html.Div(id='but-3', children=html.A('Prediction', id='tab-3-nav', href='tab3', className='nav-buttons'))


# Navbar
navbar = html.Div(id='navbar', className='top-nav' ,children=[
        but1,
        but2,
        but3,
])

first_row_tab_1 = html.Div(children=[dp_div, dd_div], className='first-row-tab1')

tab_1 = html.Div(className='tab-1', children=[first_row_tab_1, map_div])
tab_2 = html.Div(className='tab-2', children=[html.A('DUMMY TAB 2 (TO BE DONE)', id='dummy-id')])
tab_3 = html.Div(className='tab-3', children=[html.A('DUMMY TAB 3 (TO BE DONE)', id='dummy-id')])


current_tab = html.Div(id='current-tab', children=[tab_1])


app = dash.Dash(__name__, suppress_callback_exceptions=False)
app.title = 'COVID-19 Dashboard'
app.layout = html.Div(id='layout', children=[dcc.Location(id='url', refresh=False), header, html.Div(children=[navbar, current_tab])])


# Callbacks

# Navbar callbacks

@app.callback([dash.dependencies.Output('current-tab', 'children')],
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/tab1':
        return [tab_1]
    elif pathname == '/tab2':
        return [tab_2]
    elif pathname == '/tab3':
        return [tab_3]
    else:
        return [tab_1]


@app.callback(
    dash.dependencies.Output('state_map', 'figure'),
    [dash.dependencies.Input('url', 'pathname'), dash.dependencies.Input('datepicker', 'date'), dash.dependencies.Input('dropdown', 'value')])
def update_state_map(url, date, value):
    datetime_object = datetime.strptime(date, '%Y-%m-%d')
    file_name = '{:02d}-{:02d}-{:04d}'.format(datetime_object.month, datetime_object.day, datetime_object.year)
    file_path = base_data_path + file_name
    file_path = file_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    df = pd.read_csv(file_path+'.csv')
    df = utils.filter_unknown_states(df)
    df['state_abbrv'] = df['Province_State'].apply(utils.state_name_to_abbrv)
    print(value)
    print(date)
    if value in red_scheme:
        fig = go.Figure(data=go.Choropleth(
            locations=df['state_abbrv'], # Spatial coordinates
            z = df[value].astype(float), # Data to be color-coded
            locationmode = 'USA-states', # set of locations match entries in `locations`
            colorscale = 'Reds',
        ))
    else:
        fig = go.Figure(data=go.Choropleth(
            locations=df['state_abbrv'],  # Spatial coordinates
            z=df[value].astype(float),  # Data to be color-coded
            locationmode='USA-states',  # set of locations match entries in `locations`
            colorscale='Blues',
        ))


    fig.update_layout(
        title_text = value,
        geo_scope='usa', # limite map scope to USA
    )

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=True,
    )

    return fig






if __name__ == '__main__':
    app.run_server(debug=True)



