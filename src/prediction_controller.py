from analysis_controller import get_rate
from dataloader import get_data_by_location
from statsmodels.tsa.forecasting.theta import ThetaModel
# from statsmodels.tsa.arima import ARIMA
import statsmodels.api as sm

import matplotlib.pyplot as plt
import numpy as np

from statsmodels.tsa.seasonal import STL


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

if __name__ == '__main__':
    values = ['Incident_Rate', 'Deaths']
    locations = ['CA']
    date = '2020-12-14'
    past_days = 20
    res = get_prediction(locations,date,values[1],past_days, 20)
    print(res)





    



