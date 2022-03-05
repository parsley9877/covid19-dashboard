import pandas as pd
from analysis_controller import get_rate
from dataloader import get_data_by_location
from statsmodels.tsa.forecasting.theta import ThetaModel
# from statsmodels.tsa.arima import ARIMA
import statsmodels.api as sm

import matplotlib.pyplot as plt
import numpy as np

from statsmodels.tsa.seasonal import STL
import utils


def get_prediction(locations, date, value, past_day, next_days):
    df_train = get_data_by_location(locations, date, [value], past_day)

    df_val = get_data_by_location(locations, date, [value], past_day, next_days)
    
    data_train = df_train[value].to_numpy()
    data_val = df_val[value].to_numpy()

    tm = ThetaModel(data_train,period= 50)
    tm = tm.fit()
    # mod =  sm.tsa.SARIMAX(data_train, order=(1, 0, 0), trend='c')
    # tm = mod.fit()
    predicted = tm.forecast(next_days).to_numpy()
    # print(predicted)
    res = np.concatenate((data_train, predicted))
    df_val[f'{value}_predicted'] = res
    return df_val
    # plt.plot(range(len(res)),res)
    # plt.scatter(range(len(data_train),len(data_train)+len(predicted)),predicted)
    # plt.plot(data_val)
    # plt.show()


    # stl = STL(data_train,period=12)#, seasonal=13)
    # res = stl.fit()
    # fig = res.plot()
    # plt.show()

def NIKHIL_PREDICTION_FUNC(us_state, value, date, days_before, days_after):
    locations = [utils.state_name_to_abbrv(us_state)]
    df = get_prediction(locations,date,value,days_before, days_after)
    final_df = pd.DataFrame(data= {'date': df['date'].to_numpy(), 'preds': df[f'{value}_predicted'].to_numpy(), 'actual': df[value].to_numpy()})

    return final_df

if __name__ == '__main__':
    values = ['Incident_Rate', 'Deaths']
    locations = ['CA']
    date = '2020-12-14'
    past_days = 20
    df = get_prediction(locations,date,values[1],past_days, 20)
    final_df = pd.DataFrame(data= {'date': df['date'].to_numpy(), 'preds': df[f'{values[1]}_predicted'].to_numpy(), 'actual': df[values[1]].to_numpy()})

    print(final_df)





    



