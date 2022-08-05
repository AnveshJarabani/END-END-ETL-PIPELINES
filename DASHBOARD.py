<<<<<<< HEAD
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
SMRY_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_SMRY.PKL"
PIE_PATH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAMPIE.PKL"
ACT_VS_QT_PTH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_QT_VS_ACT.PKL"
LAM_SMRY = pd.read_pickle(SMRY_PATH)
PIE_COST=pd.read_pickle(PIE_PATH)
ACTQTDT=pd.read_pickle(ACT_VS_QT_PTH)
ACTQTDT['SUPPLIER']=ACTQTDT['SUPPLIER'].str[:10]
PIE_COST=PIE_COST.transpose().reset_index()
PIE_COST.columns=PIE_COST.iloc[0]
PIE_COST=PIE_COST.drop(index=0)
LAM_SMRY.rename(columns={'Material - Key':'PART NUMBER',
                'Act Shipped Qty':'QTY Shipped'},inplace=True)
LAM_SMRY.reset_index(inplace=True)
LAM_SMRY.sort_values(by=['DELTA.CAL'],ignore_index=True,ascending=True,inplace=True)
LAM_SMRY['P/L%']=(LAM_SMRY['DELTA.CAL']/LAM_SMRY['ASP'])
LAM_SMRY['COLOR']=np.where(LAM_SMRY['DELTA.CAL']<0,'red','green')
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])
LOGO = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\UCT.PNG"
test_base64 = base64.b64encode(open(LOGO, 'rb').read()).decode('ascii')
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
        html.Img(src='data:image/png;base64,{}'.format(test_base64),style={'width': '10vw','height':'8vh','display':'inline-block'}),    
        html.H1('UCT CHANDLER - KPI DASHBOARD',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'10vh',
        'font-size':'80px','display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
        dcc.Dropdown(id='CUSTOMERS', multi= False,
        options=['LAM','CYMER','KLA','AMAT'],
        value='LAM',
        placeholder='Select Customer...',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':6,'offset':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='P/LGRAPH',
    style={'padding-left':'30px','width': '70vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='pie',style={'padding-left':'50px','width': '28vw','height':'50vh','display':'inline-block'})],
    )
    ),
    dbc.Col(dbc.Button(id='btn',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':2,'offset':11},style={'padding-bottom':'10px'}),
    dcc.Download(id='download-comp'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='QTVSACT'),type='dot',fullscreen=True)])
    )
],style={'height':'200vh'},fluid=True)
@app.callback(
    Output('P/LGRAPH','figure'),
    Input('CUSTOMERS','value')    
 )
def update_graph(CUSTOMER):
    CUST = LAM_SMRY
    wtavg=(CUST['DELTA.CAL']*CUST['QTY Shipped']).sum()/(CUST['ASP']*CUST['QTY Shipped']).sum()
    barchart1 = px.bar(
        data_frame=CUST,
        x='PART NUMBER',
        y='DELTA.CAL',
        hover_data={'COLOR':False,'ASP':':$,.2f','P/L%':':.2%',
        'DELTA.CAL':':$,.2f'},
        text='QTY Shipped',
        title='LAM TOOL PERFORMANCE',
        template='seaborn',
        labels={'DELTA.CAL':'<b>PROFIT/LOSS PER EA<b>','PART NUMBER': '<b>PART NUMBER<b>'},
        color=LAM_SMRY['COLOR'],
        color_discrete_sequence=['red','green']
        )
    barchart1.update_traces(textposition='outside')
    barchart1.add_trace(go.Scatter(x=CUST['PART NUMBER'],y=CUST['P/L%'],mode='lines',
    line=dict(color='blue',width=2),yaxis='y2',name='P/L%'))
    barchart1.add_annotation(dict(text='<b>WEIGHTED AVG% = '+str('{:.2%}'.format(wtavg)),
        showarrow=False,xanchor='left',yanchor='bottom'))
    barchart1.update_layout(title_text='<b>'+CUSTOMER+" " +'<b>TOOL PERFORMANCE', title_x=0.5,title_y=.9,
        font={'family':'Arial','size':15},title_font_size=40,
        yaxis_tickformat='$,',
        yaxis={'dtick':1000},
        yaxis2=dict(title='<B>PROFIT/LOSS%',overlaying='y',side='right',dtick=.2,
        range=[-.2,1.6],showgrid=False),
        yaxis2_tickformat='.0%',
        showlegend=False)
    return barchart1
@app.callback(
    Output('pie','figure'),
    Input('P/LGRAPH','hoverData'),
    # Input('Testgraph1','clickData'),
    # Input('Testgraph1','selectedData')]
)
def pie_table(hov_data):
    if hov_data is None:
        piechart=px.pie(data_frame=PIE_COST,values=hov_data,names='TOP LEVEL',color='TOP LEVEL',
        hover_name='TOP LEVEL',labels={'TOP LEVEL':'BUILD COST'},
        title='<b>859-A30530-001 BUILD COSTS',template='presentation')
        piechart.update_traces(text=PIE_COST['859-A30530-001'].map("${:,.1f}".format),textinfo='label+text+percent',
        textposition='auto')
        piechart.update_layout(title_x=0.5,title_y=0.05,
        font={'family':'Arial','size':18},title_font_size=20,
        showlegend=False) 
    else:
        x=hov_data['points'][0]['x']
        piechart=px.pie(data_frame=PIE_COST,values=x,names='TOP LEVEL',color='TOP LEVEL',
        hover_name='TOP LEVEL',
        labels={'TOP LEVEL':'BUILD COST'},
        title='<b>'+x+' <b>BUILD COSTS',template='presentation')
        piechart.update_traces(text=PIE_COST[x].map("${:,.1f}".format),textinfo='label+text+percent',
        texttemplate = '<b>%{label}</br></br>%{text}</b></br>%{percent}</b>',
        textposition='auto')
        piechart.update_layout(title_x=0.5,title_y=0.05,
        font={'family':'Arial','size':18,},title_font_size=20,
        showlegend=False) 
    return piechart
@app.callback(
    Output('QTVSACT','figure'),
    Input('P/LGRAPH','clickData'),
)
def table(clk_data):
    global dt,y
    if clk_data is None:
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        QTVSACT = ff.create_table([ACTQTDT.columns],colorscale=colorscale)
    else:
        y=clk_data['points'][0]['x']
        dt=ACTQTDT.loc[ACTQTDT['TOP LEVEL']==str(y)]
        dt.sort_values(by='DELTA',ascending=True,inplace=True)
        dt.drop(columns=['TOP LEVEL','DESCRIPTION'],axis=1,inplace=True)
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        dt.iloc[:,3:] = dt.iloc[:,3:].apply(lambda series: series.apply(lambda x: "${:,.1f}".format(float(x))))
        QTVSACT = ff.create_table(dt,colorscale=colorscale)
        QTVSACT.update_layout(font={'family':'Arial Black','size':12})
    return QTVSACT
@app.callback(
    Output('download-comp','data'),
    Input('btn','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(dt.to_excel,'QUOTE VS ACT '+str(y)+'.xlsx',index=False)
if __name__=='__main__':
=======
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output,Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
SMRY_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_SMRY.PKL"
PIE_PATH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAMPIE.PKL"
ACT_VS_QT_PTH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_QT_VS_ACT.PKL"
LAM_SMRY = pd.read_pickle(SMRY_PATH)
PIE_COST=pd.read_pickle(PIE_PATH)
ACTQTDT=pd.read_pickle(ACT_VS_QT_PTH)
ACTQTDT['SUPPLIER']=ACTQTDT['SUPPLIER'].str[:10]
PIE_COST=PIE_COST.transpose().reset_index()
PIE_COST.columns=PIE_COST.iloc[0]
PIE_COST=PIE_COST.drop(index=0)
LAM_SMRY.rename(columns={'Material - Key':'PART NUMBER',
                'Act Shipped Qty':'QTY Shipped'},inplace=True)
LAM_SMRY.reset_index(inplace=True)
LAM_SMRY.sort_values(by=['DELTA.CAL'],ignore_index=True,ascending=True,inplace=True)
LAM_SMRY['P/L%']=(LAM_SMRY['DELTA.CAL']/LAM_SMRY['ASP'])
LAM_SMRY['COLOR']=np.where(LAM_SMRY['DELTA.CAL']<0,'red','green')
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])
LOGO = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\UCT.PNG"
test_base64 = base64.b64encode(open(LOGO, 'rb').read()).decode('ascii')
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
        html.Img(src='data:image/png;base64,{}'.format(test_base64),style={'width': '10vw','height':'8vh','display':'inline-block'}),    
        html.H1('UCT CHANDLER - KPI DASHBOARD',
        className='text-center',style={'color':'#1172FF','font-weight':'bold','width': '80vw','height':'10vh',
        'font-size':'80px','display':'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
        dcc.Dropdown(id='CUSTOMERS', multi= False,
        options=['LAM','CYMER','KLA','AMAT'],
        value='LAM',
        placeholder='Select Customer...',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'size':6,'offset':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='P/LGRAPH',
    style={'padding-left':'30px','width': '70vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='pie',style={'padding-left':'50px','width': '28vw','height':'50vh','display':'inline-block'})],
    )
    ),
    dbc.Col(dbc.Button(id='btn',children=[html.I(className='test'),'Download'],
            color='info',className='mt-1'),width={'size':2,'offset':11},style={'padding-bottom':'10px'}),
    dcc.Download(id='download-comp'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='QTVSACT'),type='dot',fullscreen=True)])
    )
],style={'height':'200vh'},fluid=True)
@app.callback(
    Output('P/LGRAPH','figure'),
    Input('CUSTOMERS','value')    
 )
def update_graph(CUSTOMER):
    CUST = LAM_SMRY
    wtavg=(CUST['DELTA.CAL']*CUST['QTY Shipped']).sum()/(CUST['ASP']*CUST['QTY Shipped']).sum()
    barchart1 = px.bar(
        data_frame=CUST,
        x='PART NUMBER',
        y='DELTA.CAL',
        hover_data={'COLOR':False,'ASP':':$,.2f','P/L%':':.2%',
        'DELTA.CAL':':$,.2f'},
        text='QTY Shipped',
        title='LAM TOOL PERFORMANCE',
        template='seaborn',
        labels={'DELTA.CAL':'<b>PROFIT/LOSS PER EA<b>','PART NUMBER': '<b>PART NUMBER<b>'},
        color=LAM_SMRY['COLOR'],
        color_discrete_sequence=['red','green']
        )
    barchart1.update_traces(textposition='outside')
    barchart1.add_trace(go.Scatter(x=CUST['PART NUMBER'],y=CUST['P/L%'],mode='lines',
    line=dict(color='blue',width=2),yaxis='y2',name='P/L%'))
    barchart1.add_annotation(dict(text='<b>WEIGHTED AVG% = '+str('{:.2%}'.format(wtavg)),
        showarrow=False,xanchor='left',yanchor='bottom'))
    barchart1.update_layout(title_text='<b>'+CUSTOMER+" " +'<b>TOOL PERFORMANCE', title_x=0.5,title_y=.9,
        font={'family':'Arial','size':15},title_font_size=40,
        yaxis_tickformat='$,',
        yaxis={'dtick':1000},
        yaxis2=dict(title='<B>PROFIT/LOSS%',overlaying='y',side='right',dtick=.2,
        range=[-.2,1.6],showgrid=False),
        yaxis2_tickformat='.0%',
        showlegend=False)
    return barchart1
@app.callback(
    Output('pie','figure'),
    Input('P/LGRAPH','hoverData'),
    # Input('Testgraph1','clickData'),
    # Input('Testgraph1','selectedData')]
)
def pie_table(hov_data):
    if hov_data is None:
        piechart=px.pie(data_frame=PIE_COST,values=hov_data,names='TOP LEVEL',color='TOP LEVEL',
        hover_name='TOP LEVEL',labels={'TOP LEVEL':'BUILD COST'},
        title='<b>859-A30530-001 BUILD COSTS',template='presentation')
        piechart.update_traces(text=PIE_COST['859-A30530-001'].map("${:,.1f}".format),textinfo='label+text+percent',
        textposition='auto')
        piechart.update_layout(title_x=0.5,title_y=0.05,
        font={'family':'Arial','size':18},title_font_size=20,
        showlegend=False) 
    else:
        x=hov_data['points'][0]['x']
        piechart=px.pie(data_frame=PIE_COST,values=x,names='TOP LEVEL',color='TOP LEVEL',
        hover_name='TOP LEVEL',
        labels={'TOP LEVEL':'BUILD COST'},
        title='<b>'+x+' <b>BUILD COSTS',template='presentation')
        piechart.update_traces(text=PIE_COST[x].map("${:,.1f}".format),textinfo='label+text+percent',
        texttemplate = '<b>%{label}</br></br>%{text}</b></br>%{percent}</b>',
        textposition='auto')
        piechart.update_layout(title_x=0.5,title_y=0.05,
        font={'family':'Arial','size':18,},title_font_size=20,
        showlegend=False) 
    return piechart
@app.callback(
    Output('QTVSACT','figure'),
    Input('P/LGRAPH','clickData'),
)
def table(clk_data):
    global dt,y
    if clk_data is None:
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        QTVSACT = ff.create_table([ACTQTDT.columns],colorscale=colorscale)
    else:
        y=clk_data['points'][0]['x']
        dt=ACTQTDT.loc[ACTQTDT['TOP LEVEL']==str(y)]
        dt.sort_values(by='DELTA',ascending=True,inplace=True)
        dt.drop(columns=['TOP LEVEL','DESCRIPTION'],axis=1,inplace=True)
        colorscale = [[0, '#4d004c'],[.5, '#f2e5ff'],[1, '#ffffff']]
        dt.iloc[:,3:] = dt.iloc[:,3:].apply(lambda series: series.apply(lambda x: "${:,.1f}".format(float(x))))
        QTVSACT = ff.create_table(dt,colorscale=colorscale)
        QTVSACT.update_layout(font={'family':'Arial Black','size':12})
    return QTVSACT
@app.callback(
    Output('download-comp','data'),
    Input('btn','n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(dt.to_excel,'QUOTE VS ACT '+str(y)+'.xlsx',index=False)
if __name__=='__main__':
>>>>>>> 5263024 (first commit)
    app.run_server(debug=True,port=3000)