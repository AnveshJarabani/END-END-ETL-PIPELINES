from operator import index
import pandas as pd
import glob
import xlwings as xl
import os
path = r'\\chafs01\ChandlerBU\Quoting\Lam Research\LATEST QUOTES PER PN'
xlm = glob.glob(path + '/*xlsm')
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
xl.books.active.sheets.active.range('A1').options(index=False).value=ft['PN']