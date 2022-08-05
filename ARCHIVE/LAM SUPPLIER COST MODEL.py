import pandas as pd
import glob
import os
pkl = r'C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM SUPPLIER MODEL.PKL'
path = r'\\chafs01\ChandlerBU\Quoting\Lam Research\LATEST QUOTES PER PN'
xlm = glob.glob(path + '/*xlsm')
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
ft =ft[~ft['Files'].str.contains(r'(RMA+|REWORK+|RWK+)')]
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
bm=pd.DataFrame()
for x in ft['Files']:
    try:
        dt = pd.read_excel(x,sheet_name='Supplier Cost Model',usecols='A:M')
        dt.columns = dt.columns.str.upper()
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        bm = pd.concat([bm,dt],axis=0,ignore_index=True)
    except:
        continue
bm.to_pickle(pkl)  