def Kbar():

    CFC_WB = pd.read_excel("World Bank/CFC worldbank.xlsx", header=3, index_col=[0])[
        [str(i) for i in range(2015, 2020, 1)]
    ]

    GFCF_WB = pd.read_excel("World Bank/GFCF worldbank.xlsx", header=3, index_col=[0])[
        [str(i) for i in range(2015, 2020, 1)]
    ]

    # we want to set to NaN values for regions that don't have both CFC and GFCF data
    CFC_WB = CFC_WB * GFCF_WB / GFCF_WB  # in case some countries have data for CFC but not GFCF
    GFCF_WB = GFCF_WB * CFC_WB / CFC_WB

    CFC_WB = rename_region(CFC_WB, "Country Name").drop("Z - Aggregated categories")
    # rename the regions to a common format
    CFC_WB["region"] = cc.convert(names=CFC_WB.index, to="EXIO3")
    # convert the common format to EXIOBASE format
    CFC_WB = CFC_WB.reset_index().set_index("region").drop("Country Name", axis=1).groupby(level="region").sum()
    # define EXIOBASE regions as index

    GFCF_WB = rename_region(GFCF_WB, "Country Name").drop("Z - Aggregated categories")
    GFCF_WB["region"] = cc.convert(names=GFCF_WB.index, to="EXIO3")
    GFCF_WB = GFCF_WB.reset_index().set_index("region").drop("Country Name", axis=1).groupby(level="region").sum()

    GFCF_over_CFC_WB = GFCF_WB / CFC_WB
    GFCF_over_CFC_WB.loc["TW"] = GFCF_over_CFC_WB.loc["CN"]
    # hypothesis: ratio of GFCF/CFC is same for Taiwan than for China

    Kbar15 = feather.read_feather("Data/Kbar/Kbar_2015.feather")

    # We calculate coefficients for year 2015 that will be multiplied by CFC for year 2017
    Kbarcoefs = Kbar15.div(Kbar15.sum(axis=1), axis=0)

    for i in range(2016, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"
        Z = feather.read_feather(pathIOT + "Z.feather").fillna(0)
        Zcoefs = Z.div(Z.sum(axis=1), axis=0)

        Kbarcoefsyear = Kbarcoefs.combine_first(Zcoefs).combine_first(
            pd.DataFrame(np.identity(9800), index=Z.index, columns=Z.columns)
        )

        GFCF_exio = feather.read_feather(pathexio + "EXIO3/IOT_" + str(i) + "_pxp/Y.feather").swaplevel(axis=1)[
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
            CFC_exio.unstack().mul(GFCF_over_CFC_exio, axis=0).div(GFCF_over_CFC_WB[str(i)], axis=0).stack()
        )

        feather.write_feather(
            Kbarcoefsyear.mul(CFC_exio_rescaled, axis=0),
            "Data/Kbar/Kbar_" + str(i) + ".feather",
        )
