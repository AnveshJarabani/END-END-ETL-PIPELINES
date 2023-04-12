import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
dash.register_page(__name__)
ACT_HRS=pd.read_hdf('LBR.H5',key='WO_TRENDS')
PLN_HRS=pd.read_hdf('LBR.H5',key='PLN_HR')
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDER',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('BUILD HOURS TRENDS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':4}),
        dbc.Col([
        dcc.Input(id='PART', 
        debounce=True,
        value='839-198032-001',
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='LABOR_HRS',
        style={'padding-left':'50px','width': '95vw','height':'70vh','display':'inline-block'})]
        ,width={'offset':.5})),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('LABOR_HRS','figure'),
    Input('PART','value')
 )
def update_graph(PART):
    LBR=ACT_HRS.loc[ACT_HRS['Order - Material (Key)']==PART]
    PLN=PLN_HRS.loc[PLN_HRS['Material']==PART]
    PLN.reset_index(inplace=True,drop=True)
    PLN_SUM=PLN.iloc[0,1] 
    avg=LBR['HRS/EA'].mean()
    LINECHART = px.line(
        LBR,x='Order',y='HRS/EA',
        hover_data={'Order - Material (Key)':False,'HRS/EA':':.2f','Operation Quantity':True,'Fiscal year/period':True},
        template='seaborn',
        labels={'HRS/EA':'<b>HOURS WORKED PER EA<b>','Order': '<b>WORK ORDER #<b>'}
        )
    LINECHART.add_hline(y=PLN_SUM,line_dash='dot',
    annotation_text='<b>PLAN HRS PER EA: '+str(('{:.2f}').format(PLN_SUM))+'Hrs',
    annotation_position='bottom left',line=dict(color='blue',width=2.5))
    LINECHART.add_hline(y=avg,line_dash='dot',
    annotation_text='<b>ACT AVG. HRS PER EA: '+str(('{:.2f}').format(avg))+'Hrs',
    annotation_position='top left',line=dict(color='blue',width=2.5))
    LINECHART.add_annotation(dict(text='<b>AVG HRS: '+str('{:.2f} Hrs, '.format(avg)) +  '<b>PLN HRS: '+str(('{:.2f}').format(PLN_SUM))+' Hrs',
    showarrow=False,xref='paper',yref='paper',x=.5,y=.9,font={'size':20}))
    LINECHART.update_layout(title = dict(text='<b>'+PART,font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial Black','size':12},yaxis_tickformat='%y{:.2f}Hrs',
        showlegend=False)
    LINECHART.update_layout(xaxis=dict(type='category'))
    return LINECHART