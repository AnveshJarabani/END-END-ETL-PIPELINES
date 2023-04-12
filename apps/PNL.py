import dash
from dash.dependencies import Input,Output
from dash import dcc, html,callback
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
dash.register_page(__name__,path='/')
SMRY=pd.read_hdf('TOOLCOSTS.H5',key='SMRY')
SMRY=SMRY.pivot_table(index=['QTR+YR','FISCAL PERIOD','CUSTOMER'],values=['SHIPPED','ACTUAL COST','DELTA'],aggfunc=np.sum)
SMRY.reset_index(inplace=True)
SMRY_QTR=SMRY.pivot_table(index=['QTR+YR','CUSTOMER'],values=['SHIPPED','ACTUAL COST','DELTA'],aggfunc=np.sum)
SMRY_QTR.reset_index(inplace=True)
SMRY_QTR.rename(columns={'QTR+YR':'PERIOD'},inplace=True)
SMRY_P=SMRY.pivot_table(index=['FISCAL PERIOD','CUSTOMER'],values=['SHIPPED','ACTUAL COST','DELTA'],aggfunc=np.sum)
SMRY_P.reset_index(inplace=True)
SMRY_P.rename(columns={'FISCAL PERIOD':'PERIOD'},inplace=True)
SMRY_P=pd.concat([SMRY_QTR,SMRY_P],ignore_index=True)
SMRY_P['P/L%']=SMRY_P['DELTA']/SMRY_P['SHIPPED']
SMRY_P=SMRY_P.melt(id_vars=['PERIOD','DELTA','P/L%','CUSTOMER'],var_name='SHIPPED/ACTUAL COST',value_name='USD (Millions)')
SMRY_LINE=SMRY_P[['PERIOD','CUSTOMER','P/L%']].drop_duplicates()
SMRY_L_Q=SMRY_LINE.loc[SMRY_LINE['PERIOD'].str.contains('QTR')]
SMRY_L_P=SMRY_LINE.loc[SMRY_LINE['PERIOD'].str.contains('Period')]

layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDERFRS',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'10vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
        dbc.Row([
        dbc.Col([
        dcc.Dropdown(id='CUSTOMERS', multi= False,
        options=list(SMRY_QTR['CUSTOMER'].unique()),
        value='KLA TENCOR',
        placeholder='Select Customer...',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':4}),
        dbc.Col([
        dcc.Dropdown(id='PERIOD', multi= False,
        options=list(SMRY_QTR['PERIOD'].unique()),
        value='2023 QTR 1',
        placeholder='Select FISCAL QUARTER',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':2})]),
      dbc.Row(
        dbc.Col([
        dcc.Graph(figure='CUSTOMER_CHART',
        style={'padding-left':'2vw','width': '45vw','height':'45vh','display':'inline-block'}),
        dcc.Graph(figure='SMRY_CHART',
        style={'padding-left':'5vw','width': '45vw','height':'45vh','display':'inline-block'})],
    )),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)

@callback(
    Output('CUSTOMER_CHART','figure'),
    Output('SMRY_CHART','figure'),
    Input('CUSTOMERS','value'),
    Input('PERIOD','value'))
def graph(CUSTOMER,PERIOD):
  SMRY=SMRY.loc[SMRY['QTR+YR']==PERIOD]
  SMRY_CHART = px.bar(
  data_frame=SMRY,
  x='PERIOD',y='USD (Millions)',
  barmode='group',
  color='SHIPPED/ACTUAL COST',
  color_discrete_map={'SHIPPED':'#7eb6f2','ACTUAL COST':'#f27ee5'},
  hover_data={'P/L%':':.2%'},
  title=CUSTOMER,
  template='seaborn',text_auto='.2s',
  )
  CUST_CHART.update_traces(textposition='outside')
  CUST_CHART.update_layout(title = dict(
  yanchor='bottom', x=0.5,y=.85,font_size=30),
  font={'family':'Arial Black','size':12},
  yaxis_tickprefix='$',
  yaxis={'dtick':1000000},
  legend=dict(orientation='v',x=.8,y=1.1,
          xanchor='right',yanchor='top',title=None,
          bgcolor='rgba(0,0,0,0)'),
          plot_bgcolor='rgba(0,0,0,0)',
          paper_bgcolor='rgba(0,0,0,0)')
  CUST_CHART.add_trace(go.Scatter(x=SMRY_QTR['PERIOD'],
  y=SMRY_QTR['P/L%'],yaxis='y2',name='P/L% BY QTR',
  line=dict(color='#3005f0',width=2),
  mode='lines+markers+text',
  text=SMRY_QTR['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
  textposition='top center'))
  CUST_CHART.add_trace(go.Scatter(x=SMRY_P['PERIOD'],
  y=SMRY_P['P/L%'],yaxis='y2',name='P/L% BY MONTH',
  line=dict(color='#b305f7',width=2),
  mode='lines+markers+text',
  text=SMRY_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
  textposition='top center'))
  CUST_CHART.update_layout( 
          yaxis2=dict(
          range=[-.4,.4],
          title='PROFIT-LOSS%',
          tickformat= ',.0%',
          anchor="free",  # specifying x - axis has to be the fixed
          overlaying="y",  # specifyinfg y - axis has to be separated
          side="right",  # specifying the side the axis should be present
          position=1  # specifying the position of the axis
      ))
  
  SMRY=SMRY.loc[SMRY['CUSTOMER']==CUSTOMER] 
  SMRY_QTR=SMRY_QTR.loc[SMRY_QTR['CUSTOMER']==CUSTOMER]
  SMRY_P=SMRY_P.loc[SMRY_P['CUSTOMER']==CUSTOMER]
  CUST_CHART = px.bar(
  data_frame=SMRY,
  x='PERIOD',y='USD (Millions)',
  barmode='group',
  color='SHIPPED/ACTUAL COST',
  color_discrete_map={'SHIPPED':'#7eb6f2','ACTUAL COST':'#f27ee5'},
  hover_data={'P/L%':':.2%'},
  title=CUSTOMER,
  template='seaborn',text_auto='.2s',
  )
  CUST_CHART.update_traces(textposition='outside')
  CUST_CHART.update_layout(title = dict(
  yanchor='bottom', x=0.5,y=.85,font_size=30),
  font={'family':'Arial Black','size':12},
  yaxis_tickprefix='$',
  yaxis={'dtick':1000000},
  legend=dict(orientation='v',x=.8,y=1.1,
          xanchor='right',yanchor='top',title=None,
          bgcolor='rgba(0,0,0,0)'),
          plot_bgcolor='rgba(0,0,0,0)',
          paper_bgcolor='rgba(0,0,0,0)')
  CUST_CHART.add_trace(go.Scatter(x=SMRY_QTR['PERIOD'],
  y=SMRY_QTR['P/L%'],yaxis='y2',name='P/L% BY QTR',
  line=dict(color='#3005f0',width=2),
  mode='lines+markers+text',
  text=SMRY_QTR['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
  textposition='top center'))
  CUST_CHART.add_trace(go.Scatter(x=SMRY_P['PERIOD'],
  y=SMRY_P['P/L%'],yaxis='y2',name='P/L% BY MONTH',
  line=dict(color='#b305f7',width=2),
  mode='lines+markers+text',
  text=SMRY_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
  textposition='top center'))
  CUST_CHART.update_layout( 
          yaxis2=dict(
          range=[-.4,.4],
          title='PROFIT-LOSS%',
          tickformat= ',.0%',
          anchor="free",  # specifying x - axis has to be the fixed
          overlaying="y",  # specifyinfg y - axis has to be separated
          side="right",  # specifying the side the axis should be present
          position=1  # specifying the position of the axis
      ))
  return CUST_CHART, SMRY_CHART
