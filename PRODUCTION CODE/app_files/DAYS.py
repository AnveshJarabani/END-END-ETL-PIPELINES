import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
dash.register_page(__name__)
DAYS_DT=pd.read_hdf('../H5/LBR.H5',key='PROCESS_DYS')
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDER',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('PROCESS AND WAIT DAYS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':4}),
        dbc.Col([
        dcc.Input(id='PART-DAYS', 
        debounce=True,
        value='839-198032-001',
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='DAYS',
        style={'padding-left':'30px','width': '90vw','height':'70vh','display':'inline-block'})]
        ,width={'offset':.5})),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('DAYS','figure'),
    Input('PART-DAYS','value')
 )
def update_graph(PART):
    DT=DAYS_DT.loc[DAYS_DT['Material']==PART]
    DT.reset_index(inplace=True,drop=True)
    STACKCHART = px.bar(
        DT,x='OP',y='DAYS',color='PROCESS/WAIT',
        hover_data={'Material':False,'DAYS':True,'PROCESS/WAIT':True},
        template='seaborn',text='DAYS',
        labels={'OP': '<b>OPERATION (SEQUENCE)','DAYS':'<b> PROCESS/WAIT DAYS'}
        )
    STACKCHART.update_traces(textfont_size=16)
    STACKCHART.update_layout(title = dict(text='<b>'+PART,font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        legend=dict(orientation='h',x=1,y=1.01,
        xanchor='right',yanchor='top',title=None,
        bgcolor='rgba(0,0,0,0)'),
        font={'family':'Arial','size':12},yaxis_tickformat='%y{:.0f}Hrs')
    return STACKCHART