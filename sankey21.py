import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.io as pio
import os
import pyarrow.feather as feather
from general_functions import *


# ..............


df = pd.read_excel("regions.xlsx")
dictreg = dict(zip(df["region"], df["full name"]))

if not os.path.exists("Sankeys"):
    os.mkdir("Sankeys")
pio.orca.config.executable = "C:/Users/andrieba/anaconda3/pkgs/plotly-orca-1.2.1-1/orca_app/orca.exe"
pio.orca.config.save()
pio.kaleido.scope.mathjax = None  # ne sert à rien car mathjax ne fonctionne pas
pyo.init_notebook_mode()

pathexio = "Data/"  # wherever you have downloaded EXIOBASE data


plt_rcParams()


##########


def verification():
    i = 1995
    year = 1995
    region = "RU"
    pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"
    Yk = feather.read_feather(pathIOT + "Yk.feather")
    Y = feather.read_feather(pathIOT + "Y.feather")
    L = feather.read_feather(pathIOT + "L.feather")
    L.columns.names = ["region cons", "sector cons"]
    L.index.names = ["region prod", "sector prod"]
    Lk = feather.read_feather(pathIOT + "Lk.feather")
    Lk.columns.names = ["region cons", "sector cons"]
    Lk.index.names = ["region prod", "sector prod"]
    S_imp = (
        pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
        / 1000000000
    )
    S_imp.index.names = ["region prod", "sector prod"]

    D_pba = (
        pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/D_pba.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
        / 1000000000
    )
    D_pba.index.names = ["region prod", "sector prod"]

    D_cba = (
        pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/D_cba.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
        / 1000000000
    )
    D_cba.index.names = ["region prod", "sector prod"]
    SL = L.mul(S_imp, axis=0).sum()
    SLk = Lk.mul(S_imp, axis=0).sum()

    SL.mul(Y["RU"].sum(axis=1)).sum() == D_cba.loc["RU"].sum()
    # cba verification

    (L.mul(Y.sum(axis=1), axis=1).sum(axis=1) * S_imp).loc["RU"].sum() == D_pba.loc["RU"].sum()
    # pba verification

    Yall = Yk.unstack().sum(axis=1)
    Yall.index.names = ["region cons", "sector cons"]
    (L.mul(Yall, axis=1).sum(axis=1) * S_imp).loc["RU"].sum()
    # pba verification from Yk

    Ykall = Yk.drop("CFC", axis=1).unstack().sum(axis=1)
    Ykall.index.names = ["region cons", "sector cons"]
    (Lk.mul(Ykall, axis=1).sum(axis=1) * S_imp).loc["RU"].sum() == D_pba.loc["RU"].sum()
    # pbak verification


#######################################


def variables(region):
    DictRoW = dict.fromkeys(
        [
            "Africa",
            "Asia",
            "Europe",
            "Middle East",
            "North America",
            "Oceania",
            "South America",
        ],
        "RoW - ",
    )
    DictRoW[region] = ""

    left_index = [
        "LY Government",
        "LY Households",
        "LY GCF",
        "LY NPISHS",
        "infRegFromRoW",
    ]
    # index = left_index (delete if no error)

    right_index = [
        "(Lk-L)Y Government",
        "(Lk-L)Y Households",
        "(Lk-L)Y NCF sup",
        "(Lk-L)Y NPISHS",
        "LY Government",
        "LY Households",
        "LY NCF sup",
        "LY NPISHS",
    ]

    position_all = [
        "0. ges",
        "1. imp reg",
        "2. imp dom",
        "3. pba",
        "4. cba",
        # "5. ncf", !!!! attention, à rajouter
        "6. endo",
        "7. cbaK",
        "8. cons",
        "9. exp",
    ]

    node_list = [
        "CFC",
        "RoW - CFC",
        # "GCF",
        # "RoW - GCF",
        "Negative capital formation",
        "RoW - Negative capital formation",
        "CFC imports re-exported",
    ]

    color_dict = dict(
        zip(
            [
                "Households direct emissions",
                "Agriculture-food",
                "Energy industry",
                "Heavy industry",
                "Manufacturing industry",
                "Services",
                "Transport services",
            ],
            [
                "#8de5a1",
                "#a1c9f4",
                "#cfcfcf",
                # "#d0bbff",
                "#debb9b",
                "#fab0e4",
                "#ff9f9b",
                "#ffb482",
                # "#fffea3"
            ],
        )
    )

    return DictRoW, left_index, right_index, position_all, node_list, color_dict


def data_from_SLY(SLY, region):
    SLY = SLY.rename(
        columns={
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)": "GHG",
            "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CO2",
            "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CH4",
            "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "N2O",
        }
    )
    SLY["SF6"] = SLY["GHG"] / 1000000 - SLY[["CO2", "CH4", "N2O"]].sum(axis=1)

    SLY = SLY.drop("GHG", axis=1).stack().unstack(level=0)
    SLY["LY GCF"] = SLY["LY CFC"].fillna(0) + SLY["LY NCF"].fillna(0)

    # "save" before aggregating sectors, will be used in InfRegFromRoW

    SLY["LY NCF save"] = SLY["LY NCF"]
    SLY["LkY NCF save"] = SLY["LkY NCF"]

    SLY["LY NCF sup save"] = SLY["LY NCF save"][SLY["LY NCF save"] > 0]
    SLY["LY NCF inf save"] = -SLY["LY NCF save"][SLY["LY NCF save"] < 0]

    SLY["LkY NCF sup save"] = SLY["LkY NCF save"][SLY["LkY NCF save"] > 0]
    SLY["LkY NCF inf save"] = -SLY["LkY NCF save"][SLY["LkY NCF save"] < 0]

    # end of save

    SLY = (
        SLY.drop(["LY NCF", "LkY NCF"], axis=1)
        .append(
            SLY.loc[[region]]
            .rename(
                index=dict(
                    {
                        "Africa": "otherreg",
                        "Asia": "otherreg",
                        "Europe": "otherreg",
                        "Middle East": "otherreg",
                        "North America": "otherreg",
                        "Oceania": "otherreg",
                        "South America": "otherreg",
                        "150100:MACHINERY AND EQUIPMENT": "othercap",
                        "150200:CONSTRUCTION": "othercap",
                        "150300:OTHER PRODUCTS": "othercap",
                        "Households direct emissions": "other",
                        "Mobility": "othersect",
                        "Shelter": "othersect",
                        "Food": "othersect",
                        "Clothing": "othersect",
                        "Education": "othersect",
                        "Health": "othersect",
                        "Other goods and services": "othersect",
                        "CH4": "othergas",
                        "CO2": "othergas",
                        "N2O": "othergas",
                        "SF6": "othergas",
                    }
                )
            )[["LY NCF", "LkY NCF"]]
            .groupby(level=SLY.index.names)
            .sum()
        )
        .append(
            SLY.drop(region)
            .rename(
                index=dict(
                    {
                        # "Africa": "otherreg",
                        # "Asia": "otherreg",
                        # "Europe": "otherreg",
                        # "Middle East": "otherreg",
                        # "North America": "otherreg",
                        # "Oceania": "otherreg",
                        # "South America": "otherreg",
                        "150100:MACHINERY AND EQUIPMENT": "othercap",
                        "150200:CONSTRUCTION": "othercap",
                        "150300:OTHER PRODUCTS": "othercap",
                        "Households direct emissions": "other",
                        # "Mobility": "othersect",
                        # "Shelter": "othersect",
                        # "Food": "othersect",
                        # "Clothing": "othersect",
                        # "Education": "othersect",
                        # "Health": "othersect",
                        # "Other goods and services": "othersect",
                        "CH4": "othergas",
                        "CO2": "othergas",
                        "N2O": "othergas",
                        "SF6": "othergas",
                    }
                )
            )[["LY NCF", "LkY NCF"]]
            .groupby(level=SLY.index.names)
            .sum()
        )
    )

    SLY["LY NCF sup"] = SLY["LY NCF"][SLY["LY NCF"] > 0]
    SLY["LY NCF inf"] = -SLY["LY NCF"][SLY["LY NCF"] < 0]

    SLY["LkY NCF sup"] = SLY["LkY NCF"][SLY["LkY NCF"] > 0]
    SLY["LkY NCF inf"] = -SLY["LkY NCF"][SLY["LkY NCF"] < 0]

    data = SLY[
        [
            "LY Government",
            "LY Households",
            "LY NCF",
            "LY NCF save",
            "LY NPISHS",
            "LY CFC",
            "LY NCF sup",
            "LY NCF inf",
            "LY GCF",
            "LkY NCF inf",
        ]
    ]
    data["(Lk-L)Y Government"] = SLY["LkY Government"] - SLY["LY Government"]
    data["(Lk-L)Y Households"] = SLY["LkY Households"] - SLY["LY Households"]
    data["(Lk-L)Y NCF save"] = SLY["LkY NCF save"] - SLY["LY NCF save"]
    data["(Lk-L)Y NCF"] = SLY["LkY NCF"] - SLY["LY NCF"]
    data["(Lk-L)Y NPISHS"] = SLY["LkY NPISHS"] - SLY["LY NPISHS"]
    data["(Lk-L)Y NCF sup"] = SLY["LkY NCF sup"] - SLY["LY NCF sup"]
    data["(Lk-L)Y NCF inf"] = SLY["LkY NCF inf"] - SLY["LY NCF inf"]
    data["(Lk-L)Y NCF sup save"] = SLY["LkY NCF sup save"] - SLY["LY NCF sup save"]
    data["(Lk-L)Y NCF inf save"] = SLY["LkY NCF inf save"] - SLY["LY NCF inf save"]

    data_reg_cons = pd.DataFrame(data.stack().unstack(level="region cons")[region])
    data_reg_cons.columns.name = "region cons"
    data_reg_cons = data_reg_cons.stack()
    data_reg_exp = pd.DataFrame(data.drop([region], level="region cons").stack().unstack(level="region prod")[region])
    data_reg_exp.columns.name = "region prod"
    data_reg_exp = data_reg_exp.stack().reorder_levels(data_reg_cons.index.names)
    data = (
        pd.concat(
            [
                pd.DataFrame(data_reg_cons),
                pd.DataFrame(data_reg_exp),
            ]
        )
        .rename(columns={0: "value"})["value"]
        .unstack(level="LY name")
    )

    df = data["LY CFC"].unstack(level="sector cons").sum(axis=1) - (
        data[
            [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF sup save",
                "(Lk-L)Y NPISHS",
            ]
        ]
        .unstack(level="sector cons")
        .sum(axis=1)
    )

    sup = pd.DataFrame(
        df[df > 0],
        index=df.index,
        columns=pd.MultiIndex.from_tuples([("CFC>(Lk-L)Y", "None")], names=["LY name", "sector cons"]),
    )
    # exports of CFC
    inf = pd.DataFrame(
        -df[df < 0],
        index=df.index,
        columns=pd.MultiIndex.from_tuples([("CFC<(Lk-L)Y", "None")], names=["LY name", "sector cons"]),
    )
    # imports of CFC
    # sup + inf = abs(df)
    df = pd.concat([data.unstack(level="sector cons"), sup, inf], axis=1).stack()
    df = df.reorder_levels(data.index.names)

    data = df

    data["(Lk-L)Y - CFC<(Lk-L)Y"] = (
        data[
            [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF sup",
                "(Lk-L)Y NPISHS",
            ]
        ]
        .sum(axis=1)
        .fillna(0)
        - data["CFC<(Lk-L)Y"].fillna(0)
    )
    data = (
        pd.DataFrame(data.stack())
        .rename(columns={0: "value"})
        .reset_index()
        .set_index(
            [
                "sector cons",
                "sector prod",
                "region prod",
                "Extensions",
                "LY name",
                "region cons",
            ]
        )
    )

    try:
        infRegFromRoW = (
            data.xs("CFC<(Lk-L)Y", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)[[region]]
            .stack(level=0)
            .unstack(level="region prod")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
        )
        infRegFromRoW["LY name"] = "infRegFromRoW"
        infRegFromRoW = infRegFromRoW.reset_index().set_index(data.index.names)
        data = pd.concat(
            [
                data,
                infRegFromRoW,
            ]
        )
    except KeyError:
        try:
            infRegFromRoW = (
                data.xs("CFC<(Lk-L)Y", level="LY name")
                .unstack(level="region cons")
                .swaplevel(axis=1)[[region]]
                .stack(level=0)
                .unstack(level="region prod")
                .swaplevel(axis=1)
                # .drop(region, axis=1)
                .stack(level=0)
            )
            infRegFromRoW["LY name"] = "infRegFromRoW"
            infRegFromRoW = infRegFromRoW.reset_index().set_index(data.index.names)
            data = pd.concat(
                [
                    data,
                    infRegFromRoW,
                ]
            )
        except KeyError:
            None

    return data


def level_0(data, left_index):
    # 0. ges

    data.loc[[i for i in data.index if i[4] in left_index], ["0. ges"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(level="Extensions")

    return data


def level_1(data, left_index):

    # 1. imp reg
    data.loc[[i for i in data.index if i[4] in left_index], ["1. imp reg"]] = (
        data.loc[[i for i in data.index if i[4] in left_index]].index.get_level_values(level="region prod") + " "
    )
    return data


def level_2(region, data, left_index):
    # 2. imp dom
    Dict_ImpDom = dict.fromkeys(
        [
            "Africa",
            "Asia",
            "Europe",
            "Middle East",
            "North America",
            "Oceania",
            "South America",
        ],
        "Imports",
    )
    Dict_ImpDom[region] = "Territorial"
    data.loc[[i for i in data.index if i[4] in left_index], ["2. imp dom"]] = (
        data.loc[[i for i in data.index if i[4] in left_index]]
        .rename(index=Dict_ImpDom)
        .index.get_level_values(level="region prod")
    )
    return data


def level_3(region, data, DictRoW, left_index):
    # 3. pba

    data.loc[[i for i in data.index if i[4] in left_index], ["3. pba"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].rename(index=DictRoW).index.get_level_values(level="region prod") + data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(
        level="sector prod"
    )
    return data


def level_4(region, data, DictRoW, left_index):

    # 4. cba

    Dict_cba = dict(
        {
            "LY Government": "Government",
            "LY Households": "Households",
            "LY GCF": "GCF",
            "LY NPISHS": "NPISHS",
            "infRegFromRoW": "RoW - GCF"
            # "CFC - CFC>(Lk-L)Y": "CFC",
            # "CFC>(Lk-L)Y": "CFC",
            # "infRegFromAll",
            # "MinusSupRoWFromReg",
        }
    )

    # i[4] : 'LY name'
    data.loc[[i for i in data.index if i[4] in left_index], ["4. cba"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].rename(index=DictRoW).index.get_level_values(level="region cons") + data.loc[
        [i for i in data.index if i[4] in left_index]
    ].rename(
        index=Dict_cba
    ).index.get_level_values(
        level="LY name"
    )

    return data


def level_5(data):

    # 5. ncf

    return data


def level_6(data, DictRoW):
    # 6. endo

    data.loc[
        [
            i
            for i in data.index
            if i[4]
            in [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF sup",
                "(Lk-L)Y NPISHS",
            ]
        ],
        ["6. endo"],
    ] = (
        data.loc[
            [
                i
                for i in data.index
                if i[4]
                in [
                    "(Lk-L)Y Government",
                    "(Lk-L)Y Households",
                    "(Lk-L)Y NCF sup",
                    "(Lk-L)Y NPISHS",
                ]
            ]
        ]
        .rename(index=DictRoW)
        .index.get_level_values(level="region cons")
        + "CFCk"
    )

    # data.loc[
    #     [i for i in data.index if i[4] in ["supRegFromAll", "MinusInfRoWFromAll"]],
    #     ["5. endo"],
    # ] = "RoW - CFCk"

    return data


def level_7(region, data, right_index):
    data2 = data

    # 7. cbaK
    DictExp = dict.fromkeys(
        [
            "Africa",
            "Asia",
            "Europe",
            "Middle East",
            "North America",
            "Oceania",
            "South America",
        ],
        "Exports",
    )
    DictCbaK = dict(
        {
            "LY Government": "Government",
            "LY Households": "Households",
            "LY NCF sup": "Net capital formation",
            "LY NPISHS": "NPISHS",
            # "supRegFromAll": "supRegFromAll",
            # "MinusInfRoWFromAll": "MinusInfRoWFromAll",
            "(Lk-L)Y Government": "Government",
            "(Lk-L)Y Households": "Households",
            "(Lk-L)Y NCF sup": "Net capital formation",
            "(Lk-L)Y NPISHS": "NPISHS",
        }
    )

    data2.loc[[i for i in data2.index if i[4] in right_index], ["7. cbaK"]] = (
        data2.loc[[i for i in data2.index if i[4] in right_index]]
        .rename(index=DictExp)
        .index.get_level_values(level="region cons")
        + data2.loc[[i for i in data2.index if i[4] in right_index]]
        .rename(index=DictCbaK)
        .index.get_level_values(level="LY name")
        + " "
    )  # Space here to differenciate level 5 nodes from level 4 nodes

    data2.replace(
        dict(
            {
                region + "Government ": "Government ",
                region + "Households ": "Households ",
                region + "Net capital formation ": "Net capital formation ",
                region + "NPISHS ": "NPISHS ",
                region + "Households direct ": "Households direct ",
                # region + "supRegFromAll ": "Exports",
                # region + "MinusInfRoWFromAll ": "Exports",
                "ExportsGovernment ": "Exports",
                "ExportsHouseholds ": "Exports",
                "ExportsNet capital formation ": "Exports",
                "ExportsNPISHS ": "Exports",
                # "ExportssupRegFromAll ": "Exports",
                # "ExportsMinusInfRoWFromAll ": "Exports",
            }
        ),
        inplace=True,
    )

    return data2


def level_8(region, data, DictRoW, right_index):
    data2 = data

    # 8. cons

    data2.loc[[i for i in data2.index if i[4] in right_index], ["8. cons"]] = data2.loc[
        [i for i in data2.index if i[4] in right_index]
    ].rename(index=DictRoW).index.get_level_values(level="region cons") + data2.loc[
        [i for i in data2.index if i[4] in right_index]
    ].index.get_level_values(
        level="sector cons"
    )
    data2.replace(
        dict.fromkeys(
            [
                "150100:MACHINERY AND EQUIPMENT",
                "150200:CONSTRUCTION",
                "150300:OTHER PRODUCTS",
                "othercap",
                "RoW - 150100:MACHINERY AND EQUIPMENT",
                "RoW - 150200:CONSTRUCTION",
                "RoW - 150300:OTHER PRODUCTS",
                "RoW - othercap" "None",
                "RoW - None",
            ],
            np.nan,
        ),
        inplace=True,
    )
    data2.loc[
        [i for i in data2.index if i[4] == "LY NCF sup" and i[5] != region], ["8. cons"]
    ] = "RoW - Net capital formation "
    data2.loc[
        [i for i in data2.index if i[4] == "(Lk-L)Y NCF sup" and i[5] != region],
        ["8. cons"],
    ] = "RoW - Net capital formation "

    # data.loc[
    #     [i for i in data.index if i[4] in ["supRegFromAll", "MinusInfRoWFromAll"]],
    #     ["7. cons"],
    # ] = "CFC imports re-exported"

    return data2


def level_9(region, data, right_index):

    # 9. exp

    data.loc[[i for i in data.index if i[4] in right_index and i[5] != region], ["9. exp"],] = data.loc[
        [i for i in data.index if i[4] in right_index and i[5] != region]
    ].index.get_level_values(level="region cons")
    return data


def data_households(year, region, data):
    # Add households direct

    F_hh = feather.read_feather("F_hh.feather")[year].unstack()[region] / 1000
    share_transport = 0.55

    for ext in F_hh.index:
        data.loc["Mobility", "Households direct emissions", region, ext, "Households direct", region,] = [
            F_hh.loc[ext] * share_transport,
            ext,
            region + " ",
            "Territorial",
            "Households direct emissions",
            "Households direct",
            np.nan,
            "Households direct ",
            "Mobility",
            np.nan,
        ]

        data.loc["Shelter", "Households direct emissions", region, ext, "Households direct", region,] = [
            F_hh.loc[ext] * (1 - share_transport),
            ext,
            region + " ",
            "Territorial",
            "Households direct emissions",
            "Households direct",
            np.nan,
            "Households direct ",
            "Shelter",
            np.nan,
        ]
    return data


def data_STV(data_sankey, data, color_dict, node_dict):
    # STV = source, target, value
    position = [
        "0. ges",
        "1. imp reg",
        "2. imp dom",
        "3. pba",
        "4. cba",
        # "5. ncf",
        # "6. endo",
        "7. cbaK",
        "8. cons",
        "9. exp",
    ]
    data_sankey = pd.DataFrame()
    for j in range(0, len(position) - 1, 1):
        data_j = pd.DataFrame()
        data_j["source"] = data[position[j]].replace(node_dict)
        data_j["target"] = data[position[j + 1]].replace(node_dict)
        data_j["value"] = data["value"]
        data_j["color label"] = data.index.get_level_values(level="sector prod")
        data_j["position"] = position[j]
        data_sankey[j] = data_j.stack(dropna=False)

    data2 = data.loc[
        [
            i
            for i in data.index
            if i[4]
            in [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF sup",
                "(Lk-L)Y NPISHS",
            ]
        ]
    ]
    data_j = pd.DataFrame()
    data_j["source"] = data2["6. endo"].replace(node_dict)
    data_j["target"] = data2["7. cbaK"].replace(node_dict)
    data_j["value"] = data2["value"]
    data_j["color label"] = data2.index.get_level_values(level="sector prod")
    data_j["position"] = "6. endo"
    data_j.stack(dropna=False)
    data_sankey[j + 1] = data_j.stack(dropna=False)

    data_sankey = data_sankey.unstack().stack(level=0)
    data_sankey = data_sankey[["source", "target", "value", "color label", "position"]]
    data_sankey = (
        data_sankey.reset_index()
        .set_index(
            [
                "sector cons",
                "sector prod",
                "region prod",
                "Extensions",
                "LY name",
                "region cons",
            ]
        )
        .drop("level_6", axis=1)
    )

    data_sankey["color"] = data_sankey["color label"].replace(color_dict)
    data_sankey = pd.DataFrame(data_sankey.reset_index())[["source", "target", "color", "value", "position"]]
    data_sankey.set_index(["source", "target", "color", "position"], inplace=True)
    data_sankey = data_sankey.groupby(level=["source", "target", "color", "position"]).sum()
    data_sankey.reset_index(col_level=0, inplace=True)

    return data_sankey


def junction_4_to_5(data_sankey, region, data, node_dict, color_dict):
    data_sankey2 = data_sankey

    # (GCF-NCF sup) to CFC

    # (RoW-GCF - RoW-NCFsup) to RoW - CFC
    # RoW-GCF (infRegFromRoW) to RoW - CFC

    # LY NCF inf to CFC
    # (Lk-L)Y NCF inf to CFC
    # RoW - LY NCF inf to RoW - CFC
    # RoW - (Lk-L)Y NCF inf to RoW - CFC

    # GCF to NCF pos
    # RoW - GCF to RoW - NCF pos (Exports)

    # (GCF-NCF sup) to CFC
    ind = [
        "Agriculture-food",
        "Energy industry",
        "Heavy industry",
        "Manufacturing industry",
        "Services",
        "Transport services",
    ]
    df = (
        pd.DataFrame(
            data.xs("LY GCF", level="LY name").xs(region, level="region cons").groupby(level="sector prod").sum(),
            index=ind,
        ).fillna(0)["value"]
        - pd.DataFrame(
            data.xs("LY NCF sup", level="LY name").xs(region, level="region cons").groupby(level="sector prod").sum(),
            index=ind,
        ).fillna(0)["value"]
    )
    data_sankey2 = pd.concat(
        [
            data_sankey2,
            pd.DataFrame(
                [
                    [node_dict["GCF"]] * len(df),
                    [node_dict["CFC"]] * len(df),
                    df.values,
                    [color_dict[i] for i in df.index.values],
                    ["4. cba"] * len(df),
                ],
                index=["source", "target", "value", "color", "position"],
            ).T,
        ]
    )

    # (RoW-GCF - RoW-NCFsup) to RoW - CFC
    df = (
        pd.DataFrame(
            data.xs("LY GCF", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum(),
            index=ind,
        )["value"]
        - pd.DataFrame(
            data.xs("LY NCF sup", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum(),
            index=ind,
        )["value"]
    )
    data_sankey2 = pd.concat(
        [
            data_sankey2,
            pd.DataFrame(
                [
                    [node_dict["RoW - GCF"]] * len(df),
                    [node_dict["RoW - CFC"]] * len(df),
                    df.values,
                    [color_dict[i] for i in df.index.values],
                    ["4. cba"] * len(df),
                ],
                index=["source", "target", "value", "color", "position"],
            ).T,
        ]
    )

    # RoW-GCF (infRegFromRoW) to RoW - CFC

    try:
        df = data.xs("infRegFromRoW", level="LY name").groupby(level="sector prod").sum()["value"]
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["RoW - GCF"]] * len(df),
                        [node_dict["RoW - CFC"]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4. cba"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # LY NCF inf to CFC

    try:
        df = (
            data.xs("LY NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["Negative capital formation"]] * len(df),
                        [node_dict["CFC"]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4.5 inf"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # (Lk-L)Y NCF inf to CFC

    try:
        df = (
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["Negative capital formation"]] * len(df),
                        [node_dict["CFC"]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4.5 inf"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # RoW - LY NCF inf to RoW - CFC

    try:
        df = (
            data.xs("LY NCF inf", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["RoW - Negative capital formation"]] * len(df),
                        [node_dict["RoW - CFC"]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4.5 inf"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # RoW - (Lk-L)Y NCF inf to RoW - CFC

    try:
        df = (
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["RoW - Negative capital formation"]] * len(df),
                        [node_dict["RoW - CFC"]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4.5 inf"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # GCF to NCF pos

    try:
        df = (
            data.xs("LY NCF sup", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["GCF"]] * len(df),
                        [node_dict["Net capital formation "]] * len(df),  # LY NCF pos
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4. cba"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None

    # RoW - GCF to RoW - NCF pos (Exports)
    try:
        df = (
            data.xs("LY NCF sup", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict["RoW - GCF"]] * len(df),
                        [node_dict["Exports"]] * len(df),  # RoW - LY NCF pos
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["4. cba"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
    except KeyError:
        None
    return data_sankey2


def junction_5_to_6(data_sankey, region, data, node_dict, color_dict):
    ind = [
        "Agriculture-food",
        "Energy industry",
        "Heavy industry",
        "Manufacturing industry",
        "Services",
        "Transport services",
    ]
    (
        GCFtoCFC,
        RoWGCFtoRoWCFC,
        NegCFtoCFC1,
        RoWNegCFtoRoWCFC1,
        RoWNegCFtoRoWCFC2,
        GCFtoNCFsup,
        RoWGCFtoExports,
        RoWCFCtoCFCk,
        CFCtoCFCk,
        CFCtoRoWCFCk,
        RoWCFCtoRoWCFCk,
        importsreexp,
    ) = [pd.DataFrame()] * 12
    data_sankey2 = data_sankey

    def reindex(df):
        return pd.DataFrame(df, index=ind, columns=["value"])["value"].fillna(0)

    def concat(data_sankey2, df, node1, node2):
        data_sankey2 = pd.concat(
            [
                data_sankey2,
                pd.DataFrame(
                    [
                        [node_dict[node1]] * len(df),
                        [node_dict[node2]] * len(df),
                        df.values,
                        [color_dict[i] for i in df.index.values],
                        ["5. ncf"] * len(df),
                    ],
                    index=["source", "target", "value", "color", "position"],
                ).T,
            ]
        )
        return data_sankey2

    # junction 1

    ###
    GCFtoCFC = reindex(
        data.xs("LY GCF", level="LY name").xs(region, level="region cons").groupby(level="sector prod").sum()
    ) - reindex(
        data.xs("LY NCF sup", level="LY name").xs(region, level="region cons").groupby(level="sector prod").sum()
    )

    ###
    RoWGCFtoRoWCFC = reindex(
        data.xs("LY GCF", level="LY name")
        .unstack(level="region cons")
        .swaplevel(axis=1)
        .drop(region, axis=1)
        .stack(level=0)
        .groupby(level="sector prod")
        .sum()
    ) - reindex(
        data.xs("LY NCF sup", level="LY name")
        .unstack(level="region cons")
        .swaplevel(axis=1)
        .drop(region, axis=1)
        .stack(level=0)
        .groupby(level="sector prod")
        .sum()
    )
    try:
        RoWGCFtoRoWCFC += reindex(data.xs("infRegFromRoW", level="LY name").groupby(level="sector prod").sum()["value"])
    except KeyError:
        None

    ###
    try:
        NegCFtoCFC1 = reindex(
            data.xs("LY NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None
    try:
        NegCFtoCFC2 = reindex(
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None

    ###
    try:
        RoWNegCFtoRoWCFC1 = reindex(
            data.xs("LY NCF inf", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None
    try:
        RoWNegCFtoRoWCFC2 = reindex(
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None

    ###

    try:
        GCFtoNCFsup = reindex(
            data.xs("LY NCF sup", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None

    ###

    try:
        RoWGCFtoExports = reindex(
            data.xs("LY NCF sup", level="LY name")
            .unstack(level="region cons")
            .swaplevel(axis=1)
            .drop(region, axis=1)
            .stack(level=0)
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None

    ###########################################################################

    # junction 2
    # RoW -CFC to CFCk

    RoWCFCtoCFCk = reindex(
        data["value"]
        .xs("CFC>(Lk-L)Y", level="LY name")
        .drop(region, level="region cons")
        .groupby(level="sector prod")
        .sum()
    )
    try:
        RoWCFCtoCFCk += reindex(data.xs("infRegFromRoW", level="LY name").groupby(level="sector prod").sum()["value"])
    except KeyError:
        None

    # CFC to CFCk = CFCk - RoW CFC to CFCk

    try:
        CFCtoCFCk = reindex(
            data["value"]
            .unstack(level="LY name")[["(Lk-L)Y Government", "(Lk-L)Y Households", "(Lk-L)Y NCF sup", "(Lk-L)Y NPISHS"]]
            .sum(axis=1)
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()
        ) - reindex(RoWCFCtoCFCk)
    except KeyError:
        None

    # CFC to RoW - CFCk = CFC - (CFC to CFCk)

    CFCtoRoWCFCk = reindex(
        reindex(
            data["value"]
            .unstack(level="LY name")[["LY CFC"]]
            .sum(axis=1)
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()
        )
    ) - reindex(CFCtoCFCk)
    try:
        CFCtoRoWCFCk += reindex(
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None

    # RoWCFCtoRoWCFCk : RoWCFC + infRegFromRoW - RoWCFCtoCFCk

    RoWCFCtoRoWCFCk = (
        reindex(
            data["value"]
            .xs("LY CFC", level="LY name")
            .drop(region, level="region cons")
            .groupby(level="sector prod")
            .sum()
        )
        - RoWCFCtoCFCk
    )
    try:
        RoWCFCtoRoWCFCk += reindex(
            data.xs("infRegFromRoW", level="LY name").groupby(level="sector prod").sum()["value"]
        )
    except KeyError:
        None

    ####

    test = RoWGCFtoRoWCFC - RoWCFCtoCFCk - RoWCFCtoRoWCFCk
    if len(RoWNegCFtoRoWCFC1) > 0:
        test += RoWNegCFtoRoWCFC1
    if len(RoWNegCFtoRoWCFC2):
        test += RoWNegCFtoRoWCFC2
    if test.sum() < 0:
        RoWCFCtoCFCk += test
        CFCtoRoWCFCk += test
        CFCtoCFCk -= test

    # imports re exported, CFCtoRoWCFCk + RoWCFCtoRoWCFCk - RoWCFCk

    try:
        importsreexp = (
            reindex(CFCtoRoWCFCk[CFCtoRoWCFCk > 0])
            + reindex(RoWCFCtoRoWCFCk[RoWCFCtoRoWCFCk > 0])
            - reindex(
                data.reset_index()
                .set_index(["7. cbaK", "6. endo", "sector prod"])
                .loc["Exports"]
                .loc["RoW - CFCk"]["value"]
                .groupby(level="sector prod")
                .sum()
            )
        )
        if importsreexp.sum() > 0:
            importsreexp = importsreexp[importsreexp > 0] * importsreexp.sum() / importsreexp[importsreexp > 0].sum()
            data_sankey2 = concat(data_sankey2, importsreexp, "RoW - CFCk", "CFC imports re-exported")
    except KeyError:
        None

    ####

    data_sankey2 = concat(data_sankey2, GCFtoCFC, "GCF", "CFC")
    data_sankey2 = concat(data_sankey2, RoWGCFtoRoWCFC, "RoW - GCF", "RoW - CFC")
    if len(NegCFtoCFC1) > 0:
        data_sankey2 = concat(data_sankey2, NegCFtoCFC1, "Negative capital formation", "CFC")
    if len(RoWNegCFtoRoWCFC1) > 0:
        data_sankey2 = concat(data_sankey2, RoWNegCFtoRoWCFC1, "RoW - Negative capital formation", "RoW - CFC")
    if len(RoWNegCFtoRoWCFC2) > 0:
        data_sankey2 = concat(data_sankey2, RoWNegCFtoRoWCFC2, "RoW - Negative capital formation", "RoW - CFC")
    if len(GCFtoNCFsup) > 0:
        data_sankey2 = concat(data_sankey2, GCFtoNCFsup, "GCF", "Net capital formation ")
    if len(RoWGCFtoExports) > 0:
        data_sankey2 = concat(data_sankey2, RoWGCFtoExports, "RoW - GCF", "Exports")
    data_sankey2 = concat(data_sankey2, RoWCFCtoCFCk, "RoW - CFC", "CFCk")
    data_sankey2 = concat(data_sankey2, CFCtoCFCk, "CFC", "CFCk")
    data_sankey2 = concat(data_sankey2, CFCtoRoWCFCk, "CFC", "RoW - CFCk")

    data_sankey2 = concat(data_sankey2, RoWCFCtoRoWCFCk, "RoW - CFC", "RoW - CFCk")

    return data_sankey2


def data_Sankey(year, region):

    SLY = feather.read_feather("SLY/" + region + "/" + str(year) + ".feather") / 1000

    DictRoW, left_index, right_index, position_all, node_list, color_dict = variables(region)

    data = pd.DataFrame()
    data = data_from_SLY(SLY, region)

    data = level_0(data, left_index)
    data = level_1(data, left_index)
    data = level_2(region, data, left_index)
    data = level_3(region, data, DictRoW, left_index)
    data = level_4(region, data, DictRoW, left_index)
    data = level_5(data)
    data = level_6(data, DictRoW)
    data = level_7(region, data, right_index)
    data = level_8(region, data, DictRoW, right_index)
    data = level_9(region, data, right_index)
    data = data_households(year, region, data)

    # Nodes

    for j in position_all:
        node_list.extend(list(dict.fromkeys(data.reset_index()[j])))
    node_list = [
        x
        for x in node_list
        if str(x) != "nan"
        and str(x) != "otherreg"
        and str(x) != "othercap"
        and str(x) != "othersect"
        and str(x) != "othergas"
    ]
    node_dict = dict(zip(node_list, list(range(0, len(node_list), 1))))

    data_sankey = pd.DataFrame()
    data_sankey = data_STV(data_sankey, data, color_dict, node_dict)

    # junctions
    # data_sankey = junction_4_to_5(data_sankey, region, data, node_dict, color_dict)
    data_sankey = junction_5_to_6(data_sankey, region, data, node_dict, color_dict)

    return node_dict, node_list, data_sankey


#########################################


def pop():
    pop = (
        rename_region(
            pd.read_csv("World Bank/pop.csv", header=[2], index_col=[0])[[str(i) for i in range(1995, 2020, 1)]],
            level="Country Name",
        )
        .drop("Z - Aggregated categories")
        .rename(
            dict(
                zip(
                    cc.name_shortas("EXIO3")["name_short"].values,
                    cc.name_shortas("EXIO3")["EXIO3"].values,
                )
            )
        )
        .groupby(level=0)
        .sum()
    )
    pop.columns = [int(i) for i in pop.columns]

    pop.loc["TW"] = pd.read_excel("pop Taiwan.xls", header=0, index_col=0)["TW"]

    feather.write_feather(pop, "pop.feather")


def nodes_data():
    population = feather.read_feather("pop.feather")
    for year in range(1995, 2020, 1):
        for region in pd.read_excel("regions.xlsx", index_col=0).index:
            # for region in ["RU"]:
            pop = population[year].loc[region] / 1000000
            node_dict, node_list, data_sankey = data_Sankey(year, region)
            nodes = pd.DataFrame(
                [],
                index=node_list,
                columns=[
                    "label Mt",
                    "value Mt",
                    "label t/cap",
                    "value t/cap",
                    "position",
                ],
            )
            target_data = data_sankey.set_index("target").groupby(level="target").sum()
            source_data = data_sankey.set_index("source").groupby(level="source").sum()
            # on va rajouter les données entre parenthèses
            for node in node_list:
                try:
                    # j_modified = pd.DataFrame(node_list).replace(dict(FR="France"))[0].loc[i]
                    # Mettre dict complet pour toutes régions
                    if node_dict[node] in source_data.index:
                        nodes["value Mt"].loc[node] = source_data["value"].loc[node_dict[node]]

                        a = data_sankey.reset_index().set_index("source")["position"].loc[node_dict[node]]
                        if node in [
                            "Negative capital formation",
                            "RoW - Negative capital formation",
                        ]:
                            nodes["position"].loc[node] = "4. cba"
                        elif type(a) == str:
                            nodes["position"].loc[node] = a
                        elif node in ["GCF", "RoW - GCF"]:
                            nodes["position"].loc[node] = "4. cba"
                        else:
                            nodes["position"].loc[node] = a.values[0]

                    else:
                        nodes["value Mt"].loc[node] = target_data["value"].loc[node_dict[node]]
                        if node in [
                            "Africa",
                            "Asia",
                            "Europe",
                            "Middle East",
                            "North America",
                            "Oceania",
                            "South America",
                        ]:
                            nodes["position"].loc[node] = "9. exp"

                        elif node in ["CFC", "RoW - CFC"]:
                            nodes["position"].loc[node] = "5. ncf"
                        elif node in ["CFCk", "RoW - CFCk"]:
                            nodes["position"].loc[node] = "6. endo"
                        else:
                            nodes["position"].loc[node] = "8. cons"
                except KeyError:
                    nodes = nodes.drop(node)
            nodes.loc["Net capital formation "]["position"] = "7. cbaK"

            nodes = nodes.drop([i for i in nodes.index if nodes["value Mt"].isnull().loc[i]])
            nodes = nodes.drop([i for i in nodes["value Mt"].index if nodes["value Mt"].loc[i] == 0])

            nodes["label Mt"] = nodes.index + " (" + [str(int(i)) for i in nodes["value Mt"]] + ")"
            nodes["value t/cap"] = nodes["value Mt"] / pop
            nodes["label t/cap"] = nodes.index + " (" + [str(round(i, 2)) for i in nodes["value t/cap"]] + ")"

            if not os.path.exists("Sankeys/" + region):
                os.mkdir("Sankeys/" + region)
            feather.write_feather(nodes, "Sankeys/" + region + "/nodes" + region + str(year) + ".feather")
            feather.write_feather(
                data_sankey,
                "Sankeys/" + region + "/data" + region + str(year) + ".feather",
            )
            feather.write_feather(
                pd.DataFrame(node_list),
                "Sankeys/" + region + "/nodelist" + region + str(year) + ".feather",
            )


def node_y(nodes, node, white, color, region):
    if node == "CFC":
        node = "GCF"
    if node == "RoW - CFC":
        node = "RoW - GCF"
    if node == "CFCk":
        node = "GCF"
    if node == "RoW - CFCk":
        node = "RoW - GCF"
    if node == "Exports":
        node = "RoW - Health"
    if node == "CFC imports re-exported":
        node = "RoW - Mobility"

    pos = nodes["position"].loc[node]
    df = nodes.reset_index().set_index(["position", "index"]).loc[pos]["value Mt"]

    if node in [
        "Households direct ",
        "Households ",
        "Government ",
        "NPISHS ",
        "Net capital formation ",
    ]:
        df2 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["8. cons"]["value Mt"]
            .loc[
                [
                    "RoW - Mobility",
                    "RoW - Shelter",
                    "RoW - Food",
                    "RoW - Clothing",
                    "RoW - Education",
                    "RoW - Health",
                    "RoW - Other goods and services",
                    "RoW - Net capital formation ",
                    # "CFC imports re-exported",
                ]
            ]
        )
        df = df.drop("Exports").append(df2)

    if node in [
        "Africa",
        "Asia",
        "Europe",
        "Middle East",
        "North America",
        "Oceania",
        "South America",
    ]:
        df2 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["8. cons"]["value Mt"]
            .loc[
                [
                    i
                    for i in [
                        "Mobility",
                        "Shelter",
                        "Food",
                        "Clothing",
                        "Education",
                        "Health",
                        "Other goods and services",
                    ]
                    if i in nodes.index
                ]
            ]
        )
        df = df.append(df2)
        df3 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["7. cbaK"]["value Mt"]
            .loc["Net capital formation "]
        )
        df.loc["Net capital formation "] = df3

    if node in [
        "RoW - Mobility",
        "RoW - Shelter",
        "RoW - Food",
        "RoW - Clothing",
        "RoW - Education",
        "RoW - Health",
        "RoW - Other goods and services",
        "RoW - Net capital formation ",
        # "CFC imports re-exported",
    ]:
        df3 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["7. cbaK"]["value Mt"]
            .loc["Net capital formation "]
        )
        df.loc["Net capital formation "] = df3

    total = max(
        nodes.reset_index().set_index("position").loc["4. cba"]["value Mt"].sum(),
        nodes.reset_index().set_index("position").loc["7. cbaK"]["value Mt"].sum(),
    )
    if pos == "0. ges":
        df = df.reindex(["CO2", "CH4", "N2O", "SF6"])
    elif pos == "1. imp reg":
        df = df.reindex(pd.Index([region + " "]).union(df.index.sort_values().drop(region + " "), sort=False))
    elif pos == "2. imp dom":
        df = df.reindex(["Territorial", "Imports"])
    elif pos == "3. pba":
        df = df.reindex(
            pd.Index(["Households direct emissions"])
            .union(
                df.loc[df.index.str[:2] != "Ro"].index.drop("Households direct emissions"),
                sort=False,
            )
            .union(df.loc[df.index.str[:2] == "Ro"].index, sort=False)
        )
    elif pos == "4. cba":
        df = df.reindex(
            [
                "Households direct",
                "Households",
                "Government",
                "NPISHS",
                "Net capital formation",
                # "Consumption of fixed capital",
                "GCF",
                "Negative capital formation",
                "RoW - Negative capital formation",
                "RoW - GCF",
                "RoW - Households",
                "RoW - Government",
                "RoW - NPISHS",
                "RoW - Net capital formation",
                # "RoW - Consumption of fixed capital ",
            ]
        )
    elif pos == "7. cbaK":
        df = df.reindex(
            [
                "Households direct ",
                "Households ",
                "Government ",
                "NPISHS ",
                "Net capital formation ",
                # "Exports",
                "RoW - Mobility",
                "RoW - Shelter",
                "RoW - Food",
                "RoW - Clothing",
                "RoW - Education",
                "RoW - Health",
                "RoW - Other goods and services",
                "RoW - Net capital formation ",
                # "CFC imports re-exported",
            ]
        )

    elif pos == "8. cons":
        df = df.reindex(
            [
                i
                for i in [
                    "Mobility",
                    "Shelter",
                    "Food",
                    "Clothing",
                    "Education",
                    "Health",
                    "Other goods and services",
                    "Net capital formation ",
                    "RoW - Mobility",
                    "RoW - Shelter",
                    "RoW - Food",
                    "RoW - Clothing",
                    "RoW - Education",
                    "RoW - Health",
                    "RoW - Other goods and services",
                    "RoW - Net capital formation ",
                    # "CFC imports re-exported",
                ]
                if i in nodes.index
            ]
        )
    elif pos == "9. exp":
        df = df.reindex(
            [
                i
                for i in [
                    "Mobility",
                    "Shelter",
                    "Food",
                    "Clothing",
                    "Education",
                    "Health",
                    "Other goods and services",
                    "Net capital formation ",
                    "Africa",
                    "Asia",
                    "Europe",
                    "Middle East",
                    "North America",
                    "Oceania",
                    "South America",
                ]
                if i in nodes.index
            ]
        )
    return (
        len(df.loc[:node]) / (len(df) + 1) * (1 - color * df.sum() / total)
        + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
    )


def Nodes(region, year, height, top_margin, bottom_margin, pad, ratio):
    nodes = feather.read_feather("Sankeys/" + region + "/nodes" + region + str(year) + ".feather")

    size = height - top_margin - bottom_margin
    n = max(nodes.reset_index().set_index("position").index.value_counts())
    pad2 = (size - ratio * (size - (n + 1) * pad)) / (n + 1)
    white = ((n + 1) * pad2) / size
    color = 1 - white

    nodes = nodes.assign(
        x=lambda d: d["position"].replace(
            dict(
                zip(
                    [
                        "0. ges",
                        "1. imp reg",
                        "2. imp dom",
                        "3. pba",
                        "4. cba",
                        "5. ncf",
                        "6. endo",
                        "7. cbaK",
                        "8. cons",
                        "9. exp",
                    ],
                    (
                        [
                            0.001,
                            0.08,  # 8
                            0.18,  # 10
                            0.27,  # 9
                            0.41,  # 13
                            0.50,  # 9
                            0.58,  # 8
                            0.7,  # 12
                            0.9,  # 10
                            0.999,
                        ]
                    ),
                )
            )
        ),
        y=lambda d: [node_y(nodes, i, white, color, region) for i in d.index],
    )
    # nodes["x"].loc["GCF"] = 0.41
    # nodes["x"].loc["RoW - GCF"] = 0.41
    nodes["x"].loc["Exports"] = 0.65
    try:
        nodes["x"].loc["CFC imports re-exported"] = 0.65
    except KeyError:
        None

    try:
        nodes["x"].loc["RoW - Negative capital formation"] = 0.45
    except KeyError:
        None

    try:
        nodes["x"].loc["Negative capital formation"] = 0.45
    except KeyError:
        None
    # nodes["x"].loc[["CFC","RoW - CFC"]] = 0.76
    # nodes["x"].loc[["CFCk","RoW - CFCk"]] = 0.76

    nodes["x"].loc[
        [
            "RoW - Mobility",
            "RoW - Shelter",
            "RoW - Food",
            "RoW - Clothing",
            "RoW - Education",
            "RoW - Health",
            "RoW - Other goods and services",
            "RoW - Net capital formation ",
        ]
    ] = 0.77
    return nodes, pad2


##########################################


def norm():
    regions = pd.read_excel("regions.xlsx")["region"].values
    df = pd.DataFrame([], columns=[i for i in range(1995, 2020, 1)], index=regions)
    for year in range(1995, 2020, 1):
        for region in regions:
            data_sankey = feather.read_feather("Sankeys/" + region + "/data" + region + str(year) + ".feather")
            df.loc[region].loc[year] = data_sankey.set_index("position").loc["0. ges"].sum().loc["value"]
    feather.write_feather(df.div(pd.DataFrame(df.T.max())[0], axis=0), "norm.feather")


def norm_cap():
    population = feather.read_feather("pop.feather")
    regions = pd.read_excel("regions.xlsx")["region"].values
    df = pd.DataFrame([], columns=[i for i in range(1995, 2020, 1)], index=regions)
    for year in range(1995, 2020, 1):
        for region in regions:
            pop = population[year].loc[region] / 1000
            data_sankey = feather.read_feather("Sankeys/" + region + "/data" + region + str(year) + ".feather")
            df.loc[region].loc[year] = data_sankey.set_index("position").loc["0. ges"].sum().loc["value"] / pop
    feather.write_feather(df.div(pd.DataFrame(df.T.max())[0], axis=0), "norm_cap.feather")


##########################################


def fig_sankey(region, year):

    norm = feather.read_feather("norm.feather")
    data_sankey = feather.read_feather("Sankeys/" + region + "/data" + region + str(year) + ".feather")
    node_list = feather.read_feather("Sankeys/" + region + "/nodelist" + region + str(year) + ".feather")[0].values

    height = 450
    width = 1100
    top_margin = 0
    bottom_margin = 0
    left_margin = 5
    right_margin = 5
    pad = 10

    ratio = norm.loc[region].loc[year]

    nodes, pad2 = Nodes(region, year, height, top_margin, bottom_margin, pad, ratio)
    # node_dict, node_list, data_sankey = data_Sankey(year, region)

    link = dict(
        source=data_sankey["source"],
        target=data_sankey["target"],
        value=data_sankey["value"],
        label=list(str(x) + " Mt CO2 eq" for x in data_sankey["value"].astype(float).round(1)),
        color=data_sankey["color"],
        hovertemplate="",
    )
    node = {
        # "label": pd.DataFrame(node_list)[0],
        "label": (pd.DataFrame(nodes, index=node_list))["label Mt"].replace(dictreg).values,
        "pad": pad2,
        "thickness": 5,
        "color": "gray",
        "x": nodes["x"].values,
        "y": nodes["y"].values,
    }

    sankey = go.Sankey(
        link=link,
        node=node,  #
        valueformat=".0f",
        valuesuffix=" Mt CO2eq",
        # arrangement="snap",
    )

    fig = go.Figure(sankey)
    fig.update_layout(
        hovermode="y",
        title="Greenhouse gas footprint of " + str(year) + " (Mt CO2eq)",
        font=dict(size=8, color="black"),
        paper_bgcolor="white",
    )

    fig.update_traces(
        legendrank=10,
        node_hoverinfo="all",
        hoverlabel=dict(align="left", bgcolor="white", bordercolor="black"),
    )

    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=left_margin, r=right_margin, t=top_margin, b=bottom_margin),
    )

    # fig.update_traces(textfont_size=7)
    # fig.write_image("Sankeys/" + region + "/fig2" + region + str(year) + ".pdf", engine="orca")
    # # fig.write_image("SankeyFR" + str(year) + ".svg", engine="orca")

    fig.show()


def fig_sankey_cap(year, region):

    pop = feather.read_feather("pop.feather")[year].loc[region] / 1000
    nodes = feather.read_feather("Sankeys/" + region + "/nodes" + region + str(year) + ".feather")
    data_sankey = feather.read_feather("Sankeys/" + region + "/data" + region + str(year) + ".feather")
    data_sankey["value"] = data_sankey["value"] / pop

    norm = feather.read_feather("norm_cap.feather")

    height = 450
    width = 1100
    top_margin = 0
    bottom_margin = 0
    left_margin = 5
    right_margin = 5
    pad = 10

    ratio = norm.loc[region].loc[year]

    size = height - top_margin - bottom_margin
    n = len(nodes.reset_index().set_index("position").loc["7. cons"])
    pad2 = (size - ratio * (size - n * pad)) / (n)
    color = (size - (n) * pad2) / size
    white = ((n) * pad2) / size

    nodes = nodes.assign(
        x=lambda d: d["position"].replace(
            dict(
                zip(
                    [
                        "0. ges",
                        "1. imp reg",
                        "2. imp dom",
                        "3. pba",
                        "4. cba",
                        "6. cbaK",
                        "7. cons",
                        "8. exp",
                    ],
                    ([0.001, 0.09, 0.20, 0.32, 0.56, 0.73, 0.86, 0.999]),
                )
            )
        ),
        y=lambda d: [node_y(nodes, i, white, color, region) for i in d.index],
    )

    nodes["x"].loc["Consumption of fixed capital"] = 0.645
    nodes["x"].loc["RoW - Consumption of fixed capital"] = 0.645

    nodes["x"].loc["Exports"] = 0.6875

    nodes["x"].loc[
        [
            "RoW - Mobility",
            "RoW - Shelter",
            "RoW - Food",
            "RoW - Clothing",
            "RoW - Education",
            "RoW - Health",
            "RoW - Other goods and services",
            "RoW - Net capital formation ",
        ]
    ] = 0.76

    for sect in [
        "Mobility",
        "Shelter",
        "Food",
        "Clothing",
        "Education",
        "Health",
        "Other goods and services",
    ]:
        try:
            nodes["x"].loc[sect] = 0.88
        except KeyError:
            None

    nodes["label t/cap"].loc["Consumption of fixed capital"] = ""
    nodes["label t/cap"].loc["RoW - Consumption of fixed capital"] = ""

    link = dict(
        source=data_sankey["source"],
        target=data_sankey["target"],
        value=data_sankey["value"],
        label=list(str(x) + " Mt CO2 eq" for x in data_sankey["value"].round(1)),
        color=data_sankey["color"],
        hovertemplate="",
    )

    node = {
        # "label": pd.DataFrame(node_list).replace(dict(FR="France"))[0],
        "label": nodes["label t/cap"].replace(dictreg),
        "pad": pad2,
        "thickness": 5,
        "color": "gray",
        "x": nodes["x"].values,
        "y": nodes["y"].values,
    }
    sankey = go.Sankey(
        link=link,
        node=node,  #
        valueformat=".0f",
        valuesuffix=" Mt CO2eq",
        # arrangement="snap",
    )

    fig = go.Figure(sankey)
    fig.update_layout(
        hovermode="y",
        title="Greenhouse gas footprint of " + str(year) + " (Mt CO2eq)",
        font=dict(size=8, color="black"),
        paper_bgcolor="white",
    )

    fig.update_traces(
        legendrank=10,
        node_hoverinfo="all",
        hoverlabel=dict(align="left", bgcolor="white", bordercolor="black"),
    )

    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=left_margin, r=right_margin, t=top_margin, b=bottom_margin),
    )

    # fig.update_traces(textfont_size=7)
    # fig.write_image("SankeyFR" + str(year) + ".pdf", engine="orca")
    # fig.write_image("SankeyFR" + str(year) + ".svg", engine="orca")
    fig.show()
