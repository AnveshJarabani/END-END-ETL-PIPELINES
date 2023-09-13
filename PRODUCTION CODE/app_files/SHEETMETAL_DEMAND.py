import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
from app_files.sql_connector import query_table
dash.register_page(__name__)
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDERS',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('DEMAND QUANTITY - 3 MONTHS OUT',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':3}),
        dbc.Col([
        dcc.Input(id='RAW', 
        debounce=True,
        placeholder='RAW MATERIAL...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Col(dbc.Button(id='BTN_PN',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':10,'offset':50},style={'padding-bottom':'10px'}),
    dcc.Download(id='DOWNLOAD_SM_DEMAND'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='SM_LIST'),type='dot',fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(Output('SM_LIST','figure'),
    Input('RAW','value'))
def TABLE(PN):
    global Num,FILTERED_LIST
    if PN is None:
        PN='40-39383'
    Num=PN
    query=f"SELECT * FROM sm_demand_forecast WHERE `RAW MATERIAL`='{PN}'"
    FILTERED_LIST=query_table(query)
    colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
    graph = ff.create_table(FILTERED_LIST,colorscale=colorscale)
    graph.update_layout(font={'family':'Arial Black','size':12})
    return graph
@callback(
    Output('DOWNLOAD_SM_DEMAND','data'),
    Input('BTN_PN','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(FILTERED_LIST.to_excel,str(Num)+' SHEET METAL DEMAND.xlsx',index=False,engine='xlsxwriter')