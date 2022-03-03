import numpy as np
from pandas import DataFrame

from dataloader import get_data_by_location
from scipy import stats

import utils

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

def get_top_regions(date, values, past_day, num_regions):
    # locations = utils.us_states.values()
    locations = [utils.state_name_to_abbrv(loc) for loc in utils.us_states.keys() if loc not in utils.unknown_states]
    res = {}
    rate_vals = []
    for i,loc in enumerate(locations):
        # print(loc)
        df = get_data_by_location([loc], date, values, past_day)
        # print(df.shape)
        if df.shape[0] < 1:
            continue
        df = get_rate(df, values)
        res[i] = df
        rate_vals.append(np.mean(df[values[0]].to_numpy()))
    top_rate = np.argsort(rate_vals)
    final_res = {}
    for i in range(1,num_regions+1):
        # print(rate_vals[top_rate[-i]])
        final_res[i] = res[top_rate[-i]]
    return final_res

if __name__ == '__main__':
    values = ['Incident_Rate', 'Deaths']
    locations = ['CA']
    date = '2020-12-14'
    past_days = 5
    # res = get_rate_by_loc(locations, date, values, past_days)
    # print(res)


    # df = get_data_by_location(['CA'],'2020-12-14',value, 30)
    # print(df)
    # print(get_rate(df, value))
    # print(get_correlation(df[value[0]].to_numpy(),df[value[1]].to_numpy()))

    print(get_top_regions(date, values, past_days, 2))
