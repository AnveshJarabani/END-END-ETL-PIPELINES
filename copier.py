import glob
import os
import pickle
import numpy as np
import multiprocessing as mp
import shutil
pths = pickle.load(open('hd_xlpth_dict.pkl', 'rb'))
pth = r"C:\Users\ajarabani\Downloads\PIR_EXCELS"
dlod_lst = glob.glob(pth + '/*xlsx')
dload_lst=[os.path.basename(i) for i in dlod_lst]
filt_dct={i:val for i,val in pths.items() if val not in dload_lst}
lst = [i for i in filt_dct.keys()]
for i in lst:
    try:
        shutil.copy(i, r"C:\Users\ajarabani\Downloads\PIR_EXCELS")
    except:
        continue
