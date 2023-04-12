import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
dash.register_page(__name__)
ACTVSQT=pd.read_pickle('FRAMES_QT_VS_ACT.PKL')
ACTVSQT=ACTVSQT.fillna(0)
FRAMECOSTS=pd.read_pickle('FRAME.COSTS.PKL')
FRAMECOSTS.iloc[:,1] = FRAMECOSTS.iloc[:,1].astype(str)
PIE_COST=pd.read_pickle('FRAMES_PIE.PKL')
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
            html.H2('FRAME COSTS',
            style={'font':'Arial Black','color':'BLACK','font-weight':'bold','font-size':30,'text-decoration':'underline'})]
            ,width={'size':3}),
        dbc.Col([
        dcc.Dropdown(id='TIER', multi= False,
        options=['TIER 1','TIER 3','TIER 5','TIER 10'],
        value='TIER 3',
        placeholder='Select TIER...',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='P/LFRGRAPH',
        style={'padding-left':'30px','width': '65vw','height':'70vh','display':'inline-block'}),
        dcc.Graph(id='pie_fr',style={'padding-left':'50px','width': '25vw','height':'70vh','display':'inline-block'})],
    )),
    dbc.Col(dbc.Button(id='BTN_FR',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':2,'offset':11},style={'padding-bottom':'10px'}),
    dcc.Download(id='download-framecomp'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='FRAMECOSTS'),type='dot',fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
],style={'height':'200vh'},fluid=True)
@callback(
    Output('P/LFRGRAPH','figure'),
    Input('TIER','value')
 )
def update_graph(TIER):
    TEMP=ACTVSQT[['P/N','BUR ACT',TIER, '▲ '+TIER]]
    TEMP.sort_values(by=['▲ '+TIER],ignore_index=True,ascending=True,inplace=True)
    TEMP['P/L%']=(TEMP['▲ '+TIER]/TEMP[TIER])
    conditions=[TEMP['▲ '+TIER]<0,TEMP['▲ '+TIER]==0,
                TEMP['▲ '+TIER]>0]
    choices=['red','grey','green']
    TEMP['COLOR']=np.select(conditions,choices)
    barchart1 = px.bar(
        data_frame=TEMP,
        x='P/N',
        y='▲ '+TIER,
        hover_data={'COLOR':False,TIER:':$,.2f','P/L%':':.2%',
        '▲ '+TIER:':$,.2f'},
        title='FRAMES PERFORMANCE BY TIER PRICING',
        template='seaborn',
        labels={'▲ '+TIER:'<b>PROFIT/LOSS PER EA<b>','P/N': '<b>PART NUMBER<b>'},
        color=TEMP['COLOR'],
        color_discrete_sequence= ['red','green']
        )
    barchart1.update_traces(textposition='outside')
    barchart1.update_layout(title = dict(text='<b>FRAMES PERFORMANCE - '+TIER,
        yanchor='bottom', x=0.5,y=.95,font_size=30),
        font={'family':'Arial','size':12},
        yaxis_tickformat='$,',
        yaxis={'dtick':1000},
        showlegend=False)
    return barchart1
@callback(Output('pie_fr','figure'),
    Input('P/LFRGRAPH','hoverData'))
def pie_table(hov_data):
    if hov_data is None:
        x='839-198032-001'
    else:
        x=hov_data['points'][0]['x']
    SUM_COST=PIE_COST[x].sum()
    te='<b>ACTUAL COST = <b>' + str('${:,.1f}'.format(SUM_COST))
    piechart=px.pie(data_frame=PIE_COST,values=x,names='TOPLEVEL',color='TOPLEVEL',
    hover_name='TOPLEVEL',
    labels={'TOPLEVEL':'BUILD COST'},
    title='<b>'+x+' <b>'+te,template='presentation')
    piechart.update_traces(text=PIE_COST[x].map("${:,.1f}".format),textinfo='label+text+percent',
    texttemplate = '<b>%{label}</br></br>%{text}</b></br>%{percent}</b>',
    textposition='auto')
    piechart.update_layout(title_x=0.5,title_y=0.12,
    font={'family':'Arial','size':18,},title_font_size=20,
    showlegend=False)
    return piechart
@callback(
    Output('FRAMECOSTS','figure'),
    Input('P/LFRGRAPH','clickData'),
)
def table(clk_data):
    global dtf,y
    y=clk_data['points'][0]['x']
    dtf=FRAMECOSTS.loc[FRAMECOSTS['TOPLEVEL']==str(y)]
    dtf.drop(columns=['TOPLEVEL'],axis=1,inplace=True)
    dtf.iloc[:,2:4] = dtf.iloc[:,2:4].apply(lambda series: series.apply(lambda x: "{:,.2f}".format(float(x))))
    dtf.iloc[:,4:] = dtf.iloc[:,4:].apply(lambda series: series.apply(lambda x: "${:,.2f}".format(float(x))))
    colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
    QTVSACT = ff.create_table(dtf,colorscale=colorscale)
    QTVSACT.update_layout(font={'family':'Arial Black','size':12})
    return QTVSACT
@callback(
    Output('download-framecomp','data'),
    Input('BTN_FR','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(dtf.to_excel,str(y)+' ACTUAL COSTS.xlsx',index=False,sheet_name=str(y))
