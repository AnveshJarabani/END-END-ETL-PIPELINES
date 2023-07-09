import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from app_files.tree_to_df import tree_to_df
dash.register_page(__name__)
BOM=pd.read_hdf('../H5/ST_BM_BR.H5',key='BOM')
FRAMECOSTS=pd.read_pickle('../PKL/FRAME.COSTS.PKL')
FRAMECOSTS.iloc[:,1] = FRAMECOSTS.iloc[:,1].astype(str)
PIE_COST=pd.read_pickle('../PKL/FRAMES_PIE.PKL')
PIE_COST=PIE_COST.transpose().reset_index()
PIE_COST.columns=PIE_COST.iloc[0]
PIE_COST=PIE_COST.drop(index=0)
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDERFRS',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('PART COSTS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':3}),
        dbc.Col([
        dcc.Input(id='PART', 
        debounce=True,
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='pie_part',style={'width': '25vw','height':'70vh','display':'inline-block'})],
    width={'offset':4})),
    dbc.Col(dbc.Button(id='BTN_PN',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':2,'offset':11},style={'padding-bottom':'10px'}),
    dcc.Download(id='download-prcomp'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='PARTCOSTS'),type='dot',fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(Output('pie_part','figure'),
    Output('PARTCOSTS','figure'),
    Input('PART','value'))
def pie_table(PN):
    global COSTS
    global PART_NM
    PART_NM=PN
    if PN is None:
        PN='UC-66-112093-00'
    PN=PN.strip().upper()
    PH = pd.read_hdf('../H5/PH.H5',key='PH')
    PH.rename(columns={'Material - Key':'PH'},inplace=True)
    # ___________BOMEXTRACT_________________________________________________
    LVLBOMS=tree_to_df(PN)
    LVLBOMS['TOPLEVEL']=PN
    LVLBOMS=LVLBOMS[['TOPLEVEL','PARENT','PN','QTY','TQ']]
    LVLBOMS.columns=['TOPLEVEL', 'MATERIAL', 'COMP', 'QTY', 'TOP LVL QTY']
    # ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
    STD=pd.read_hdf('../H5/ST_BM_BR.H5',key="STD")
    LBR = pd.read_hdf('../H5/LBR.H5',key="ACT_V_PL_CST")
    OVS = pd.read_hdf("../H5/OVS.H5",key='OVS')
    COSTS = LVLBOMS.merge(PH,left_on='COMP',right_on='PH',how='left')
    COSTS.drop(columns=['PH'],axis=1,inplace=True)
    COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
    def colrename():
        COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
        COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
    colrename()
    COSTS.fillna(0,inplace=True)
    COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
    COSTS = COSTS.iloc[:,:6]
    COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
    COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
    COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
    COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
    COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
    COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
    colrename()
    COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
    COSTS=COSTS.fillna(0)
    COSTS['BUR ACT MAT']=1.106*COSTS['ACT MAT COST']
    PIE_COST=COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT', 'ACT LBR COST', 'OVS COST'],aggfunc=np.sum)
    PIE_COST.reset_index(inplace=True)
    PIE_COST=PIE_COST.transpose().reset_index()
    PIE_COST.columns=PIE_COST.iloc[0]
    PIE_COST=PIE_COST.drop(index=0)
    SUM_COST=PIE_COST.sum()
    te='<b>ACTUAL COST = <b>' + str('${:,.1f}'.format(SUM_COST[1]))
    piechart=px.pie(data_frame=PIE_COST,values=PN,names='TOPLEVEL',color='TOPLEVEL',
    hover_name='TOPLEVEL',
    labels={'TOPLEVEL':'BUILD COST'},
    title='<b>'+PN+' <b>'+te,template='presentation')
    piechart.update_traces(text=PIE_COST[PN].map("${:,.1f}".format),textinfo='label+text+percent',
    texttemplate = '<b>%{label}</br></br>%{text}</b></br>%{percent}</b>',
    textposition='auto')
    piechart.update_layout(title_x=0.5,title_y=0.1,
    font={'family':'Arial','size':18,},title_font_size=20,
    showlegend=False)
    COSTS=COSTS.pivot_table(index=['TOPLEVEL','MATERIAL','COMP'],values=['TOP LVL QTY','BUR ACT MAT','ACT LBR COST','OVS COST'],aggfunc=np.sum)
    COSTS.reset_index(inplace=True)
    COSTS=COSTS[['TOPLEVEL','MATERIAL','COMP','TOP LVL QTY','BUR ACT MAT','ACT LBR COST','OVS COST']]
    COSTS.iloc[:,3:4] = COSTS.iloc[:,3:4].apply(lambda series: series.apply(lambda x: "{:,.2f}".format(float(x))))
    COSTS.iloc[:,4:] = COSTS.iloc[:,4:].apply(lambda series: series.apply(lambda x: "${:,.2f}".format(float(x))))
    colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
    TABLE = ff.create_table(COSTS,colorscale=colorscale)
    TABLE.update_layout(font={'family':'Arial Black','size':12})
    return piechart,TABLE
@callback(
    Output('download-prcomp','data'),
    Input('BTN_PN','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(COSTS.to_excel,f'{PART_NM} ACTUAL COST.xlsx',index=False,engine='xlsxwriter')