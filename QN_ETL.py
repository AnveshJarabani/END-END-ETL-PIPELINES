import pandas as pd
import numpy as np
QN_raw = pd.read_pickle('QN M-18.pkl')
QN = QN_raw[['Plant', 'Calendar Year/Week', 'Notification PS Text - Long Text',
            'CAUSEDBY', 'Defect Type', 'Defect Group', 'Vendor-Key',
            'Vendor Desc', 'Material group', 'Material - Key', 'Material - Medium Text',
            'Standard Price', 'Rejected Amount', 'Total QN Quantity']]
for col in ['Rejected Amount', 'Standard Price']:
    QN[col]=pd.to_numeric(QN[col].str.replace('$',''))
QN.to_pickle('QN M-18.pkl')