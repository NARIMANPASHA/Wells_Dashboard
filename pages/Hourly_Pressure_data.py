
import pandas as pd
import dash
import vaex
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash import callback
from flask import Flask
from dash.dependencies import Input, Output,ALL, State, MATCH, ALLSMALLER
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pyodbc
import os
#import datetime as dt
import datetime
import dash_bootstrap_components as dbc
from plotly_resampler import FigureResampler, FigureWidgetResampler
from flask_caching import Cache
from datetime import date
#from app import app

#app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN],title='SDÖ-1 Quyular Təzyiq Məlumatları')


dash.register_page(__name__, path='/')

#-----------------------------------------------------------------------------------------
# Set up the caching mechanism
#cache = Cache(app.server, config={
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': 'cache-directory'
#})
# set negative to disable (useful for testing/benchmarking)
#CACHE_TIMEOUT = int(os.environ.get('DASH_CACHE_TIMEOUT', '60'))

#----------------------------------------------------------------------------------------
# Create an app layout

#Layout Section: Bootstrap
layout = html.Div([
    html.Div(children=[
        html.Button('Add New Graph', id='add-chart', n_clicks=0),
    ]),
    dbc.Col(html.H1('2 Saatlıq Təzyiqlər Trendi', className='text-center text-primary, mb-4'), width={'size': 12}),
    html.Div(id='container', children=[]),
    # all the graphs will go insde children[] as user creates new chart with add_chart
    # html.Button('Remove Chart', id='remove-chart', n_clicks=0)
])


@callback(
    Output('container', 'children'),
    [Input('add-chart', 'n_clicks')],
    # Input('remove-chart', 'n_clicks')],
    [State('container', 'children')]

)
def display_graphs(n_clicks, div_children):
    new_child = html.Div(
        children=[dbc.Container([
            dbc.Row([
                # dbc.Col(html.H1('Well Pressures Graph',
                #            className='text-center text-primary, mb-4'),
                #    width={'size':12})
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div(html.Label(['Tarixi Seçin'], style={'color': 'blue', 'fontSize': 20})),

                    # Option for Date interval
                    html.Div(dcc.DatePickerRange(id={'type': 'my-date-picker-range', 'index': n_clicks},
                                                 calendar_orientation='horizontal',  # vertical or horizontal
                                                 day_size=39,  # size of calendar image. Default is 39
                                                 end_date_placeholder_text="Return",
                                                 start_date=date(2012,1,1),
                                                 #end_date=date.today(),
                                                 end_date=datetime.datetime.today(),
                                                 with_portal=False,
                                                 first_day_of_week=1,  # Display of calendar when open (0 = Sunday)
                                                 reopen_calendar_on_clear=True,
                                                 is_RTL=False,  # True or False for direction of calendar
                                                 clearable=False,  # whether or not the user can clear the dropdown
                                                 number_of_months_shown=1,
                                                 display_format='DD/MM/YYYY',
                                                 month_format='MMMM YYYY',
                                                 minimum_nights=2,
                                                 persistence=True,
                                                 persisted_props=['start_date','end_date'],
                                                 persistence_type='session',
                                                 updatemode='bothdates',
                                                 ))
                ], width={'size': 4, 'offset': 0, 'order': 1}),

                dbc.Col([
                    html.Label(['Quyunu Seçin'], style={'color': 'blue', 'fontSize': 20}),

                    # multiple dropdown option
                    dcc.Dropdown(id={'type': 'Select a well', 'index': n_clicks}, multi=True, searchable=True,persistence=True,persistence_type='memory',
                                 # value='U1_18_DATA'
                                 # style = dict(width = '100%',display = 'inline-block',verticalAlign = "baseline"),
                                 options=[{'label': i, 'value': i} for i in
                                          ['U1_10_DATA', 'U1_14_DATA', 'U1_16_DATA', 'U1_18_DATA']])
                    # ,className='btn btn-secondary dropdown-toggle')
                ], width={'size': 4, 'offset': 0, 'order': 2})

            ], justify='start'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id={'type': 'pressure-trend-graph', 'index': n_clicks},
                              figure={"layout": {"height": 850}})
                ], width={'size': 12})

            ])

        ], fluid=True)
        ])

    div_children.append(new_child)
    return div_children


@callback(
    Output({'type': 'pressure-trend-graph', 'index': MATCH}, 'figure'),
    [Input(component_id={'type': 'Select a well', 'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'my-date-picker-range', 'index': MATCH}, component_property='start_date'),
     Input(component_id={'type': 'my-date-picker-range', 'index': MATCH}, component_property='end_date'),

     ],

)
def get_pressure_trend(entered_well, start_date, end_date):
    fig = go.Figure()
    #fig = FigureResampler(go.Figure())
    
    mydtype={'Dchoke (mm)': 'str',
         'WHP (atm)': 'float64',
         'DHGP (atm)': 'float64',
         'DHGP (psi)': 'float64',
         'A-annulus Pres (atm)': 'float64',
         '7x10 Annulus Pressure (atm)': 'float64',
         '10x13 Annulus Pressure (atm)': 'float64',
         '13x18 Annulus Pressure (atm)': 'float64',
         '18x24 Annulus Pressure (atm)': 'float64',
         '24x28 Annulus Pressure (atm)': 'float64',
         '28x32 Annulus Pressure (atm)': 'float64',
         'SSSV Pressure (atm)':'float64',
         'Choke Pressure (atm)':'float64',
         'I-II Choke Pressure  (atm)':'float64',
         'II-III Choke Pressure  (atm)':'float64',
         'III Choke Pressure (atm)':'float64',
         'III pille Temperature (Celcius)':'float64',
         'DHGT (Celcius)':'float64',
        }
    
    

    wellnames = ['U1_10_DATA', 'U1_14_DATA', 'U1_16_DATA', 'U1_18_DATA']
    # create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if type(entered_well) == str:
        for i, m in enumerate(wellnames):
            if entered_well == m:
                # path to CSv files
                #mydf = vaex.from_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(m), convert=True, chunk_size=50000,parse_dates=['Date'],index_col=[0])
                #mydf = vaex.from_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(m), chunk_size=50000,parse_dates=['Date'],index_col=[0])
                mydf = pd.read_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(m),parse_dates=['Date'],dtype=mydtype,index_col=[0])

                #mydf=mydf[(mydf['Date']>start_date) & (mydf['Date']<end_date)]
                # adds traces to the graph
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['WHP (atm)'].values, name=m[:5] + '_' + 'Quyu Ağzı Təzyiq'),
                              secondary_y=False)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['DHGP (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + 'Quyu Dibi Təzyiq'), secondary_y=False)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['A-annulus Pres (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + 'Boru Arxası Təzyiq'), secondary_y=True)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['7x10 Annulus Pressure (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + '7x10 Kəmər Təzyiqi'), secondary_y=True)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['10x13 Annulus Pressure (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + '10x13 Kəmər Təzyiqi'), secondary_y=True)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['13x18 Annulus Pressure (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + '13x18 Kəmər Təzyiqi'), secondary_y=True)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['18x24 Annulus Pressure (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + '18x24 Kəmər Təzyiqi'), secondary_y=True)
                fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['24x28 Annulus Pressure (atm)'].values, visible='legendonly',
                                           name=m[:5] + '_' + '24x28 Kəmər Təzyiqi'), secondary_y=True)
    else:
        for k in entered_well:
            # path to CSv files
            #mydf = vaex.from_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(k), convert=True, chunk_size=50000,parse_dates=['Date'],index_col=[0])
            #mydf = vaex.from_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(k), chunk_size=50000,parse_dates=['Date'],index_col=[0])
            mydf = pd.read_csv('D:\\Umid Wells Dashboard DataBase Final\\{}.csv'.format(k),parse_dates=['Date'],dtype=mydtype,index_col=[0])
            
            mydf = mydf[(mydf['Date'] > start_date) & (mydf['Date'] < end_date)]
            # adds traces to the graph
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['WHP (atm)'].values, name=k[:5] + '_' + 'Quyu Ağzı Təzyiq'),
                          secondary_y=False)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['DHGP (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + 'Quyu Dibi Təzyiq'), secondary_y=False)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['A-annulus Pres (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + 'Boru Arxası Təzyiq'), secondary_y=True)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['7x10 Annulus Pressure (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + '7x10 Kəmər Təzyiqi'), secondary_y=True)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['10x13 Annulus Pressure (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + '10x13 Kəmər Təzyiqi'), secondary_y=True)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['13x18 Annulus Pressure (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + '13x18 Kəmər Təzyiqi'), secondary_y=True)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['18x24 Annulus Pressure (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + '18x24 Kəmər Təzyiqi'), secondary_y=True)
            fig.add_trace(go.Scattergl(x=mydf['Date'].values, y=mydf['24x28 Annulus Pressure (atm)'].values, visible='legendonly',
                                       name=k[:5] + '_' + '24x28 Kəmər Təzyiqi'), secondary_y=True)

    # set each graph's title and size,color, etc
    fig.update_layout(title_text=entered_well[0][:5] + ' ' + 'Saylı Quyu Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)

    # Set x-axis title
    fig.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)

    # Set y-axis titles
    fig.update_yaxes(title_text="Quyu ağzı/dibi Təzyiqlər (atm)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    fig.update_yaxes(title_text="Kəmər Təzyiqləri (atm)", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)

    # Sets hover moode
    fig.update_layout(hovermode="x unified")
    # fig.update_layout(hovermode="x")

    # Changes hover mode appearance
    fig.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))

    fig.show()
    # fig.show_dash(mode='inline')

    return fig

#-------------------------------
# Run the app
#from waitress import serve

#if __name__ == '__main__':
    #app.run_server(debug=True) 
#    serve(app.server,host='10.10.135.89',port=8080)
    #serve(app.server,host='10.253.54.13',port=8080)
    
    #serve(app.server)
    #app.run_server(debug=True)
    #app.run_server(debug=False,host='10.10.135.89',port='8050')
    #app.run_server(debug=False, host='0.0.0.0', port='8050')
    #app.run_server(debug=False)

#-----------------------------------------------------------------------------------

#use this command in the terminal
#waitress-serve --host=10.10.135.89 --port=8080  aa:app.server

# above command is equivalent to :
#import UmidWellsDashboard
#waitress.serve(UmidWellsDashboard.app.server,host=10.10.135.89,port=8080,)

# 1.   waitress-serve --port=8041 --url-scheme=https myapp:wsgifunc

# 2. import myapp
#    waitress.serve(myapp.wsgifunc, port=8041, url_scheme='https')
#---------------------------------------------------------------------------

