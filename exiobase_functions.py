import pandas as pd
import os
import pandas as pd
import os
import pyarrow.feather as feather


# function to diaggregate GDP into all the formats needed
def Y_all():

    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"
        Kbar = feather.read_feather(pathexio + "Kbar/Kbar" + str(i) + ".feather").fillna(0)
        Y = feather.read_feather(pathIOT + "Y.feather")

        df = pd.DataFrame([], index=Y.stack(level=0).index)
        df["Households"] = Y.stack(level=0)["Final consumption expenditure by households"]
        df["Government"] = Y.stack(level=0)["Final consumption expenditure by government"]
        df["NPISHS"] = Y.stack(level=0)[
            "Final consumption expenditure by non-profit organisations serving households (NPISH)"
        ]
        df["CFC"] = Kbar.groupby(level="region", axis=1).sum().stack()
        df["NCF"] = (
            Y.stack(level=0)[
                [
                    "Changes in inventories",
                    "Changes in valuables",
                    "Exports: Total (fob)",
                    "Gross fixed capital formation",
                ]
            ].sum(axis=1)
            - Kbar.groupby(level="region", axis=1).sum().stack()
        )
        df.index.names = ["region prod", "sector prod", "region cons"]
        # en fait devrait etre ["region cons", "sector cons", "region"]

        feather.write_feather(df, pathIOT + "Yk.feather")

    return None


# function to calculate Lk from Z and Kbar
def L_and_Lk():
    """Calculates Lk from Kbar and saves it to the Exiobase data files.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"
        Y = feather.read_feather(pathIOT + "Y.feather").groupby(level="region", axis=1).sum()
        Z = feather.read_feather(pathIOT + "Z.feather").fillna(0)
        Kbar = feather.read_feather(pathexio + "Kbar/Kbar" + str(i) + ".feather").fillna(0)

        Zk = Z + Kbar
        x = Z.sum(axis=1) + Y.sum(axis=1)
        Ak = pymrio.calc_A(Zk, x)
        feather.write_feather(pymrio.calc_L(Ak), pathIOT + "Lk.feather")
        A = pymrio.calc_A(Z, x)
        feather.write_feather(pymrio.calc_L(A), pathIOT + "L.feather")

    return None


def SLY():
    """Calculates SLY with all the possible combinations of S, L and Y.
    Sectors are aggregated according to concordance.xlsx.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    impacts = [
        "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)",
        "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
        "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
        "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
    ]

    if not os.path.exists("SLY"):
        os.mkdir("SLY")

    conc_sec_cons = pd.read_excel("concordance.xlsx", sheet_name="sector cons", index_col=[0, 1])
    conc_sec_prod = pd.read_excel("concordance.xlsx", sheet_name="sector prod", index_col=[0, 1])
    conc_reg_prod = pd.read_excel(
        "concordance.xlsx",
        sheet_name="region prod",
        index_col=[0, 1],
    )
    conc_reg_cons = pd.read_excel(
        "concordance.xlsx",
        sheet_name="region cons",
        index_col=[0, 1],
    )
    conc_cap = pd.read_excel("concordance.xlsx", sheet_name="capital", index_col=[0, 1])

    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"

        Yk = feather.read_feather(pathIOT + "Yk.feather")
        L = feather.read_feather(pathIOT + "L.feather")
        L.columns.names = ["region cons", "sector cons"]
        L.index.names = ["region prod", "sector prod"]
        Lk = feather.read_feather(pathIOT + "Lk.feather")
        Lk.columns.names = ["region cons", "sector cons"]
        Lk.index.names = ["region prod", "sector prod"]

        LY_all = pd.DataFrame()
        for col in Yk.columns:
            Y = Yk[col].unstack()
            Y.index.names = ["region cons", "sector cons"]
            LY = pd.DataFrame()
            LkY = pd.DataFrame()
            for j in Y.columns:
                if col in ["CFC", "NCF"]:
                    conc = conc_cap
                else:
                    conc = conc_sec_cons

                LY_intermediate = agg(
                    L.mul(Y[j], axis=1).groupby(level="sector cons", axis=1).sum(),
                    conc,
                    axis=1,
                )
                LY[j] = LY_intermediate.stack()

                LkY_intermediate = agg(
                    Lk.mul(Y[j], axis=1).groupby(level="sector cons", axis=1).sum(),
                    conc,
                    axis=1,
                )
                LkY[j] = LkY_intermediate.stack()

            LY_all = pd.concat(
                [
                    LY_all,
                    pd.concat([LY, LkY], axis=1, keys=["LY " + col, "LkY " + col]).unstack(),
                ],
                axis=1,
            )

        LY_all = LY_all.drop("LkY CFC", axis=1)
        LY_all.columns.names = ["LY name", "region cons", "sector cons"]
        LY_all.index.names = ["region prod", "sector prod"]

        SLY = pd.DataFrame()

        S_imp = pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        )
        S_imp.columns.names = ["region prod", "sector prod"]

        for j in impacts:
            SLY[j] = agg(LY_all.mul(S_imp.loc[j], axis=0), conc_sec_prod).unstack().unstack()

        SLY.columns.names = ["Extensions"]
        SLY = SLY.stack().unstack(level="sector cons")
        SLY["Food"] = SLY["Food"] + 0.5 * SLY["Food and shelter"]
        SLY["Shelter"] = SLY["Shelter"] + 0.5 * SLY["Food and shelter"]
        SLY = SLY.drop("Food and shelter", axis=1)
        SLY = (
            SLY.stack()
            .unstack(level="Extensions")
            .reorder_levels(["LY name", "region cons", "sector cons", "sector prod", "region prod"])
        )

        for region in Yk.unstack().stack(level=0).columns:
            if not os.path.exists("SLY/" + region):
                os.mkdir("SLY/" + region)
            feather.write_feather(
                agg(
                    agg(SLY, conc_reg_prod.drop([region])),
                    conc_reg_cons.drop([region]),
                ),
                "SLY/" + region + "/" + str(i) + ".feather",
            )


def F_hh():
    F_hh = pd.DataFrame()
    for year in range(1995, 2020, 1):
        F_hh_imp = (
            pd.read_csv(
                pathexio + "EXIO3/IOT_" + str(year) + "_pxp/impacts/F_hh.txt",
                delimiter="\t",
                header=[0, 1],
                index_col=[0],
            )
            .loc[
                [
                    "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)",
                    "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
                    "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
                    "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
                ]
            ]
            .rename(
                index={
                    "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)": "GHG",
                    "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CO2",
                    "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "CH4",
                    "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)": "N2O",
                }
            )
        )
        F_hh_imp.loc["SF6"] = F_hh_imp.loc["GHG"] / 1000000 - F_hh_imp.loc[["CO2", "N2O", "CH4"]].sum()
        F_hh_imp = F_hh_imp.drop("GHG")
        F_hh[year] = F_hh_imp.groupby(level="region", axis=1).sum().stack()
    feather.write_feather(F_hh, "F_hh.feather")
