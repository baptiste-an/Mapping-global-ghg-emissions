import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.io as pio
import os
import pyarrow.feather as feather
from general_functions import *

#######

df = pd.read_excel("Data/regions.xlsx")
dictreg = dict(zip(df["region"], df["full name"]))

if not os.path.exists("Results/Sankeys"):
    os.mkdir("Results/Sankeys")

# adapt to your environment
pio.orca.config.executable = (
    "C:/Users/andrieba/anaconda3/pkgs/plotly-orca-1.2.1-1/orca_app/orca.exe"
)
pio.orca.config.save()
pio.kaleido.scope.mathjax = None
pyo.init_notebook_mode()
pio.renderers.default = "vscode"

plt_rcParams()

#######

# "Households direct   " => "Direct emissions"


def variables(region):
    """Defines some of the variables necessary to build sankey.

    Parameters
    ----------
    None

    region : string
        region studied

    Returns
    -------
    DictRoW : dictionnary
        converts continents into RoW
    left_index : list
        name of SLY index used in left hand side of sankey
    right_index : list
        name of SLY index used in left right side of sankey
    position_all : list
        name of the main levels of sankey
    node_list : list
        name of some sankey nodes (those whose treatment is not automated)
    color_dict : dictionnary
        assigns a color to a production sector

    """
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
    DictRoW[dictreg[region]] = ""

    left_index = [
        "LY Government",
        "LY Households",
        "LY GCF",
        "LY NPISHS",
        "infRegFromRoW",
    ]

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
        # "5. ncf", added later
        "6. endo",
        "7. cbaK",
        "8. cons",
        "9. exp",
    ]

    node_list = [
        "CFC",
        "RoW - CFC",
        "Negative capital formation",
        "RoW - Negative capital formation",
        "CFC imports re-exported",
    ]

    color_dict = dict(
        zip(
            [
                "Direct emissions",  # "Households direct   "
                "Agriculture-food",
                "Energy industry",
                "Heavy industry",
                "Manufacturing industry",
                "Services",
                "Transport services",
            ],
            [
                "#8de5a1",  # colors will be changed later on with another dict
                "#a1c9f4",
                "#cfcfcf",
                "#debb9b",
                "#fab0e4",
                "#ff9f9b",
                "#ffb482",
            ],
        )
    )

    return DictRoW, left_index, right_index, position_all, node_list, color_dict


def level_0(data, left_index):
    """Adds the level GHG to data.

    Add a columns "0. ges" corresponding to the index level Extensions, if 'LY name' is in left_index

    Parameters
    ----------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    left_index : list
        Names of the SLY levels used in the left hand size of the diagram

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """
    # i[4] : 'LY name'
    data.loc[[i for i in data.index if i[4] in left_index], ["0. ges"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(level="Extensions")

    return data


def level_1(data, left_index):
    """Adds the level region of production to data.

    Add a columns "1. imp reg" corresponding to the index level "region prod", if 'LY name' is in left_index

    Parameters
    ----------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    left_index : list
        Names of the SLY levels used in the left hand size of the diagram

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """
    # i[4] : 'LY name'
    data.loc[[i for i in data.index if i[4] in left_index], ["1. imp reg"]] = (
        data.loc[[i for i in data.index if i[4] in left_index]].index.get_level_values(
            level="region prod"
        )
        + " "
    )  # spaces here to differentiate from exports
    return data


def level_2(region, data, left_index):
    """Adds the level importation/territorial to data.

    Add a columns "2. imp dom" corresponding to the index level "region prod", if 'LY name' is in left_index

    Parameters
    ----------
    region : string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    left_index : list
        Names of the SLY levels used in the left hand size of the diagram

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """

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
    Dict_ImpDom[dictreg[region]] = "Territorial"
    # i[4] : 'LY name'
    data.loc[[i for i in data.index if i[4] in left_index], ["2. imp dom"]] = (
        data.loc[[i for i in data.index if i[4] in left_index]]
        .rename(index=Dict_ImpDom)
        .index.get_level_values(level="region prod")
    )
    return data


def level_3(data, DictRoW, left_index):
    """Adds the pba sectors to data.

    Add a columns "3. pba" corresponding to the index level "sector prod", if 'LY name' is in left_index

    Parameters
    ----------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    DictRoW : dictionnary
        To transform regions into continents
    left_index : list
        Names of the SLY levels used in the left hand size of the diagram

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """
    # i[4] : 'LY name'
    data.loc[[i for i in data.index if i[4] in left_index], ["3. pba"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].rename(index=DictRoW).index.get_level_values(level="region prod") + data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(
        level="sector prod"
    )
    return data


def level_4(data, DictRoW, left_index):
    """Adds the cba consumption types to data (households, government, etc.).

    Add a columns "4. cba" corresponding to the index level "LY name", if 'LY name' is in left_index

    Parameters
    ----------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    DictRoW : dictionnary
        To transform regions into continents
    left_index : list
        Names of the SLY levels used in the left hand size of the diagram

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """

    Dict_cba = dict(
        {
            "LY Government": "Government",
            "LY Households": "Households",
            "LY GCF": "GCF",
            "LY NPISHS": "NPISHS",
            "infRegFromRoW": "RoW - GCF",
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


def level_6(data, DictRoW):
    """Adds the cba consumption types to data (households, government, etc.).

    Add a columns "6. endo" corresponding to the index level "LY name", for capital levels.

    Parameters
    ----------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    DictRoW : dictionnary
        To transform regions into continents

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """

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

    return data


def level_7(region, data, right_index):
    """Adds the cbaK consumption types to data (households, government, etc.).

    Add a columns "7. cbaK" corresponding to the index level "LY name", if 'LY name' is in right_index

    Parameters
    ----------
    region : string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    right_index : list
        Names of the SLY levels used in the right hand size of the diagram

    Returns
    -------
    data2 : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """

    data2 = data

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
            "LY NCF sup": "Positive capital formation",
            "LY NPISHS": "NPISHS",
            "(Lk-L)Y Government": "Government",
            "(Lk-L)Y Households": "Households",
            "(Lk-L)Y NCF sup": "Positive capital formation",
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
    )  # Space here to differenciate from nodes with same name

    data2.replace(
        dict(
            {
                region + "Government ": "Government ",
                region + "Households ": "Households ",
                region + "Positive capital formation ": "Positive capital formation ",
                region + "NPISHS ": "NPISHS ",
                # dictreg[region] + "Households direct ": "Households direct ",
                "ExportsGovernment ": "Exports",
                "ExportsHouseholds ": "Exports",
                "ExportsPositive capital formation ": "Exports",
                "ExportsNPISHS ": "Exports",
            }
        ),
        inplace=True,
    )

    return data2


def level_8(region, data, DictRoW, right_index):
    """Adds the final consumption sectors to data (shelter, food, etc.).

    Add a columns "8. cons" corresponding to the index level "LY name", if 'LY name' is in right_index

    Parameters
    ----------
    region : string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    DictRoW : dictionnary
        To transform regions into continents
    right_index : list
        Names of the SLY levels used in the right hand size of the diagram

    Returns
    -------
    data2 : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """
    data2 = data

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
                "RoW - othercap",
                "None",
                "RoW - None",
            ],
            np.nan,
        ),
        inplace=True,
    )
    data2.loc[
        [i for i in data2.index if i[4] == "LY NCF sup" and i[5] != region], ["8. cons"]
    ] = "RoW - Positive capital formation "
    data2.loc[
        [i for i in data2.index if i[4] == "(Lk-L)Y NCF sup" and i[5] != region],
        ["8. cons"],
    ] = "RoW - Positive capital formation "

    return data2


def level_9(region, data, right_index):
    """Adds the final consumption region to data.

    Add a columns "9. exp" corresponding to the final consumption region, if 'LY name' is in right_index

    Parameters
    ----------
    region: string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    right_index : list
        Names of the SLY levels used in the right hand size of the diagram

    Returns
    -------
    data2 : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """

    data2 = data

    data2.loc[
        [
            i
            for i in data2.index
            if i[4] in right_index
            and i[5] == region
            and i[0]
            in [
                "Clothing",
                "Education",
                "Food",
                "Health",
                "Mobility",
                "Other goods and services",
                "Shelter",
            ]
        ],
        ["9. exp"],
    ] = "Footprint"

    data2.loc[
        [i for i in data2.index if i[4] in right_index and i[5] != region],
        ["9. exp"],
    ] = data2.loc[
        [i for i in data2.index if i[4] in right_index and i[5] != region]
    ].index.get_level_values(
        level="region cons"
    )
    return data2


def data_households(year, region, data):
    """Adds the households direct emissions to data.

    Parameters
    ----------
    year : string
    region : string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    Returns
    -------
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.

    """
    # Add households direct

    F_hh = feather.read_feather("Data/F_hh.feather")[year].unstack()[region] / 1000
    share_direct = (
        feather.read_feather("Results/share_direct_final.feather")
        .xs(region, level="region")
        .xs(year, level=2)
    )

    for ext in ["CH4", "CO2", "N2O"]:
        for sectcons in [
            "Mobility",
            "Shelter",
            "Food",
            "Other goods and services",
            # "Education", no direct emissions
            # "Health", no direct emissions
            # "Clothing", no direct emissions
        ]:
            for sectfd in ["Households", "NPISHS", "Government"]:
                fddict = dict(
                    {
                        "Households": "Final consumption expenditure by households",
                        "NPISHS": "Final consumption expenditure by non-profit organisations serving households (NPISH)",
                        "Government": "Final consumption expenditure by government",
                    }
                )
                share = share_direct.loc[ext].loc[sectfd].loc[sectcons]

                data.loc[
                    sectcons,  # "Mobility",
                    "Direct emissions",  # "Households direct   "
                    region,
                    ext,
                    sectfd,  # "Households direct",
                    region,
                ] = [
                    F_hh.loc[ext].loc[fddict[sectfd]] * share,
                    ext,
                    dictreg[region] + " ",
                    "Territorial",
                    "Direct emissions",  # "Households direct   "
                    sectfd,  # "Households direct"
                    np.nan,
                    sectfd + " ",  # "Households direct ",
                    sectcons,  # "Mobility",
                    "Footprint",
                ]

                # # data.loc[
                # #     "Shelter",
                # #     "Households direct   ",
                # #     region,
                # #     ext,
                # #     "Households direct",
                # #     region,
                # # ] = [
                # #     F_hh.loc[ext] * (1 - share_transport),
                # #     ext,
                # #     dictreg[region] + " ",
                # #     "Territorial",
                # #     "Households direct   ",
                # #     "Households direct",
                # #     np.nan,
                # #     "Households direct ",
                # #     "Shelter",
                # #     "Footprint",
                # # ]
    return data


def data_STV(data_sankey, data, color_dict, node_dict):
    """Adds "source", "target", "value", 'color' to data_sankey to represnet the flows between nodes.

    Parameters
    ----------
    data_sankey : pd.DataFrame
        Table used to represent the flows in the format source/target/value
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    color_dict : dictionnary
        Dict to transform production sector into color
    node_dict : dictionnary
        Dict to transform node names into node numbers

    Returns
    -------
    data_sankey : pd.DataFrame
        Table used to represent the flows in the format source/target/value

    """

    # STV = source, target, value
    position = [
        "0. ges",
        "1. imp reg",
        "2. imp dom",
        "3. pba",
        "4. cba",
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
    data_sankey = pd.DataFrame(data_sankey.reset_index())[
        ["source", "target", "color", "value", "position"]
    ]
    data_sankey.set_index(["source", "target", "color", "position"], inplace=True)
    data_sankey = data_sankey.groupby(
        level=["source", "target", "color", "position"]
    ).sum()
    data_sankey.reset_index(col_level=0, inplace=True)

    return data_sankey


def junction_5_to_6(data_sankey, region, data, node_dict, color_dict):
    """Adds the flows for the junction between cba and cbak.

    As one cannot precisely trace all the flows, we use many steps to represent the flows avoiding negative flows.
    Many conditions exist to adapt to all particular cases.

    Parameters
    ----------
    data_sankey : pd.DataFrame
        Table used to represent the flows in the format source/target/value
    region : string
    data : pd.DataFrame
        Table that will in the end contain all the information required to build sankey.
    node_dict : dictionnary
        Dict to transform node names into node numbers
    color_dict : dictionnary
        Dict to transform production sector into color


    Returns
    -------
    data_sankey : pd.DataFrame
        Table used to represent the flows in the format source/target/value

    """
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
        NegCFtoCFC2,
        RoWNegCFtoRoWCFC1,
        RoWNegCFtoRoWCFC2,
        GCFtoNCFsup,
        RoWGCFtoExports,
        RoWCFCtoCFCk,
        CFCtoCFCk,
        CFCtoRoWCFCk,
        RoWCFCtoRoWCFCk,
        importsreexp,
    ) = [
        pd.DataFrame()
    ] * 13  # all of the flows to be added
    data_sankey2 = data_sankey

    def reindex(df):
        return pd.DataFrame(df, index=ind, columns=["value"])["value"].fillna(
            0
        )  # add nans to a dataframe and indexes it using "ind" to make operations with other dataframew with same index

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

    def to_abs(df):
        if df.sum() > 0:
            return reindex(df[df > 0] * df.sum() / df[df > 0].sum())
        else:
            return reindex(df[df < 0] * df.sum() / df[df < 0].sum())

    # junction 1

    ###
    GCFtoCFC = reindex(
        data.xs("LY GCF", level="LY name")
        .xs(region, level="region cons")
        .groupby(level="sector prod")
        .sum()
    ) - reindex(
        data.xs("LY NCF sup", level="LY name")
        .xs(region, level="region cons")
        .groupby(level="sector prod")
        .sum()
    )
    GCFtoCFC = to_abs(GCFtoCFC)

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
        RoWGCFtoRoWCFC += reindex(
            data.xs("infRegFromRoW", level="LY name")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None
    RoWGCFtoRoWCFC = to_abs(RoWGCFtoRoWCFC)

    ###
    try:
        NegCFtoCFC1 = reindex(
            data.xs("LY NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        NegCFtoCFC1 = to_abs(NegCFtoCFC1)
    except KeyError:
        None
    try:
        NegCFtoCFC2 = reindex(
            data.xs("(Lk-L)Y NCF inf", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        NegCFtoCFC2 = to_abs(NegCFtoCFC2)
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
        RoWNegCFtoRoWCFC1 = to_abs(RoWNegCFtoRoWCFC1)
    except KeyError:
        try:
            cols = (
                data.xs("LY NCF inf", level="LY name")
                .stack()
                .unstack(level="region cons")
                .columns
            )
            if region not in cols:
                try:
                    RoWNegCFtoRoWCFC1 = reindex(
                        data.xs("LY NCF inf", level="LY name")
                        .groupby(level="sector prod")
                        .sum()["value"]
                    )
                    RoWNegCFtoRoWCFC1 = to_abs(RoWNegCFtoRoWCFC1)
                except KeyError:
                    None
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
        RoWNegCFtoRoWCFC2 = to_abs(RoWNegCFtoRoWCFC2)
    except KeyError:
        try:
            cols = (
                data.xs("(Lk-L)Y NCF inf", level="LY name")
                .stack()
                .unstack(level="region cons")
                .columns
            )
            if region not in cols:
                try:
                    RoWNegCFtoRoWCFC2 = reindex(
                        data.xs("(Lk-L)Y NCF inf", level="LY name")
                        .groupby(level="sector prod")
                        .sum()["value"]
                    )
                    RoWNegCFtoRoWCFC2 = to_abs(RoWNegCFtoRoWCFC2)
                except KeyError:
                    None
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
        GCFtoNCFsup = to_abs(GCFtoNCFsup)
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
        RoWGCFtoExports = to_abs(RoWGCFtoExports)
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
        RoWCFCtoCFCk += reindex(
            data.xs("infRegFromRoW", level="LY name")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None
    RoWCFCtoCFCk = to_abs(RoWCFCtoCFCk)

    # CFC to CFCk = CFCk - RoW CFC to CFCk

    CFCtoCFCk = reindex(
        data["value"]
        .unstack(level="LY name")[
            [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF sup",
                "(Lk-L)Y NPISHS",
            ]
        ]
        .sum(axis=1)
        .xs(region, level="region cons")
        .groupby(level="sector prod")
        .sum()
    ) - reindex(RoWCFCtoCFCk)
    if abs(CFCtoCFCk).sum() > CFCtoCFCk.sum():
        CFCtoCFCk = abs(CFCtoCFCk) * CFCtoCFCk.sum() / abs(CFCtoCFCk).sum()
    CFCtoCFCk = to_abs(CFCtoCFCk)

    ###

    # CFC to RoW - CFCk = CFC - (CFC to CFCk)

    CFCtoRoWCFCk = reindex(GCFtoCFC) - reindex(CFCtoCFCk)
    if len(NegCFtoCFC1) > 0:
        CFCtoRoWCFCk += reindex(NegCFtoCFC1)
    if len(NegCFtoCFC2) > 0:
        CFCtoRoWCFCk += reindex(NegCFtoCFC2)
    CFCtoRoWCFCk = to_abs(CFCtoRoWCFCk)

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
    if len(RoWNegCFtoRoWCFC1) > 0:
        RoWCFCtoRoWCFCk += reindex(RoWNegCFtoRoWCFC1)
    if len(RoWNegCFtoRoWCFC2) > 0:
        RoWCFCtoRoWCFCk += reindex(RoWNegCFtoRoWCFC2)
    try:
        RoWCFCtoRoWCFCk += reindex(
            data.xs("infRegFromRoW", level="LY name")
            .groupby(level="sector prod")
            .sum()["value"]
        )
    except KeyError:
        None
    RoWCFCtoRoWCFCk = to_abs(RoWCFCtoRoWCFCk)

    #### adjust RoW CFC

    test = RoWGCFtoRoWCFC - RoWCFCtoCFCk - RoWCFCtoRoWCFCk
    if len(RoWNegCFtoRoWCFC1) > 0:
        test += RoWNegCFtoRoWCFC1
    if len(RoWNegCFtoRoWCFC2):
        test += RoWNegCFtoRoWCFC2

    if test.sum() < 0:
        CFCtoCFCk -= test
        RoWCFCtoCFCk += test
        CFCtoCFCk = to_abs(CFCtoCFCk)
        RoWCFCtoCFCk = to_abs(RoWCFCtoCFCk)

    #### adjust CFC

    test = GCFtoCFC - CFCtoCFCk - CFCtoRoWCFCk
    if len(NegCFtoCFC1) > 0:
        test += NegCFtoCFC1
    if len(NegCFtoCFC2):
        test += NegCFtoCFC2

    if test.sum() < 0:
        CFCtoRoWCFCk += test
        RoWCFCtoRoWCFCk -= test
        CFCtoRoWCFCk = to_abs(CFCtoRoWCFCk)
        RoWCFCtoRoWCFCk = to_abs(RoWCFCtoRoWCFCk)

    #### adjust RoW CFC again

    test = RoWGCFtoRoWCFC - RoWCFCtoCFCk - RoWCFCtoRoWCFCk
    if len(RoWNegCFtoRoWCFC1) > 0:
        test += RoWNegCFtoRoWCFC1
    if len(RoWNegCFtoRoWCFC2):
        test += RoWNegCFtoRoWCFC2

    if test.sum() < 0:
        RoWCFCtoRoWCFCk += test
        RoWCFCtoRoWCFCk = to_abs(RoWCFCtoRoWCFCk)

    ### if negative values
    if to_abs(CFCtoCFCk).sum() < 0:
        RoWCFCtoCFCk = to_abs(RoWCFCtoCFCk + to_abs(CFCtoCFCk))
        RoWCFCtoRoWCFCk = to_abs(RoWCFCtoRoWCFCk - to_abs(CFCtoCFCk))
        CFCtoCFCk = CFCtoCFCk - CFCtoCFCk

    if to_abs(CFCtoRoWCFCk).sum() < 0:
        CFCtoCFCk = to_abs(CFCtoCFCk + to_abs(CFCtoRoWCFCk))
        RoWCFCtoCFCk = to_abs(RoWCFCtoCFCk - to_abs(CFCtoRoWCFCk))
        RoWCFCtoRoWCFCk = to_abs(
            RoWCFCtoRoWCFCk + to_abs(CFCtoRoWCFCk)
        )  # different from above because adjustment made by CFC imports re-exported
        CFCtoRoWCFCk = CFCtoRoWCFCk - CFCtoRoWCFCk

    if to_abs(RoWCFCtoCFCk).sum() < 0:
        CFCtoCFCk = to_abs(CFCtoCFCk + to_abs(RoWCFCtoCFCk))
        RoWCFCtoRoWCFCk = to_abs(RoWCFCtoRoWCFCk + to_abs(RoWCFCtoCFCk))
        CFCtoRoWCFCk = to_abs(CFCtoRoWCFCk - to_abs(RoWCFCtoCFCk))

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
            importsreexp = to_abs(importsreexp)
            data_sankey2 = concat(
                data_sankey2, importsreexp, "RoW - CFCk", "CFC imports re-exported"
            )
    except KeyError:
        None

    ####

    data_sankey2 = concat(data_sankey2, GCFtoCFC, "GCF", "CFC")
    data_sankey2 = concat(data_sankey2, RoWGCFtoRoWCFC, "RoW - GCF", "RoW - CFC")
    if len(NegCFtoCFC1) > 0 and len(NegCFtoCFC2):
        df = to_abs(NegCFtoCFC1 + NegCFtoCFC2)
        if df.sum() > 0:
            data_sankey2 = concat(data_sankey2, df, "Negative capital formation", "CFC")
    elif len(NegCFtoCFC1) > 0:
        df = to_abs(NegCFtoCFC1)
        if df.sum() > 0:
            data_sankey2 = concat(data_sankey2, df, "Negative capital formation", "CFC")
    elif len(NegCFtoCFC2) > 0:
        df = to_abs(NegCFtoCFC2)
        if df.sum() > 0:
            data_sankey2 = concat(data_sankey2, df, "Negative capital formation", "CFC")
    if len(RoWNegCFtoRoWCFC1) > 0 and len(RoWNegCFtoRoWCFC2) > 0:
        df = to_abs(RoWNegCFtoRoWCFC1 + RoWNegCFtoRoWCFC2)
        if df.sum() > 0:
            data_sankey2 = concat(
                data_sankey2, df, "RoW - Negative capital formation", "RoW - CFC"
            )
    elif len(RoWNegCFtoRoWCFC1) > 0:
        df = to_abs(RoWNegCFtoRoWCFC1)
        if df.sum() > 0:
            data_sankey2 = concat(
                data_sankey2, df, "RoW - Negative capital formation", "RoW - CFC"
            )
    elif len(RoWNegCFtoRoWCFC2) > 0:
        df = to_abs(RoWNegCFtoRoWCFC2)
        if df.sum() > 0:
            data_sankey2 = concat(
                data_sankey2, df, "RoW - Negative capital formation", "RoW - CFC"
            )
    if len(GCFtoNCFsup) > 0:
        data_sankey2 = concat(
            data_sankey2, GCFtoNCFsup, "GCF", "Positive capital formation "
        )
    if len(RoWGCFtoExports) > 0:
        data_sankey2 = concat(data_sankey2, RoWGCFtoExports, "RoW - GCF", "Exports")
    data_sankey2 = concat(data_sankey2, RoWCFCtoCFCk, "RoW - CFC", "CFCk")
    data_sankey2 = concat(data_sankey2, CFCtoCFCk, "CFC", "CFCk")
    data_sankey2 = concat(data_sankey2, CFCtoRoWCFCk, "CFC", "RoW - CFCk")

    data_sankey2 = concat(data_sankey2, RoWCFCtoRoWCFCk, "RoW - CFC", "RoW - CFCk")

    return data_sankey2


def data_from_SLY(SLY, region):
    """Extracts necessary information from SLY.

    Parameters
    ----------
    None
    SLY : pd.DataFrame
        calculated from function SLY of exiobase_functions
    region : string
        region studied

    Returns
    -------
    data : pd.DataFrame
        dataframe that will in the end contain all the information necessary to build sankey

    """
    SLY = SLY.rename(
        columns={
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)": "GHG",
            "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CO2",
            "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CH4",
            "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "N2O",
        }
    )
    SLY["F-gases"] = SLY["GHG"] / 1000000 - SLY[["CO2", "CH4", "N2O"]].sum(
        axis=1
    )  # used to be SF6

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
            SLY.loc[[region]][["LY NCF", "LkY NCF"]]  # we select region of consumption
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
                        "Direct emissions": "other",  # "Households direct   "
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
            )
            .groupby(level=SLY.index.names)
            .sum()
        )
        .append(
            SLY.drop(region)[["LY NCF", "LkY NCF"]]
            .rename(
                index=dict(
                    {
                        "150100:MACHINERY AND EQUIPMENT": "othercap",
                        "150200:CONSTRUCTION": "othercap",
                        "150300:OTHER PRODUCTS": "othercap",
                        "Direct emissions": "other",  # "Households direct   "
                        "CH4": "othergas",
                        "CO2": "othergas",
                        "N2O": "othergas",
                        "F-gases": "othergas",  # used to be
                    }
                )
            )
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
    data_reg_exp = pd.DataFrame(
        data.drop([region], level="region cons")
        .stack()
        .unstack(level="region prod")[region]
    )
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
        columns=pd.MultiIndex.from_tuples(
            [("CFC>(Lk-L)Y", "None")], names=["LY name", "sector cons"]
        ),
    )
    # exports of CFC
    inf = pd.DataFrame(
        -df[df < 0],
        index=df.index,
        columns=pd.MultiIndex.from_tuples(
            [("CFC<(Lk-L)Y", "None")], names=["LY name", "sector cons"]
        ),
    )
    # imports of CFC
    # sup + inf = abs(df)
    df = pd.concat([data.unstack(level="sector cons"), sup, inf], axis=1).stack()
    df = df.reorder_levels(data.index.names)

    data = df
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
        df2 = pd.DataFrame(
            data.unstack(level="LY name")
            .swaplevel(axis=1)["LY CFC"]
            .stack()
            .unstack(level="sector cons")
            .sum(axis=1)
            .unstack()
            - (
                data.unstack(level="LY name")
                .swaplevel(axis=1)[
                    [
                        "(Lk-L)Y Government",
                        "(Lk-L)Y Households",
                        "(Lk-L)Y NCF save",
                        "(Lk-L)Y NPISHS",
                    ]
                ]
                .stack()
                .unstack(level="sector cons")
                .sum(axis=1)
                .unstack()
            )
        )
        df2["LY name"] = "infRegFromRoW"
        df2["sector cons"] = "NA"
        df2 = df2.reset_index()
        df2["region cons"] = region
        df2 = df2.set_index(data.index.names)
        df2.columns = ["value"]
        df2 = df2.groupby(level=df2.index.names).sum()
        if df2.sum().value < 0:
            try:
                todrop = df2.xs(region, level="region prod").sum().value
                if todrop < 0:
                    df2 = (
                        df2.drop(region, level="region prod")
                        * df2.sum()
                        / df2.drop(region, level="region prod").sum()
                    )
                else:
                    df2 = (
                        df2.drop(region, level="region prod")
                        * df2.sum()
                        / (df2.sum() - df2.xs(region, level="region prod").sum())
                    )
            except KeyError:
                None

            data = pd.concat(
                [
                    -df2[df2 < 0] * df2.sum() / df2[df2 < 0].sum(),
                    data,
                ]
            )
    except KeyError:
        None

    return data


def data_Sankey(year, region):
    """Transforms SLY into three files used to build sankey.

    Parameters
    ----------
    year : string
    region : string

    Returns
    -------
    node_dict : dictionnary
        dictionnary between nodes names and numbers
    node_list : list
        list of the names of all the nodes
    data_sankey : pd.DataFrame
        all the data needed to build sankey

    """

    SLY = (
        feather.read_feather("Results/SLY/" + region + "/" + str(year) + ".feather")
        / 1000
    )

    DictRoW, left_index, right_index, position_all, node_list, color_dict = variables(
        region
    )

    data = pd.DataFrame()
    data = data_from_SLY(SLY, region).rename(dictreg, level="region prod")
    data = level_0(data, left_index)
    data = level_1(data, left_index)
    data = level_2(region, data, left_index)
    data = level_3(data, DictRoW, left_index)
    data = level_4(data, DictRoW, left_index)
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
    data_sankey = junction_5_to_6(data_sankey, region, data, node_dict, color_dict)

    return node_dict, node_list, data_sankey


####


def nodes_data():
    """For every year and region, saves the files nodes.feather, nodelist.feather and data.feather.

    These three files will be read by the function fig_sankey to build the figures.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    population = feather.read_feather("Data/pop.feather")
    for region in (
        pd.read_excel("Data/regions.xlsx", index_col=0)
        .sort_values(by="full name")
        .index
    ):
        for year in range(1995, 2020, 1):
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
                        nodes.loc[node, "value Mt"] = source_data["value"].loc[
                            node_dict[node]
                        ]

                        a = (
                            data_sankey.reset_index()
                            .set_index("source")["position"]
                            .loc[node_dict[node]]
                        )
                        if node in [
                            "Negative capital formation",
                            "RoW - Negative capital formation",
                        ]:
                            nodes.loc[node, "position"] = "4. cba"
                        elif type(a) == str:
                            nodes["position"].loc[node] = a
                        elif node in ["GCF", "RoW - GCF"]:
                            nodes.loc[node, "position"] = "4. cba"
                        else:
                            nodes.loc[node, "position"] = a.values[0]

                    else:
                        nodes["value Mt"].loc[node] = target_data["value"].loc[
                            node_dict[node]
                        ]
                        if node in [
                            "Africa",
                            "Asia",
                            "Europe",
                            "Middle East",
                            "North America",
                            "Oceania",
                            "South America",
                            "Footprint",
                        ]:
                            nodes.loc[node, "position"] = "9. exp"

                        elif node in ["CFC", "RoW - CFC"]:
                            nodes.loc[node, "position"] = "5. ncf"
                        elif node in ["CFCk", "RoW - CFCk"]:
                            nodes.loc[node, "position"] = "6. endo"
                        else:
                            nodes.loc[node, "position"] = "8. cons"
                except KeyError:
                    nodes = nodes.drop(node)
            nodes.loc["Positive capital formation ", "position"] = "7. cbaK"

            nodes = nodes.drop(
                [i for i in nodes.index if nodes["value Mt"].isnull().loc[i]]
            )
            nodes = nodes.drop(
                [i for i in nodes["value Mt"].index if nodes["value Mt"].loc[i] == 0]
            )

            nodes["label Mt"] = (
                nodes.rename(
                    index=dict(
                        {
                            "RoW - Other goods and services": "RoW - Other",
                            "Other goods and services": "Other",
                            "RoW - Positive capital formation ": "RoW - Pos. CF",
                            "Territorial": dictreg[region],
                        }
                    )
                ).index
                + " ("
                + [str(round(i)) for i in nodes["value Mt"]]
                + ")"
            )
            nodes["value t/cap"] = nodes["value Mt"] / pop
            nodes["label t/cap"] = (
                nodes.rename(
                    index=dict(
                        {
                            "RoW - Other goods and services": "RoW - Other",
                            "Other goods and services": "Other",
                            "RoW - Positive capital formation ": "RoW - Pos. CF",
                            "Territorial": dictreg[region],
                        }
                    )
                ).index
                + " ("
                + [str(round(i, 2)) for i in nodes["value t/cap"]]
                + ")"
            )
            if not os.path.exists("Results/Sankey_data"):
                os.mkdir("Results/Sankey_data")
            if not os.path.exists("Results/Sankey_data/" + region):
                os.mkdir("Results/Sankey_data/" + region)
            feather.write_feather(
                nodes,
                "Results/Sankey_data/"
                + region
                + "/nodes"
                + region
                + str(year)
                + ".feather",
            )
            feather.write_feather(
                data_sankey,
                "Results/Sankey_data/"
                + region
                + "/data"
                + region
                + str(year)
                + ".feather",
            )
            feather.write_feather(
                pd.DataFrame(node_list),
                "Results/Sankey_data/"
                + region
                + "/nodelist"
                + region
                + str(year)
                + ".feather",
            )


def norm():
    """Creates coefficients to normalize sankey diagrams in Mt for every region so that flow sizes vary with time.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    regions = pd.read_excel("regions.xlsx")["region"].values
    df = pd.DataFrame([], columns=[i for i in range(1995, 2020, 1)], index=regions)
    for year in range(1995, 2020, 1):
        for region in regions:
            data_sankey = feather.read_feather(
                "Sankeys/" + region + "/data" + region + str(year) + ".feather"
            )
            df.loc[region].loc[year] = (
                data_sankey.set_index("position").loc["0. ges"].sum().loc["value"]
            )
    feather.write_feather(
        df.div(pd.DataFrame(df.T.max())[0], axis=0), "Results/norm.feather"
    )


def norm_cap():
    """Creates coefficients to normalize sankey diagrams in t/cap for every region so that flow sizes vary with time.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    population = feather.read_feather("pop.feather")
    regions = pd.read_excel("regions.xlsx")["region"].values
    df = pd.DataFrame([], columns=[i for i in range(1995, 2020, 1)], index=regions)
    for year in range(1995, 2020, 1):
        for region in regions:
            pop = population[year].loc[region] / 1000
            data_sankey = feather.read_feather(
                "Sankeys/" + region + "/data" + region + str(year) + ".feather"
            )
            df.loc[region].loc[year] = (
                data_sankey.set_index("position").loc["0. ges"].sum().loc["value"] / pop
            )
    feather.write_feather(
        df.div(pd.DataFrame(df.T.max())[0], axis=0), "Results/norm_cap.feather"
    )


def totals():
    pba = pd.DataFrame()
    cba = pd.DataFrame()
    cbak = pd.DataFrame()
    for i in range(1995, 2020, 1):
        pathIOT = "Data/EXIO3/IOT_" + str(i) + "_pxp/"

        Yk = feather.read_feather(pathIOT + "Yk.feather")
        L = feather.read_feather(pathIOT + "L.feather")
        L.columns.names = ["region cons", "sector cons"]
        L.index.names = ["region prod", "sector prod"]
        Lk = feather.read_feather(pathIOT + "Lk.feather")
        Lk.columns.names = ["region cons", "sector cons"]
        Lk.index.names = ["region prod", "sector prod"]

        S_imp = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc[
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
        ]
        S_imp.index.names = ["region prod", "sector prod"]

        D_cba = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/impacts/D_cba.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc[
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
        ]
        D_pba = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/impacts/D_pba.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc[
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
        ]
        F_Y = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/impacts/F_Y.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc[
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
        ]

        SLkY = pd.DataFrame()
        Y_k = Yk.drop(["NCF", "CFC"], axis=1).sum(axis=1).unstack()
        Y_k.index.names = ["region cons", "sector cons"]
        for reg in Y_k.columns:
            SLkY[reg] = Lk.mul(Y_k[reg], axis=1).mul(S_imp, axis=0).sum()

        cba[i] = D_cba.groupby(level=0).sum() + F_Y.groupby(level=0).sum()
        pba[i] = D_cba.groupby(level=0).sum() + F_Y.groupby(level=0).sum()
        cbak[i] = SLkY.sum() + F_Y.groupby(level=0).sum()
    totals = pd.DataFrame()
    totals["pba"] = pba.stack()
    totals["cba"] = cba.stack()
    totals["cbak"] = cbak.stack()
    feather.write_feather(totals, "Results/totals.feather")
    pd.write_excel(totals, "Results/totals.xlsx")
    totals.to_excel("Results/totals.xlsx")


##
