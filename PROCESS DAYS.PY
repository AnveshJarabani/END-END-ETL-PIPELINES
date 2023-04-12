import pandas as pd
import numpy as np
RAWLBR=pd.read_pickle('LBR M-18.PKL')
RAWLBR=RAWLBR[['Order - Material (Key)','Order', 'Operation', 'Standard Text Key','End Date' ]]
RAWLBR=RAWLBR.loc[RAWLBR['Order - Material (Key)']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['Order']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['Standard Text Key']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['End Date'].notna()]
mins=RAWLBR.pivot_table(index=['Order - Material (Key)','Order','Standard Text Key', 'Operation'],values='End Date',aggfunc=np.min)
mins.reset_index(inplace=True)
mins.rename(columns={'End Date': 'Oldest'},inplace=True)
maxs=RAWLBR.pivot_table(index=['Order - Material (Key)','Order','Standard Text Key', 'Operation'],values='End Date',aggfunc=np.max)
maxs.reset_index(inplace=True)
maxs.rename(columns={'End Date': 'Latest'},inplace=True)
merge=mins.merge(maxs,how='left')
merge['Oldest']=merge['Oldest'].astype('datetime64[ns]')
merge['Latest']=merge['Latest'].astype('datetime64[ns]')
A=[d.date() for d in merge['Oldest']]
B=[d.date() for d in merge['Latest']]
merge['days']=np.busday_count(A,B)
merge.loc[merge['days']==0,'days']=1
merge[['Operation','Order']]=merge[['Operation','Order']].astype(int)
merge.sort_values(by=['Order','Operation'],inplace=True,ignore_index=True)
merge[['Oldest','Latest']]=merge[['Oldest','Latest']].astype(str)
for i in merge.index:
    if merge.loc[0:i,'Order'].value_counts()[merge.loc[i,'Order']]==1:
        merge.loc[i,'WAIT']=0
        continue
    merge.loc[i,'WAIT']=np.busday_count(merge.loc[i-1,'Latest'],merge.loc[i,'Oldest'])
merge.loc[merge['WAIT']<0,'WAIT']=0
merge=merge.pivot_table(index=['Order - Material (Key)','Standard Text Key','Operation'],values=['days','WAIT'],aggfunc=np.average)
merge.reset_index(inplace=True)
merge[['WAIT','days']]=np.ceil(merge[['WAIT','days']])
for i in merge.index:
    if i == (len(merge)-1):
        merge.loc[i,'WAITTEMP']=0
    else:
        merge.loc[i,'WAITTEMP']=merge.loc[i+1,'WAIT']
merge.drop(columns=['WAIT'],inplace=True)
merge.rename(columns={'WAITTEMP':'WAIT'},inplace=True)
merge['REF']=merge['Standard Text Key']+' ('+merge['Operation'].astype(str)+')'
merge.rename(columns={'Order - Material (Key)':'Material'},inplace=True)
# RT=pd.read_excel('SAP ROUTING 3321 & 22.xlsx',sheet_name='Sheet1',usecols='C,F,D')
RT=pd.read_pickle('RT-TEMP FOR PROCESS DAYS.PKL')
RT.dropna(axis=0,inplace=True,how='all')
RT['REF']=RT['StTextKy']+' ('+RT['OpAc'].astype(str)+')'
FIN=RT.merge(merge,how='left')
FIN=FIN[['Material','OpAc','REF','days','WAIT']]
FIN.rename(columns={'REF':'OP','days':'PROCESS DAYS','WAIT':'WAIT DAYS'},inplace=True)
FIN=FIN.melt(id_vars=['Material','OpAc','OP'],
        var_name='PROCESS/WAIT',value_name='DAYS')
FIN['DAYS'].fillna(1,inplace=True)
FIN.dropna(subset=['OP'],inplace=True)
FIN['DAYS']=FIN['DAYS'].astype(int)
FIN.sort_values(by=['OpAc'],inplace=True,ignore_index=True)
FIN.dropna(subset=['OpAc'],inplace=True)
FIN.to_hdf('LBR.H5',key='PROCESS_DYS',mode='a')