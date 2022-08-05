import re
import pandas as pd
import glob
import os
pkl = r'C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM QUOTES.PKL'
path = r'\\chafs01\ChandlerBU\Quoting\Lam Research\LATEST QUOTES PER PN'
xlm = glob.glob(path + '/*xlsm')
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
ft =ft[~ft['Files'].str.contains(r'(RMA+|REWORK+|RWK+)')]
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
bm = pd.DataFrame(columns=['TOP LEVEL', 'Lam Part#','Description', 'EXT QTY',
                            'SUPPLIER', 'UnitCost','Ext$$','UnitCost.1','Ext$$.1',
                            'UnitCost.2','Ext$$.2',
                            'UnitCost.3','Ext$$.3',
                            'UnitCost.4','Ext$$.4'])
bm.columns = bm.columns.str.upper()
BOM_STRING=r'costed bom'
for x in ft['Files']:
    try:
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.match(BOM_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        dt = pd.read_excel(x,sheet_name=sheet,usecols='A:AB',skiprows=[0])
        dt.columns = dt.columns.str.upper()
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        bm = pd.concat([bm,dt],axis=0,ignore_index=True)
        bm = bm[bm.iloc[:,4] != 'ZZ']
        bm.dropna(subset=['LAM PART#',"UNITCOST"],inplace=True)
        bm =  bm[bm['UNITCOST'] != 0]
        bm = bm.iloc[:,:15].reset_index(drop=True)
    except:
        continue
CS=pd.DataFrame()
SUPPLIER_STRING=r'supplier cost'
for x in ft['Files']:
    try:
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.match(SUPPLIER_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        dt = pd.read_excel(x,sheet_name=sheet,usecols='A:M')
        dt.columns = dt.columns.str.upper()
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        CS = pd.concat([CS,dt],axis=0,ignore_index=True)
    except:
        continue
CS=CS.fillna(0)
CS=CS.applymap(lambda x:x.strip() if isinstance(x,str) else x)
BUILD_HRS=CS.iloc[:,[0,6,7]]
BUILD_HRS=BUILD_HRS[~BUILD_HRS.iloc[:,1].apply(lambda x: isinstance(x,str))]
BUILD_HRS=BUILD_HRS[~BUILD_HRS.iloc[:,2].apply(lambda x: isinstance(x,str))]
BUILD_HRS['BUILD HRS']=BUILD_HRS.iloc[:,1]+BUILD_HRS.iloc[:,2]
BUILD_HRS=BUILD_HRS.iloc[:,[0,3]]
BUILD_HRS=BUILD_HRS[BUILD_HRS['BUILD HRS']!=0]
BUILD_HRS.drop_duplicates(subset=['TOP LEVEL'],inplace=True)
BUILD_HRS.reset_index(drop=True)
BUILD_HRS['LAM PART#']=BUILD_HRS['TOP LEVEL']
BUILD_HRS['EXT QTY']=1
BUILD_HRS['UNITCOST']=BUILD_HRS['BUILD HRS']*64.5*1.15
XL=['EXT$$','UNITCOST.1','EXT$$.1','UNITCOST.2','EXT$$.2','UNITCOST.3','EXT$$.3','UNITCOST.4','EXT$$.4']
for i in range(0,9):
    BUILD_HRS[XL[i]]=BUILD_HRS['UNITCOST']
BUILD_HRS.drop(['BUILD HRS'],axis=1,inplace=True)
SUBPARTS=CS.iloc[:,[0,1,3,4,5,6]]
SUBPARTS=SUBPARTS[SUBPARTS.iloc[:,1].str.fullmatch(r'\d*-*\d*-\d*',na=False)]
SUBPARTS=SUBPARTS[SUBPARTS.iloc[:,2]!=0]
SUBPARTS=SUBPARTS[SUBPARTS.iloc[:,0]!=SUBPARTS.iloc[:,1]]
SUBPARTS=SUBPARTS[~SUBPARTS.iloc[:,2].str.contains(r'FAI|Program|Art|silk',na=False,flags=re.IGNORECASE)]
SUBPARTS=SUBPARTS[SUBPARTS.iloc[:,3:4].sum(axis=1)!=0]
SUBTEMP=SUBPARTS[SUBPARTS.iloc[:,2].apply(lambda x: isinstance(x,str))]
SUBTEMP.drop(['UNNAMED: 2'],axis=1,inplace=True)
SUBTEMP=SUBTEMP[SUBTEMP.iloc[:,3:4].sum(axis=1)!=0]
SUBTEMP=SUBTEMP[~SUBTEMP.iloc[:,2].apply(lambda x: isinstance(x,str))]
SUBPARTS=SUBPARTS[~SUBPARTS.iloc[:,2].apply(lambda x: isinstance(x,str))]
SUBPARTS=SUBPARTS[SUBPARTS.iloc[:,2]<100]
SUBPARTS.drop(['UNNAMED: 5'],axis=1,inplace=True)
SUBPARTS.columns=['TOP LEVEL','LAM PART#','EXT QTY','COST','BUR']
SUBTEMP.columns=['TOP LEVEL','LAM PART#','EXT QTY','COST','BUR']
SUBPARTS=pd.concat([SUBPARTS,SUBTEMP],ignore_index=True)
SUBPARTS['BUR COST']=SUBPARTS.iloc[:,3:5].sum(axis=1)
SUBPARTS['EXT']=SUBPARTS['BUR COST']*SUBPARTS['EXT QTY']
SUBPARTS.drop(['COST','BUR'],axis=1,inplace=True)
SM = pd.DataFrame(columns=['TOP LEVEL', 'Lam Part#','EXT QTY',
                            'UnitCost','Ext$$','UnitCost.1','Ext$$.1',
                            'UnitCost.2','Ext$$.2',
                            'UnitCost.3','Ext$$.3',
                            'UnitCost.4','Ext$$.4'])
SM.columns=SM.columns.str.upper()
SUBPARTS.columns=['TOP LEVEL','LAM PART#','EXT QTY','UNITCOST','EXT$$']
TEMP=SUBPARTS.drop_duplicates(subset=['TOP LEVEL','LAM PART#'])
SUBPARTS['TC']=SUBPARTS.groupby(['TOP LEVEL','LAM PART#']).cumcount()+1
SUBPARTS=pd.concat([SM,SUBPARTS])
SUBPARTS.reset_index(drop=True,inplace=True)
SM=pd.concat([SM,TEMP])
SM.reset_index(drop=True,inplace=True)
CL=['UNITCOST.1','EXT$$.1','UNITCOST.2','EXT$$.2','UNITCOST.3','EXT$$.3','UNITCOST.4','EXT$$.4']
for y in range(2,6):
    for TL in SM['TOP LEVEL'].unique():
        for LM in SM['LAM PART#'].unique():
            if SUBPARTS.loc[(SUBPARTS['TC']==y)&(SUBPARTS['TOP LEVEL']==TL)&(SUBPARTS['LAM PART#']==LM)].empty:
                continue
            else: 
                T=SUBPARTS.loc[(SUBPARTS['TC']==y)& (SUBPARTS['TOP LEVEL']==TL) & (SUBPARTS['LAM PART#']==LM),'UNITCOST'].reset_index(drop=True)
                Q=SUBPARTS.loc[(SUBPARTS['TC']==y)& (SUBPARTS['TOP LEVEL']==TL) & (SUBPARTS['LAM PART#']==LM),'EXT$$'].reset_index(drop=True)
                SM.loc[(SM['TOP LEVEL']==TL)&(SM['LAM PART#']==LM),CL[(y-2)*2]]=T.loc[0]
                SM.loc[(SM['TOP LEVEL']==TL)&(SM['LAM PART#']==LM),CL[((y-1)*2)-1]]=Q.loc[0]
SM=pd.concat([BUILD_HRS,SM],axis=0,ignore_index=True)
SM=pd.concat([bm,SM],axis=0,ignore_index=True)
SM[['TOP LEVEL','LAM PART#']] = SM[['TOP LEVEL','LAM PART#']].apply(lambda x: x.str.strip())
SM.to_pickle(pkl)