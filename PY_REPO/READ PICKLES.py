import numpy as np
import xlwings as xl
import pandas as pd
import glob
import h5py, time
import glob, PyPDF2, tabula
from rich import print
import sqlalchemy,json,pickle
from true_cost_finder import PN_TRUE_COST
from trees_to_df import tree_to_df
rout=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT')
rout.columns
plants=pd.read_pickle('../PKL/RAW_LBR.PKL')
pns=xl.books.active.sheets.active.range('a1:a1188').options(index=False).options(pd.DataFrame,index=False).value
tree_to_df('CY-210257').iloc[:,1:]
clb=pd.DataFrame(columns=['TOPLEVEL','PN','TQ'])
for i in pns['Material']:
    df=tree_to_df(i).iloc[:,1:]
    df['TOPLEVEL']=i
    df=df[['TOPLEVEL','PN','TQ',]]
    clb=pd.concat([clb,df])
bom=pd.read_hdf('../H5/ST_BM_BR.H5',key='BOM')
desc=xl.books.active.sheets.active.range('a1:b191515').options(index=False).options(pd.DataFrame,index=False).value
pns_with_bom=pns.merge(bom,left_on='Material',right_on='MATERIAL',how='left')
pns_with_bom=pns_with_bom[['MATERIAL','COMPONENT','QTY']]
pns_with_bom=pns_with_bom.merge(desc,left_on='COMPONENT',right_on='PART_NUMBER')
pns_with_bom=pns_with_bom[['MATERIAL','COMPONENT','PART_DESCRIPTION','QTY']]
no_40s=pns_with_bom.loc[pns_with_bom['MATERIAL'].isin(no_mat_lst)]
pns_with_bom=pns_with_bom.loc[pns_with_bom['COMPONENT'].str.startswith('40-',na=False) | pns_with_bom['COMPONENT'].str.startswith('42-',na=False)]
desc=desc.drop_duplicates(ignore_index=True)
clb_with_dsc=clb.merge(desc,left_on='PN',right_on='PART_NUMBER',how='left')
clb_with_dsc=clb_with_dsc[['TOPLEVEL','PN','PART_DESCRIPTION','TQ']]
clb_with_dsc=clb_with_dsc.loc[clb_with_dsc['TOPLEVEL']!=clb_with_dsc['PN']]
clb_with_dsc=clb_with_dsc.loc[clb_with_dsc['PN'].str.startswith('40-',na=False)]
xl.books.active.sheets.active.range('A1').options(index=False).value=clb_with_dsc
no_mat_lst=[i for i in pns['Material'].unique() if i not in pns_with_bom['MATERIAL'].unique()]

xl.books.active.sheets.active.range('k1').options(index=False,transpose=True).value=no_mat_lst

bom=bom[['MATERIAL','PLANT']]
bom.drop_duplicates(ignore_index=True,inplace=True)


new_rout=xl.books.active.sheets.active.range('a1:b104').options(index=False).options(pd.DataFrame,index=False).value

clb.reset_index(inplace=True)
clb=clb.iloc[:,1:]
rout=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT')
br=pd.read_hdf('../H5/ST_BM_BR.H5',key='BR')
rout.loc[rout['Unit_Labor Run']=='MIN','Labor Run']=rout['Labor Run']/60
rout['HRS']=(rout['Setup']+rout['Labor Run'])/rout['Base Quantity']
br['WC']=br['WC'].apply(lambda x: int(x) if isinstance(x,float) else x)
hr_df=rout.loc[rout['STD_KEY'].isin(br['ST KEY'])]


hr_df=hr_df.groupby(['Material'])['HRS'].sum().reset_index()
hr_df['HRS']=hr_df['HRS'].round(2)
hr_df=hr_df.merge(bom,left_on='Material',right_on='MATERIAL',how='left')
clb_hrs=clb.merge(hr_df,left_on='PN',right_on='MATERIAL',how='left')

clb_hrs['TL_HRS']=clb_hrs['HRS']*clb_hrs['TQ']
clb_hrs[clb_hrs['TOPLEVEL']=='CY-210257']
total_hrs=clb_hrs.groupby(['TOPLEVEL','PN','PLANT'])['TL_HRS'].sum().reset_index()
total_hrs.loc[total_hrs['TOPLEVEL']=='CY-210257']
p_total_hrs=total_hrs.pivot_table(index=['TOPLEVEL'],columns=['Plant'],values=['TL_HRS'],aggfunc=np.sum).reset_index()
xl.books.active.sheets.active.range('G1').options(index=False).value=total_hrs

rt.columns
rt=xl.books.active.sheets.active.range('A1:AY124784').options(index=False).options(pd.DataFrame,index=False).value
y=pns['Material'].apply(lambda x:tree_to_df(x))
print(bom)
PN_LIST=bom['MATERIAL'].unique()

lbr=pd.read_pickle('../pkl/RAW_LBR.PKL')
lbr.to_parquet('RAW_LBR.parquet',index=False)
lbr=lbr.loc[lbr['END_DATE'].str[-2:]=='23']
lbr=lbr[['PART_NUMBER','WORK_ORDER']]
lbr.drop_duplicates(inplace=True,ignore_index=True)
lbr=lbr.pivot_table(index='PART_NUMBER',values='WORK_ORDER',aggfunc='count')
lbr.reset_index(inplace=True)
xl.books.active.sheets.active.range('A1').options(index=False).value=lbr
std=pd.read_hdf("../H5/ST_BM_BR.H5",key='STD')
ph=pd.read_hdf("../H5/PH.H5",key='PH')
with open('../PKL/FOREST.PKL','rb') as f:
        FOREST=pickle.load(f)
keys= json.load(open("../PRIVATE/encrypt.json", "r"))
LOCAL_LEET_CN=sqlalchemy.create_engine(keys['con_str_leetcode_pg'])
LOCAL_PG_CN = sqlalchemy.create_engine(
    keys['con_str_uct_pg']) 

ACT_TABLE=xl.books.active.sheets.active.range('A1').expand().options(index=False).options(pd.DataFrame,index=False).value
ACT_TABLE['ACT COST']=ACT_TABLE['PN'].apply(lambda x:PN_TRUE_COST(x))

ACT_TABLE.to_sql(name='friend',con=LOCAL_LEET_CN,if_exists='replace',index=False)

MERGED=ACT_TABLE.merge(std,left_on='PN',right_on='MATERIAL',how='left')
MERGED=MERGED.merge(ph,left_on='PN',right_on='PH',how='left')
MERGED.loc[MERGED['ACT LBR COST']!=0,'STD COST']=0
MERGED['STD-ACT MATERIAL']=MERGED['STD COST']-MERGED['ACT MAT COST'].astype(float)
xl.books.active.sheets.active.range('k1').options(index=False).value=MERGED
start_time=time.time()
LBR = pd.read_pickle("../PKL/LBR M-18.pkl")
print(time.time()-start_time)
start_time=time.time()
lbr1=pd.read_sql_table('lbr m-18',LOCAL_PG_CN)
print(time.time()-start_time)

lst = glob.glob("../*pdf")
for pdf in lst:
    reader = PyPDF2.PdfReader(open(pdf, "rb"))
    num_pages = len(reader.pages)
    for page in range(num_pages):
        print(reader.pages[page].extract_text())
        print("\n")
    # try:
    #     tables=tabula.read_pdf(pdf,pages='all')
    #     for table in tables:
    #         print(table)
    #         print('\n')
    # except:
    #     continue
import h5py, pickle, sqlalchemy
from bigtree import print_tree, tree_to_dot, tree_to_dataframe
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

yt = pd.read_hdf(r"C:\Users\ajarabani\Downloads\PYTHON\QUOTES.H5", key="CY")
rw = yt[(yt["TOP LEVEL"] == "CY-217644") & (yt["P/N"] == "CY-210151")].index[0]
for i in range(1, 13):
    val = yt.loc[
        (yt["P/N"] == "CY-217185") & (yt["TOP LEVEL"] == "CY-213633"), yt.columns[i]
    ].values[0]
    yt.iat[rw, i] = val
# cn=sqlalchemy.create_engine('mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/uct_data',
#                             connect_args={'ssl_ca':'DigiCertGlobalRootCA.crt.pem'})

# lbr_raw=pd.read_pickle('LBR M-18.PKL')
# lbr_raw.to_sql(name='lbr m-18',con=cn,if_exists='replace',index=False)
yt.to_hdf(r"C:\Users\ajarabani\Downloads\PYTHON\QUOTES.H5", key="CY", mode="a")
with open("FOREST.PKL", "rb") as f:
    FOREST = pickle.load(f)

tree = FOREST["839-198032-001"]
# create a graph
G = nx.DiGraph()
# Add nodes and edges to the graph
levels = {tree: 0}
stack = [tree]
while stack:
    node = stack.pop()
    level = levels[node]
    for child in node.children:
        levels[child] = level + 1
        stack.append(child)

# Create the graph
G = nx.DiGraph()

# Add nodes and edges
for node, level in levels.items():
    G.add_node(node.name, level=level)
    if node is not tree:
        parent_name = node.parent.name
        G.add_edge(parent_name, node.name)

# Set the positions of the nodes
pos = {}
for level in set(levels.values()):
    nodes_in_level = [
        node for node, node_level in levels.items() if node_level == level
    ]
    level_width = len(nodes_in_level)
    for i, node in enumerate(nodes_in_level):
        pos[node.name] = ((i + 0.5) / level_width, -level)

# for node in tree.descendants:
#     G.add_node(node)
#     if node.parent:
#         G.add_edge(node.parent, node)
#     if node.children:
#          G.add_nodes_from([child.name for child in node.children])
#          G.add_edges_from([(node.name, child.name) for child in node.children])


# Draw the graph
# G.graph['rankdir']='BT'
# pos = nx.spring_layout(G, seed=42)
nx.draw_networkx(
    G,
    pos=pos,
    with_labels=True,
    node_color="lightblue",
    node_size=1000,
    font_size=10,
    font_weight="bold",
)
plt.axis("off")
plt.show()

print(FOREST)
sm = pd.read_hdf("ST_BM_BR.H5", key="AGILE_BOM")
# x=pd.read_hdf('LBR.H5',key='WO_TRENDS')
multi = (
    xl.books.active.sheets.active.range("A1:DF3105")
    .options(index=False)
    .options(pd.DataFrame, index=False)
    .value
)

# x=xl.books.active.sheets.active.range('A1').current_region.options(index=False).options(pd.DataFrame,index=False).value

print(multi)

