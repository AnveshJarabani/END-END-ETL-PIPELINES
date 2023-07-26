import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
def costby_bom(DF,PART):
    LVLBOM=BOM_EXTRACT(PART)
    REL_CLM=DF.columns[4]
    CST_CLM=DF.columns[2]
    PN=DF.columns[1]
    DT_LBR=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
    DT_LBR=DT_LBR.loc[DT_LBR[REL_CLM].notna()]
    DT_LBR[REL_CLM]=DT_LBR[REL_CLM]*DT_LBR['TOP LVL QTY']
    DT_LBR=DT_LBR.pivot_table(index=['Q+YR','TOPLEVEL'],values=[CST_CLM,REL_CLM],aggfunc=np.sum)
    DT_LBR.reset_index(inplace=True)
    DT_LBR.rename(columns={'TOPLEVEL':'PN'},inplace=True)
    DT_LBR=DT_LBR[['Q+YR','PN',CST_CLM,REL_CLM]]
    DT_LBR=sort_QS(DT_LBR)
    return DT_LBR
def costby_buy_bom(DF,PART):
    LVLBOM=BOM_EXTRACT(PART)
    REL_CLM=DF.columns[4]
    CST_CLM=DF.columns[2]
    PN=DF.columns[1]
    DT_BUY=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
    DT_BUY=DT_BUY.loc[DT_BUY[REL_CLM].notna()]
    DT_BUY=DT_BUY[['Q+YR','PN',CST_CLM,REL_CLM]].drop_duplicates()
    DT_BUY.reset_index(inplace=True,drop=True)
    DT_BUY.rename(columns={'TOPLEVEL':'PN'},inplace=True)
    DT_BUY=sort_QS(DT_BUY)
    return DT_BUY
def sort_QS(DF):
    pi=DF.merge(QS,left_on='Q+YR',right_on='Q+YR',how='left')
    pi.sort_values(by=['YR','MONTH'],ascending=True,inplace=True)
    pi=pi[DF.columns]
    pi.drop_duplicates(inplace=True)
    return pi
 #BOM EXTRACT-----------
def BOM_EXTRACT(PN):
    LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
    # BOM EXTRACT ----------------------------------------
    if (PH['PH']==PN).any():
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
    else:
        BM = BOM[BOM['MATERIAL']==PN].reset_index(drop=True)
        x = 0
        while x <= (len(BM.index)-1) :
            if BM.iloc[x,1] in PH['PH'].values:
                x +=1
                continue
            nx = BOM[BOM['MATERIAL']==BM.iloc[x, 1]].reset_index(drop=True)
            BM = pd.concat([BM,nx],axis = 0)
            x +=1
        BM.reset_index(drop=True, inplace=True)
        BM.loc[-1] = [PN,PN,1]
        BM.index = BM.index + 1
        BM = BM.sort_index()
        BM.columns = ['MATERIAL', 'COMP', 'QTY']
        # TOOL QTY ----------------------------------------
        BM['TOP LVL QTY'] = BM[BM['MATERIAL']==PN]['QTY']
        BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
        x = BM.where(BM['MATERIAL']==PN).last_valid_index() + 1
        BM.iloc[:x-1,3] = BM.iloc[:x-1,2]
        for k in range(x,len(BM.index)):
            y = sum(BM.iloc[:k+1,4]==BM.iloc[k,4])
            t = 0    
            for l in range(0,k):
                if BM.iloc[l,1] == BM.iloc[k,0]:
                    t +=1    
                    if t ==y:
                        BM.iloc[k,3] = BM.iloc[l,3]*BM.iloc[k,2]
        BM.insert(0,'TOPLEVEL',PN)
        BM = BM.iloc[:,:5]
        LVLBOMS = pd.concat([LVLBOMS,BM],ignore_index=True)
    LVLBOMS=LVLBOMS[LVLBOMS['TOPLEVEL'].notnull()]
    LVLBOMS=LVLBOMS.loc[~LVLBOMS['COMP'].str.endswith('-UCT',na=False)]
    LVLBOMS=LVLBOMS.pivot_table(index=['TOPLEVEL','COMP'],values=['TOP LVL QTY'],aggfunc=np.sum)
    LVLBOMS.reset_index(inplace=True)
    return LVLBOMS
def fig(PN,DT_PN):
        # CST_22=DT_PN.iloc[-1,2]
        # CST_21=DT_PN.iloc[-5,2]
        # CHANGE=(CST_22-CST_21)/CST_21
        graph=px.bar(
        DT_PN,x='Q+YR',y='DELTA %',
        hover_data={'PN':True,'DELTA %':True},
        template='seaborn',text_auto=True,
        labels={'Q+YR': '<b>Y.LY QUARTERS','DELTA %':'<b> QLY RELATIVE COST TREND'})
        graph.update_traces(textfont_size=16)
        graph.update_layout(title = dict(text='<b>'+PN + ' BUY Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%') 
        graph.update_yaxes(tickfont_family="Arial Black")
        graph.update_xaxes(tickfont_family="Arial Black")
        # graph.add_hline(y=CHANGE,line_dash='dot',
        # annotation_text='<b>% CHANGE in 2022: '+str(('{:.2f}%').format(CHANGE*100)),
        # annotation_position='top left',line=dict(color='blue',width=2.5))
        return graph
dash.register_page(__name__)
LBR_COSTS_REL=pd.read_hdf('../H5/LBR.H5',key='Q_TRENDS')
OVS_COSTS_REL=pd.read_hdf('../H5/OVS.H5',key='TREND')
PH_COSTS_REL=pd.read_hdf('../H5/PH.H5',key='TREND')
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
            html.H2('QLY RELATIVE COST TRENDS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':4}),
        dbc.Col([
        dcc.Input(id='PART-COSTS_REL', 
        debounce=True,
        value='CY-133400',
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Collapse(dbc.Row(
        dbc.Col([
        dcc.Graph(id='LBR_COSTS_REL',
        style={'padding-left':'30px','width': '40vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='OVS_COSTS_REL',
        style={'padding-left':'60px','width': '40vw','height':'50vh','display':'inline-block'})
        ]
        ,width={'offset':1})),id='hide_1',is_open=True),        
    dbc.Row([
        dbc.Col([
    dcc.Loading(html.Div(id='1set_rel',children=[]),type='dot',fullscreen=True),
    ],width={'offset':1,'size':3}),
    dbc.Col([
    html.Div(id='2set_rel',children=[])
    ],width={'offset':2,'size':3})
    ]),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('LBR_COSTS_REL','figure'),
    Output('OVS_COSTS_REL','figure'),
    Output('1set_rel','children'),
    Output('2set_rel','children'),
    Output('hide_1','is_open'),
    Input('PART-COSTS_REL','value'),
 )
def update_graph(PART):
    DT_LBR=costby_bom(LBR_COSTS_REL,PART)
    DT_OVS=costby_bom(OVS_COSTS_REL,PART)
    DT_PH=costby_buy_bom(PH_COSTS_REL,PART)
    is_open=True
    if len(DT_LBR)==0:
        LBR=px.bar()
        is_open=False
    else:
        # CST_22=DT_LBR.iloc[-1,2]
        # CST_21=DT_LBR.iloc[-5,2]
        # CHANGE=(CST_22-CST_21)/CST_21
        LBR = px.bar(
            DT_LBR,x='Q+YR',y='DELTA %',
            hover_data={'PN':True,'DELTA %':True},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','DELTA %':'<b> ACT LABOR RELATIVE COST TREND'}
            )
        LBR.update_traces(textfont_size=16)
        LBR.update_layout(title = dict(text='<b>'+PART + ' Labor Trend (Includes Subs)',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%')
        LBR.update_yaxes(tickfont_family="Arial Black")
        LBR.update_xaxes(tickfont_family="Arial Black")
        # LBR.add_hline(y=CHANGE,line_dash='dot',
        # annotation_text='<b>% CHANGE in 2022: '+str(('{:.2f}%').format(CHANGE*100)),
        # annotation_position='top left',line=dict(color='blue',width=2.5))
    if len(DT_OVS)==0:
        OVS=px.bar()
        OVS.update_layout(title = dict(text='<b>'+PART + ' has NO OVS Cost',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12})
    else:
        # CST_22=DT_OVS.iloc[-1,2]
        # CST_21=DT_OVS.iloc[-5,2]
        # CHANGE=(CST_22-CST_21)/CST_21
        OVS = px.bar(
            DT_OVS,x='Q+YR',y='DELTA %',
            hover_data={'PN':True,'DELTA %':True},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','DELTA %':'<b> OVS COST RELATIVE TREND'}
            )
        OVS.update_traces(textfont_size=16)
        OVS.update_layout(title = dict(text='<b>'+PART + ' OVS Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%')
        OVS.update_xaxes(tickfont_family="Arial Black")
        OVS.update_yaxes(tickfont_family="Arial Black")
        # OVS.add_hline(y=CHANGE,line_dash='dot',
        # annotation_text='<b>% CHANGE in 2022: '+str(('{:.2f}%').format(CHANGE*100)),
        # annotation_position='top left',line=dict(color='blue',width=2.5))
    gs1=[]
    gs2=[]
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