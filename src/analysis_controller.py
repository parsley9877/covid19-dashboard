import numpy as np
from pandas import DataFrame

from dataloader import get_data_by_location
from scipy import stats

def get_rate(data : DataFrame, values):
    for value in values:    
        value_data = data[value].to_numpy()
        value_data = (value_data[1:]-value_data[:-1])/value_data[:-1]*100
        data[value].iloc[1:] = value_data
    # print(value_data)
    return data.iloc[1:]

def get_correlation(data_1, data_2):
    return stats.pearsonr(data_1, data_2)

def get_rate_by_loc(locations, date, values, past_day):
    df = get_data_by_location(locations,date,values, past_day)
    res = {}
    res['rate'] = get_rate(df, values)
    for i in range(len(values)-1):
        res[f'corr_{values[i]}-{values[i+1]}'] = get_correlation(df[values[i]].to_numpy(),df[values[i+1]].to_numpy())
    return res

if __name__ == '__main__':
    values = ['Incident_Rate', 'Deaths']
    locations = ['CA']
    date = '2020-12-14'
    past_days = 10
    res = get_rate_by_loc(locations, date, values, past_days)
    print(res)
    # df = get_data_by_location(['CA'],'2020-12-14',value, 30)
    # print(df)
    # print(get_rate(df, value))
    # print(get_correlation(df[value[0]].to_numpy(),df[value[1]].to_numpy()))