import json
import numpy as np
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


def get_data_by_location(locations, date, value, past_days=30, next_days=0):
    df_range = pd.DataFrame()
    datetime_object = datetime.strptime(date, '%Y-%m-%d')
    start_date = datetime_object + timedelta(days=-past_days)
    end_date = datetime_object + timedelta(days=next_days)
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

    df1 = read_file(vac_data_path_base)
    df_new = []
    date_range1 = pd.date_range(start=start_date, end=end_date, closed='right').strftime('%m/%d/%Y')
    for date in date_range1:
            
            for location in locations:
                
                    temp_df = df1.loc[(df1['Date']==date) & (df1['Location']==location)]
                    if not temp_df.empty:
                        temp_df = temp_df.loc[:,['Distributed']].values
                        df_new.append(temp_df[0][0])
                    else:
                        df_new.append(np.NaN)
                        
                        
    #df2 = pd.DataFrame(df_new)
    #df2.rename(columns = {0:'Distributed'},inplace=True)
    selected_df.insert(selected_df.shape[1],'Administered',df_new)
    
    return selected_df[['date','Province_State','state_abbrv', *value]]

if __name__ == '__main__':
    df = get_data_by_location(['CA'],'2020-12-25',['Incident_Rate','Administered'], 30)
    print(df)