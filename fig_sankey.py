import pandas as pd
import plotly.graph_objs as go
import pyarrow.feather as feather
import pathlib
import json
from flask_caching import Cache


# cache = Cache(app.server, config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})

DATA_PATH = pathlib.Path(__file__).parent  # .joinpath("data").resolve()

REGIONS = {}

with open(f"{DATA_PATH}/regions.json") as f:
    REGIONS = json.loads(f.read())

LABELS = [{"label": v, "value": k} for k, v in REGIONS.items()]


color_dict = dict(
    {
        "#8de5a1": "#0072ff",
        "#a1c9f4": "#00cafe",
        "#cfcfcf": "#b0ebff",
        "#debb9b": "#fff1b7",
        "#fab0e4": "#ffdc23",
        "#ff9f9b": "#ffb758",
        "#ffb482": "#ff8200",
    }
)


def fig_sankey(year, region):

    norm = feather.read_feather(DATA_PATH.joinpath("norm.feather"))

    ratio = norm.loc[region].loc[year]

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
        if node == "Footprint":
            node = "Food"

        pos = nodes["position"].loc[node]
        df = nodes.reset_index().set_index(["position", "index"]).loc[pos]["value Mt"]

        if node in [
            "Households direct ",
            "Households ",
            "Government ",
            "NPISHS ",
            "Positive capital formation ",
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
                        "RoW - Positive capital formation ",
                    ]
                ]
            )
            df = pd.concat([df.drop("Exports"), df2])

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
            df = pd.concat([df, df2])
            df3 = (
                nodes.reset_index()
                .set_index(["position", "index"])
                .loc["7. cbaK"]["value Mt"]
                .loc["Positive capital formation "]
            )
            df.loc["Positive capital formation "] = df3

        if node in [
            "RoW - Mobility",
            "RoW - Shelter",
            "RoW - Food",
            "RoW - Clothing",
            "RoW - Education",
            "RoW - Health",
            "RoW - Other goods and services",
            "RoW - Positive capital formation ",
        ]:
            df3 = (
                nodes.reset_index()
                .set_index(["position", "index"])
                .loc["7. cbaK"]["value Mt"]
                .loc["Positive capital formation "]
            )
            df.loc["Positive capital formation "] = df3

        total = max(
            nodes.reset_index().set_index("position").loc["4. cba"]["value Mt"].sum(),
            nodes.reset_index().set_index("position").loc["7. cbaK"]["value Mt"].sum(),
        )
        if pos == "0. ges":
            df = df.reindex(["CO2", "CH4", "N2O", "SF6"])
        elif pos == "1. imp reg":
            df = df.reindex(
                pd.Index([REGIONS[region] + " "]).union(df.index.sort_values().drop(REGIONS[region] + " "), sort=False)
            )
        elif pos == "2. imp dom":
            df = df.reindex(["Territorial", "Imports"])
        elif pos == "3. pba":
            df = df.reindex(
                pd.Index(["Households direct   "])
                .union(
                    df.loc[df.index.str[:2] != "Ro"].index.drop("Households direct   "),
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
                    # "Positive capital formation",
                    "GCF",
                    "Negative capital formation",
                    "RoW - Negative capital formation",
                    "RoW - GCF",
                    "RoW - Households",
                    "RoW - Government",
                    "RoW - NPISHS",
                    # "RoW - Positive capital formation",
                ]
            )
        elif pos == "7. cbaK":
            df = df.reindex(
                [
                    "Households direct ",
                    "Households ",
                    "Government ",
                    "NPISHS ",
                    "Positive capital formation ",
                    # "RoW - Mobility",
                    # "RoW - Shelter",
                    # "RoW - Food",
                    "RoW - Clothing",
                    "RoW - Education",
                    "RoW - Health",
                    "RoW - Other goods and services",
                    "RoW - Positive capital formation ",
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
                        "Positive capital formation ",
                        # "Households direct ",
                        "RoW - Mobility",
                        "RoW - Shelter",
                        "RoW - Food",
                        "RoW - Clothing",
                        "RoW - Education",
                        "RoW - Health",
                        "RoW - Other goods and services",
                        "RoW - Positive capital formation ",
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
                        "Positive capital formation ",
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
            len(df.loc[:node]) / (len(df) + 1) * (1 - color * df.sum() / total)  # white
            + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
        )

    def Nodes(region, year, height, top_margin, bottom_margin, pad, ratio):
        nodes = feather.read_feather(
            DATA_PATH.joinpath("Sankeys/" + region + "/nodes" + region + str(year) + ".feather")
        )

        size = height - top_margin - bottom_margin
        n = max(nodes.reset_index().set_index("position").index.value_counts())
        n = 13
        pad2 = (size - ratio * (size - (n - 1) * pad)) / (n + 1)
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
                                0.00001,
                                0.095,  # 9.5
                                0.19,  # 9.5
                                0.285,  # 9.5
                                0.44,  # 15.5
                                0.52,  # 8
                                0.6,  # 8
                                0.68,  # 8
                                0.835,  # 15.5
                                1,  # 16.5
                            ]
                        ),
                    )
                )
            ),
            y=lambda d: [node_y(nodes, i, white, color, region) for i in d.index],
        )

        # nodes["x"].loc["Exports"] = 0.67
        if "CFC imports re-exported" in nodes.index:
            try:
                nodes["x", "CFC imports re-exported"] = 0.68
            except KeyError:
                None

        try:
            nodes["x", "RoW - Negative capital formation"] = 0.48
        except KeyError:
            None

        try:
            nodes["x", "Negative capital formation"] = 0.48
        except KeyError:
            None

        nodes["x", "Footprint"] = 1

        return nodes, pad2

    data_sankey = feather.read_feather(
        DATA_PATH.joinpath("Sankeys/" + region + "/data" + region + str(year) + ".feather")
    ).replace(color_dict)
    node_list = feather.read_feather(
        DATA_PATH.joinpath("Sankeys/" + region + "/nodelist" + region + str(year) + ".feather")
    )[0].values

    height = 480
    width = 1100
    top_margin = 30
    bottom_margin = 10
    left_margin = 10
    right_margin = 10
    pad = 10

    nodes, pad2 = Nodes(region, year, height, top_margin, bottom_margin, pad, ratio)

    link = dict(
        source=data_sankey["source"],
        target=data_sankey["target"],
        value=data_sankey["value"],
        label=list(str(x) + " MtCO2eq" for x in data_sankey["value"].astype(float).round(1)),
        color=data_sankey["color"],
        hovertemplate="",
    )

    node = {
        "label": (pd.DataFrame(nodes, index=node_list))["label Mt"].replace(REGIONS).values,
        "pad": pad2,
        "thickness": 2,
        "color": "#00005A",  # ,#00008E, #0028dc
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
        title=f"<b>Greenhouse gas footprint of {REGIONS[region]} in {year} (Mt CO2eq)<b>",
        font=dict(size=10, color="black"),
        paper_bgcolor="white",
        title_x=0.5,
        font_family="Arial",
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
    fig.write_image("suppr.svg", engine="orca")

    return fig


def fig_sankey_cap(year, region):

    norm = feather.read_feather(DATA_PATH.joinpath("norm_cap.feather"))  # Different norm in t/cap and Mt
    pop = feather.read_feather(DATA_PATH.joinpath("pop.feather"))

    ratio = norm.loc[region].loc[year]

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
        if node == "Footprint":
            node = "Food"

        pos = nodes["position"].loc[node]
        df = nodes.reset_index().set_index(["position", "index"]).loc[pos]["value Mt"]

        if node in [
            "Households direct ",
            "Households ",
            "Government ",
            "NPISHS ",
            "Positive capital formation ",
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
                        "RoW - Positive capital formation ",
                    ]
                ]
            )
            df = pd.concat([df.drop("Exports"), df2])

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
            df = pd.concat([df, df2])
            df3 = (
                nodes.reset_index()
                .set_index(["position", "index"])
                .loc["7. cbaK"]["value Mt"]
                .loc["Positive capital formation "]
            )
            df.loc["Positive capital formation "] = df3

        if node in [
            "RoW - Mobility",
            "RoW - Shelter",
            "RoW - Food",
            "RoW - Clothing",
            "RoW - Education",
            "RoW - Health",
            "RoW - Other goods and services",
            "RoW - Positive capital formation ",
        ]:
            df3 = (
                nodes.reset_index()
                .set_index(["position", "index"])
                .loc["7. cbaK"]["value Mt"]
                .loc["Positive capital formation "]
            )
            df.loc["Positive capital formation "] = df3

        total = max(
            nodes.reset_index().set_index("position").loc["4. cba"]["value Mt"].sum(),
            nodes.reset_index().set_index("position").loc["7. cbaK"]["value Mt"].sum(),
        )
        if pos == "0. ges":
            df = df.reindex(["CO2", "CH4", "N2O", "SF6"])
        elif pos == "1. imp reg":
            df = df.reindex(
                pd.Index([REGIONS[region] + " "]).union(df.index.sort_values().drop(REGIONS[region] + " "), sort=False)
            )
        elif pos == "2. imp dom":
            df = df.reindex(["Territorial", "Imports"])
        elif pos == "3. pba":
            df = df.reindex(
                pd.Index(["Households direct   "])
                .union(
                    df.loc[df.index.str[:2] != "Ro"].index.drop("Households direct   "),
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
                    # "Positive capital formation",
                    "GCF",
                    "Negative capital formation",
                    "RoW - Negative capital formation",
                    "RoW - GCF",
                    "RoW - Households",
                    "RoW - Government",
                    "RoW - NPISHS",
                    # "RoW - Positive capital formation",
                ]
            )
        elif pos == "7. cbaK":
            df = df.reindex(
                [
                    "Households direct ",
                    "Households ",
                    "Government ",
                    "NPISHS ",
                    "Positive capital formation ",
                    # "RoW - Mobility",
                    # "RoW - Shelter",
                    # "RoW - Food",
                    "RoW - Clothing",
                    "RoW - Education",
                    "RoW - Health",
                    "RoW - Other goods and services",
                    "RoW - Positive capital formation ",
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
                        "Positive capital formation ",
                        # "Households direct ",
                        "RoW - Mobility",
                        "RoW - Shelter",
                        "RoW - Food",
                        "RoW - Clothing",
                        "RoW - Education",
                        "RoW - Health",
                        "RoW - Other goods and services",
                        "RoW - Positive capital formation ",
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
                        "Positive capital formation ",
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
            len(df.loc[:node]) / (len(df) + 1) * (1 - color * df.sum() / total)  # white
            + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
        )

    def Nodes(region, year, height, top_margin, bottom_margin, pad, ratio):
        nodes = feather.read_feather(
            DATA_PATH.joinpath("Sankeys/" + region + "/nodes" + region + str(year) + ".feather")
        )

        size = height - top_margin - bottom_margin
        n = max(nodes.reset_index().set_index("position").index.value_counts())
        n = 13
        pad2 = (size - ratio * (size - (n - 1) * pad)) / (n + 1)
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
                                0.67,  # 12
                                0.84,  # 10
                                0.999,
                            ]
                        ),
                    )
                )
            ),
            y=lambda d: [node_y(nodes, i, white, color, region) for i in d.index],
        )

        nodes["x", "Exports"] = 0.67
        if "CFC imports re-exported" in nodes.index:
            try:
                nodes["x", "CFC imports re-exported"] = 0.65
            except KeyError:
                None

        try:
            nodes["x", "RoW - Negative capital formation"] = 0.45
        except KeyError:
            None

        try:
            nodes["x", "Negative capital formation"] = 0.45
        except KeyError:
            None

        nodes["x", "Footprint"] = 0.999

        return nodes, pad2

    data_sankey = feather.read_feather(
        DATA_PATH.joinpath("Sankeys/" + region + "/data" + region + str(year) + ".feather")
    ).replace(color_dict)
    node_list = feather.read_feather(
        DATA_PATH.joinpath("Sankeys/" + region + "/nodelist" + region + str(year) + ".feather")
    )[0].values

    height = 450
    width = 1100
    top_margin = 50
    bottom_margin = 0
    left_margin = 50
    right_margin = 50
    pad = 10

    nodes, pad2 = Nodes(region, year, height, top_margin, bottom_margin, pad, ratio)
    # node_dict, node_list, data_sankey = data_Sankey(year, region)

    link = dict(
        source=data_sankey["source"],
        target=data_sankey["target"],
        value=data_sankey["value"] * 1000000 / pop.loc[region].loc[year],
        label=list(str(x) + " tCO2eq/capita" for x in data_sankey["value"].astype(float).round(1)),
        color=data_sankey["color"],
        hovertemplate="",
    )

    node = {
        # "label": pd.DataFrame(node_list)[0],
        "label": (pd.DataFrame(nodes, index=node_list))["label t/cap"].replace(REGIONS).values,
        "pad": pad2,
        "thickness": 2,
        # "line" : dict(color = "black", width = 0.5),
        # "color": "white",  #00005A,#00008E, #0028dc
        "color": "#00005A",  # ,#00008E, #0028dc
        "x": nodes["x"].values,
        "y": nodes["y"].values,
    }

    sankey = go.Sankey(
        link=link,
        node=node,  #
        valueformat=".0f",
        valuesuffix=" tCO2eq/capita",
        # arrangement="snap",
    )

    fig = go.Figure(sankey)
    fig.update_layout(
        hovermode="y",
        title=f"<b>Greenhouse gas footprint of {REGIONS[region]} in {year} (tCO2eq/capita)<b>",
        font=dict(size=8, color="black"),
        paper_bgcolor="white",
        title_x=0.5,
        font_family="Arial",
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
    # fig.write_image(
    #     "Sankeys/" + region + "/fig2" + region + str(year) + ".pdf", engine="orca"
    # )
    # # fig.write_image("SankeyFR" + str(year) + ".svg", engine="orca")

    return fig
