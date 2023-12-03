import pandas as pd
import os
import pandas as pd
import os
import pyarrow.feather as feather
from general_functions import *
import pymrio
import numpy as np


def Kbar():
    """Calculates Kbar for years 2016-2019 by nowcasting Kbar2015.

    We use CFC data of years 2016-2019 but first rescale them using WorldBank values
    so that the ratio GFCF/CFC is the same for EXIOBASE and WorldBank data.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # read data from WorldBank
    CFC_WB = pd.read_excel(
        "Data/World Bank/CFC worldbank.xlsx", header=3, index_col=[0]
    )[
        [str(i) for i in range(2015, 2020, 1)]
    ]  # consumption of fixed capital

    GFCF_WB = pd.read_excel(
        "Data/World Bank/GFCF worldbank.xlsx", header=3, index_col=[0]
    )[
        [str(i) for i in range(2015, 2020, 1)]
    ]  # gross fixed capital formation

    # here we want to aggregate WorldBank data to Exiobase regions

    # first, set to NaN values the regions that don't have both CFC and GFCF data
    CFC_WB = (
        CFC_WB * GFCF_WB / GFCF_WB
    )  # in case some countries have data for CFC but not GFCF
    GFCF_WB = GFCF_WB * CFC_WB / CFC_WB

    # rename the regions to a common format
    CFC_WB = rename_region(CFC_WB, "Country Name").drop("Z - Aggregated categories")
    # convert the common format to EXIOBASE format
    CFC_WB["region"] = cc.convert(names=CFC_WB.index, to="EXIO3")
    # define EXIOBASE regions as index
    CFC_WB = (
        CFC_WB.reset_index()
        .set_index("region")
        .drop("Country Name", axis=1)
        .groupby(level="region")
        .sum()
    )

    # same as above for GFCF data
    GFCF_WB = rename_region(GFCF_WB, "Country Name").drop("Z - Aggregated categories")
    GFCF_WB["region"] = cc.convert(names=GFCF_WB.index, to="EXIO3")
    GFCF_WB = (
        GFCF_WB.reset_index()
        .set_index("region")
        .drop("Country Name", axis=1)
        .groupby(level="region")
        .sum()
    )

    GFCF_over_CFC_WB = GFCF_WB / CFC_WB
    GFCF_over_CFC_WB.loc["TW"] = GFCF_over_CFC_WB.loc["CN"]
    # hypothesis: ratio of GFCF/CFC is same for Taiwan than for China

    Kbar15 = feather.read_feather("Data/Kbar/Kbar_2015.feather")

    # We calculate coefficients for year 2015 that will be multiplied by CFC for other years
    Kbarcoefs = Kbar15.div(Kbar15.sum(axis=1), axis=0)  # the sum of the lines = CFC

    for i in range(2016, 2020, 1):
        pathIOT = "Data/EXIO3/IOT_" + str(i) + "_pxp/"
        Z = feather.read_feather(pathIOT + "Z.feather").fillna(
            0
        )  # if some coefs don't exist in Kbar15, we use those of Z
        Zcoefs = Z.div(Z.sum(axis=1), axis=0)

        Kbarcoefsyear = Kbarcoefs.combine_first(Zcoefs).combine_first(
            pd.DataFrame(np.identity(9800), index=Z.index, columns=Z.columns)
        )

        GFCF_exio = feather.read_feather(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/Y.feather"
        ).swaplevel(axis=1)[
            "Gross fixed capital formation"
        ]  # aggregated 49 regions, 1 product

        CFC_exio = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/satellite/F.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["Operating surplus: Consumption of fixed capital"]

        GFCF_over_CFC_exio = GFCF_exio.sum() / CFC_exio.unstack().sum(axis=1)

        CFC_exio_rescaled = (
            CFC_exio.unstack()
            .mul(GFCF_over_CFC_exio, axis=0)
            .div(GFCF_over_CFC_WB[str(i)], axis=0)
            .stack()
        )

        feather.write_feather(
            Kbarcoefsyear.mul(CFC_exio_rescaled, axis=0),
            "Data/Kbar/Kbar_" + str(i) + ".feather",
        )


def Y_all():
    """Disaggregates GDP into all the formats needed, saves it to Yk.feather.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    for i in range(1995, 2020, 1):
        pathIOT = "Data/EXIO3/IOT_" + str(i) + "_pxp/"
        Kbar = feather.read_feather("Data/Kbar/Kbar_" + str(i) + ".feather").fillna(0)
        Y = feather.read_feather(pathIOT + "Y.feather")

        df = pd.DataFrame([], index=Y.stack(level=0).index)
        df["Households"] = Y.stack(level=0)[
            "Final consumption expenditure by households"
        ]
        df["Government"] = Y.stack(level=0)[
            "Final consumption expenditure by government"
        ]
        df["NPISHS"] = Y.stack(level=0)[
            "Final consumption expenditure by non-profit organisations serving households (NPISH)"
        ]

        NET = pd.DataFrame(index=df.unstack().index)
        CFC = pd.DataFrame(index=df.unstack().index)
        for region in Y.stack().columns:
            cfc = Kbar.loc[region].sum(
                axis=1
            )  # CFC of region for each one of the 200 sectors

            # where does the CFC come from? We use the same shares as GCF data

            # à comparer avec GCF du pays
            gcf_all = (
                Y.stack(level=0)[
                    [
                        "Changes in inventories",
                        "Changes in valuables",
                        "Exports: Total (fob)",
                        "Gross fixed capital formation",
                    ]
                ]
                .sum(axis=1)
                .unstack()[region]
                .unstack()
            )  # lines=regions, columns=sectors of GCF

            gcf_shares = gcf_all.div(
                gcf_all.sum(), axis=1
            )  # share of origin region for each sector
            gcf_shares.loc[region, gcf_shares.isnull().all()] = 1
            gcf = gcf_all.sum()
            diff = gcf - cfc
            NET[region] = gcf_shares.mul(diff, axis=1).stack()
            CFC[region] = gcf_shares.mul(cfc, axis=1).stack()

        df["CFC"] = CFC.stack()
        df["NCF"] = NET.stack()

        df.index.names = ["region prod", "sector prod", "region cons"]
        # names will be changed again in SLY()

        feather.write_feather(df, pathIOT + "Yk.feather")

    return None


def L_and_Lk():
    """Calculates Lk and L and saves it to the Exiobase data files.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    for i in range(1995, 2020, 1):
        pathIOT = "Data/EXIO3/IOT_" + str(i) + "_pxp/"
        Y = (
            feather.read_feather(pathIOT + "Y.feather")
            .groupby(level="region", axis=1)
            .sum()
        )
        Z = feather.read_feather(pathIOT + "Z.feather").fillna(0)
        Kbar = feather.read_feather("Data/Kbar/Kbar_" + str(i) + ".feather").fillna(0)

        Zk = pd.DataFrame(
            Z + Kbar, index=Z.index, columns=Z.columns
        )  # EXTREMELY important to reindex, otherwise pymrio.calc_L doesn't work properly
        x = Z.sum(axis=1) + Y.sum(axis=1)
        Ak = pymrio.calc_A(Zk, x)
        feather.write_feather(pymrio.calc_L(Ak), pathIOT + "Lk.feather")
        A = pymrio.calc_A(Z, x)
        feather.write_feather(pymrio.calc_L(A), pathIOT + "L.feather")

    return None


def SLY():
    """Calculates SLY with all the possible combinations of S, L and Y.
    Sectors are aggregated according to concordance.xlsx
    Results are saved in folder SLY/region/year.feather

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

    conc_sec_cons = pd.read_excel(
        "Data/concordance.xlsx", sheet_name="sector cons", index_col=[0, 1]
    )
    conc_sec_prod = pd.read_excel(
        "Data/concordance.xlsx", sheet_name="sector prod", index_col=[0, 1]
    )
    conc_reg_prod = pd.read_excel(
        "Data/concordance.xlsx",
        sheet_name="region prod",
        index_col=[0, 1],
    )
    conc_reg_cons = pd.read_excel(
        "Data/concordance.xlsx",
        sheet_name="region cons",
        index_col=[0, 1],
    )
    conc_cap = pd.read_excel(
        "Data/concordance.xlsx", sheet_name="capital", index_col=[0, 1]
    )

    for i in range(1995, 2020, 1):
        pathIOT = "Data/EXIO3/IOT_" + str(i) + "_pxp/"

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
                    pd.concat(
                        [LY, LkY], axis=1, keys=["LY " + col, "LkY " + col]
                    ).unstack(),
                ],
                axis=1,
            )

        LY_all = LY_all.drop("LkY CFC", axis=1)
        LY_all.columns.names = ["LY name", "region cons", "sector cons"]
        LY_all.index.names = ["region prod", "sector prod"]

        SLY = pd.DataFrame()

        S_imp = pd.read_csv(
            "Data/EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        )
        S_imp.columns.names = ["region prod", "sector prod"]

        for j in impacts:
            SLY[j] = (
                agg(LY_all.mul(S_imp.loc[j], axis=0), conc_sec_prod).unstack().unstack()
            )

        SLY.columns.names = ["Extensions"]
        SLY = SLY.stack().unstack(level="sector cons")
        SLY["Food"] = SLY["Food"] + 0.5 * SLY["Food and shelter"]
        SLY["Shelter"] = SLY["Shelter"] + 0.5 * SLY["Food and shelter"]
        SLY = SLY.drop("Food and shelter", axis=1)
        SLY = (
            SLY.stack()
            .unstack(level="Extensions")
            .reorder_levels(
                ["LY name", "region cons", "sector cons", "sector prod", "region prod"]
            )
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
    """Aggregates direct emissions by households into a single file F_hh.feather.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    F_hh = pd.DataFrame()
    for year in range(1995, 2020, 1):
        F_hh_imp = (
            pd.read_csv(
                "Data/EXIO3/IOT_" + str(year) + "_pxp/impacts/F_Y.txt",
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
        F_hh_imp.loc["F-gases"] = (
            F_hh_imp.loc["GHG"] / 1000000 - F_hh_imp.loc[["CO2", "N2O", "CH4"]].sum()
        )  # SF6
        F_hh_imp = F_hh_imp.drop("GHG")
        # F_hh[year] = F_hh_imp.groupby(level="region", axis=1).sum().stack()
        F_hh[year] = F_hh_imp.stack().stack()
    feather.write_feather(F_hh, "Data/F_hh.feather")


def share_houheholds_old():
    """Disaggregates direct emissions by households into residental and non residential.

    Based on UNFCCC data. Results saved to "share households residential.feather"

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    df = (
        pd.read_excel("Data/UNFCCC hh data.xlsx", index_col=0)
        / feather.read_feather("Data/F_hh.feather").groupby(level="region").sum()
    )
    # df.count().sum(), 900 values
    # df[df>0.9].count().sum(), 14 values out of 900 are above 90%, too much for residential
    # we make the hypothesis of a saturation at 90%
    df2 = df.fillna(0.5)  # when no data, 50%
    df2[df2 > 0.9] = 0.9
    feather.write_feather(df2, "Results/share households residential.feather")

    # share_direct=pd.DataFrame()
    # share_direct_0 = pd.DataFrame()
    # share_direct_0["Shelter"] = feather.read_feather("Results/share households residential.feather").stack()
    # share_direct_0["Mobility"] = 1 - share_res.stack()
    # for i in ["Food", "Other goods and services", "Education", "Health", "Clothing"]:
    #     share_direct_0[i] = 0
    # for i in ["Households", "NPISHS", "Government"]:
    #     share_direct[i] =share_direct_0.stack()

    # feather.write_feather(share_direct,"Results/share_direct.feather")


def share_houheholds():
    """preprocesses direct emissions by households into the best format"

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    df = pd.read_parquet("hhld_emissions.parquet")
    df = df.drop("unit", axis=1)
    df = df.reset_index().set_index(
        ["year", "stressor", "category", "region", "sector"]
    )
    conc_sec_cons = pd.read_excel(
        "Data/concordance.xlsx", sheet_name="sector cons", index_col=[0, 1]
    )
    df = agg(df, conc_sec_cons, axis=0)
    df = (
        df["value"]
        .unstack(level=0)
        .loc[
            [
                "CH4 - combustion - air",
                "CO2 - combustion - air",
                "N2O - combustion - air",
            ]
        ]
    )
    df.columns = [int(i) for i in df.columns]
    short = dict(
        {
            "CH4 - combustion - air": "CH4",
            "CO2 - combustion - air": "CO2",
            "N2O - combustion - air": "N2O",
            "Final consumption expenditure by government": "Government",
            "Final consumption expenditure by households": "Households",
            "Final consumption expenditure by non-profit organisations serving households (NPISH)": "NPISHS",
        }
    )
    df = df.rename(index=short)
    df = df.stack().unstack(level="sector")
    df_share = df.div(df.sum(axis=1), axis=0)
    df_share = df_share.unstack(level=[2, 3]).stack(dropna=False).stack(dropna=False)
    feather.write_feather(df_share, "Results/share_direct_final.feather")


def pop():
    """Converts population data form WorldBank format to EXIOBASE format, save it in pop.feather.


    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    pop = (
        rename_region(
            pd.read_csv("Data/World Bank/pop.csv", header=[2], index_col=[0])[
                [str(i) for i in range(1995, 2020, 1)]
            ],
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

    pop.loc["TW"] = pd.read_excel("Data/pop Taiwan.xls", header=0, index_col=0)["TW"]

    feather.write_feather(pop, "Data/pop.feather")
