import pandas as pd
import multiprocessing as mp
import pickle,os,warnings,sys
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
input_bytes=sys.stdin.buffer.read()
df=pickle.loads(input_bytes)
groups=df.groupby(['Order - Material (Key)','Standard Text Key'])
List=[i for _,i in groups]
def remove_outliers(group):
    Q1 = group.quantile(0.25)
    Q3 = group.quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5*IQR
    lower_bound = Q1 - 1.5*IQR
    return group[(group > lower_bound) & (group < upper_bound)]
if __name__=='__main__':
    pool=mp.Pool(processes=mp.cpu_count())
    output=pool.imap(remove_outliers,List)
    result=pd.concat(output)
    result_bytes=pickle.dumps(result)
    sys.stdout.buffer.write(result_bytes)
    sys.stdout.flush()