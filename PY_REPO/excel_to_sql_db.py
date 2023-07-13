import pickle,json,sqlalchemy
import xlwings as xl
import pandas as pd
with open('../PKL/FOREST.PKL','rb') as f:
        FOREST=pickle.load(f)
keys= json.load(open("../PRIVATE/encrypt.json", "r"))
LOCAL_LEET_CN=sqlalchemy.create_engine(keys['con_str_leetcode_pg'])
LOCAL_PG_CN = sqlalchemy.create_engine(
    keys['con_str_uct_pg']) 

ACT_TABLE=xl.books.active.sheets.active.range('A1').expand().options(index=False).options(pd.DataFrame,index=False).value

ACT_TABLE.to_sql(name='friend',con=LOCAL_LEET_CN,if_exists='replace',index=False)