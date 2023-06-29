import multiprocessing as mp
import pandas as pd
from bigtree import Node
import warnings,pickle,os
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
from time import time
start=time()
BOM=pd.read_hdf('../H5/ST_BM_BR.H5',key='BOM')
List=list(BOM['MATERIAL'].unique())
span=len(List)
if len(List)>12:
    count=mp.cpu_count()
else:
    count=1
def PN_TO_TREE(PN):
    BM=BOM[BOM['MATERIAL']==PN.name]
    if BM.empty:
        return 
    BM.apply(lambda row: Node(row['COMPONENT'], parent=PN, 
            QTY=row['QTY'], TQ=row['QTY']*PN.TQ), axis=1)
def BOM_TO_TREE(ASSY):
    TREE=Node(ASSY,QTY=1,TQ=1)
    PN_TO_TREE(TREE)
    for PART in TREE.descendants:
        PN_TO_TREE(PART)
    print(ASSY)
    return TREE
if __name__=='__main__':
    # print(List.index(ASSY)/span)
    pool=mp.Pool(processes=count)
    FOREST=pool.imap(BOM_TO_TREE,List)
    forest_dict={tree.name: tree for tree in FOREST}
    with open('../PKL/FOREST.PKL','wb') as f:
        pickle.dump(forest_dict,f)
    print((time()-start)/60)