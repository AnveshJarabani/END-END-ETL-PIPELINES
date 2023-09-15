import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
from app_files.sql_connector import table,query_table,drop,temp_table
from app_files.tree_to_df import tree_to_df
def costby_bom(name,PART):
    cols={
    'ovs_trend':['OVS COST','Q+YR','MATERIAL'],
    'lbr_q_trends':['ACT LBR COST/EA','Q+YR','PN'],
    'ph_trend':['BUY COST','Q+YR','PN']}
    LVLBOM=BOM_EXTRACT(PART)
    temp_table(LVLBOM)
    if name in ('ovs_trend','lbr_q_trends'):
        str=f'''
                WITH CTE AS (select *,
                `{cols[name][0]}`*`TOP LVL QTY` as COST_CLM,
                `QLY_DELTA`*`TOP LVL QTY` as `REL_CLM`
                from temp tp
                join {name.lower()} df on df.`{cols[name][2]}`=tp.`COMP`
                WHERE `{cols[name][0]}` is not null)
                SELECT `{cols[name][1]}`,`TOPLEVEL` AS `PN`,SUM(`COST_CLM`) AS `QLY_COST`,
                ROUND(SUM(`REL_CLM`),2) AS `QLY_DELTA`
                FROM CTE
                GROUP BY 1,2
                '''
        DT=query_table(str)
    else:
        DT=query_table(f"""
                            select `Q+YR`,`PN`,
                            `{cols[name][0]}` as QLY_COST,
                            `QLY_DELTA` from temp tp
                            join {name.lower()} df on df.`{cols[name][2]}`=tp.`COMP`
                            WHERE `{cols[name][0]}` is not null
                            """)
    drop('temp')
    # LVLBOM=BOM_EXTRACT(PART)
    # REL_CLM=DF.columns[4]
    # CST_CLM=DF.columns[2]
    # PN=DF.columns[1]
    # DT_LBR=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
    # DT_LBR=DT_LBR.loc[DT_LBR[REL_CLM].notna()]
    # DT_LBR[REL_CLM]=DT_LBR[REL_CLM]*DT_LBR['TOP LVL QTY']
    # DT_LBR=DT_LBR.pivot_table(index=['Q+YR','TOPLEVEL'],values=[CST_CLM,REL_CLM],aggfunc=np.sum)
    # DT_LBR.reset_index(inplace=True)
    # DT_LBR.rename(columns={'TOPLEVEL':'PN'},inplace=True)
    # DT_LBR=DT_LBR[['Q+YR','PN',CST_CLM,REL_CLM]]
    return DT
# def costby_buy_bom(DF,PART):
#     LVLBOM=BOM_EXTRACT(PART)
#     REL_CLM=DF.columns[4]
#     CST_CLM=DF.columns[2]
#     PN=DF.columns[1]
#     DT_BUY=LVLBOM.merge(DF,left_on='COMP',right_on=PN,how='left')
#     DT_BUY=DT_BUY.loc[DT_BUY[REL_CLM].notna()]
#     DT_BUY=DT_BUY[['Q+YR','PN',CST_CLM,REL_CLM]].drop_duplicates()
#     DT_BUY.reset_index(inplace=True,drop=True)
#     DT_BUY.rename(columns={'TOPLEVEL':'PN'},inplace=True)
#     return DT_BUY
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
        DT_PN,x='Q+YR',y='QLY_DELTA',
        hover_data={'PN':True,'QLY_DELTA':True},
        template='seaborn',text_auto=True,
        labels={'Q+YR': '<b>Y.LY QUARTERS','QLY_DELTA':'<b> QLY RELATIVE COST TREND'})
        graph.update_traces(textfont_size=16)
        graph.update_layout(title = dict(text='<b>'+PN + ' BUY Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%') 
        graph.update_yaxes(tickfont_family="Arial Black")
        graph.update_xaxes(tickfont_family="Arial Black")
        return graph
dash.register_page(__name__)
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
    DT_LBR=costby_bom('lbr_q_trends',PART)
    DT_OVS=costby_bom('ovs_trend',PART)
    DT_PH=costby_bom('ph_trend',PART)
    is_open=True
    if len(DT_LBR)==0:
        LBR=px.bar()
        is_open=False
    else:
        LBR = px.bar(
            DT_LBR,x='Q+YR',y='QLY_DELTA',
            hover_data={'PN':True,'QLY_DELTA':True},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','QLY_DELTA':'<b> ACT LABOR RELATIVE COST TREND'}
            )
        LBR.update_traces(textfont_size=16)
        LBR.update_layout(title = dict(text='<b>'+PART + ' Labor Trend (Includes Subs)',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%')
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
            DT_OVS,x='Q+YR',y='QLY_DELTA',
            hover_data={'PN':True,'QLY_DELTA':True},
            template='seaborn',text_auto=True,
            labels={'Q+YR': '<b>Y.LY QUARTERS','QLY_DELTA':'<b> OVS COST RELATIVE TREND'}
            )
        OVS.update_traces(textfont_size=16)
        OVS.update_layout(title = dict(text='<b>'+PART + ' OVS Cost Trend',font_size=30,
            yanchor='bottom', x=0.5,y=.95),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family':'Arial','size':12},yaxis_tickformat='.2%')
        OVS.update_xaxes(tickfont_family="Arial Black")
        OVS.update_yaxes(tickfont_family="Arial Black")
    gs1=[]
    gs2=[]
    m=1
    if len(DT_PH['PN'].unique())!=1:
        DT_PH=DT_PH.loc[DT_PH['QLY_COST']>10]
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