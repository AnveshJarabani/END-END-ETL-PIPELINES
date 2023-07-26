import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
dash.register_page(__name__)
WC_LOAD=pd.read_hdf('../H5/LBR.H5',key='WC_LOAD')
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDER',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('WORK CENTER LOADING',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':4}),
        dbc.Col([
        dcc.Dropdown(id='WORK CENTER', multi= False,
        options=WC_LOAD['WORK_CENTER'].unique(),
        value='WELDING',
        placeholder='Select Work Center',
        maxHeight=600,
        style={'color':'black',"font-weight":'bold','justify-content':'center',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':4})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='WC_LOAD',
        style={'padding-left':'50px','width': '95vw','height':'70vh','display':'inline-block'})]
        ,width={'offset':.5})),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('WC_LOAD','figure'),
    Input('WORK CENTER','value')
 )
def update_graph(WC):
    LOAD=WC_LOAD.loc[WC_LOAD['WORK_CENTER']==WC]
    AVG=LOAD['MONTHLY AVG. HRS'].unique()[0]
    BAR = px.bar(
        LOAD,x='X',y='Hours Worked',
        hover_data={'MONTHLY AVG. HRS':False,'Hours Worked':':.2f','Work Center':False},
        template='seaborn',
        labels={'X':'<b>WORK CENTER<b>'},
        text='Hours Worked')
    BAR.add_hline(y=AVG,line_dash='solid',
    annotation_text='<b>MONTHLY AVG. HRS: '+str(('{:.2f}').format(AVG))+'Hrs',
    annotation_position='bottom left',line=dict(color='black',width=2.5))
    BAR.update_layout(title = dict(text='<b>'+WC,font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial Black','size':12},yaxis_tickformat='%y{:.2f}Hrs',
        showlegend=False)
    return BAR