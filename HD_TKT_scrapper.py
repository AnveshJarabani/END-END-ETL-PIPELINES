import xlwings as xl
import pandas as pd
import re,glob,os
import warnings,pickle
import numpy as np
import multiprocessing as mp
pths=pickle.load(open('hd_xlpth_dict.pkl','rb'))
flip_pths={key:val for val,key in pths.items()}
# lst=[r'{}'.format(i) for i in pths.keys()]
local_pth = r"C:\Users\ajarabani\Downloads\PIR_EXCELS"
lst=glob.glob(local_pth+'/*xlsx')
# lst = [r"{}".format(path) for path in lst]
count = mp.cpu_count()
warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
chk_lst = ['path','Part number', 'Plant/Pur Org', 'Unit Cost',	'Vendor Number', 'Vendor Name',
           'Standard Qty', 'Contract Number', 'Contract Item Line', 'Leadtime(Calendar days)', 'MOQ']
m = 1
def load_dfs(path):
    global m
    m+=1
    print(path,m)
    try:
        df=pd.read_excel(path,header=None,nrows=500)
        df=df.dropna(how='all')
        df.reset_index(inplace=True)
        columns_row=df.apply(lambda row: row.notnull().any(),axis=1).idxmax()
        df.columns=df.iloc[columns_row]
        df=df.iloc[columns_row+1:]
        df.columns=df.columns.str.strip()
        cols = list(set(df.columns).intersection(chk_lst))
    except:
        return
    if len(cols)!=0:
        df['path']=flip_pths[os.path.basename(path)]
        cols.append('path')
        df=df[cols]
        return df.loc[:,~df.columns.duplicated()]
# df = pd.DataFrame(columns=chk_lst)
# for i in lst:
#     df=pd.concat([df,load_dfs(i)],ignore_index=True)
#     print(len(df))
# df.to_pickle('PIR_HD.pkl')

if __name__=='__main__':
    pool=mp.Pool(processes=12)
    results=list(pool.imap(load_dfs,lst))
    df=pd.concat(results,ignore_index=True)
    df[['Month/Year', 'HD#']] = df['path'].str.extract(
        r'\\\\[^\\]+\\[^\\]+\\[^\\]+\\[^\\]+\\([^\\]+)\\([^\\]+)\\')
    df.to_pickle('PIR_HD.pkl')







# path = r"\\hayfs1\public\SHARED\Help_Desk_Attachments_2023-05"
# def collect_file_paths(root):
#     l = glob.glob(root + '/*xlsx')
#     if l:
#         return l
# subdirectories = [os.path.join(path, d) for d in os.listdir(
#     path) if os.path.isdir(os.path.join(path, d))]
# sub2_dirs=[os.path.join(x,d) for x in subdirectories for d in os.listdir(x)]
# lst = []
# if __name__ == '__main__':
#     pool=mp.Pool(processes=50)
#     for i in pool.imap(collect_file_paths,sub2_dirs):
#         if i:
#             lst.extend(i)

#     data_dict = {file_path: os.path.basename(
#         file_path) for file_path in lst}

#     with open("hd_xlpth_dict.pkl", "wb") as file:
#         pickle.dump(data_dict, file)

