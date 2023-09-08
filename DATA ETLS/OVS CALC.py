import numpy as np
import pandas as pd
import math
QS=pd.read_pickle('../PKL/QLY_INTS.PKL')
def sort_QS(DF):
    pi=DF.merge(QS,left_on='Q+YR',right_on='Q+YR',how='left')
    pi.sort_values(by=['YR','MONTH'],ascending=True,inplace=True)
    pi=pi[DF.columns]
    pi.drop_duplicates(inplace=True,ignore_index=True)
    return pi
OVS_RAW = pd.read_pickle('../PKL/OVS_RAW.PKL')
OVS = OVS_RAW.loc[~OVS_RAW['PO_AMOUNT'].isna()]
OVS['YR']=OVS['YR+QTR'].str.extract(r'(\d{2})$')
OVS['MONTH']=OVS['YR+QTR'].str.extract(r'\b(\d{2})\b')
OVS=OVS.loc[OVS['MONTH'].notna()].reset_index()
OVS['MONTH']=OVS['MONTH'].astype('int')
OVS['QTR']=OVS['MONTH'].apply(lambda x: f"Q{math.ceil(x/3)}")
OVS.sort_values(by=['YR','MONTH'],ascending=False,inplace=True)
OVS['Q+YR']= OVS['QTR'].astype(str)+" "+OVS['YR'].astype(str)
OVS = OVS.pivot_table(index=['Q+YR','PART_NUMBER', 'OVS_OPERATION'],values=['PO_PRICE'], aggfunc=np.mean)
OVS.reset_index(inplace=True)
OVS['OVS_OPERATION']=OVS['OVS_OPERATION'].astype(float)
OVS['OVS_OPERATION']=OVS['OVS_OPERATION'].astype(int)
ROUT=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT')
ROUT=ROUT.loc[ROUT['STD_KEY'].str.contains('^21-',regex=True,na=False)]
OVS=pd.merge(ROUT,OVS,how='left',left_on=['MATERIAL','OP_NUMBER'],right_on=['PART_NUMBER','OVS_OPERATION'])
OVS=OVS.loc[OVS['OVS_OPERATION'].notna()]
OVS = OVS.pivot_table(index=['Q+YR','PART_NUMBER'], values=['PO_PRICE'], aggfunc=np.sum)
OVS.reset_index(inplace=True)
OVS.rename(columns={'PART_NUMBER': 'MATERIAL', 'PO_PRICE' : 'OVS COST'},inplace=True)
OVS['OVS COST']=OVS['OVS COST'].round(2)
OVS=sort_QS(OVS)
for i in OVS['MATERIAL'].unique():
    OVS.loc[OVS['MATERIAL']==i,'LAST Q COST']=OVS.loc[OVS['MATERIAL']==i,'OVS COST'].shift(1)
OVS['DELTA %']=(OVS['OVS COST']-OVS['LAST Q COST'])/OVS['LAST Q COST']
OVS[['OVS COST','DELTA %']]=OVS[['OVS COST','DELTA %']].round(2)
OVS['DELTA %'].replace(np.nan,0,inplace=True)
OVS.dropna(how='all',inplace=True)
OVS.to_hdf('../H5/OVS.H5',key='TREND',mode='a') # OVS TREND FOR THE DASHBOARD
for i in OVS.iloc[:,1].unique():
    OVS.loc[OVS.iloc[:,1]==i,'TEMP']=np.roll(OVS.loc[OVS.iloc[:,1]==i,'OVS COST'],1)
OVS=OVS.loc[OVS.iloc[:,2]<OVS.iloc[:,3]*10]
OVS=OVS.iloc[:,1:3]
OVS=OVS.drop_duplicates(subset=['MATERIAL'],keep='last',ignore_index=True)
OVS.to_hdf('../H5/OVS.H5',key='OVS',mode='a') # OVS COST FOR USING IN QUOTE CALCULATION
print('OVS.H5 OVS COMPLETE')