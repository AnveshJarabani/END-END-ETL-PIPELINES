from dash import html
from app import app
import dash_bootstrap_components as dbc
from dash import Output,Input,State,dcc
import base64
from app_files import TOOLCOSTS,FAB,PARTSEARCH,WO_HRS,DAYS,Version,QLY_TRENDS,WC_LOAD,QLY_RELATIVE_TRENDS,SHEETMETAL_DEMAND,PNL,FPY,FPY_PN
test_base64 = base64.b64encode(open('UCT.PNG', 'rb').read()).decode('ascii')
offcanvas = html.Div([
        dbc.Button("Explore",id="Open-offcanvas", n_clicks=0,size='lg',class_name='me-1'),
        dbc.Offcanvas(
                 dbc.ListGroup(
            [
                # dbc.ListGroupItem("PROFIT-LOSS", href="/apps/"),
                dbc.ListGroupItem("TOOL COSTS", href="/apps/TOOLCOSTS"),
                dbc.ListGroupItem("QLY. COST TRENDS", href="/apps/QLY_TRENDS"),
                dbc.ListGroupItem("DEMAND FORECAST", href="/apps/SHEETMETAL_DEMAND"),
                dbc.ListGroupItem("QLY. RELATIVE TRENDS", href="/apps/QLY_RELATIVE_TRENDS"),
                dbc.ListGroupItem("FRAME COSTS", href="/apps/FAB"),
                dbc.ListGroupItem("PART COST FINDER", href="/apps/PARTSEARCH"),
                dbc.ListGroupItem("BUILD HOUR TRENDS", href="/apps/WO_HRS"),
                dbc.ListGroupItem("PROCESS & WAIT DAYS", href="/apps/DAYS"),
                dbc.ListGroupItem("WORK CENTER LOAD", href="/apps/WC_LOAD"),
                dbc.ListGroupItem("QUALITY DATA", href="/apps/FPY"),
                dbc.ListGroupItem("QUALITY DATA BY PN", href="/apps/FPY_PN"),
                dbc.ListGroupItem("VERSION", href="/apps/version"),
                ]
        ),
            placement='end',
            id="offcanvas",
            title="Options",
            is_open=False,
        ),
    ]
)

@app.callback(
    Output("offcanvas", "is_open"),
    Input("Open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
navbar= dbc.Navbar(
        dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(test_base64), width='200px',height="100px")),
                        dbc.Col(dbc.NavbarBrand("UCT CHANDLER - KPI DASHBOARD", style= {'justify-content-center':'center',
                   'align-items':'center',
                  'font': 'Arial Bold',
                  'font-size': 60,
                  'font-weight': 'bold',
                  'color':'#1172FF',#'className':'h-50',
                   'height':'10vh',})),
                    ],
                    align="center",
                    className="g-0",
                ),
            ),
            offcanvas,
        ],fluid=True,
    ),
    color="#AAC9F5",
    dark=True,
    fixed='top')
@app.callback(Output('page-content','children'),Input('url','pathname'))
def display_page(pathname):
    # if pathname=='/apps/':
    #     return PNL.layout
    if pathname=='/apps/TOOLCOSTS': return TOOLCOSTS.layout
    if pathname=='/apps/FAB': return FAB.layout
    if pathname=='/apps/PARTSEARCH': return PARTSEARCH.layout
    if pathname=='/apps/version': return Version.modal
    if pathname=='/apps/WO_HRS': return WO_HRS.layout
    if pathname=='/apps/DAYS': return DAYS.layout
    if pathname=='/apps/QLY_TRENDS': return QLY_TRENDS.layout
    if pathname=='/apps/QLY_RELATIVE_TRENDS': return QLY_RELATIVE_TRENDS.layout
    if pathname=='/apps/WC_LOAD': return WC_LOAD.layout
    if pathname=='/apps/FPY': return FPY.layout
    if pathname=='/apps/FPY_PN': return FPY_PN.layout  
    if pathname=='/apps/SHEETMETAL_DEMAND': return SHEETMETAL_DEMAND.layout
    else: return 'TRY LATER'
app.layout = dbc.Container(
    [navbar,dcc.Location(id='url',refresh=False,pathname='/apps/'),html.Div(id='page-content',children=[])],
    style={'height':'200vh'},fluid=True)
if __name__== '__main__': app.run_server(debug=True,port=5055)