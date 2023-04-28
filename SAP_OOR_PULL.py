import win32com.client as win
import pandas as pd
from datetime import datetime
import subprocess,pyautogui
import time,os
import xlwings as xl
os.system("TASKKILL /F /IM saplogon.exe")
os.system("TASKKILL /F /IM excel.exe")
time.sleep(3)
subprocess.Popen([r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"],shell=True)
time.sleep(5)
gui=win.GetObject('SAPGUI')
today=datetime.today().strftime('%m.%d.%y')
oor_file="OOR "+today+".XLSX"
application=gui.GetScriptingEngine
pyautogui.press('down')
pyautogui.press('down')
pyautogui.press('enter')
time.sleep(5)
pyautogui.press('enter')
time.sleep(2)
pyautogui.typewrite('ZQ2COPENSO\n')
for i in range(8):
    pyautogui.typewrite('down')
pyautogui.typewrite('3321')
pyautogui.press('tab')
pyautogui.typewrite('3322')
for i in range(3):
    pyautogui.press('tab')
pyautogui.press('down')
pyautogui.press('tab')
pyautogui.press('enter')
time.sleep(120)


subprocess.call(['cscript.exe',r"C:\Users\ajarabani\Downloads\PYTHON\SAP OOR.vbs"])
mtime=os.path.getmtime(r"C:\Users\ajarabani\Downloads\OOR.XLSX")
while True:
    if time.time()-mtime<60:
        break
    time.sleep(1)
wb=xl.Book(r"C:\Users\ajarabani\Downloads\OOR.XLSX")
ws=wb.sheets.active
data_range=ws.used_range
df=pd.DataFrame(data_range.value)
df.columns=df.iloc[0]
df=df[1:]
df=df[['Order Type','Shipping plant','Ship-to name','Sale Order number','Material','Material Description','First date','Delv Schedule line date','Schedule Line Quantity','Unit price','Open SO quantity','Sold to name','Ship-to Country','Current Cust Need By date','Rejection reason code']]
df=df.loc[~df['Order Type'].str.contains('ZKB|ZLBO|ZRO')]
df=df.loc[df['Rejection reason code'].isna()]
df=df.loc[df['Open SO quantity']!=0]
try:
    df['Open SO quantity']=df['Open SO quantity'].astype(float)
except:
    df['Open SO quantity']=df['Open SO quantity']+','
    df['Open SO quantity']=df['Open SO quantity'].str.replace(',','')
    df['Open SO quantity']=df['Open SO quantity'].astype(float)
df['Delv Schedule line date']=pd.to_datetime(df['Delv Schedule line date'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%m/%d/%Y')
df.to_pickle('OOR.PKL')
print('OOR.PKL COMPLETE')
os.system("TASKKILL /F /IM saplogon.exe")
os.system("TASKKILL /F /IM excel.exe")