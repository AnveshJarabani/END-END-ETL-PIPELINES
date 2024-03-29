import pandas as pd
import numpy as np

wl = pd.read_pickle("../PKL/RAW_LBR.PKL")
rt = pd.read_hdf("../H5/ST_BM_BR.H5", key="ROUT")
br = pd.read_hdf("../H5/ST_BM_BR.H5", key="BR")
br.rename(columns={"ST KEY": "STD_KEY"}, inplace=True)
rt = rt.merge(br[["WC", "STD_KEY"]], on="STD_KEY", how="left")
SM = pd.DataFrame()
rt
SM["SM"] = np.array(
    rt.loc[rt["WC"].str.contains(r"BRAKE|LASER|TRT", na=False), "MATERIAL"].unique()
).tolist()
SM.to_hdf("../H5/ST_BM_BR.H5", key="SM_PARTS", mode="a")
cst = pd.read_hdf("../H5/ST_BM_BR.H5", key="BR")
wl = wl[(wl["PART_NUMBER"] != "#") & (wl["WORK_ORDER"] != "#") & (wl["STD_KEY"] != "#")]
cst["BUR_RATE"] *= 1.15
wl = wl.merge(cst, left_on="STD_KEY", right_on="ST KEY", how="left")
wl.drop(columns=["ST KEY"], axis=1, inplace=True)
wl = wl.assign(COST=lambda x: (x["BUR_RATE"] * x["HRS_WORKED"]))
pi = wl.pivot_table(
    index=["PART_NUMBER", "WORK_ORDER", "STD_KEY", "OP_QTY"],
    values=["HRS_WORKED", "COST"],
    aggfunc=np.sum,
)
pi.reset_index(inplace=True)
pi["ACT COST/EA"] = pi["COST"] / pi["OP_QTY"]
pi["HRS/EA"] = pi["HRS_WORKED"] / pi["OP_QTY"]
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how="any", inplace=True)
pi = pi.loc[pi["COST"] != 0]
pi = pi[["PART_NUMBER", "WORK_ORDER", "STD_KEY", "ACT COST/EA", "HRS/EA"]]


def remove_outliers(group):
    mean = group.mean()
    median = group.median()
    mad = np.median(np.abs(group - median))
    z_scores = 0.6745 * np.abs((group - mean) / mad)
    return group[z_scores < 3.5]


def remove_outliers(group):
    Q1 = group.quantile(0.25)
    Q3 = group.quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 0.5 * IQR
    lower_bound = Q1 - 0.5 * IQR
    return group[(group > lower_bound) & (group < upper_bound)]


# pi[['ACT COST/EA_t', 'HRS/EA_t']] = pi.groupby(['PART_NUMBER', 'STD_KEY'])[['ACT COST/EA', 'HRS/EA']].transform(remove_outliers)
pi_temp = pi.pivot_table(
    index=["PART_NUMBER", "STD_KEY"], values=["ACT COST/EA"], aggfunc=np.mean
)
pi_temp.reset_index(inplace=True)
pi_temp.columns = ["MAT_TEMP", "STKEY_TEMP", "COST/EA_AVG"]
pi = pi.merge(
    pi_temp,
    left_on=["PART_NUMBER", "STD_KEY"],
    right_on=["MAT_TEMP", "STKEY_TEMP"],
    how="left",
)
pi = pi.loc[
    (pi["COST/EA_AVG"] / 5 < pi["ACT COST/EA"])
    & (pi["COST/EA_AVG"] * 5 > pi["ACT COST/EA"])
]
pi = pi.pivot_table(
    index=["PART_NUMBER", "STD_KEY"], values=["HRS/EA", "ACT COST/EA"], aggfunc=np.mean
)
pi.reset_index(inplace=True)
QTY = wl[["PART_NUMBER", "WORK_ORDER", "OP_QTY"]]
QTY = QTY.drop_duplicates()
QTY = QTY.pivot_table(index=["PART_NUMBER"], values=["OP_QTY"], aggfunc=np.mean)
QTY.reset_index(inplace=True)
rt = rt.merge(QTY, left_on="MATERIAL", right_on="PART_NUMBER", how="left")
rt.drop(columns=["PART_NUMBER"], axis=1, inplace=True)
rt.loc[
    (rt["OP_QTY"].isnull()) & (rt["WC"].str.contains(r"BRAKE|LASER|TRT|SAW")),
    "BASE_QUANTITY",
] = 10
rt.loc[(rt["OP_QTY"] != 1), "BASE_QUANTITY"] = 10
mat_list = rt.loc[rt["BASE_QUANTITY"] == 10, "MATERIAL"].unique()
rt.loc[rt["MATERIAL"].isin(mat_list), "BASE_QUANTITY"] = 10
rt.loc[rt["OP_QTY"].isnull(), "OP_QTY"] = rt["BASE_QUANTITY"]
rt["PLN HR/EA"] = ((rt["SETUP"] + rt["RUN"]) / rt["BASE_QUANTITY"]).where(
    rt["RUN_UNIT"] == "H", (rt["SETUP"] + (rt["RUN"] / 60)) / rt["BASE_QUANTITY"]
)
rt = rt.pivot_table(index=["MATERIAL", "STD_KEY"], values=["PLN HR/EA"], aggfunc=np.sum)
rt.reset_index(inplace=True)
pi3 = pi.pivot_table(
    index=["PART_NUMBER"], values=["ACT COST/EA", "HRS/EA"], aggfunc=np.sum
)
pi3.reset_index(inplace=True)
rt = rt.merge(cst, left_on="STD_KEY", right_on="ST KEY", how="left")
rt.drop(columns=["ST KEY"], axis=1, inplace=True)
rt["PLN COST/EA"] = rt["PLN HR/EA"] * rt["BUR_RATE"]
rt = rt.pivot_table(index=["MATERIAL"], values=["PLN COST/EA"], aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.merge(pi3, left_on="MATERIAL", right_on="PART_NUMBER", how="left")
rt["ACT COST/EA"] = rt["ACT COST/EA"].replace("", pd.NA).fillna(rt["PLN COST/EA"])
rt.loc[
    (rt["ACT COST/EA"] == 0) | (rt["ACT COST/EA"] < 0.6 * rt["PLN COST/EA"]),
    "ACT COST/EA",
] = rt["PLN COST/EA"]
rt.drop(columns=["PART_NUMBER"], axis=1, inplace=True)
rt.to_hdf("../H5/LBR.H5", key="ACT_V_PL_CST", mode="a")
print("LBR.H5 ACT_V_PL_CST COMPLETE")
