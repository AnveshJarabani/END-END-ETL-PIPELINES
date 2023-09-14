import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from app_files.sql_connector import table as sql,query_table
# dash.register_page(__name__)
smry_dct={'LAM':'toolcosts_lm_smry',
          'KLA':'toolcosts_kla_smry',
          'CYMER':'toolcosts_cy_smry',}
LAM_PIE=sql('TOOLCOSTS_LM_PIE')
LAM_ACTQTDT=sql('TOOLCOSTS_LM_QT_VS_ACT')
LAM_ACTQTDT['VENDOR']=LAM_ACTQTDT['VENDOR'].str[:10]
CYMER_PIE=sql('TOOLCOSTS_CY_PIE')
CYMER_ACTQTDT=sql('TOOLCOSTS_CY_QT_VS_ACT')
KLA_PIE=sql('TOOLCOSTS_KLA_PIE')
KLA_ACTQTDT=sql('TOOLCOSTS_KLA_QT_VS_ACT')
KLA_ACTQTDT['VENDOR']=KLA_ACTQTDT['VENDOR'].str[:10]
new_cols=['TOP LEVEL','PN','DESC','VENDOR','QTY']
for i in [KLA_ACTQTDT,CYMER_ACTQTDT,LAM_ACTQTDT]:
    i.columns=new_cols+list(i.columns[len(new_cols):])
KLA_ACTQTDT.rename(columns={'DELTA T3':'DELTA'},inplace=True)
PIE_COST=pd.concat([LAM_PIE,CYMER_PIE,KLA_PIE])


PERIODS=sql('FISCAL_CAL')
PERIODS.drop_duplicates(inplace=True,ignore_index=True)
QTR=PERIODS.loc[PERIODS['FISCAL PERIOD']=='Period 9','QTR'].reset_index().iloc[0,1]
PIE_COST_P=PIE_COST.loc[PIE_COST['QTR']==QTR]
PIE_COST_P=PIE_COST_P.iloc[:,:4]
PIE_COST_P=PIE_COST_P.transpose().reset_index()
PIE_COST_P.columns=PIE_COST_P.iloc[0]
PIE_COST_P=PIE_COST_P.drop(index=0)
def add_color(CUST):
    CUST.rename(columns={'Material - Key':'PART NUMBER',
                'Act Shipped Qty':'QTY Shipped'},inplace=True)
    CUST.reset_index(inplace=True)
    CUST.sort_values(by=['DELTA.CAL'],ignore_index=True,ascending=True,inplace=True)
    CUST['P/L%']=(CUST['DELTA.CAL']/CUST['ASP'])
    conditions=[CUST['DELTA.CAL']<0,
                CUST['DELTA.CAL']>0]
    choices=['red','green']
    CUST['COLOR']=np.select(conditions,choices)
    return CUST
# for i in [LAM_SMRY,CYMER_SMRY,KLA_SMRY]:
#     add_color(i)
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDER',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('TOOL COSTS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':3}),
        dbc.Col([
        dcc.Dropdown(id='CUSTOMERS', multi= False,
        options=['LAM','CYMER','KLA'],
        value='LAM',
        placeholder='Select Customer...',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':4}),
        dbc.Col([
        dcc.Dropdown(id='PERIOD', multi= False,
        options=['Period 1','Period 2','Period 3','Period 4','Period 5','Period 6',
                'Period 7','Period 8','Period 9','Period 10','Period 11','Period 12'],
        value='Period 9',
        placeholder='Select FISCAL MONTH',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':2})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='P/LGRAPH',
        style={'padding-left':'30px','width': '65vw','height':'70vh','display':'inline-block'}),
        dcc.Graph(id='pie',style={'padding-left':'50px','width': '25vw','height':'70vh','display':'inline-block'})],
    )),
    dbc.Col(dbc.Button(id='btn',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':2,'offset':11},style={'padding-bottom':'10px'}),
    dcc.Download(id='download-comp'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='QTVSACT'),type='dot',fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('P/LGRAPH','figure'),
    Input('CUSTOMERS','value'),
    Input('PERIOD','value'),
 )
def update_graph(CUSTOMER,PERIOD):
    global PIE_COST_P
    CUST=query_table(f'SELECT * FROM {smry_dct[CUSTOMER]} WHERE `FISCAL PERIOD`=\'{PERIOD}\'')
    add_color(CUST)
    SHIPPED=(CUST['DELTA.CAL']*CUST['QTY Shipped']).sum()
    ACTUALCOST=(CUST['ASP']*CUST['QTY Shipped']).sum()
    wtavg=SHIPPED/ACTUALCOST
    barchart1 = px.bar(
        data_frame=CUST,
        x='PART NUMBER',
        y='DELTA.CAL',
        hover_data={'COLOR':False,'ASP':':$,.2f','P/L%':':.2%',
        'DELTA.CAL':':$,.2f'},
        text='QTY Shipped',
        template='seaborn',
        labels={'DELTA.CAL':'<b>PROFIT/LOSS PER EA<b>','PART NUMBER': '<b>PART NUMBER<b>'},
        color=CUST['COLOR'],
        color_discrete_sequence= CUST['COLOR'].unique()
        )
    barchart1.update_traces(textposition='outside')
    barchart1.add_annotation(dict(text='<b>WEIGHTED AVG% = '+str('{:.2%}'.format(wtavg)),
    showarrow=False,xref='paper',yref='paper',x=.5,y=.9,font={'size':20}))
    barchart1.update_layout(title = dict(text='<b>'+CUSTOMER+" " +'<b>TOOL PERFORMANCE',
        yanchor='bottom', x=0.5,y=.95,font_size=30),
        font={'family':'Arial','size':12},
        yaxis_tickformat='$,',
        yaxis={'dtick':1000},
        showlegend=False)
    QTR=PERIODS.loc[PERIODS['FISCAL PERIOD']==PERIOD,'QTR'].reset_index().iloc[0,1]
    PIE_COST_P=PIE_COST.loc[PIE_COST['QTR']==QTR]
    PIE_COST_P=PIE_COST_P.iloc[:,:4]
    PIE_COST_P=PIE_COST_P.transpose().reset_index()
    PIE_COST_P.columns=PIE_COST_P.iloc[0]
    PIE_COST_P=PIE_COST_P.drop(index=0)
    return barchart1
@callback(Output('pie','figure'),
    Input('P/LGRAPH','hoverData'))
def pie_table(hov_data):
    if hov_data is None:
        x='853-289353-007'
    else:
        x=hov_data['points'][0]['x']
    piechart=px.pie(data_frame=PIE_COST_P,values=x,names='TOP LEVEL',color='TOP LEVEL',
    hover_name='TOP LEVEL',
    labels={'TOP LEVEL':'BUILD COST'},
    title='<b>'+x+' <b>BUILD COSTS',template='presentation')
    piechart.update_traces(text=PIE_COST_P[x].map("${:,.1f}".format),textinfo='label+text+percent',
    texttemplate = '<b>%{label}</br></br>%{text}</b></br>%{percent}</b>',textposition='auto')
    piechart.update_layout(title_x=0.5,title_y=0.05,
    font={'family':'Arial','size':18,},title_font_size=20,
    showlegend=False)
    return piechart
@callback(
    Output('QTVSACT','figure'),
    Input('P/LGRAPH','clickData')
)
def table(clk_data):
    global dt,y
    if clk_data is None:
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        QTVSACT = ff.create_table([CYMER_ACTQTDT.columns],colorscale=colorscale)
    else:
        y=clk_data['points'][0]['x']
        for i in [KLA_ACTQTDT,CYMER_ACTQTDT,LAM_ACTQTDT]:
            if (i.iloc[:,0]==y).any():
                dt=i.loc[i['TOP LEVEL']==str(y)]
                continue
        dt.drop(columns=['TOP LEVEL','DESC'],axis=1,inplace=True)
        dt.iloc[:,4:] = dt.iloc[:,4:].apply(lambda series: series.apply(lambda x: "${:,.2f}".format(float(x))))
        dt.sort_values(by='DELTA',ascending=True,inplace=True)
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        QTVSACT = ff.create_table(dt,colorscale=colorscale)
        QTVSACT.update_layout(font={'family':'Arial Black','size':12})
    return QTVSACT
@callback(
    Output('download-comp','data'),
    Input('btn','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(dt.to_excel,'QUOTE VS ACT '+str(y)+'.xlsx',index=False,engine='xlsxwriter')
