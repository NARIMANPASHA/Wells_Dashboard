import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import Hourly_Pressure_data, Daily_Production_data


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('2 Saatlıq Təzyiq Trendi|', href='/apps/Hourly_Pressure_data'),
        dcc.Link('Günlük Hasilat Trendi', href='/apps/Daily_Production_data'),
    ], className="row"),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/Hourly_Pressure_data':
        return Hourly_Pressure_data.layout
    if pathname == '/apps/Daily_Production_data':
        return Daily_Production_data.layout
    else:
        return "Səhifəyə Keçid Edin"


#if __name__ == '__main__':
#    app.run_server(debug=False)
    
    
    
from waitress import serve

if __name__ == '__main__':
    serve(app.server,host='10.10.135.89',port=8080)
        