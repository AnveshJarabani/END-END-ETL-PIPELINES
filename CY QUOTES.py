import pandas as pd
import xlwings as xl
import re
CYMER_QUOTES_PATH=r"C:\Users\ajarabani\Downloads\CYMER CURRENT QUOTES.xlsx"
QUOTES=pd.DataFrame(columns=['P/N','DESC','TYPE','QTY EXT','COST EA','COST EXT'])
ws=xl.Book(CYMER_QUOTES_PATH)
for i in range(1,ws.sheets.count+1):
    temp=ws.sheets(i).range('A1:Q25000').options(pd.DataFrame,index=False).value
    temp['COST EXT']=temp['COST EXT'].astype(float)
    temp=temp[temp['COST EXT'].notna()]
    temp['TOOL'] = 'CY-'+ ws.sheets(i).name
    temp=temp[['TOOL','P/N','DESC','TYPE','QTY EXT','COST EA','COST EXT']]
    temp.loc[temp['COST EA'].str.contains('Labor',na=False),'P/N']='Labor'
    temp.loc[temp['COST EA'].str.contains('Crate Sell',na=False),'P/N']='Crate Sell Price'
    temp=temp[temp['P/N'].notnull()]
    temp['BUR EXT'] = temp['COST EXT']*1.11825
    temp.loc[temp['P/N'].str.contains('Labor',na=False),'BUR EXT'] = temp['COST EXT']
    temp.loc[temp['P/N'].str.contains('Crate Sell Price',na=False),'BUR EXT'] = temp['COST EXT']
    temp.loc[temp['TYPE'].str.contains('AAM65',na=False),'BUR EXT'] = temp['COST EXT']
    temp.loc[temp['TYPE'].str.contains('H-PART',na=False),'BUR EXT'] = temp['COST EXT']*1.125
    temp.reset_index(inplace=True,drop=True)
    temp['P/N']=temp['P/N'].astype(str,errors='ignore').replace('\.0','',regex=True)
    temp['P/N']='CY-'+temp['P/N']
    QUOTES=pd.concat([QUOTES,temp],axis=0,ignore_index=True)
QUOTES['P/N']=QUOTES['P/N'].apply(lambda x: re.sub(r'^CY-',"",x) if r'CY-CY-' in x else x)
QUOTES[['TOOL','P/N','DESC','TYPE']]=QUOTES[['TOOL','P/N','DESC','TYPE']].apply(lambda x: x.str.strip())
QUOTES=QUOTES.loc[QUOTES['TYPE']!='ZZ']
QUOTES.rename(columns={'TYPE':'QUOTE TYPE'},inplace=True)
TYPES=pd.read_pickle('OLD-NEW TYPES.PKL')
QUOTES=QUOTES.merge(TYPES,left_on='QUOTE TYPE',right_on='OLD TYPE',how='left')
QUOTES.to_pickle('CYMER QUOTES.PKL')