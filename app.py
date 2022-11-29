import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# meta_tags are required for the app layout to be mobile responsive
#app = dash.Dash(__name__, suppress_callback_exceptions=True,
#                meta_tags=[{'name': 'viewport',
 #                           'content': 'width=device-width, initial-scale=1.0'}]
#                )



#external_stylesheets= ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, use_pages=True,suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.CERULEAN])
#app = dash.Dash(__name__, use_pages=True,suppress_callback_exceptions=True)


sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=False,
            pills=True,
            className="bg-light",
)

#------------------------------------------------------------------------------
app.layout = html.Div(
     [
        # main app framework
        #html.Div("Python Multipage App with Dash", style={'fontSize':50, 'textAlign':'center'}),
        
        #html.Div([]),
        html.Div([
            sidebar
            #dcc.Link(page['name']+"  |  ", href=page['path'])
            #for page in dash.page_registry.values()
        ]),
        html.Hr(),

        # content of each page
        dash.page_container
   ]
)
#------------------------------------------------------------------------------




#if __name__ == "__main__":
 #   app.run(debug=True)


from waitress import serve

if __name__ == '__main__':
    #app.run_server(debug=True) 
    serve(app.server,host='10.10.135.89',port=8080)  