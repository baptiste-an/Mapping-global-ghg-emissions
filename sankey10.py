import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.core.reshape.merge import merge
from pandas.io.pytables import Fixed
import pymrio
import scipy.io
from matplotlib import colors as mcolors, rc_params
import seaborn as sns
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.io as pio
import os
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.patches as mpatches
import matplotlib.markers as mmark
import matplotlib.lines as mlines
from scipy import stats
import country_converter as coco
import pyarrow.feather as feather

df = pd.read_excel("regions.xlsx")
dictreg = dict(zip(df["region"], df["full name"]))

if not os.path.exists("Sankeys"):
    os.mkdir("Sankeys")
pio.orca.config.executable = (
    "C:/Users/andrieba/anaconda3/pkgs/plotly-orca-1.2.1-1/orca_app/orca.exe"
)
pio.orca.config.save()
pio.kaleido.scope.mathjax = None  # ne sert à rien car mathjax ne fonctionne pas
pyo.init_notebook_mode()

pathexio = "C:/Users/andrieba/Documents/Data/"
impacts = [
    "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)",
    "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
    "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
    "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)",
]


def plt_rcParams():
    fsize = 10
    tsize = 4
    tdir = "out"
    major = 5.0
    minor = 3.0
    lwidth = 0.8
    lhandle = 2.0
    plt.style.use("default")
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.size"] = fsize
    plt.rcParams["legend.fontsize"] = tsize
    plt.rcParams["xtick.direction"] = tdir
    plt.rcParams["ytick.direction"] = tdir
    plt.rcParams["xtick.major.size"] = major
    plt.rcParams["xtick.minor.size"] = minor
    plt.rcParams["ytick.major.size"] = 3.0
    plt.rcParams["ytick.minor.size"] = 1.0
    plt.rcParams["axes.linewidth"] = lwidth
    plt.rcParams["legend.handlelength"] = lhandle
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.axisbelow"] = True
    return None


plt_rcParams()

# ........CREATE FUNCTION TO CONVERT ANY REGION NAME FORMAT TO A COMMON FORMAT................

dict_regions = dict()  # create a dict that will be used to rename regions
cc = coco.CountryConverter(
    include_obsolete=True
)  # documentation for coco here: https://github.com/konstantinstadler/country_converter
for i in [
    n for n in cc.valid_class if n != "name_short"
]:  # we convert all the regions in cc to name short and add it to the dict
    dict_regions.update(cc.get_correspondence_dict(i, "name_short"))
name_short = cc.ISO3as("name_short")[
    "name_short"
].values  # array containing all region names in short_name format


def dict_regions_update():
    """Adds to dict the encountered region names that were not in coco.

    If a region is wider than a country (for example "European Union"), it is added to "Z - Aggregated categories" in order to be deleted later.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    dict_regions["Bolivia (Plurinational State of)"] = "Bolivia"
    dict_regions["Czechia"] = "Czech Republic"
    dict_regions["Iran (Islamic Republic of)"] = "Iran"
    dict_regions["China, Taiwan Province of China"] = "Taiwan"
    dict_regions["Congo"] = "Congo Republic"
    dict_regions["Venezuela (Bolivarian Republic of)"] = "Venezuela"
    dict_regions["Dem. People's Republic of Korea"] = "North Korea"
    dict_regions["Bahamas, The"] = "Bahamas"
    dict_regions["Congo, Dem. Rep."] = "DR Congo"
    dict_regions["Congo, Rep."] = "Congo Republic"
    dict_regions["Egypt, Arab Rep."] = "Egypt"
    dict_regions["Faroe Islands"] = "Faeroe Islands"
    dict_regions["Gambia, The"] = "Gambia"
    dict_regions["Hong Kong SAR, China"] = "Hong Kong"
    dict_regions["Iran, Islamic Rep."] = "Iran"
    dict_regions["Korea, Dem. People's Rep."] = "North Korea"
    dict_regions["Korea, Rep."] = "South Korea"
    dict_regions["Lao PDR"] = "Laos"
    dict_regions["Macao SAR, China"] = "Macau"
    dict_regions["North Macedonia"] = "Macedonia"
    dict_regions["Russian Federation"] = "Russia"
    dict_regions["Sint Maarten (Dutch part)"] = "Sint Maarten"
    dict_regions["Slovak Republic"] = "Slovakia"
    dict_regions["St. Martin (French part)"] = "Saint-Martin"
    dict_regions["Syrian Arab Republic"] = "Syria"
    dict_regions["Virgin Islands (U.S.)"] = "United States Virgin Islands"
    dict_regions["West Bank and Gaza"] = "Palestine"
    dict_regions["Yemen, Rep."] = "Yemen"
    dict_regions["Venezuela, RB"] = "Venezuela"
    dict_regions["Brunei"] = "Brunei Darussalam"
    dict_regions["Cape Verde"] = "Cabo Verde"
    dict_regions["Dem. People's Rep. Korea"] = "North Korea"
    dict_regions["Swaziland"] = "Eswatini"
    dict_regions["Taiwan, China"] = "Taiwan"
    dict_regions["Virgin Islands"] = "United States Virgin Islands"
    dict_regions["Yemen, PDR"] = "Yemen"
    dict_regions["Réunion"] = "Reunion"
    dict_regions["Saint Helena"] = "St. Helena"
    dict_regions["China, Hong Kong SAR"] = "Hong Kong"
    dict_regions["China, Macao SAR"] = "Macau"
    dict_regions[
        "Bonaire, Sint Eustatius and Saba"
    ] = "Bonaire, Saint Eustatius and Saba"
    dict_regions["Curaçao"] = "Curacao"
    dict_regions["Saint Barthélemy"] = "St. Barths"
    dict_regions["Saint Martin (French part)"] = "Saint-Martin"
    dict_regions["Micronesia (Fed. States of)"] = "Micronesia, Fed. Sts."
    dict_regions["Micronesia, Federated State=s of"] = "Micronesia, Fed. Sts."
    dict_regions["Bonaire"] = "Bonaire, Saint Eustatius and Saba"
    dict_regions["São Tomé and Principe"] = "Sao Tome and Principe"
    dict_regions["Virgin Islands, British"] = "British Virgin Islands"
    dict_regions["Wallis and Futuna"] = "Wallis and Futuna Islands"
    dict_regions["Micronesia, Federated States of"] = "Micronesia, Fed. Sts."

    dict_regions["VIR"] = "United States Virgin Islands"
    dict_regions["GMB"] = "Gambia"
    dict_regions["NAM"] = "Namibia"
    dict_regions["BHS"] = "Bahamas"
    dict_regions["The Bahamas"] = "Bahamas"
    dict_regions["The Gambia"] = "Gambia"
    dict_regions["Virgin Islands, U.S."] = "United States Virgin Islands"
    dict_regions["Congo, DRC"] = "DR Congo"
    dict_regions["Marshall Is."] = "Marshall Islands"
    dict_regions["Solomon Is."] = "Solomon Islands"
    dict_regions["Timor Leste"] = "Timor-Leste"

    for j in [
        "Africa Eastern and Southern",
        "Africa Western and Central",
        "Arab World",
        "Caribbean small states",
        "Central Europe and the Baltics",
        "Early-demographic dividend",
        "East Asia & Pacific",
        "East Asia & Pacific (excluding high income)",
        "East Asia & Pacific (IDA & IBRD countries)",
        "Euro area",
        "Europe & Central Asia",
        "Europe & Central Asia (excluding high income)",
        "Europe & Central Asia (IDA & IBRD countries)",
        "European Union",
        "Fragile and conflict affected situations",
        "Heavily indebted poor countries (HIPC)",
        "High income",
        "IBRD only",
        "IDA & IBRD total",
        "IDA blend",
        "IDA only",
        "IDA total",
        "Late-demographic dividend",
        "Latin America & Caribbean",
        "Latin America & Caribbean (excluding high income)",
        "Latin America & the Caribbean (IDA & IBRD countries)",
        "Least developed countries: UN classification",
        "Low & middle income",
        "Low income",
        "Lower middle income",
        "Middle East & North Africa",
        "Middle East & North Africa (excluding high income)",
        "Middle East & North Africa (IDA & IBRD countries)",
        "Middle income",
        "North America",
        "Not classified",
        "OECD members",
        "Other small states",
        "Pacific island small states",
        "Post-demographic dividend",
        "Pre-demographic dividend",
        "Small states",
        "South Asia",
        "South Asia (IDA & IBRD)",
        "Sub-Saharan Africa",
        "Sub-Saharan Africa (excluding high income)",
        "Sub-Saharan Africa (IDA & IBRD countries)",
        "Upper middle income",
        "World",
        "Arab League states",
        "China and India",
        "Czechoslovakia",
        "East Asia & Pacific (all income levels)",
        "East Asia & Pacific (IDA & IBRD)",
        "East Asia and the Pacific (IFC classification)",
        "EASTERN EUROPE",
        "Europe & Central Asia (all income levels)",
        "Europe & Central Asia (IDA & IBRD)",
        "Europe and Central Asia (IFC classification)",
        "European Community",
        "High income: nonOECD",
        "High income: OECD",
        "Latin America & Caribbean (all income levels)",
        "Latin America & Caribbean (IDA & IBRD)",
        "Latin America and the Caribbean (IFC classification)",
        "Low income, excluding China and India",
        "Low-income Africa",
        "Middle East & North Africa (all income levels)",
        "Middle East & North Africa (IDA & IBRD)",
        "Middle East (developing only)",
        "Middle East and North Africa (IFC classification)",
        "Other low-income",
        "Serbia and Montenegro",
        "Severely Indebted",
        "South Asia (IFC classification)",
        "Sub-Saharan Africa (all income levels)",
        "SUB-SAHARAN AFRICA (excl. Nigeria)",
        "Sub-Saharan Africa (IDA & IBRD)",
        "Sub-Saharan Africa (IFC classification)",
        "WORLD",
        "UN development groups",
        "More developed regions",
        "Less developed regions",
        "Least developed countries",
        "Less developed regions, excluding least developed countries",
        "Less developed regions, excluding China",
        "Land-locked Developing Countries (LLDC)",
        "Small Island Developing States (SIDS)",
        "World Bank income groups",
        "High-income countries",
        "Middle-income countries",
        "Upper-middle-income countries",
        "Lower-middle-income countries",
        "Low-income countries",
        "No income group available",
        "Geographic regions",
        "Latin America and the Caribbean",
        "Sustainable Development Goal (SDG) regions",
        "SUB-SAHARAN AFRICA",
        "NORTHERN AFRICA AND WESTERN ASIA",
        "CENTRAL AND SOUTHERN ASIA",
        "EASTERN AND SOUTH-EASTERN ASIA",
        "LATIN AMERICA AND THE CARIBBEAN",
        "AUSTRALIA/NEW ZEALAND",
        "OCEANIA (EXCLUDING AUSTRALIA AND NEW ZEALAND)",
        "EUROPE AND NORTHERN AMERICA",
        "EUROPE",
        "Holy See",
        "NORTHERN AMERICA",
        "East Asia & Pacific (ICP)",
        "Europe & Central Asia (ICP)",
        "Latin America & Caribbean (ICP)",
        "Middle East & North Africa (ICP)",
        "North America (ICP)",
        "South Asia (ICP)",
        "Sub-Saharan Africa (ICP)",
        "Andean Latin America",
        "Australasia",
        "Central Latin America",
        "Central Sub-Saharan Africa",
        "East Asia",
        "Eastern Sub-Saharan Africa",
        "Global",
        "High-income",
        "High-income Asia Pacific",
        "High-income North America",
        "Latin America and Caribbean",
        "North Africa and Middle East",
        "Southeast Asia",
        "Southern Latin America",
        "Southern Sub-Saharan Africa",
        "Tropical Latin America",
        "Western Sub-Saharan Africa",
        "Central Europe",
        "Oceania",
        "Central Asia",
        "Western Europe",
        "Eastern Europe",
    ]:
        dict_regions[j] = "Z - Aggregated categories"
    return None


dict_regions_update()

# all the regions that do not correspond to a country are in 'Z - Aggregated categories'
# rename the appropriate level of dataframe using dict_regions
def rename_region(df, level="LOCATION"):
    """Renames the regions of a DataFrame into name_short format.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame whose regions must be renamed
    level : string
        Name of the level containing the region names

    Returns
    df : pd.DataFrame
        DataFrame with regions in name_short format
    -------
    None
    """
    if level in df.index.names:
        axis = 0
    else:
        axis = 1
        df = df.T

    index_names = df.index.names
    df = df.reset_index()
    df = df.set_index(level)
    df = df.rename(index=dict_regions)  # rename index according to dict
    ind = df.index.values
    for i in range(0, len(ind), 1):
        if type(ind[i]) == list:
            # if len(ind[i])==0:
            ind[i] = ind[i][0]
    df = df.reindex(ind)
    df = df.reset_index().set_index(index_names)
    for i in df.index.get_level_values(level).unique():
        if i not in name_short and i != "Z - Aggregated categories":
            print(
                i
                + " is not in dict_regions\nAdd it using\n  >>> dict_regions['"
                + i
                + "'] = 'region' # name_short format\n"
            )
    if axis == 1:
        df = df.T
    return df


# ........CREATE KBAR MATRIX FOR YEARS 2016-2019................


def Kbar():

    CFC_WB = pd.read_excel("World Bank/CFC worldbank.xlsx", header=3, index_col=[0])[
        [str(i) for i in range(2015, 2020, 1)]
    ]

    GFCF_WB = pd.read_excel("World Bank/GFCF worldbank.xlsx", header=3, index_col=[0])[
        [str(i) for i in range(2015, 2020, 1)]
    ]

    # we want to set to NaN values for regions that don't have both CFC and GFCF data
    CFC_WB = (
        CFC_WB * GFCF_WB / GFCF_WB
    )  # in case some countries have data for CFC but not GFCF
    GFCF_WB = GFCF_WB * CFC_WB / CFC_WB

    CFC_WB = rename_region(CFC_WB, "Country Name").drop("Z - Aggregated categories")
    # rename the regions to a common format
    CFC_WB["region"] = cc.convert(names=CFC_WB.index, to="EXIO3")
    # convert the common format to EXIOBASE format
    CFC_WB = (
        CFC_WB.reset_index()
        .set_index("region")
        .drop("Country Name", axis=1)
        .groupby(level="region")
        .sum()
    )
    # define EXIOBASE regions as index

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

    Kbar15 = feather.read_feather(
        "C:/Users/andrieba/Documents/Data/Kbar/Kbar_2015pxp.feather"
    )

    # We calculate coefficients for year 2015 that will be multiplied by CFC for year 2017
    Kbarcoefs = (
        Kbar15.div(Kbar15.sum(), axis=1)
    ).stack()  # stacked because we need to access CY later

    # also load Kbar data from 2014 as CY is an outlier for Kbar2015
    Kbar14 = feather.read_feather(
        "C:/Users/andrieba/Documents/Data/Kbar/Kbar_2014pxp.feather"
    )

    Kbarcoefs["CY"] = Kbar14.div(Kbar14.sum(), axis=1).stack()[
        "CY"
    ]  # because wrong data for CY in Kbar15
    Kbarcoefs = Kbarcoefs.unstack()

    for i in range(2016, 2020, 1):
        GFCF_exio = feather.read_feather(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/Y.feather"
        ).swaplevel(axis=1)[
            "Gross fixed capital formation"
        ]  # aggregated 49 regions, 1 product

        CFC_exio = pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/satellite/F.txt",
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
            Kbarcoefs.mul(CFC_exio_rescaled, axis=1),
            "C:/Users/andrieba/Documents/Data/Kbar/Kbar_" + str(i) + "pxp.feather",
        )


# la somme des lignes donne CFC/GFCF


# ........CREATE FUNCTION TO AGGREGATE A DATAFRAME FROM GIVEN CONCORDANCE TABLE................


def agg(df: pd.DataFrame, table: pd.DataFrame, axis=0) -> pd.DataFrame:
    """Aggregates a DataFrame on the level specified in the concordance table, on the axis specified.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to be aggregated
    table : pd.DataFrame
        Concordance table for the agregation.
        It can be one-to-one or one-to-many but be of the appropriate shape.
        If one-to-one index_col=[0,1]. If one to many, index_col=0 and header=0.
        The name of the level to be aggregated must be the name of index_col=0.
    axis : int
        Axis that contains the level to be aggregated. Default=0.

    Returns
    -------
    df_agg : pd.DataFrame
        The aggregated DataFrame
    """
    if isinstance(table.index, pd.MultiIndex):
        if axis == 0:
            df_agg = (
                df.rename(index=dict(table.index)).groupby(level=df.index.names).sum()
            )
        else:
            df_agg = (
                df.rename(columns=dict(table.index))
                .groupby(level=df.columns.names, axis=1)
                .sum()
            )
        return df_agg

    else:
        if axis == 1:
            df = df.T

        levels_to_unstack = list(df.index.names)
        levels_to_unstack.remove(table.index.names[0])
        df = df.unstack(levels_to_unstack)

        df_agg = pd.DataFrame()
        for i in table.columns:
            df_agg[i] = df.mul(table[i], axis=0).sum()
        df_agg.columns.names = [table.index.names[0]]

        if axis == 0:
            return df_agg.unstack(levels_to_unstack).T
        else:
            return df_agg.unstack(levels_to_unstack)


# .........CALCULATIONS......................................

# function to diaggregate GDP into all the formats needed
def Y_all():

    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"

        Kbar = feather.read_feather(
            pathexio + "Kbar/Kbar_" + str(i) + "pxp.feather"
        ).fillna(0)
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
def Lk():
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
        Y = (
            feather.read_feather(pathIOT + "Y.feather")
            .groupby(level="region", axis=1)
            .sum()
        )
        Z = feather.read_feather(pathIOT + "Z.feather").fillna(0)
        Kbar = feather.read_feather(
            pathexio + "Kbar/Kbar_" + str(i) + "pxp.feather"
        ).fillna(0)
        Kbar = pd.DataFrame(Kbar, index=Z.index, columns=Z.columns).fillna(0)
        # EXTREMELY important to reindex, calc_L won't function properly otherwise

        Zk = Z + Kbar
        x = Z.sum(axis=1) + Y.sum(axis=1)
        Ak = pymrio.calc_A(Zk, x)
        feather.write_feather(pymrio.calc_L(Ak), pathIOT + "Lk.feather")

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

    conc_sec_cons = pd.read_excel(
        "concordance.xlsx", sheet_name="sector cons", index_col=0
    )
    conc_sec_prod = pd.read_excel(
        "concordance.xlsx", sheet_name="sector prod", index_col=[0, 1]
    )
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
                LY[j] = agg(
                    L.mul(Y[j], axis=1).groupby(level="sector cons", axis=1).sum(),
                    conc,
                    axis=1,
                ).stack()
                LkY[j] = agg(
                    Lk.mul(Y[j], axis=1).groupby(level="sector cons", axis=1).sum(),
                    conc,
                    axis=1,
                ).stack()

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
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
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
        F_hh_imp.loc["SF6"] = (
            F_hh_imp.loc["GHG"] / 1000000 - F_hh_imp.loc[["CO2", "N2O", "CH4"]].sum()
        )
        F_hh_imp = F_hh_imp.drop("GHG")
        F_hh[year] = F_hh_imp.groupby(level="region", axis=1).sum().stack()
    feather.write_feather(F_hh, "F_hh.feather")


##


def norm():
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
    feather.write_feather(df.div(pd.DataFrame(df.T.max())[0], axis=0), "norm.feather")


# il manque 349 mais il y a 575 qui arrivent donc ca fait 226 à rajouter. Or on a déjà rajouté 12 donc 214. Sur Sankey, 913-699 = 214


def data_Sankey(year, region):
    pathexio = "C:/Users/andrieba/Documents/Data/"
    pathIOT = pathexio + "EXIO3/IOT_" + str(year) + "_pxp/"
    SLY = feather.read_feather("SLY/" + region + "/" + str(year) + ".feather") / 1000
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

    data = SLY[["LY Government", "LY Households", "LY NCF", "LY NPISHS", "LY CFC"]]
    data["(Lk-L)Y Government"] = SLY["LkY Government"] - SLY["LY Government"]
    data["(Lk-L)Y Households"] = SLY["LkY Households"] - SLY["LY Households"]
    data["(Lk-L)Y NCF"] = SLY["LkY NCF"] - SLY["LY NCF"]
    data["(Lk-L)Y NPISHS"] = SLY["LkY NPISHS"] - SLY["LY NPISHS"]
    # capital component of footprint
    # data = data.drop("LY CFC", axis=1)
    # CFC is not needed anymore
    # Lk-L is used after capital endogenization
    # CFC<(Lk-L)Y, CFC>(Lk-L)Y and CFC - CFC>(Lk-L)Y, are used before capital endogenization

    # select only the data relevant to 'region'
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
                "(Lk-L)Y NCF",
                "(Lk-L)Y NPISHS",
            ]
        ]
        .unstack(level="sector cons")
        .sum(axis=1)
    )  # when df>0, CFC is imported
    # when df<0, CFC is exported
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
    data["CFC - CFC>(Lk-L)Y"] = data["LY CFC"].fillna(0) - data["CFC>(Lk-L)Y"].fillna(0)
    data = data.drop("LY CFC", axis=1)
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

    # for FR:
    # "CFC - CFC>(Lk-L)Y"FR from FR + "CFC>(Lk-L)Y" FR from FR
    # for RoW:
    # "CFC - CFC>(Lk-L)Y"RoW from FR + "CFC<(Lk-L)Y" FR from FR - "CFC>(Lk-L)Y" RoW from RoW
    # "CFC<(Lk-L)Y" from RoW

    # add to right
    try:
        supRegFromRoW = (
            data.stack()
            .unstack(level="LY name")["CFC>(Lk-L)Y"]
            .unstack(level="region cons")[[region]]
            .stack()
            .unstack(level="region prod")
            .drop(region, axis=1)
            .stack()
            .unstack(level=3)
        )
        supRegFromRoW["LY name"] = "supRegFromRoW"
        supRegFromRoW = supRegFromRoW.reset_index().set_index(data.index.names)
        data = pd.concat(
            [
                data,
                supRegFromRoW,
            ]
        )
    except KeyError:
        None

    # add to left infRegFromAll-supRoWFromReg

    try:
        infRegFromAll = (
            data.stack()
            .unstack(level="LY name")["CFC<(Lk-L)Y"]
            .unstack(level="region cons")[[region]]
            .stack()
            .unstack(level=4)
        )
        infRegFromAll["LY name"] = "infRegFromAll"
        infRegFromAll = infRegFromAll.reset_index().set_index(data.index.names)
        data = pd.concat(
            [
                data,
                infRegFromAll,
            ]
        )
    except KeyError:
        None

    try:
        MinusSupRoWFromReg = (
            -data.stack()
            .unstack(level="LY name")["CFC>(Lk-L)Y"]
            .unstack(level="region cons")
            .drop(region, axis=1)
            .stack()
            .unstack(level="region prod")[[region]]
            .stack()
            .unstack(level=3)
        )
        MinusSupRoWFromReg["LY name"] = "MinusSupRoWFromReg"
        MinusSupRoWFromReg = MinusSupRoWFromReg.reset_index().set_index(
            data.index.names
        )
        data = pd.concat(
            [
                data,
                MinusSupRoWFromReg,
            ]
        )
    except KeyError:
        None

    left_index = [
        "CFC - CFC>(Lk-L)Y",
        "CFC>(Lk-L)Y",
        "LY Government",
        "LY Households",
        "LY NCF",
        "LY NPISHS",
        "infRegFromAll",
        "MinusSupRoWFromReg",
    ]

    right_index = [
        "(Lk-L)Y Government",
        "(Lk-L)Y Households",
        "(Lk-L)Y NCF",
        "(Lk-L)Y NPISHS",
        "LY Government",
        "LY Households",
        "LY NCF",
        "LY NPISHS",
        "supRegFromRoW",
    ]

    # 0. ges
    data.loc[[i for i in data.index if i[4] in left_index], ["0. ges"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(level="Extensions")

    # 1. imp reg
    data.loc[[i for i in data.index if i[4] in left_index], ["1. imp reg"]] = (
        data.loc[[i for i in data.index if i[4] in left_index]].index.get_level_values(
            level="region prod"
        )
        + " "
    )

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

    # 3. pba

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

    data.loc[[i for i in data.index if i[4] in left_index], ["3. pba"]] = data.loc[
        [i for i in data.index if i[4] in left_index]
    ].rename(index=DictRoW).index.get_level_values(level="region prod") + data.loc[
        [i for i in data.index if i[4] in left_index]
    ].index.get_level_values(
        level="sector prod"
    )

    # 4. cba

    Dict_cba = dict(
        {
            "LY Government": "Government",
            "LY Households": "Households",
            "LY NCF": "Net capital formation",
            "LY NPISHS": "NPISHS",
            "CFC - CFC>(Lk-L)Y": "CFC",
            "CFC>(Lk-L)Y": "CFC",
            # "infRegFromAll",
            # "MinusSupRoWFromReg",
        }
    )

    left_index_partial = [
        "CFC - CFC>(Lk-L)Y",
        "LY Government",
        "LY Households",
        "LY NCF",
        "LY NPISHS",
        "CFC>(Lk-L)Y",
    ]
    data.loc[
        [i for i in data.index if i[4] in left_index_partial], ["4. cba"]
    ] = data.loc[[i for i in data.index if i[4] in left_index_partial]].rename(
        index=DictRoW
    ).index.get_level_values(
        level="region cons"
    ) + data.loc[
        [i for i in data.index if i[4] in left_index_partial]
    ].rename(
        index=Dict_cba
    ).index.get_level_values(
        level="LY name"
    )

    data.loc[
        [i for i in data.index if i[4] in ["infRegFromAll", "MinusSupRoWFromReg"]],
        ["4. cba"],
    ] = "RoW - CFC"

    # 5. endo

    data.loc[
        [
            i
            for i in data.index
            if i[4]
            in [
                "(Lk-L)Y Government",
                "(Lk-L)Y Households",
                "(Lk-L)Y NCF",
                "(Lk-L)Y NPISHS",
            ]
        ],
        ["5. endo"],
    ] = (
        data.loc[
            [
                i
                for i in data.index
                if i[4]
                in [
                    "(Lk-L)Y Government",
                    "(Lk-L)Y Households",
                    "(Lk-L)Y NCF",
                    "(Lk-L)Y NPISHS",
                ]
            ]
        ]
        .rename(index=DictRoW)
        .index.get_level_values(level="region cons")
        + "CFCk"
    )

    data.loc[
        [i for i in data.index if i[4] == "supRegFromRoW"],
        ["5. endo"],
    ] = "RoW - CFCk"

    # 6. cbaK
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
            "LY NCF": "Net capital formation",
            "LY NPISHS": "NPISHS",
            "supRegFromRoW": "supRegFromRoW",
            "(Lk-L)Y Government": "Government",
            "(Lk-L)Y Households": "Households",
            "(Lk-L)Y NCF": "Net capital formation",
            "(Lk-L)Y NPISHS": "NPISHS",
        }
    )

    data.loc[[i for i in data.index if i[4] in right_index], ["6. cbaK"]] = (
        data.loc[[i for i in data.index if i[4] in right_index]]
        .rename(index=DictExp)
        .index.get_level_values(level="region cons")
        + data.loc[[i for i in data.index if i[4] in right_index]]
        .rename(index=DictCbaK)
        .index.get_level_values(level="LY name")
        + " "
    )  # Space here to differenciate level 5 nodes from level 4 nodes

    data = data.replace(
        dict(
            {
                region + "Government ": "Government ",
                region + "Households ": "Households ",
                region + "Net capital formation ": "Net capital formation ",
                region + "NPISHS ": "NPISHS ",
                region + "Households direct ": "Households direct ",
                region + "supRegFromRoW ": "Exports",
                "ExportsGovernment ": "Exports",
                "ExportsHouseholds ": "Exports",
                "ExportsNet capital formation ": "Exports",
                "ExportsNPISHS ": "Exports",
                "ExportssupRegFromRow ": "Exports",
            }
        )
    )

    # 7. cons

    data.loc[[i for i in data.index if i[4] in right_index], ["7. cons"]] = data.loc[
        [i for i in data.index if i[4] in right_index]
    ].rename(index=DictRoW).index.get_level_values(level="region cons") + data.loc[
        [i for i in data.index if i[4] in right_index]
    ].index.get_level_values(
        level="sector cons"
    )
    data = data.replace(
        dict.fromkeys(
            [
                "150100:MACHINERY AND EQUIPMENT",
                "150200:CONSTRUCTION",
                "150300:OTHER PRODUCTS",
                "RoW - 150100:MACHINERY AND EQUIPMENT",
                "RoW - 150200:CONSTRUCTION",
                "RoW - 150300:OTHER PRODUCTS",
                "None",
                "RoW - None",
            ],
            np.nan,
        )
    )
    data.loc[
        [i for i in data.index if i[4] == "LY NCF" and i[5] != region], ["7. cons"]
    ] = "RoW - Net capital formation "
    data.loc[
        [i for i in data.index if i[4] == "(Lk-L)Y NCF" and i[5] != region], ["7. cons"]
    ] = "RoW - Net capital formation "

    # 8. exp

    data.loc[
        [i for i in data.index if i[4] in right_index and i[5] != region], ["8. exp"]
    ] = data.loc[
        [i for i in data.index if i[4] in right_index and i[5] != region]
    ].index.get_level_values(
        level="region cons"
    )

    # Add households direct

    F_hh = feather.read_feather("F_hh.feather")[year].unstack()[region] / 1000
    share_transport = 0.55

    for ext in F_hh.index:
        data.loc[
            "Mobility",
            "Households direct emissions",
            region,
            ext,
            "Households direct",
            region,
        ] = [
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

        data.loc[
            "Shelter",
            "Households direct emissions",
            region,
            ext,
            "Households direct",
            region,
        ] = [
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

    # Nodes

    position_all = [
        "0. ges",
        "1. imp reg",
        "2. imp dom",
        "3. pba",
        "4. cba",
        "5. endo",
        "6. cbaK",
        "7. cons",
        "8. exp",
    ]

    node_list = []
    for j in position_all:
        node_list.extend(list(dict.fromkeys(data.reset_index()[j])))
    node_list = [x for x in node_list if str(x) != "nan"]
    node_dict = dict(zip(node_list, list(range(0, len(node_list), 1))))

    position = [
        "0. ges",
        "1. imp reg",
        "2. imp dom",
        "3. pba",
        "4. cba",
        # "5. endo",
        "6. cbaK",
        "7. cons",
        "8. exp",
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

    df = (
        data[["5. endo", "6. cbaK", "value"]]
        .replace(node_dict)
        .dropna()
        .rename(columns={"5. endo": "source", "6. cbaK": "target"})
    )
    df["color label"] = df.index.get_level_values(level="sector prod")
    df["position"] = "5. endo"
    data_sankey = pd.concat([data_sankey, df])

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

    data_sankey["color"] = data_sankey["color label"].replace(color_dict)
    data_sankey = pd.DataFrame(data_sankey.reset_index())[
        ["source", "target", "color", "value", "position"]
    ]
    data_sankey.set_index(["source", "target", "color", "position"], inplace=True)
    data_sankey = data_sankey.groupby(
        level=["source", "target", "color", "position"]
    ).sum()
    data_sankey.reset_index(col_level=0, inplace=True)

    # junction

    # CFC to CFCk
    if (
        region
        in data.xs("CFC - CFC>(Lk-L)Y", level="LY name")
        .index.get_level_values(level="region cons")
        .unique()
    ):
        df = (
            data.xs("CFC - CFC>(Lk-L)Y", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey = data_sankey.append(
            pd.DataFrame(
                [
                    [node_dict["CFC"]] * len(df),
                    [node_dict["CFCk"]] * len(df),
                    df.values,
                    [color_dict[i] for i in df.index.values],
                    ["4. cba"] * len(df),
                ],
                index=["source", "target", "value", "color", "position"],
            ).T
        )

    # RoW - CFC to RoW - CFCk
    try:
        df = (
            data.xs("CFC - CFC>(Lk-L)Y", level="LY name")["value"]
            .unstack(level="region cons")
            .groupby(level="sector prod")
            .sum()
            .drop(region, axis=1)
            .sum(axis=1)
        )
    except KeyError:
        df = (
            data.xs("CFC - CFC>(Lk-L)Y", level="LY name")["value"]
            .unstack(level="region cons")
            .groupby(level="sector prod")
            .sum()
            .sum(axis=1)
        )
    data_sankey = data_sankey.append(
        pd.DataFrame(
            [
                [node_dict["RoW - CFC"]] * len(df),
                [node_dict["RoW - CFCk"]] * len(df),
                df.values,
                [color_dict[i] for i in df.index.values],
                ["4. cba"] * len(df),
            ],
            index=["source", "target", "value", "color", "position"],
        ).T
    )

    # CFC to RoW - CFCk
    if (
        region
        in data.xs("CFC>(Lk-L)Y", level="LY name")
        .index.get_level_values(level="region cons")
        .unique()
    ):
        df = (
            data.xs("CFC>(Lk-L)Y", level="LY name")
            .xs(region, level="region cons")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey = data_sankey.append(
            pd.DataFrame(
                [
                    [node_dict["CFC"]] * len(df),
                    [node_dict["RoW - CFCk"]] * len(df),
                    df.values,
                    [color_dict[i] for i in df.index.values],
                    ["4. cba"] * len(df),
                ],
                index=["source", "target", "value", "color", "position"],
            ).T
        )

    # RoW - CFC to CFCk
    try:
        df = (
            data.xs("CFC>(Lk-L)Y", level="LY name")
            .stack()
            .unstack(level="region cons")
            .drop(region, axis=1)
            .sum(axis=1)
            .groupby(level="sector prod")
            .sum()
        )
    except KeyError:
        df = (
            data.xs("CFC>(Lk-L)Y", level="LY name")
            .groupby(level="sector prod")
            .sum()["value"]
        )
        data_sankey = data_sankey.append(
            pd.DataFrame(
                [
                    [node_dict["RoW - CFC"]] * len(df),
                    [node_dict["CFCk"]] * len(df),
                    df.values,
                    [color_dict[i] for i in df.index.values],
                    ["4. cba"] * len(df),
                ],
                index=["source", "target", "value", "color", "position"],
            ).T
        )

    # RoW - CFC to CFCk
    df = (
        data.loc[
            [i for i in data.index if i[4] in ["infRegFromAll", "MinusSupRoWFromReg"]]
        ]
        .groupby(level="sector prod")
        .sum()["value"]
    )
    data_sankey = data_sankey.append(
        pd.DataFrame(
            [
                [node_dict["RoW - CFC"]] * len(df),
                [node_dict["CFCk"]] * len(df),
                df.values,
                [color_dict[i] for i in df.index.values],
                ["4. cba"] * len(df),
            ],
            index=["source", "target", "value", "color", "position"],
        ).T
    )
    return node_dict, node_list, data_sankey


def fig_sankey(year, region):

    nodes = feather.read_feather(
        "Sankeys/" + region + "/nodes" + region + str(year) + ".feather"
    )
    data_sankey = feather.read_feather(
        "Sankeys/" + region + "/data" + region + str(year) + ".feather"
    ).sort_values(by="color")
    norm = feather.read_feather("norm.feather")

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

    nodes["x"].loc["CFCk"] = 0.645
    nodes["x"].loc["RoW - CFCk"] = 0.645

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

    nodes["x"].loc[
        [
            "Mobility",
            "Shelter",
            "Food",
            "Clothing",
            "Education",
            "Health",
            "Other goods and services",
        ]
    ] = 0.88

    nodes["label Mt"].loc["Consumption of fixed capital"] = ""

    nodes["label Mt"].loc["RoW - Consumption of fixed capital"] = ""
    # nodes["x"].loc[
    #     "Clothing",
    #     "Education",
    #     "Food",
    #     "Health",
    #     "Mobility",
    #     "Other goods and services",
    #     "Shelter",
    # ] = (
    #     1 - 0.001
    # )

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
        "label": nodes["label Mt"].replace(dictreg),
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
    fig.write_image(
        "Sankeys/" + region + "/fig2" + region + str(year) + ".pdf", engine="orca"
    )
    # fig.write_image("SankeyFR" + str(year) + ".svg", engine="orca")
    fig.show()


def pop():
    pop = (
        rename_region(
            pd.read_csv("World Bank/pop.csv", header=[2], index_col=[0])[
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

    pop.loc["TW"] = pd.read_excel("pop Taiwan.xls", header=0, index_col=0)["TW"]

    feather.write_feather(pop, "pop.feather")


def norm_cap():
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
        df.div(pd.DataFrame(df.T.max())[0], axis=0), "norm_cap.feather"
    )


def fig_sankey_cap(year, region):

    pop = feather.read_feather("pop.feather")[year].loc[region] / 1000
    nodes = feather.read_feather(
        "Sankeys/" + region + "/nodes" + region + str(year) + ".feather"
    )
    data_sankey = feather.read_feather(
        "Sankeys/" + region + "/data" + region + str(year) + ".feather"
    )
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

    nodes["x"].loc[
        [
            "Mobility",
            "Shelter",
            "Food",
            "Clothing",
            "Education",
            "Health",
            "Other goods and services",
        ]
    ] = 0.88

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


def node_y(nodes, node, white, color, region):
    if node == "CFCk":
        node = "CFC"
    if node == "RoW - CFCk":
        node = "RoW - CFC"
    if node == "Exports":
        node = "RoW - Clothing"

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
            .loc["7. cons"]["value Mt"]
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
            .loc["7. cons"]["value Mt"]
            .loc[
                [
                    "Mobility",
                    "Shelter",
                    "Food",
                    "Clothing",
                    "Education",
                    "Health",
                    "Other goods and services",
                ]
            ]
        )
        df = df.append(df2)
        df3 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["6. cbaK"]["value Mt"]
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
    ]:
        df3 = (
            nodes.reset_index()
            .set_index(["position", "index"])
            .loc["6. cbaK"]["value Mt"]
            .loc["Net capital formation "]
        )
        df.loc["Net capital formation "] = df3

    total = nodes.reset_index().set_index("position").loc["0. ges"]["value Mt"].sum()
    if pos == "0. ges":
        df = df.reindex(["CO2", "CH4", "N2O", "SF6"])
    elif pos == "1. imp reg":
        df = df.reindex(
            pd.Index([region + " "]).union(
                df.index.sort_values().drop(region + " "), sort=False
            )
        )
    elif pos == "2. imp dom":
        df = df.reindex(["Territorial", "Imports"])
    elif pos == "3. pba":
        df = df.reindex(
            pd.Index(["Households direct emissions"])
            .union(
                df.loc[df.index.str[:2] != "Ro"].index.drop(
                    "Households direct emissions"
                ),
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
                "CFC",
                "RoW - CFC",
                "RoW - Households",
                "RoW - Government",
                "RoW - NPISHS",
                "RoW - Net capital formation",
                # "RoW - Consumption of fixed capital ",
            ]
        )
    elif pos == "6. cbaK":
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
            ]
        )

    elif pos == "7. cons":
        df = df.reindex(
            [
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
            ]
        )
    elif pos == "8. exp":
        df = df.reindex(
            [
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
        )
    return (
        len(df.loc[:node]) / (len(df) + 1) * white
        + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
    )


def nodes_data():
    population = feather.read_feather("pop.feather")
    for year in range(2019, 2020, 1):
        # for region in pd.read_excel("regions.xlsx", index_col=0).index:
        for region in ["CN"]:
            pop = population[year].loc[region] / 1000
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
                # j_modified = pd.DataFrame(node_list).replace(dict(FR="France"))[0].loc[i]
                # Mettre dict complet pour toutes régions
                if node_dict[node] in source_data.index:
                    nodes["value Mt"].loc[node] = source_data["value"].loc[
                        node_dict[node]
                    ]

                    a = (
                        data_sankey.reset_index()
                        .set_index("source")["position"]
                        .loc[node_dict[node]]
                    )
                    if type(a) == str:
                        nodes["position"].loc[node] = a
                    else:
                        nodes["position"].loc[node] = a.values[0]
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
                    ]:
                        nodes["position"].loc[node] = "8. exp"
                    elif node in ["CFC", "RoW - CFC"]:
                        nodes["position"].loc[node] = "4. cba"
                    else:
                        nodes["position"].loc[node] = "7. cons"
            nodes.loc["Net capital formation "]["position"] = "6. cbaK"
            nodes["label Mt"] = (
                nodes.index + " (" + [str(int(i)) for i in nodes["value Mt"]] + ")"
            )
            nodes["value t/cap"] = nodes["value Mt"] / pop
            nodes["label t/cap"] = (
                nodes.index
                + " ("
                + [str(round(i, 2)) for i in nodes["value t/cap"]]
                + ")"
            )

            if not os.path.exists("Sankeys/" + region):
                os.mkdir("Sankeys/" + region)
            feather.write_feather(
                nodes, "Sankeys/" + region + "/nodes" + region + str(year) + ".feather"
            )
            feather.write_feather(
                data_sankey,
                "Sankeys/" + region + "/data" + region + str(year) + ".feather",
            )


# hh from IPCC
# ajouter Net capital formation pour calcul noeuds RoW (exemple CN cap 1995)

# app rester éveillée
# app onglets
