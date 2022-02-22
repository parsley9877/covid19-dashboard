from dash import dcc
from dash import html
import dash



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

tab_1 = html.Div(className='tab-1', children=[html.A('DUMMY TAB 1 (TO BE DONE)', id='dummy-id')])
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

if __name__ == '__main__':
    app.run_server(debug=True)



