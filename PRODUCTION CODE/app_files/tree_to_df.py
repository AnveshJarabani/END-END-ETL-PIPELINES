from bigtree import tree_to_dataframe
import pickle
import pandas as pd
with open('../PKL/FOREST.PKL','rb') as f: 
        FOREST=pickle.load(f)
def tree_to_df(ASSY):
        if FOREST.get(ASSY,False):
                return tree_to_dataframe(FOREST[ASSY],name_col='PN',
                                 parent_col='PARENT',all_attrs=True)
        else:
                return pd.DataFrame({'path':ASSY,
                                     'PN':ASSY,
                                     'PARENT':'None',
                                     'QTY':1,
                                     "TQ":1},index=[0])
