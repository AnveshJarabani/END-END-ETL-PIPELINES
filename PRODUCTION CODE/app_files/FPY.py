import dash
from dash import dcc, html, callback
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
dash.register_page(__name__)
QN = pd.read_pickle('../PKL/QN M-18.pkl')
fiscal_cal = pd.read_pickle('../PKL/FISCAL CAL.PKL')
QN = QN.merge(fiscal_cal, left_on='Required Start Date',
              right_on='DATE', how='left')
QN.reset_index(inplace=True)
QN = QN.loc[QN['QTR+YR'].notna()]
QN.drop(columns=['Required Start Date','FISCAL PERIOD','QTR'], inplace=True)
fiscal_cal['DATE'] = fiscal_cal['DATE'].dt.strftime('%Y-%m-%d').apply(lambda x: str(x))
drop_down = list(QN['QTR+YR'].unique()) 
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
            dcc.Dropdown(id='QTR', multi=False,
                         options=drop_down,
                         value=drop_down[0],
                         placeholder='Select QTR...',
                         style={'color': 'black', "font-weight": 'bold',
                                'font-size': '22px', 'margin-bottom': '20px'})],width={'size': 3})]),
    dbc.Row(
        dbc.Col([
        dcc.Graph(id='VENDOR_COST',
        style={'padding-left':'30px','width': '40vw','height':'50vh','display':'inline-block'}),
        dcc.Graph(id='VENDOR_COUNT',
        style={'padding-left':'60px','width': '40vw','height':'50vh','display':'inline-block'})],
        width={'offset':1})),
    dbc.Col(dbc.Button(id='BTN_QN', children=[html.I(className='test'), 'Download'],
            color='info', className='mt-1'), width={'size': 10, 'offset': 50}, style={'padding-bottom': '10px'}),
    dcc.Download(id='DOWNLOAD_QN_REPORT'),
    dbc.Row(
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='QN_LIST'), type='dot', fullscreen=True)])
    ),
    dcc.Store(id='session', storage_type='session'),
], style={'height': '200vh'}, fluid=True)
@callback(Output('QN_LIST', 'figure'),
          Output('VENDOR_COST', 'figure'),
          Output('VENDOR_COUNT','figure'),
          Input('QTR', 'value'))
def TABLE(QTR):
    global result,Q
    if QTR is None:
        QTR='2023 QTR 2'
    Q=QTR
    result=QN.loc[QN['QTR+YR']==QTR]
    show_table=result.head(200)
    show_table=show_table.applymap(lambda x: x[:10] if isinstance(x,str) else x)
    colorscale = [[0, '#4d004c'], [.5, '#f2e5ff'], [1, '#ffffff']]
    table = ff.create_table(show_table, colorscale=colorscale,index=False)
    table.update_layout(font={'family': 'Arial Black', 'size': 12})
    cost_group=result.pivot_table(index='Vendor Desc',values='Rejected Amount',aggfunc=np.sum)
    cost_group.reset_index(inplace=True)
    cost_group=cost_group.sort_values(by='Rejected Amount',ascending=False)
    cost_group=cost_group.loc[cost_group['Vendor Desc']!='Not assigned']
    cost_group=cost_group[0:15]
    cost_graph=px.bar(
            cost_group,x='Vendor Desc',y='Rejected Amount',
            hover_data={'Vendor Desc':True,'Rejected Amount':':$,.2f'},
            template='seaborn',text_auto=True)
    cost_graph.update_traces(textfont_size=16)
    cost_graph.update_layout(title = dict(text='<b>'+QTR + ' Supplier Quality Trend Cost',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12},yaxis_tickformat='$,')
    cost_graph.update_yaxes(tickfont_family="Arial Black")
    cost_graph.update_xaxes(tickfont_family="Arial Black")
    
    count_group=result.pivot_table(index='Vendor Desc',values='Total QN Quantity',aggfunc=np.sum)
    count_group.reset_index(inplace=True)
    count_group=count_group.sort_values(by='Total QN Quantity',ascending=False)
    count_group=count_group.loc[count_group['Vendor Desc']!='Not assigned']
    count_group=count_group[0:15]
    count_graph=px.bar(
            count_group,x='Vendor Desc',y='Total QN Quantity',
            hover_data={'Vendor Desc':True,'Total QN Quantity':':,'},
            template='seaborn',text_auto=True)
    count_graph.update_traces(textfont_size=16)
    count_graph.update_layout(title = dict(text='<b>'+QTR + ' Supplier Quality Trend Count',font_size=30,
        yanchor='bottom', x=0.5,y=.95),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family':'Arial','size':12},yaxis_tickformat=',')
    count_graph.update_yaxes(tickfont_family="Arial Black")
    count_graph.update_xaxes(tickfont_family="Arial Black")
    return table,cost_graph,count_graph
@callback(
    Output('DOWNLOAD_QN_REPORT', 'data'),
    Input('BTN_QN', 'n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(result.to_excel, f'{Q} QN REPORT.xlsx', index=False, engine='xlsxwriter')