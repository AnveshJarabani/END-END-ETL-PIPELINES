import numpy as np
import xlwings as xl
import pandas as pd
import h5py,pickle
from bigtree import print_tree,tree_to_dot
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

with open('FOREST.PKL', 'rb') as f:
    FOREST = pickle.load(f)

tree=FOREST['0730923-001']
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
    nodes_in_level = [node for node, node_level in levels.items() if node_level == level]
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
nx.draw_networkx(G, pos=pos, with_labels=True, node_color="lightblue", node_size=1000, font_size=10, font_weight="bold")
plt.axis("off")
plt.show()

print(FOREST)
sm=pd.read_hdf('ST_BM_BR.H5',key='AGILE_BOM')
# x=pd.read_hdf('LBR.H5',key='WO_TRENDS')
multi=xl.books.active.sheets.active.range('A1:DF3105').options(index=False).options(pd.DataFrame,index=False).value

# x=xl.books.active.sheets.active.range('A1').current_region.options(index=False).options(pd.DataFrame,index=False).value

print(multi)

# OVS=pd.read_hdf('OVS.H5',key='TREND')
# # for i in PH['PN'].unique():
# #     PH.loc[PH['PN']==i,'LAST Q COST']=PH.loc[PH['PN']==i,'BUY COST'].shift(-1)
# # PH['DELTA %']=(PH['BUY COST']-PH['LAST Q COST'])/PH['LAST Q COST']
# # PH[['BUY COST','DELTA %']]=PH[['BUY COST','DELTA %']].round(2)
# # PH['DELTA %'].replace(np.nan,0,inplace=True)
# # PH.dropna(how='all',inplace=True)
# # PH.to_hdf('PH.H5',key='TREND',mode='a')

# for i in LBR['PN'].unique():
#     LBR.loc[LBR['PN']==i,'LAST Q COST']=LBR.loc[LBR['PN']==i,'ACT LBR COST/EA'].shift(1)
# LBR['DELTA %']=(LBR['ACT LBR COST/EA']-LBR['LAST Q COST'])/LBR['LAST Q COST']
# LBR[['ACT LBR COST/EA','DELTA %']]=LBR[['ACT LBR COST/EA','DELTA %']].round(2)
# LBR.replace([np.inf,-np.inf],np.nan,inplace=True)
# LBR['DELTA %'].replace(np.nan,0,inplace=True)
# LBR.dropna(how='all',inplace=True)
# LBR.to_hdf('LBR.H5',key='Q_TRENDS',mode='a')

# with h5py.File('TOOLCOSTS.H5',  "a") as f:
#     del f['CY_QT_VS_ACT']
#     del f['KLA_QT_VS_ACT']
#     del f['LM_QT_VS_ACT']
# for i in ['CY_PIE','CY_SMRY','KLA_PIE','KLA_SMRY','LM_PIE','LM_SMRY']:
#     x=pd.read_hdf('TOOLCOSTS.H5',key=i)
#     x.to_hdf('TOOLTEMP.H5',key=i)
# for i in  h5py.File('ST_BM_BR.H5').keys():
#     print(i)
# CS=xl.books.active.sheets.active.range('N12:O35').options(index=False).options(pd.DataFrame,index=False).value
# CS.to_pickle('OLD-NEW TYPES.PKL')
# CS = pd.read_pickle('KLA QUOTES.PKL')
# CS.loc[CS['PART#']=='257-666879-001','QTY']=.002
# dt=pd.read_excel("LABOR HOURS 2020 - 9.22.22.xlsx",sheet_name='Employee Labor Hours',skiprows=[0],usecols="A:AR")
# dt.to_pickle('LABOR HOURS 2020 - 9.22.22.PKL')
# xl.books.active.sheets.active.range('A1').options(index=False).value=ma
 