import dash
from dash import dcc, html, callback
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import numpy as np
from app_files.sql_connector import table as sql,query_table
dash.register_page(__name__)
dct={'LAM':'lm',
          'KLA':'kla',
          'CYMER':'cy',}
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
    CUST=query_table(f'SELECT * FROM toolcosts_{dct[CUSTOMER]}_smry WHERE `FISCAL PERIOD`=\'{PERIOD}\'')
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
    QTR=query_table(f"select QTR from fiscal_cal where `FISCAL PERIOD`='{PERIOD}'").iloc[0,0]
    PIE_COST_P=query_table(f"select * from toolcosts_{dct[CUSTOMER]}_pie where `QTR`='{QTR}'")
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
    Input('P/LGRAPH','clickData'),
    Input('CUSTOMERS','value')
)
def table(clk_data,CUSTOMER):
    global dt,y
    if clk_data is None:
        dt = query_table(f"""
                       SELECT * FROM toolcosts_{dct['CYMER']}_qt_vs_act
                       """).iloc[:,:10]
    else:
        y=clk_data['points'][0]['x']
        dt=query_table(f"""
                       SELECT * FROM toolcosts_{dct[CUSTOMER]}_qt_vs_act
                       where `TOP LEVEL`='{y}'
                       """)
    dt['VENDOR']=dt['VENDOR'].str[:10]
    if 'DESC' in dt.columns:
        dt.drop(columns=['TOP LEVEL','DESC'],axis=1,inplace=True)
    else:
        dt.drop(columns=['TOP LEVEL','DESCRIPTION'],axis=1,inplace=True)
    dt.iloc[:,2:]=dt.iloc[:,2:].applymap(lambda x:round(x,2) if isinstance(x,float) else x)
    dt.iloc[:,4:] = dt.iloc[:,4:].apply(lambda series: series.apply(lambda x: "${:,.2f}".format(float(x))))
    dt.sort_values(by='DELTA',ascending=True,inplace=True)
    colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
    QTVSACT = ff.create_table(dt[:30],colorscale=colorscale)
    QTVSACT.update_layout(font={'family':'Arial Black','size':12})
    return QTVSACT
@callback(
    Output('download-comp','data'),
    Input('btn','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(dt.to_excel,'QUOTE VS ACT '+str(y)+'.xlsx',index=False,engine='xlsxwriter')
