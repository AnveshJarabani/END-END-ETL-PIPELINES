import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from app_files.tree_to_df import tree_to_df
def costby_bom(DF,PART):
    LVLBOM=BOM_EXTRACT(PART)
    COST_CLM=DF.columns[2]
    PN=DF.columns[1]
    DT_LBR=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
    DT_LBR=DT_LBR.loc[DT_LBR[COST_CLM].notna()]
    DT_LBR[COST_CLM]=DT_LBR[COST_CLM]*DT_LBR['TOP LVL QTY']
    DT_LBR=DT_LBR.pivot_table(index=['Q+YR','TOPLEVEL'],values=[COST_CLM],aggfunc=np.sum)
    DT_LBR.reset_index(inplace=True)
    DT_LBR.rename(columns={'TOPLEVEL':'PN'},inplace=True)
    DT_LBR=sort_QS(DT_LBR)
    return DT_LBR
def costby_buy_bom(DF,PART):
    LVLBOM=BOM_EXTRACT(PART)
    COST_CLM=DF.columns[2]
    PN=DF.columns[1]
    DT_LBR=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
    DT_LBR=DT_LBR.loc[DT_LBR[COST_CLM].notna()]
    DT_LBR=DT_LBR[['Q+YR','PN',COST_CLM]].drop_duplicates()
    DT_LBR.reset_index(inplace=True,drop=True)
    DT_LBR.rename(columns={'TOPLEVEL':'PN'},inplace=True)
    DT_LBR=sort_QS(DT_LBR)
    return DT_LBR
def sort_QS(DF):
    pi=DF.merge(QS,left_on='Q+YR',right_on='Q+YR',how='left')
    pi.sort_values(by=['YR','MONTH'],ascending=True,inplace=True)
    pi=pi[DF.columns]
    pi.drop_duplicates(inplace=True)
    return pi
 #BOM EXTRACT-----------
def BOM_EXTRACT(PN):
    #___________BOMEXTRACT_________________________________________________
    LVLBOMS=tree_to_df(PN)
    LVLBOMS['TOPLEVEL']=PN
    LVLBOMS=LVLBOMS[['TOPLEVEL','PARENT','PN','QTY','TQ']]
    LVLBOMS.columns=['TOPLEVEL', 'MATERIAL', 'COMP', 'QTY', 'TOP LVL QTY']
    LVLBOMS=LVLBOMS.pivot_table(index=['TOPLEVEL','COMP'],values=['TOP LVL QTY'],aggfunc=np.sum)
    LVLBOMS.reset_index(inplace=True)
    return LVLBOMS
def fig(PN,DT_PN):
        graph=px.bar(
        DT_PN,x='Q+YR',y='BUY COST',
        hover_data={'PN':True,'BUY COST':':$,.2f'},
        template='seaborn',text_auto=True,
        labels={'Q+YR': '<b>Y.LY QUARTERS','BUY COST':'<b> BUY COST TREND (QLY. AVG.)'})
        graph.update_traces(textfont_size=16)
        graph.update_layout(title = dict(text='<b>'+PN + ' BUY Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='$,')
        graph.update_yaxes(tickfont_family="Arial Black")
        graph.update_xaxes(tickfont_family="Arial Black")
        return graph
dash.register_page(__name__)
LBR_COSTS=pd.read_hdf('../H5/LBR.H5',key='Q_TRENDS')
LBR_COSTS.rename(columns={'Q+YR':'Q+YR'},inplace=True)
OVS_COSTS=pd.read_hdf('../H5/OVS.H5',key='TREND')
PH_COSTS=pd.read_hdf('../H5/PH.H5',key='TREND')
PH=pd.read_pickle('../PKL/PH.PKL')
BOM=pd.read_hdf('../H5/ST_BM_BR.H5',key='BOM')
QS=pd.read_pickle('../PKL/QLY_INTS.PKL')
layout = dbc.Container([
  dbc.Row([
        dbc.Col([
        html.H1('PLACEHOLDER',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'15vh',
        'font-size':50,'display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('QUARTERLY COST TRENDS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':4}),
        dbc.Col([
        dcc.Input(id='PART-COSTS', 
        debounce=True,
        value='CY-133400',
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Collapse(dbc.Row(
        dbc.Col([
        dcc.Graph(id='LBR_COSTS',
        style={'padding-left':'30px','width': '40vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='OVS_COSTS',
        style={'padding-left':'60px','width': '40vw','height':'50vh','display':'inline-block'})
        ]
        ,width={'offset':1})),id='hide',is_open=True),        
    dbc.Row([
        dbc.Col([
    dcc.Loading(html.Div(id='1set',children=[]),type='dot',fullscreen=True),
    ],width={'offset':1,'size':3}),
    dbc.Col([
    html.Div(id='2set',children=[])
    ],width={'offset':2,'size':3})
    ]),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('LBR_COSTS','figure'),
    Output('OVS_COSTS','figure'),
    Output('1set','children'),
    Output('2set','children'),
    Output('hide','is_open'),
    Input('PART-COSTS','value'),
 )
def update_graph(PART):
    PART=PART.strip().upper()
    DT_LBR=costby_bom(LBR_COSTS,PART)
    DT_OVS=costby_bom(OVS_COSTS,PART)
    DT_PH=costby_buy_bom(PH_COSTS,PART)
    is_open=True
    if len(DT_LBR)==0:
        LBR=px.bar()
        is_open=False
    else:
        LBR = px.bar(
            DT_LBR,x='Q+YR',y='ACT LBR COST/EA',
            hover_data={'PN':True,'ACT LBR COST/EA':':$,.2f'},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','ACT LBR COST/EA':'<b> ACT LABOR COST TREND (QLY. AVG.)'}
            )
        LBR.update_traces(textfont_size=16)
        LBR.update_layout(title = dict(text='<b>'+PART + ' Labor Trend (Includes Subs)',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='$,')
        LBR.update_yaxes(tickfont_family="Arial Black")
        LBR.update_xaxes(tickfont_family="Arial Black")
    if len(DT_OVS)==0:
        OVS=px.bar()
        OVS.update_layout(title = dict(text='<b>'+PART + ' has NO OVS Cost',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12})
    else:
        OVS = px.bar(
            DT_OVS,x='Q+YR',y='OVS COST',
            hover_data={'PN':True,'OVS COST':':$,.2f'},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','OVS COST':'<b> OVS COST TREND (QLY. AVG.)'}
            )
        OVS.update_traces(textfont_size=16)
        OVS.update_layout(title = dict(text='<b>'+PART + ' OVS Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='$,')
        OVS.update_xaxes(tickfont_family="Arial Black")
        OVS.update_yaxes(tickfont_family="Arial Black")
    gs1 , gs2 = [] , []
    m=1
    if len(DT_PH['PN'].unique())!=1:
        DT_PH=DT_PH.loc[DT_PH['BUY COST']>10]
    for i in DT_PH['PN'].unique():
        DT_PN=DT_PH.loc[DT_PH['PN']==i]
        if (m%2)!=0:
            gs1.append(dcc.Graph(id='graph-{}'.format(i),figure=fig(i,DT_PN),
            style={'padding-left':'30px','width': '40vw','height':'50vh','display':'inline-block'}))
        else:
            gs2.append(dcc.Graph(id='graph-{}'.format(i),figure=fig(i,DT_PN),
            style={'padding-left':'60px','width': '40vw','height':'50vh','display':'inline-block'}))
        m+=1
    ht1= html.Div(gs1)
    ht2= html.Div(gs2)
    return LBR,OVS,ht1,ht2,is_open