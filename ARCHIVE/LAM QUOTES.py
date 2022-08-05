import pandas as pd
import glob
import os
pkl = r'C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM_QUOTES.PKL'
path = r'\\chafs01\ChandlerBU\Quoting\Lam Research\LATEST QUOTES PER PN'
xlm = glob.glob(path + '/*xlsm')
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
ft['RMA'] = ft['Files'].str.extract(r'(RMA+|REWORK+)',expand=True)
ft = ft.loc[(ft['RMA'] !='RMA') & (ft['RMA'] !='REWORK')]
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
bm = pd.DataFrame(columns=['TOP LEVEL', 'Lam Part#','Description', 'EXT QTY',
                            'SUPPLIER', 'UnitCost','Ext$$','UnitCost.1','Ext$$.1',
                            'UnitCost.2','Ext$$.2',
                            'UnitCost.3','Ext$$.3',
                            'UnitCost.4','Ext$$.4',
                            'UnitCost.5','Ext$$.5'])
bm.columns = bm.columns.str.upper()
for x in ft['Files']:
    try:
        dt = pd.read_excel(x,sheet_name='costed bom',usecols='A:AB',skiprows=[0])
        dt.columns = dt.columns.str.upper()
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        bm = pd.concat([bm,dt],axis=0,ignore_index=True)
    except:
        continue
bm = bm[bm.iloc[:,4] != 'ZZ']
bm.dropna(subset=['LAM PART#',"UNITCOST"],inplace=True)
bm =  bm[bm['UNITCOST'] != 0]
bm = bm.iloc[:,:17].reset_index(drop=True)
bm.to_pickle(pkl)  