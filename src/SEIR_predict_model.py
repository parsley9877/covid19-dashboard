#Zhuofan Li
import numpy as np
import pandas as pd
import os

class data_reader:
    '''
    My own version of reading the data
    folder: the path to the folder of the CSSE US data
    path = 'COVID-19_Vaccinations_in_the_United_States_County.csv'
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

def base_seir_model(s=100000,e=0,i=1000,r=0, beta=0.0090, sigma=0.5066, gamma=0.0054, t=200):
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
    S, E, I, R = [s], [e], [i], [r]
    new_infect = [0]
    dt=1
    for _ in range(t):
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

    return np.stack([S, E, I, R,new_infect]).T