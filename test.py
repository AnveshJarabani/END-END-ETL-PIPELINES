import pandas as pd
CUST=pd.read_pickle('CY_SMRY.PKL')
print((CUST['DELTA.CAL']*CUST['QTY Shipped']).sum()/(CUST['ASP']*CUST['QTY Shipped']).sum())