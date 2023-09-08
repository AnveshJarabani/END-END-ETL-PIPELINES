import pandas as pd
import numpy as np
from datetime import datetime,timedelta
RAWLBR=pd.read_pickle('../PKL/RAW_LBR.PKL')
RAWLBR = RAWLBR[(RAWLBR['PART_NUMBER'] != '#') &
            (RAWLBR['WORK_ORDER'] != '#') & (RAWLBR['STD_KEY'] != '#')]
RAWLBR=RAWLBR.loc[RAWLBR['END_DATE'].notna()]
RAWLBR['END_DATE']=RAWLBR['END_DATE'].astype('datetime64[ns]')
filt_date=RAWLBR['END_DATE'].max()-timedelta(days=7*30)
RAWLBR=RAWLBR.loc[RAWLBR['END_DATE']>filt_date]
mins=RAWLBR.pivot_table(index=['PART_NUMBER','WORK_ORDER','STD_KEY', 'OPERATION'],values='END_DATE',aggfunc=np.min)
mins.reset_index(inplace=True)
mins.rename(columns={'END_DATE': 'Oldest'},inplace=True)
maxs=RAWLBR.pivot_table(index=['PART_NUMBER','WORK_ORDER','STD_KEY', 'OPERATION'],values='END_DATE',aggfunc=np.max)
maxs.reset_index(inplace=True)
maxs.rename(columns={'END_DATE': 'Latest'},inplace=True)
merge=mins.merge(maxs,how='left')
merge['days']=(merge['Latest']-merge["Oldest"]).dt.days
merge.loc[merge['days']==0,'days']=1
merge[['OPERATION','WORK_ORDER']]=merge[['OPERATION','WORK_ORDER']].astype(int)
merge.sort_values(by=['WORK_ORDER','OPERATION'],inplace=True,ignore_index=True)
x=merge.groupby('WORK_ORDER')
merge['WAIT']=(x['Oldest'].shift(0)-x['Latest'].shift(1)).dt.days
merge.loc[merge['WAIT'].isna() | (merge['WAIT']<0),'WAIT']=0
merge=merge.pivot_table(index=['PART_NUMBER','STD_KEY','OPERATION'],values=['days','WAIT'],aggfunc=np.average)
merge.reset_index(inplace=True)
RT=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT')
RT=RT[['MATERIAL','OP_NUMBER']]
merge['OPERATION']=merge['OPERATION'].astype('int64')
RT=RT.merge(merge,left_on=['MATERIAL','OP_NUMBER'],right_on=['PART_NUMBER','OPERATION'],how='left')
RT['OP']=RT['STD_KEY']+"("+RT['OPERATION'].astype(str)+")"
RT=RT[['MATERIAL','OP','OPERATION','days','WAIT']]
RT.columns=['MATERIAL','OP','OPERATION','PROCESS DAYS','WAIT DAYS']
RT.dropna(how='any',inplace=True)
RT=RT.melt(id_vars=['MATERIAL','OP','OPERATION'],
        var_name='PROCESS/WAIT',value_name='DAYS')
RT=RT.sort_values(by='OPERATION',ignore_index=True)
RT['DAYS']=RT['DAYS'].astype(int)
RT.dropna(subset=['OP'],inplace=True)
RT.to_hdf('../H5/LBR.H5',key='PROCESS_DYS',mode='a')
print('PROCESS DAYS COMPLETE')


