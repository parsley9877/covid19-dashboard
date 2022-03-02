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
from datetime import timedelta
import utils

base_data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/'
data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/01-01-2021.csv'
vac_data_path_base = './data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv'
raw_link = data_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

TEMP_DIR = 'temp_data/'

def read_file(filepath):
    temp_path = TEMP_DIR+filepath.split('/')[-1]
    if os.path.exists(temp_path):
        df = pd.read_csv(temp_path)
    else:
        df = pd.read_csv(filepath)
        os.makedirs(TEMP_DIR,exist_ok=True)
        df.to_csv(temp_path)
    return df


def get_data_by_location(locations, date, value, past_days=30):
    df_range = pd.DataFrame()
    datetime_object = datetime.strptime(date, '%Y-%m-%d')
    start_date = datetime_object + timedelta(days=-past_days)
    end_date = datetime_object
    date_range = pd.date_range(start=start_date, end=end_date, closed='right').strftime('%m-%d-%Y')
    
    #Gather csvs with range of date +-5
    for date_object in date_range:
        # print(date_object)
        file_name = date_object
        file_path = base_data_path + file_name
        file_path = file_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        df = read_file(file_path+'.csv')
        df = utils.filter_unknown_states(df)
        df['state_abbrv'] = df['Province_State'].apply(utils.state_name_to_abbrv)
        df['date'] = date_object
        df_range = pd.concat([df_range, df])
    # print(df_range)
    state_list = locations
        
    selected_df = df_range[df_range['state_abbrv'].isin(state_list)]
    return selected_df[['date','Province_State','state_abbrv', *value]]

if __name__ == '__main__':
    df = get_data_by_location(['AL','CA'],'2020-12-14','Incident_Rate', 30)
    print(df)