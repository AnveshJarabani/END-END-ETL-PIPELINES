import multiprocessing as mp
import pandas as pd
from bigtree import tree_to_dataframe
import pickle,os,warnings,sys
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
string=sys.stdin.buffer.read().decode('utf-8')
List=list(map(str,string.split(' ')))
with open('FOREST.PKL','rb') as f:
        FOREST=pickle.load(f)
reminder=[i for i in List if i not in FOREST]
reminder_rows = [{'PN': i, 'PARENT': None, 'QTY': 1, 'TQ': 1, 'TOPLEVEL': i} for i in reminder]
df_remainder=pd.DataFrame(reminder_rows)
List=[i for i in List if i in FOREST]
def tree_to_df(ASSY):
        return tree_to_dataframe(FOREST[ASSY],name_col='PN',
                                 parent_col='PARENT',all_attrs=True)
if __name__=='__main__':
        pool=mp.Pool(processes=mp.cpu_count())
        output=pool.imap(tree_to_df,List)
        DFs=pd.concat(output)
        DFs['TOPLEVEL']=DFs['path'].str.extract('^/([^/]+)')
        DFs.drop(columns=['path'],inplace=True)
        DFs=pd.concat([DFs,df_remainder],ignore_index=True)
        send=pickle.dumps(DFs)
        sys.stdout.buffer.write(send)