#Zhuofan Li
#by Zhuofan Li
import numpy as np
import pandas as pd
import os
from dataloader import read_file, get_data_by_location
from datetime import datetime, timedelta
import utils
import json
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import time
import matplotlib.pyplot as plt
#the path of the files
base_data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/'
data_path = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports_us/01-01-2021.csv'
vac_data_path_base = './data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv'
raw_link = data_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

#A timer
def tic():
  return time.time()
def toc(tstart, name="Operation"):
  print('%s took: %s sec.\n' % (name,(time.time() - tstart)))


class data_reader:
    '''
    My own version of reading the data
    folder: the path to the folder of the CSSE US data
    path = 'COVID-19_Vaccinations_in_the_United_States_County.csv'

    This one is not used in the final project
    '''
    def __init__(self,folder) -> None:
        assert isinstance(folder, str)
        print('Initializing folder: ', folder)
        self.folder = folder
        first_f = os.listdir(folder)[0]
        data = pd.read_csv(os.path.join(folder,first_f), index_col=0)
        self.states = set(data.index)
        self.timeline = []
        for i in os.listdir(folder)[:-1]:
            self.timeline.append(pd.Timestamp(i[:-4]))
        print('Finished initialization')
        

    def read_trend(self,state):
        '''
        Reads 3-D pixel value of the top left corner of each image in folder
        and returns an n x 3 matrix X containing the pixel values 
        '''  
        assert (state in self.states) and isinstance(state, str) 
        infect = []
        death = []
        recovered = []
        incident = []
        for filename in os.listdir(self.folder)[:-1]:  
            data = pd.read_csv(os.path.join(self.folder,filename), index_col=0) 
            infect.append(data.loc[state,'Confirmed'])
            death.append(data.loc[state,'Deaths'])
            recovered.append(data.loc[state,'Recovered'])
            incident.append(data.loc[state,'Incident_Rate'])
        
        stat = pd.DataFrame({'infect':infect, 'death':death, 'recovered':recovered, 'incident_rate':incident}, index=self.timeline)
        stat = stat.sort_index()
        print(stat.head())
        print(stat.tail())
        return stat

def base_seir_model(s=100000,e=0,i=1000,r=0, beta=0.1066, sigma=0.18, gamma=0.0714, t=100):
    '''
    A basic suspect, exposed, infected, recovered model,
    which models the trend of the population in each part

    input:
    s,e,i,r: the initial population of each part
    beta: The rate of transmission. 
    sigma: The rate of infected people became infectants (rate of symptom reveals)
    gamma: rate of recovery
    t: the total time length to do the prediction

    Output:
    A pandas array P
    P[0]: the Suspectable population trend
    P[1]: the Exposed population trend
    P[2]: the Infectant population trend
    P[3]: the Recovered population trend
    P[4]: New infectant per day
    '''
    assert s>0 and e>=0 and i>0 and r>=0, 'Invalid input for population!'
    assert beta>0 and sigma>0 and gamma>0,'Invalid input for parameters!'
    assert isinstance(t,int) and t>0,'Invalid input for time!'

    S, E, I, R = [s], [e], [i], [r]
    new_infect = [0]
    dt=1
    for _ in range(t-1):
        new = sigma*E[-1]
        new_infect.append(new)
        N=S[-1]+E[-1]+I[-1]+R[-1]
        next_S = S[-1] - (beta*S[-1]*I[-1])/N*dt
        next_E = E[-1] + (beta*S[-1]*I[-1]/N - new)*dt
        next_I = I[-1] + (new - gamma*I[-1])*dt
        next_R = R[-1] + (gamma*I[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        R.append(next_R)
    
    data = np.stack([S, E, I, R,new_infect]).T
    s = pd.DataFrame(data, columns=['Susceptible','Exposed','Infectant','Recovered','New Infect'])
    return s

def generate_trend_SEIR(date_start, states, days, R0):
    '''
    Given a State and the starting date,
    The function simulates the population change in 
    the following days using SEIR model 

    Input: 
    date_start: the starting date of the simulation
    states: the states you want to investigate
    days: the time length for sumulation
    '''
    assert isinstance(states, list), 'The state input shall be a list, even if only one state is used to do the prediction'
    assert isinstance(days, int),'Invalid input for days'
    assert isinstance(R0, float) and R0>0,'Invalid input for R0'
    simulation_pop = pd.DataFrame()
    #get the incident rate of the date
    data = get_data_by_location(states, date_start, ['Incident_Rate'], past_days=1)
    s = data['state_abbrv']
    i=0
    for state in s:
        #the initial values of simulation
        I = data['Incident_Rate'].to_numpy()[i]
        E = 0.5*R0*I
        S = 100000-I-E
        R = 0
        #simulation
        simulation = base_seir_model(S,E,I,R, t = days)
        simulation['State'] = state
        simulation['Date'] = list(range(days))
        simulation_pop = simulation_pop.append(simulation)
        i+=1

    simulation_pop.index = list(range(simulation_pop.shape[0]))
    return simulation_pop


def learn_vaccine(date_start, learning_period=420,predict_period=50,states=['CA']):
    '''
    Learn the parameters of a polynomial model

    input: 
    date_start: The starting date of the learning (shall be a date exist in the record), format(y-m-d)
    learning_period: The peroid of data for learning
    predict_period: the peroid use for prediction
    states: the states to do the learning
    '''
    assert isinstance(date_start,str)
    assert isinstance(learning_period, int)
    assert isinstance(predict_period, int)
    assert isinstance(states,list)
    vac_data = pd.read_csv(vac_data_path_base)#load data
    result = pd.DataFrame()
    #construct a list of time
    datetime_object = datetime.strptime(date_start, '%Y-%m-%d')
    #use the past peroid days to train
    start_date = datetime_object+ timedelta(days=-learning_period)
    end_date = datetime_object 
    date_range= pd.date_range(start=start_date, end=end_date, closed='right').strftime('%Y-%m-%d')
    
    for state in states:
        if state in set(vac_data['Location']):
            #focus on one state
            b = vac_data[vac_data['Location']==state]
            b.fillna(0) #loss data are always of no record and shall be 0
            b.index=list(pd.to_datetime(b['Date']))

            #do the query based on the time
            distributed = []
            for i in date_range:
                distributed.append(b.loc[i,'Dist_Per_100K'][0])
            
            new = np.array(distributed[1:])-np.array(distributed[:-1])

            #polynomial regression (x: time, y: number per 100k of people taken vaccine)
            poly = PolynomialFeatures(degree=6, include_bias=False)
            poly_features = poly.fit_transform(np.array(range(learning_period-1)).reshape(-1, 1))
            predict_features = poly.fit_transform(np.array(range(learning_period,learning_period+predict_period)).reshape(-1, 1))
            
            poly_reg_model = LinearRegression()
            poly_reg_model.fit(poly_features, new)
            y_predict = np.array(poly_reg_model.predict(predict_features))
            result[state] = np.maximum(np.zeros(len(y_predict)),np.array(y_predict))
        
    return(result)
    
def predict_whole_america_SEIR(period=50):
    '''
    Generate the prediction of SEIR around America
    The result is stored in a csv file.

    date: Starting day of the prediction
    period: The length of prediction, the shall not be too large 
    '''
    us_states_json_path = './src/assets/us_states.json'
    with open(us_states_json_path, 'r') as obj:
        us_states = json.load(obj)
    states_abv = list(us_states.values())
    RES = generate_trend_SEIR('2022-02-27',states_abv, period, R0 = 2.5)
    RES.to_csv('data/prediction_SEIR.csv')

def predict_vac(period=50):
    '''
    Predict the future vaccine data (Injection per day)

    period: length of prediction
    '''
    us_states_json_path = './src/assets/us_states.json'
    with open(us_states_json_path, 'r') as obj:
        us_states = json.load(obj)
    states_abv = list(us_states.values())
    RES = learn_vaccine('2022-02-27',learning_period=420,predict_period=period,states=states_abv)
    RES.to_csv('data/prediction_vac.csv')


if __name__=='__main__':
    predict_whole_america_SEIR(period=50)
    predict_vac(period=50)
