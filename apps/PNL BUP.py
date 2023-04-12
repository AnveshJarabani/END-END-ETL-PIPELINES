import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
dash.register_page(__name__,path='/')
LM_SMRY=pd.read_hdf('TOOLCOSTS.H5',key='LM_SMRY')
CY_SMRY=pd.read_hdf('TOOLCOSTS.H5',key='CY_SMRY')
KLA_SMRY=pd.read_hdf('TOOLCOSTS.H5',key='KLA_SMRY')
LM_SMRY['$SOLD']=LM_SMRY['Act Shipped Qty']*LM_SMRY['ASP']
LM_SMRY['BUILD COST']=LM_SMRY['Act Shipped Qty']*LM_SMRY['ACTUAL COST']
LM_SMRY['P/L']=LM_SMRY['Act Shipped Qty']*LM_SMRY['DELTA.CAL']
LM_SMRY_QTR=LM_SMRY.pivot_table(index=['QTR'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
LM_SMRY_QTR.reset_index(inplace=True)
LM_SMRY_QTR.rename(columns={'QTR':'PERIOD'},inplace=True)
LM_SMRY_P=LM_SMRY.pivot_table(index=['FISCAL PERIOD'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
LM_SMRY_P.reset_index(inplace=True)
LM_SMRY_P.rename(columns={'FISCAL PERIOD':'PERIOD'},inplace=True)
LM_SMRY_P=pd.concat([LM_SMRY_QTR,LM_SMRY_P],ignore_index=True)
LM_SMRY_P['P/L%']=LM_SMRY_P['P/L']/LM_SMRY_P['$SOLD']
LM_SMRY_P=LM_SMRY_P.melt(id_vars=['PERIOD','P/L','P/L%'],var_name='$SOLD/BUILD COST',value_name='USD (Millions)')
LM_SMRY_LINE=LM_SMRY_P[['PERIOD','P/L%']].drop_duplicates()
LM_SMRY_L_Q=LM_SMRY_LINE.loc[LM_SMRY_LINE['PERIOD'].str.contains('QTR')]
LM_SMRY_L_P=LM_SMRY_LINE.loc[LM_SMRY_LINE['PERIOD'].str.contains('Period')]

CY_SMRY['$SOLD']=CY_SMRY['Act Shipped Qty']*CY_SMRY['ASP']
CY_SMRY['BUILD COST']=CY_SMRY['Act Shipped Qty']*CY_SMRY['ACTUAL COST']
CY_SMRY['P/L']=CY_SMRY['Act Shipped Qty']*CY_SMRY['DELTA.CAL']
CY_SMRY_QTR=CY_SMRY.pivot_table(index=['QTR'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
CY_SMRY_QTR.reset_index(inplace=True)
CY_SMRY_QTR.rename(columns={'QTR':'PERIOD'},inplace=True)
CY_SMRY_P=CY_SMRY.pivot_table(index=['FISCAL PERIOD'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
CY_SMRY_P.reset_index(inplace=True)
CY_SMRY_P.rename(columns={'FISCAL PERIOD':'PERIOD'},inplace=True)
CY_SMRY_P=pd.concat([CY_SMRY_QTR,CY_SMRY_P],ignore_index=True)
CY_SMRY_P['P/L%']=CY_SMRY_P['P/L']/CY_SMRY_P['$SOLD']
CY_SMRY_P=CY_SMRY_P.melt(id_vars=['PERIOD','P/L','P/L%'],var_name='$SOLD/BUILD COST',value_name='USD (Millions)')
CY_SMRY_LINE=CY_SMRY_P[['PERIOD','P/L%']].drop_duplicates()
CY_SMRY_L_Q=CY_SMRY_LINE.loc[CY_SMRY_LINE['PERIOD'].str.contains('QTR')]
CY_SMRY_L_P=CY_SMRY_LINE.loc[CY_SMRY_LINE['PERIOD'].str.contains('Period')]

KLA_SMRY['$SOLD']=KLA_SMRY['Act Shipped Qty']*KLA_SMRY['ASP']
KLA_SMRY['BUILD COST']=KLA_SMRY['Act Shipped Qty']*KLA_SMRY['ACTUAL COST']
KLA_SMRY['P/L']=KLA_SMRY['Act Shipped Qty']*KLA_SMRY['DELTA.CAL']
KLA_SMRY_QTR=KLA_SMRY.pivot_table(index=['QTR'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
KLA_SMRY_QTR.reset_index(inplace=True)
KLA_SMRY_QTR.rename(columns={'QTR':'PERIOD'},inplace=True)
KLA_SMRY_P=KLA_SMRY.pivot_table(index=['FISCAL PERIOD'],values=['$SOLD','BUILD COST','P/L'],aggfunc=np.sum)
KLA_SMRY_P.reset_index(inplace=True)
KLA_SMRY_P.rename(columns={'FISCAL PERIOD':'PERIOD'},inplace=True)
KLA_SMRY_P=pd.concat([KLA_SMRY_QTR,KLA_SMRY_P],ignore_index=True)
KLA_SMRY_P['P/L%']=KLA_SMRY_P['P/L']/KLA_SMRY_P['$SOLD']
KLA_SMRY_P=KLA_SMRY_P.melt(id_vars=['PERIOD','P/L','P/L%'],var_name='$SOLD/BUILD COST',value_name='USD (Millions)')
KLA_SMRY_LINE=KLA_SMRY_P[['PERIOD','P/L%']].drop_duplicates()
KLA_SMRY_L_Q=KLA_SMRY_LINE.loc[KLA_SMRY_LINE['PERIOD'].str.contains('QTR')]
KLA_SMRY_L_P=KLA_SMRY_LINE.loc[KLA_SMRY_LINE['PERIOD'].str.contains('Period')]

LM_CHART = px.bar(
data_frame=LM_SMRY_P,
x='PERIOD',y='USD (Millions)',
barmode='group',
color='$SOLD/BUILD COST',
color_discrete_map={'$SOLD':'#7eb6f2','BUILD COST':'#f27ee5'},
hover_data={'P/L%':':.2%'},
title='LAM',
template='seaborn',text_auto='.2s',
)
LM_CHART.update_traces(textposition='outside')
LM_CHART.update_layout(title = dict(
yanchor='bottom', x=0.5,y=.85,font_size=30),
font={'family':'Arial Black','size':12},
yaxis_tickprefix='$',
yaxis={'dtick':1000000},
legend=dict(orientation='v',x=.8,y=1.1,
        xanchor='right',yanchor='top',title=None,
        bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)')
LM_CHART.add_trace(go.Scatter(x=LM_SMRY_L_Q['PERIOD'],
y=LM_SMRY_L_Q['P/L%'],yaxis='y2',name='P/L% BY QTR',
line=dict(color='#3005f0',width=2),
mode='lines+markers+text',
text=LM_SMRY_L_Q['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
LM_CHART.add_trace(go.Scatter(x=LM_SMRY_L_P['PERIOD'],
y=LM_SMRY_L_P['P/L%'],yaxis='y2',name='P/L% BY MONTH',
line=dict(color='#b305f7',width=2),
mode='lines+markers+text',
text=LM_SMRY_L_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
LM_CHART.update_layout( 
        yaxis2=dict(
        range=[-.4,.4],
        title='PROFIT-LOSS%',
        tickformat= ',.0%',
        anchor="free",  # specifying x - axis has to be the fixed
        overlaying="y",  # specifyinfg y - axis has to be separated
        side="right",  # specifying the side the axis should be present
        position=1  # specifying the position of the axis
    ))


CY_CHART = px.bar(
data_frame=CY_SMRY_P,
x='PERIOD',y='USD (Millions)',
barmode='group',
color='$SOLD/BUILD COST',
color_discrete_map={'$SOLD':'#7eb6f2','BUILD COST':'#f27ee5'},
hover_data={'P/L%':':.2%'},
title='CYMER',
template='seaborn',text_auto='.2s',
)
CY_CHART.update_traces(textposition='outside')
CY_CHART.update_layout(title = dict(
yanchor='bottom', x=0.5,y=.85,font_size=30),
font={'family':'Arial Black','size':12},
yaxis_tickprefix='$',
yaxis={'dtick':1000000},
legend=dict(orientation='v',x=.8,y=1.1,
        xanchor='right',yanchor='top',title=None,
        bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)')
CY_CHART.add_trace(go.Scatter(x=CY_SMRY_L_Q['PERIOD'],
y=CY_SMRY_L_Q['P/L%'],yaxis='y2',name='P/L% BY QTR',
line=dict(color='#3005f0',width=2),
mode='lines+markers+text',
text=CY_SMRY_L_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
CY_CHART.add_trace(go.Scatter(x=CY_SMRY_L_P['PERIOD'],
y=CY_SMRY_L_P['P/L%'],yaxis='y2',name='P/L% BY MONTH',
line=dict(color='#b305f7',width=2),
mode='lines+markers+text',
text=CY_SMRY_L_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
CY_CHART.update_layout( 
        yaxis2=dict(
        range=[-.4,.2],
        title='PROFIT-LOSS%',
        tickformat= ',.0%',
        anchor="free",  # specifying x - axis has to be the fixed
        overlaying="y",  # specifyinfg y - axis has to be separated
        side="right",  # specifying the side the axis should be present
        position=1  # specifying the position of the axis
    ))

KLA_CHART = px.bar(
data_frame=KLA_SMRY_P,
x='PERIOD',y='USD (Millions)',
barmode='group',
color='$SOLD/BUILD COST',
color_discrete_map={'$SOLD':'#7eb6f2','BUILD COST':'#f27ee5'},
hover_data={'P/L%':':.2%'},
title='KLA',
template='seaborn',text_auto='.2s',
)
KLA_CHART.update_traces(textposition='outside')
KLA_CHART.update_layout(title = dict(
yanchor='bottom', x=0.5,y=.85,font_size=30),
yaxis_tickprefix='$',
font={'family':'Arial Black','size':12},
yaxis={'dtick':1000000},
legend=dict(orientation='v',x=.8,y=1.1,
        xanchor='right',yanchor='top',title=None,
        bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)')
KLA_CHART.add_trace(go.Scatter(x=KLA_SMRY_L_Q['PERIOD'],
y=KLA_SMRY_L_Q['P/L%'],yaxis='y2',name='P/L% BY QTR',
line=dict(color='#3005f0',width=2),
mode='lines+markers+text',
text=KLA_SMRY_L_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
KLA_CHART.add_trace(go.Scatter(x=KLA_SMRY_L_P['PERIOD'],
y=KLA_SMRY_L_P['P/L%'],yaxis='y2',name='P/L% BY MONTH',
line=dict(color='#b305f7',width=2),
mode='lines+markers+text',
text=KLA_SMRY_L_P['P/L%'].apply(lambda x: str(round(x*100,2))+'%').to_list(),
textposition='top center'))
KLA_CHART.update_layout( 
        yaxis2=dict(
        range=[-.4,.5],
        title='PROFIT-LOSS%',
        tickformat= ',.0%',
        anchor="free",  # specifying x - axis has to be the fixed
        overlaying="y",  # specifyinfg y - axis has to be separated
        side="right",  # specifying the side the axis should be present
        position=1  # specifying the position of the axis
    ))

layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDERFRS',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'7vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
      dbc.Row(
        dbc.Col([
        dcc.Graph(figure=LM_CHART,
        style={'padding-left':'2vw','width': '45vw','height':'45vh','display':'inline-block'}),
        dcc.Graph(figure=CY_CHART,
        style={'padding-left':'5vw','width': '45vw','height':'45vh','display':'inline-block'})],
    )),
    dbc.Row(
        dbc.Col([
        dcc.Graph(figure=KLA_CHART,
        style={'padding-left':'2vw','width': '45vw','height':'45vh','display':'inline-block'})],
    )),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)