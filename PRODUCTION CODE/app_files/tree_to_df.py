from bigtree import tree_to_dataframe
import pickle
with open('../PKL/FOREST.PKL','rb') as f: 
        FOREST=pickle.load(f)
def tree_to_df(ASSY):
        return tree_to_dataframe(FOREST[ASSY],name_col='PN',
                                 parent_col='PARENT',all_attrs=True)
