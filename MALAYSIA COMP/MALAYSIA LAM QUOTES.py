import re
import pandas as pd
import glob
path=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\PRICE CHANGE MACRO 3322\PYTHON\MALAYSIA COMP"
xlx = glob.glob(path+'/*xlsx')
ft = pd.DataFrame(xlx)
ft.columns = ['Files']
bm = pd.DataFrame(columns=['Lam Part#'])
bm.columns = bm.columns.str.upper()
BOM_STRING=r'costed bom'
for x in ft['Files']:
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.search(BOM_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        dt = pd.read_excel(x,sheet_name=sheet,usecols='E:F',skiprows=[0])
        dt.columns = dt.columns.str.upper()
        dt = dt[dt.iloc[:,1].notna()]
        dt.drop(columns=['COMMODITY TYPE'],inplace=True)
        bm = pd.concat([bm,dt],axis=0,ignore_index=True)
        bm = bm.reset_index(drop=True)
        bm.drop_duplicates(inplace=True,ignore_index=True)
bm.to_pickle('MALAYSIA QUOTE PNS.PKL')