import json

import numpy as np
import pandas


us_states_json_path = './src/assets/us_states.json'
with open(us_states_json_path, 'r') as obj:
    us_states = json.load(obj)

unknown_states = ['Virgin Islands', 'Northern Mariana Islands', 'Guam', 'Grand Princess', 'Diamond Princess', 'American Samoa']

def state_name_to_abbrv(state_name):
    return us_states[state_name]

def filter_unknown_states(df):
    new_df = df[~df['Province_State'].isin(unknown_states)]
    return new_df

empty_bar =  {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
    "paper_bgcolor": '#a4b6fa',
        "margin": {'l':20, 'r':20, 't':20, 'b':20},
        "annotations": [
            {
                "text": "Empty Plot: Please Select States on Map",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ],

    }
}

empty_heatmap =  {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
    "paper_bgcolor": '#a4b6fa',
        "margin": {'l':20, 'r':20, 't':20, 'b':20},
        "annotations": [
            {
                "text": "Empty Heatmap: Please set params and hit the button!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ],

    }
}

empty_pred_line =  {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
    "paper_bgcolor": '#a4b6fa',
        "margin": {'l':20, 'r':20, 't':20, 'b':20},
        "annotations": [
            {
                "text": "Empty Prediction: Please set params and hit the button!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ],

    }
}
