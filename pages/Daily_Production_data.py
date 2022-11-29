
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
import pathlib
#from app import app

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

dash.register_page(__name__)

#external_stylesheets= ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#app.layout=html.Div([
layout=html.Div([
    dbc.Col(html.H1('Günlük Hasilat Trendi', className='text-center text-primary, mb-4'), width={'size': 12}),
    html.Div(
        dcc.DatePickerRange(id='my-date-picker-range',
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
                                  #disabled=True,
                                  updatemode='bothdates')                    
               
               ),
    
     html.Div([
         html.Div([
#             html.H1('U1-16 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='production-trend-graph16',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         
         html.Div([
#             html.H1('U1-18 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='production-trend-graph18',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         ],className='row'),
     
     html.Div([
         html.Div([
#             html.H1('U1-16 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='production-trend-graph14',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         
         html.Div([
#             html.H1('U1-18 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='production-trend-graph10',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         ],className='row'),
     
     #--------------------------
     
     html.Div([
         html.Div([
#             html.H1('U1-16 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='total-gasproduction-trend',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         
         html.Div([
#             html.H1('U1-18 Günlük Hasilatı',
#                style = {'textAlign':'center',  
#                                    'color':'darkblue',
#                                    'fontSize'  : '30px',
#                                    'fontWeight': 'bold'}
#                ),
        
     
             dcc.Graph(id='total-condensateproduction-trend',figure={"layout": {"height": 850}}),
             ],className='six columns'),
         ],className='row'),
     #---------------------
     
     
#     html.Div([
#         html.Div([
#             dcc.Graph(id='total-production-trend',figure={"layout": {"height": 850}}),
#             ]),
         
#         ],className='row'),   
     
     ])
     
@callback(
    Output(component_id='production-trend-graph16', component_property='figure'),
    Output(component_id='production-trend-graph18', component_property='figure'),
    Output(component_id='production-trend-graph14', component_property='figure'),
    Output(component_id='production-trend-graph10', component_property='figure'),
    Output(component_id='total-gasproduction-trend', component_property='figure'),
    Output(component_id='total-condensateproduction-trend', component_property='figure'),
    [Input(component_id='my-date-picker-range', component_property='start_date'),
     Input(component_id='my-date-picker-range', component_property='end_date')]
)



def get_pressure_trend(start_date, end_date):  
    fig16 = go.Figure()
    fig18 = go.Figure()
    fig14 = go.Figure()
    fig10 = go.Figure()
    figgastotal = go.Figure()
    figcontotal = go.Figure()
        
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
       

    fig16 = make_subplots(specs=[[{"secondary_y": True}]])
    fig18 = make_subplots(specs=[[{"secondary_y": True}]])
    fig14 = make_subplots(specs=[[{"secondary_y": True}]])
    fig10 = make_subplots(specs=[[{"secondary_y": True}]])
    figgastotal = make_subplots(specs=[[{"secondary_y": True}]])
    figcontotal = make_subplots(specs=[[{"secondary_y": True}]])
    
    U1_16_df = pd.read_csv(DATA_PATH.joinpath('U1_16_Daily_Production.csv'),parse_dates=['Date'],dtype=mydtype,encoding='unicode_escape')
    U1_16_df = U1_16_df[(U1_16_df['Date'] > start_date) & (U1_16_df['Date'] < end_date)]
    
    U1_18_df = pd.read_csv(DATA_PATH.joinpath('U1_18_Daily_Production.csv'),parse_dates=['Date'],dtype=mydtype,encoding='unicode_escape')
    U1_18_df = U1_18_df[(U1_18_df['Date'] > start_date) & (U1_18_df['Date'] < end_date)]
    
    U1_14_df = pd.read_csv(DATA_PATH.joinpath('U1_14_Daily_Production.csv'),parse_dates=['Date'],dtype=mydtype,encoding='unicode_escape')
    U1_14_df = U1_14_df[(U1_14_df['Date'] > start_date) & (U1_14_df['Date'] < end_date)]
    
    U1_10_df = pd.read_csv(DATA_PATH.joinpath('U1_10_Daily_Production.csv'),parse_dates=['Date'],dtype=mydtype,encoding='unicode_escape')
    U1_10_df = U1_10_df[(U1_10_df['Date'] > start_date) & (U1_10_df['Date'] < end_date)]
    
    SDO1_df = pd.read_csv(DATA_PATH.joinpath('Total_Production.csv'),parse_dates=['Date'],dtype=mydtype,encoding='unicode_escape')
    SDO1_df = SDO1_df[(SDO1_df['Date'] > start_date) & (SDO1_df['Date'] < end_date)]
    
    # adds traces to the graph
    fig16.add_trace(go.Scattergl(x=U1_16_df['Date'].values, y=U1_16_df['Well_Head_Pressure_(atm)'].values, visible='legendonly',name='Quyu Ağzı Təzyiq'),secondary_y=False)       
    fig16.add_trace(go.Scattergl(x=U1_16_df['Date'].values, y=U1_16_df['Downhole_Gauge_Pressure_(atm)'].values, visible='legendonly',name='Quyu Dibi Təzyiq'), secondary_y=False)
    fig16.add_trace(go.Scattergl(x=U1_16_df['Date'].values, y=U1_16_df['Daily_Gas_Production_(1000 m³/day)'].values,name='Qaz Hasilati (1000 m3/gün)'), secondary_y=True)
    fig16.add_trace(go.Scattergl(x=U1_16_df['Date'].values, y=U1_16_df['Daily_Condensate_Production_(ton/day)'].values,name='Kondensat Hasilati (ton/gün)'), secondary_y=True)
    fig16.add_trace(go.Scattergl(x=U1_16_df['Date'].values, y=U1_16_df['Daily_Water_Production_(ton/day)'].values, visible='legendonly',name='Su Hasilati (ton/gün)'), secondary_y=True)
    
    fig18.add_trace(go.Scattergl(x=U1_18_df['Date'].values, y=U1_18_df['Well_Head_Pressure_(atm)'].values,visible='legendonly',name='Quyu Ağzı Təzyiq'),secondary_y=False)       
    fig18.add_trace(go.Scattergl(x=U1_18_df['Date'].values, y=U1_18_df['Downhole_Gauge_Pressure_(atm)'].values, visible='legendonly',name='Quyu Dibi Təzyiq'), secondary_y=False)
    fig18.add_trace(go.Scattergl(x=U1_18_df['Date'].values, y=U1_18_df['Daily_Gas_Production_(1000 m³/day)'].values,name='Qaz Hasilati (1000 m3/gün)'), secondary_y=True)
    fig18.add_trace(go.Scattergl(x=U1_18_df['Date'].values, y=U1_18_df['Daily_Condensate_Production_(ton/day)'].values,name='Kondensat Hasilati (ton/gün)'), secondary_y=True)
    fig18.add_trace(go.Scattergl(x=U1_18_df['Date'].values, y=U1_18_df['Daily_Water_Production_(ton/day)'].values, visible='legendonly',name='Su Hasilati (ton/gün)'), secondary_y=True)

    fig14.add_trace(go.Scattergl(x=U1_14_df['Date'].values, y=U1_14_df['Well_Head_Pressure_(atm)'].values,visible='legendonly', name='Quyu Ağzı Təzyiq'),secondary_y=False)       
    fig14.add_trace(go.Scattergl(x=U1_14_df['Date'].values, y=U1_14_df['Downhole_Gauge_Pressure_(atm)'].values, visible='legendonly',name='Quyu Dibi Təzyiq'), secondary_y=False) 
    fig14.add_trace(go.Scattergl(x=U1_14_df['Date'].values, y=U1_14_df['Daily_Gas_Production_(1000 m³/day)'].values, name='Qaz Hasilati (1000 m3/gün)'), secondary_y=True)
    fig14.add_trace(go.Scattergl(x=U1_14_df['Date'].values, y=U1_14_df['Daily_Condensate_Production_(ton/day)'].values, name='Kondensat Hasilati (ton/gün)'), secondary_y=True)
    fig14.add_trace(go.Scattergl(x=U1_14_df['Date'].values, y=U1_14_df['Daily_Water_Production_(ton/day)'].values, visible='legendonly',name='Su Hasilati (ton/gün)'), secondary_y=True)
    
    
    fig10.add_trace(go.Scattergl(x=U1_10_df['Date'].values, y=U1_10_df['Well_Head_Pressure_(atm)'].values, visible='legendonly',name='Quyu Ağzı Təzyiq'),secondary_y=False)       
    fig10.add_trace(go.Scattergl(x=U1_10_df['Date'].values, y=U1_10_df['Downhole_Gauge_Pressure_(atm)'].values, visible='legendonly',name='Quyu Dibi Təzyiq'), secondary_y=False) 
    fig10.add_trace(go.Scattergl(x=U1_10_df['Date'].values, y=U1_10_df['Daily_Gas_Production_(1000 m³/day)'].values, name='Qaz Hasilati (1000 m3/gün)'), secondary_y=True)
    fig10.add_trace(go.Scattergl(x=U1_10_df['Date'].values, y=U1_10_df['Daily_Condensate_Production_(ton/day)'].values, name='Kondensat Hasilati (ton/gün)'), secondary_y=True)
    fig10.add_trace(go.Scattergl(x=U1_10_df['Date'].values, y=U1_10_df['Daily_Water_Production_(ton/day)'].values, visible='legendonly',name='Su Hasilati (ton/gün)'), secondary_y=True)
    
    
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_10_Daily_Gas_Production_(1000 m³/day)'].values, name='U1_10 Qaz Hasilatı'),secondary_y=False)
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_12_Daily_Gas_Production_(1000 m³/day)'].values, name='U1_12 Qaz Hasilatı'),secondary_y=False)
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_14_Daily_Gas_Production_(1000 m³/day)'].values, name='U1_14 Qaz Hasilatı'),secondary_y=False)
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_16_Daily_Gas_Production_(1000 m³/day)'].values, name='U1_16 Qaz Hasilatı'),secondary_y=False)
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_18_Daily_Gas_Production_(1000 m³/day)'].values, name='U1_18 Qaz Hasilatı'),secondary_y=False)
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['SDO1_Daily_Gas_Production_(1000 m³/day)'].values, name='SDO-1 Qaz Hasilatı'),secondary_y=False) 
    figgastotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['SDO1_Total_Gas_Production_(MM m³/day)'].values, name='SDO-1 Toplam Qaz Hasilatı'),secondary_y=True) 


    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_10_Daily_Condensate_Production_(ton/day)'].values, name='U1_10 Kondensat Hasilatı'),secondary_y=False)
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_12_Daily_Condensate_Production_(ton/day)'].values, name='U1_12 Kondensat Hasilatı'),secondary_y=False)
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_14_Daily_Condensate_Production_(ton/day)'].values, name='U1_14 Kondensat Hasilatı'),secondary_y=False)
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_16_Daily_Condensate_Production_(ton/day)'].values, name='U1_16 Kondensat Hasilatı'),secondary_y=False)
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['U1_18_Daily_Condensate_Production_(ton/day)'].values, name='U1_18 Kondensat Hasilatı'),secondary_y=False)
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['SDO1_Daily_Condensate_Production_(ton/day)'].values, name='SDO-1 Kondensat Hasilatı'),secondary_y=False) 
    figcontotal.add_trace(go.Scattergl(x=SDO1_df['Date'].values, y=SDO1_df['SDO1_Total_Condensate_Production_(ton/day)'].values, name='SDO-1 Toplam Kondensat Hasilatı'),secondary_y=True)             
    
    
    import plotly.io as pio
    pio.templates.default = 'plotly_white'
    #fig16.update_layout({'plot_bgcolor': 'white',
                         #'paper_bgcolor':'black'
     #                    })
    #fig16.update_xaxes(showgrid=True, gridwidth=1, gridcolor='Brown')
    #fig16.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')
    #fig16.update_traces(marker_line_color('rgb(0, 2, 1)'))
    #fig16.update_layout=(line={'width': 1, 'color': 'black'})
    
                  
    
    # set each graph's title and size,color, etc
    fig16.update_layout(title_text='U1-16 Gündəlik Hasilat Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)
    
    fig18.update_layout(title_text='U1-18 Gündəlik Hasilat Trendi',
                     title_font_size=24, title_font_color='blue', title_x=0.5)
    
    fig14.update_layout(title_text='U1-14 Gündəlik Hasilat Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)
    
    fig10.update_layout(title_text='U1-10 Gündəlik Hasilat Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)
    
    figgastotal.update_layout(title_text='SD0-1 Gündəlik Qaz Hasilat Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)
    
    figcontotal.update_layout(title_text='SD0-1 Gündəlik Kondensat Hasilat Trendi',
                      title_font_size=24, title_font_color='blue', title_x=0.5)

    # Set x-axis title
    fig16.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)
    fig18.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)
    fig14.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)
    fig10.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)
    figgastotal.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)
    figcontotal.update_xaxes(title_text="Zaman", color="blue", title_font_size=20)

    # Set y-axis titles
    fig16.update_yaxes(title_text="Quyu ağzı/dibi Təzyiqlər (atm)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    fig18.update_yaxes(title_text="Quyu ağzı/dibi Təzyiqlər (atm)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    
    fig14.update_yaxes(title_text="Quyu ağzı/dibi Təzyiqlər (atm)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    fig10.update_yaxes(title_text="Quyu ağzı/dibi Təzyiqlər (atm)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    
    fig16.update_yaxes(title_text="Gündəlik Hasilat", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    fig18.update_yaxes(title_text="Gündəlik Hasilat", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    
    fig14.update_yaxes(title_text="Gündəlik Hasilat", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    fig10.update_yaxes(title_text="Gündəlik Hasilat", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    figgastotal.update_yaxes(title_text="SDO-1 Toplam Qaz Hasilatı (MM m3)", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    
    figgastotal.update_yaxes(title_text="Qaz Hasilatı (1000 m3/gün)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)
    
    figcontotal.update_yaxes(title_text="SDO-1 Toplam Kondensat Hasilatı (ton)", title_font_color="blue", color="blue", title_font_size=20,
                     secondary_y=True)
    
    figcontotal.update_yaxes(title_text="Kondensat Hasilatı (ton/gün)", title_font_color="blue", title_font_size=20,
                     color="blue", secondary_y=False)

    # Sets hover moode
    fig16.update_layout(hovermode="x unified")
    fig18.update_layout(hovermode="x unified")
    fig14.update_layout(hovermode="x unified")
    fig10.update_layout(hovermode="x unified")
    figgastotal.update_layout(hovermode="x unified")
    figcontotal.update_layout(hovermode="x unified")
    
    # fig.update_layout(hovermode="x")

    # Changes hover mode appearance
    fig16.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    fig18.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    fig14.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    fig10.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    figgastotal.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    figcontotal.update_layout(hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell", namelength=-1))
    
    # Changes legend location
    fig16.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    fig18.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    fig14.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    fig10.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    figgastotal.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    figcontotal.update_layout(legend=dict(orientation="h",y=-0.1,x=0))
    #fig18.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    #entrywidth=70,
    
    fig16.show()
    fig18.show()
    fig14.show()
    fig10.show()
    figgastotal.show()
    figcontotal.show()
    # fig.show_dash(mode='inline')

    return fig16,fig18,fig14,fig10,figgastotal,figcontotal
       
#from waitress import serve

#if __name__ == '__main__':
    #app.run_server(debug=True) 
#    serve(app.server,host='10.10.135.89',port=8080)  