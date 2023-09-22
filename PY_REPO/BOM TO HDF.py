import pandas as pd
import numpy as np

# UPDATE THE BOM & ROUTING PATHS BEFORE EXECUTING THE CODE.
int_path = "../../3321 BOM DUMP 07172023_v1.csv"
fab_path = "../../3322_BOM_DUMP_07172023_v1.csv"
int_bom = pd.read_csv(int_path)
int_bom = int_bom.loc[:, ["/BIC/ZMATERIAL", "/BIC/ZBCOMNT", "/BIC/ZBOMQTY"]]
int_bom.columns = ["MATERIAL", "COMPONENT", "QTY"]
def float_conversion(LIST):
    LIST = LIST.astype(str) + ","
    LIST = LIST.str.replace(",", "", regex=True)
    LIST = LIST.astype(float)
    return LIST
def to_numeric_or_str(val):
    try:
        return pd.to_numeric(val)
    except ValueError:
        return str(val)
int_bom[["MATERIAL", "COMPONENT"]] = int_bom[["MATERIAL", "COMPONENT"]].applymap(
    to_numeric_or_str
)
int_bom["QTY"] = float_conversion(int_bom["QTY"])
int_bom.drop_duplicates(inplace=True, ignore_index=True)
int_bom = int_bom[int_bom["COMPONENT"] != ""]
FRAMES = pd.read_pickle("../PKL/FRAMES.PKL")
int_bom = int_bom.pivot_table(
    index=["MATERIAL", "COMPONENT"], values=["QTY"], aggfunc=np.sum
)
int_bom.reset_index(inplace=True)
int_bom["PLANT"] = "INTEGRATION"
wl = pd.read_pickle("../PKL/RAW_LBR.PKL")
wl = wl.loc[:, ["PART_NUMBER", "OP_QTY"]]
wl = wl[wl["PART_NUMBER"] != "#"]
QTY = wl.pivot_table(
    index=["PART_NUMBER"], values=["OP_QTY"], aggfunc=np.mean
)
QTY.reset_index(inplace=True)
QTY.columns = ["MATERIALKEY", "OP QTY"]
fab_bom = pd.read_csv(fab_path)
fab_bom = fab_bom.loc[~fab_bom["/BIC/ZCH_NUM"].str.startswith("IR", na=False)]
fab_bom = fab_bom.loc[:, ["/BIC/ZMATERIAL", "/BIC/ZBCOMNT", "/BIC/ZBOMQTY", "FMENG"]]
fab_bom.columns = ["MATERIAL", "COMPONENT", "QTY", "FIXEDQTY"]
fab_bom[["MATERIAL", "COMPONENT"]] = fab_bom[["MATERIAL", "COMPONENT"]].applymap(
    to_numeric_or_str
)
fab_bom = fab_bom.loc[fab_bom["MATERIAL"] != "0379982-001"]
fab_bom["QTY"] = float_conversion(fab_bom["QTY"])
fab_bom = fab_bom.merge(QTY, left_on="MATERIAL", right_on="MATERIALKEY", how="left")
fab_bom["OP QTY"].fillna(10, inplace=True)
fab_bom.loc[fab_bom["FIXEDQTY"] == "X", "QTY"] = fab_bom["QTY"] / fab_bom["OP QTY"]
fab_bom.drop_duplicates(inplace=True, ignore_index=True)
fab_bom = fab_bom[fab_bom["COMPONENT"] != ""]
fab_bom = fab_bom.pivot_table(
    index=["MATERIAL", "COMPONENT"], values=["QTY"], aggfunc=np.sum
)
fab_bom.reset_index(inplace=True)
fab_bom["PLANT"] = "FABRICATION"
BOM = pd.concat([fab_bom, int_bom], axis=0, ignore_index=True)
BOM.drop_duplicates(subset=["MATERIAL", "COMPONENT"], inplace=True, ignore_index=True)
BOM = BOM.loc[~BOM["COMPONENT"].str.endswith("-UCT", na=True)]
BOM = BOM.loc[~BOM["MATERIAL"].str.endswith("-UCT", na=True)]
BOM["QTY"] = BOM["QTY"].round(5)
# PH = pd.read_hdf("../H5/PH.H5", key="PH")
# BOM = BOM[~BOM["MATERIAL"].isin(PH["PH"])]
# AGILE_BOM = pd.read_hdf("../H5/ST_BM_BR.Hk5", key="AGILE_BOM")
# BOM = BOM[BOM["MATERIAL"].isin(AGILE_BOM["PART_NUMBER"])] test commit
BOM.to_hdf("../H5/ST_BM_BR.H5", key="BOM")
