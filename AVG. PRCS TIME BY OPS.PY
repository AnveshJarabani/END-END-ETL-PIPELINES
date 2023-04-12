import pandas as pd
import numpy as np
RAWLBR=pd.read_pickle('Labor Hrs Q3 21 - 9.22.22.PKL')
RAWLBR=RAWLBR[['Order - Material (Key)','Order', 'Operation','Operation Quantity', 'Standard Text Key','Hours Worked' ]]
RAWLBR=RAWLBR.loc[RAWLBR['Order - Material (Key)']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['Order']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['Standard Text Key']!='#']
RAWLBR=RAWLBR.loc[RAWLBR['Hours Worked'].notna()]
hrs=RAWLBR.pivot_table(index=['Order - Material (Key)','Order','Standard Text Key', 'Operation'],values='Hours Worked',aggfunc=np.sum)
hrs.reset_index(inplace=True)
merge=pd.read_pickle('mergetemp.pkl')
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
# FIN.to_pickle('PLACEHOLDER.PKL')