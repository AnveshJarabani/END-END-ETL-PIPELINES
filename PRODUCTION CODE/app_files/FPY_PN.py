import dash
from dash import dcc, html, callback
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
dash.register_page(__name__)
QN = pd.read_pickle('../PKL/QN_DATA.pkl')
fiscal_cal = pd.read_pickle('../PKL/FISCAL_CAL.PKL')
fiscal_cal['Month-Year'] = fiscal_cal['DATE'].dt.strftime('%b-%Y')
QN = QN.merge(fiscal_cal, left_on='DATE',
              right_on='DATE', how='left')
QN.reset_index(inplace=True)
QN = QN.loc[QN['QTR+YR'].notna()]
QN.drop(columns=['FISCAL PERIOD','QTR'], inplace=True)
QN['DATE']=QN['DATE'].dt.strftime('%Y-%m-%d')
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('PLACEHOLDERS',
                    className='text-center', style={'color': '#1172FF', 'font-weight': 'bold', 'width': '80vw', 'height': '15vh', 'font-size': 50, 'display': 'inline-block'}),
        ])]),
    dbc.Row([
        dbc.Col([
            html.H2('QUALITY METRICS',
                    style={'font': 'Arial Black', 'color': 'BLACK', 'font-weight': 'bold', 'font-size': 30, 'text-decoration': 'underline'})], width={'size': 3}),
      dbc.Col([
        dcc.Input(id='FPY_PN', 
        debounce=True,
        value='839-198032-001',
        placeholder='ENTER PART NUMBER...',
        size='40',
        style={'color':'black',"font-weight":'bold',
        'font-size':'22px','margin-bottom':'20px'})],width={'offset':1,'size':3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='QN_COST',
        style={'padding-left':'30px','width': '40vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='QN_COUNT',
        style={'padding-left':'60px','width': '40vw','height':'50vh','display':'inline-block'})],
        width={'offset':1})),
    dbc.Col(dbc.Button(id='BTN_QN', children=[html.I(className='test'), 'Download'],
            color='info', className='mt-1'), width={'size': 10, 'offset': 50}, style={'padding-bottom': '10px'}),
    dcc.Download(id='DOWNLOAD_QN_BY_PN'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='QN_LIST_PN'), type='dot', fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
], style={'height': '200vh'}, fluid=True)
@callback(Output('QN_LIST_PN', 'figure'),
          Output('QN_COST', 'figure'),
          Output('QN_COUNT','figure'),
          Input('FPY_PN', 'value'))
def TABLE(PN):
    global result,part
    if PN is None:
        PN='839-198032-001'
    part=PN
    result=QN.loc[QN['Material - Key']==PN]
    show_table=result.head(200)
    show_table=show_table.applymap(lambda x: x[:10] if isinstance(x,str) else x)
    show_table.rename(columns=lambda x: x[:15],inplace=True)
    colorscale = [[0, '#4d004c'], [.5, '#f2e5ff'], [1, '#ffffff']]
    table = ff.create_table(show_table, colorscale=colorscale,index=False)
    table.update_layout(font={'family': 'Arial Black', 'size': 12})
    cost_group=result.pivot_table(index='Month-Year',values='Rejected Amount',aggfunc=np.sum)
    cost_group.reset_index(inplace=True)
    cost_group.sort_values('Month-Year',key=lambda x:pd.to_datetime(x,format='%b-%Y'),inplace=True)
    cost_graph=px.bar(
            cost_group,x='Month-Year',y='Rejected Amount',
            hover_data={'Month-Year':True,'Rejected Amount':':$,.2f'},
            template='seaborn',text_auto=True)
    cost_graph.update_traces(textfont_size=16)
    cost_graph.update_layout(title = dict(text='<b>'+PN + ' Supplier Quality Trend Cost',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12},yaxis_tickformat='$,')
    cost_graph.update_yaxes(tickfont_family="Arial Black")
    cost_graph.update_xaxes(tickfont_family="Arial Black")
    
    count_group=result.pivot_table(index='Month-Year',values='Total QN Quantity',aggfunc=np.sum)
    count_group.reset_index(inplace=True)
    count_group=count_group.sort_values(by='Total QN Quantity',ascending=False)
    count_group.sort_values('Month-Year',key=lambda x:pd.to_datetime(x,format='%b-%Y'),inplace=True)
    count_graph=px.bar(
            count_group,x='Month-Year',y='Total QN Quantity',
            hover_data={'Month-Year':True,'Total QN Quantity':':,'},
            template='seaborn',text_auto=True)
    count_graph.update_traces(textfont_size=16)
    count_graph.update_layout(title = dict(text='<b>'+PN + ' Supplier Quality Trend Count',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12},yaxis_tickformat=',')
    count_graph.update_yaxes(tickfont_family="Arial Black")
    count_graph.update_xaxes(tickfont_family="Arial Black")
    return table,cost_graph,count_graph
@callback(
    Output('DOWNLOAD_QN_BY_PN', 'data'),
    Input('BTN_QN', 'n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(result.to_excel, f'{part} QN REPORT.xlsx', index=False, engine='xlsxwriter')
