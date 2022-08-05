import pandas as pd
import glob
import xlwings as xl
import os
path = r"C:\Users\ajarabani\Desktop\Parts\ECO\QSM SKID PLATES UPDATE 11122 ECO"
xlm = glob.glob(path + '/*pdf')
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*-[0-9a-zA-Z]*)',expand = True)
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
xl.books.active.sheets.active.range('S1').options(index=False).value=ft['PN']