import pandas as pd
import plotly.graph_objs as go
import pyarrow.feather as feather
import pathlib
import json
from flask_caching import Cache
import os


DATA_PATH = pathlib.Path(__file__).parent  # .joinpath("Data").resolve()

REGIONS = {}

with open(f"{DATA_PATH}/Data/regions.json") as f:
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


def node_y(nodes, node, color, region):
    rename_nodes = {
        "CFC": "GCF",
        "RoW - CFC": "RoW - GCF",
        "CFCk": "GCF",
        "RoW - CFCk": "RoW - GCF",
        "Exports": "RoW - Health",
        "CFC imports re-exported": "RoW - Food",
        "Footprint": "Food",
    }
    node = rename_nodes.get(node, node)

    pos = nodes["position"].loc[node]
    df = nodes.reset_index().set_index(["position", "index"]).loc[pos]["value Mt"]

    fd_category = ["Households ", "Government ", "NPISHS ", "Positive capital formation "]
    row_sect = [
        "RoW - " + sect
        for sect in ["Mobility", "Shelter", "Food", "Clothing", "Education", "Health", "Other goods and services"]
    ] + ["RoW - Positive capital formation "]
    regions = ["Africa", "Asia", "Europe", "Middle East", "North America", "Oceania", "South America"]
    fd_sect = ["Mobility", "Shelter", "Food", "Clothing", "Education", "Health", "Other goods and services"]

    loc_idx = nodes.reset_index().set_index(["position", "index"])

    if node in fd_category:
        df2 = loc_idx.loc["8. cons"]["value Mt"].loc[row_sect]
        df = pd.concat([df.drop("Exports"), df2])

    if node in regions:
        df2 = loc_idx.loc["8. cons"]["value Mt"].loc[[i for i in fd_sect if i in nodes.index]]
        df3 = loc_idx.loc["7. cbaK"]["value Mt"].loc["Positive capital formation "]
        df = pd.concat([df, df2])
        df.loc["Positive capital formation "] = df3

    if node in row_sect:
        df.loc["Positive capital formation "] = loc_idx.loc["7. cbaK"]["value Mt"].loc["Positive capital formation "]

    total = max(
        nodes.reset_index().set_index("position").loc["4. cba"]["value Mt"].sum(),
        nodes.reset_index().set_index("position").loc["7. cbaK"]["value Mt"].sum(),
    )

    pos_reindex = {
        "0. ges": ["CO2", "CH4", "N2O", "F-gases"],
        "1. imp reg": [REGIONS[region] + " "] + sorted(list(set(df.index) - {REGIONS[region] + " "})),
        "2. imp dom": ["Territorial", "Imports"],
        "3. pba": ["Direct emissions"]
        + sorted([i for i in df.index if "Ro" not in i and i != "Direct emissions"])
        + [i for i in df.index if "Ro" in i],
        "4. cba": [
            "Households",
            "Government",
            "NPISHS",
            "GCF",
            "Negative capital formation",
            "RoW - Negative capital formation",
            "RoW - GCF",
            "RoW - Households",
            "RoW - Government",
            "RoW - NPISHS",
        ],
        "7. cbaK": fd_category + row_sect,
        "8. cons": [i for i in fd_sect + row_sect if i in nodes.index],
        "9. exp": [i for i in fd_sect + regions if i in nodes.index],
    }

    if pos in pos_reindex:
        df = df.reindex(pos_reindex[pos])

    return (
        len(df.loc[:node]) / (len(df) + 1) * (1 - color * df.sum() / total)
        + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
    )


def Nodes(region, year, height, top_margin, bottom_margin, pad, ratio):
    nodes_path = DATA_PATH.joinpath(f"Results/Sankey_data/{region}/nodes{region}{year}.feather")
    nodes = feather.read_feather(nodes_path)

    size = height - top_margin - bottom_margin
    n = 13
    pad2 = (size - ratio * (size - (n - 1) * pad)) / (n + 1)
    white = ((n + 1) * pad2) / size
    color = 1 - white

    positions = {
        "0. ges": 0.00001,
        "1. imp reg": 0.095,
        "2. imp dom": 0.19,
        "3. pba": 0.285,
        "4. cba": 0.44,
        "5. ncf": 0.52,
        "6. endo": 0.6,
        "7. cbaK": 0.68,
        "8. cons": 0.835,
        "9. exp": 1,
    }
    nodes["x"] = nodes["position"].map(positions)
    nodes["y"] = nodes.index.map(lambda i: node_y(nodes, i, color, region))

    x_overrides = {
        "CFC imports re-exported": 0.68,
        "RoW - Negative capital formation": 0.44,
        "Negative capital formation": 0.44,
        "Footprint": 1,
    }

    for node, x_val in x_overrides.items():
        if node in nodes.index:
            nodes.loc[node, "x"] = x_val

    return nodes, pad2


def add_arrow(fig, x0, x1, y0, y1, arrowhead_width=0.009, arrowhead_length=0.007, color="black"):
    """Add a double-headed arrow shape to a Plotly figure."""

    # Arrowhead pointing to the left
    left_x = x0 + arrowhead_length
    left_y1 = y0 - arrowhead_width
    left_y2 = y0 + arrowhead_width

    # Arrowhead pointing to the right
    right_x = x1 - arrowhead_length
    right_y1 = y1 - arrowhead_width
    right_y2 = y1 + arrowhead_width

    fig.add_shape(
        type="path",
        path=f"M {left_x},{left_y1} L {x0},{y0} L {left_x},{left_y2} M {x0},{y0} L {x1},{y1} M {right_x},{right_y1} L {x1},{y1} L {right_x},{right_y2}",
        xref="paper",
        yref="paper",
        line=dict(
            color=color,
            width=2.5,  # Increased width
        ),
    )


def add_arrows_and_labels(fig, year, region, unit):
    arrow_y = 1  # y-coordinate for arrows
    arrow_text_y = 1.09  # y-coordinate for text above arrows

    totals = feather.read_feather("Results/totals.feather").loc[region].loc[year] / 1000000000
    if unit == "tCO<sub>2</sub>eq/capita":
        pop = feather.read_feather(DATA_PATH.joinpath("Data/pop.feather"))
        totals = totals / pop.loc[region].loc[year] * 1000000

    # Create a helper function to reduce repetition
    def create_arrow_text(key, label):
        value = round(totals.loc[key], 1) if unit == "tCO<sub>2</sub>eq/capita" else round(totals.loc[key])
        return [label, f"{value} {unit}"]

    arrow_info = [
        {"x0": 0.085, "x1": 0.295, "texts": create_arrow_text("pba", "Production based account (PBA)")},
        {"x0": 0.43, "x1": 0.45, "texts": create_arrow_text("cba", "Consumption based account (CBA)")},
        {
            "x0": 0.67,
            "x1": 1.002,
            "texts": create_arrow_text("cbak", "Consumption based account with capital endogenized (CBAk)"),
        },
    ]

    spacing_between_lines = 0.033  # Adjust this for gap between lines

    for arrow in arrow_info:
        add_arrow(fig, arrow["x0"], arrow["x1"], arrow_y, arrow_y)

        for i, text in enumerate(arrow["texts"]):
            fig.add_annotation(
                text=text,
                x=(arrow["x0"] + arrow["x1"]) / 2,
                y=arrow_text_y - i * spacing_between_lines,
                xref="paper",
                yref="paper",
                xanchor="center",
                showarrow=False,
                font=dict(size=12.5),
            )


def add_steps_and_legend(fig):
    x_positions = [0.00001, 0.095, 0.19, 0.285, 0.44, 0.52, 0.6, 0.68, 0.835, 1]
    labels = [
        "<br>All GHGs",
        "<br>PBA by<br>region",
        "<br>PBA by<br>region",
        "<br>PBA by<br>sector",
        "<br>CBA by final<br>demand category",
        "<br>Capital not<br>endogenized",
        "<br>Capital<br>endogenized",
        "<br>CBAk by final<br>demand category",
        "<br>CBAk by<br>sector",
        "<br>CBAk by<br>region",
    ]

    for i, x in enumerate(x_positions):
        fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=x,
                x1=x,
                y0=-0.018,
                y1=0.016,
                yref="paper",
                line=dict(color="black", dash="dot"),
            )
        )
        anchor_value = "left" if i == 0 else "right" if i == len(x_positions) - 1 else "center"
        fig.add_annotation(
            text=f"Step {i+1}: {labels[i]}",
            x=x,
            y=-0.011,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor=anchor_value,
            yanchor="top",
        )

    colors = ["white", "#0072ff", "#00cafe", "#b0ebff", "#fff1b7", "#ffdc23", "#ffb758", "#ff8200"]
    legend_names = [
        "<b>Colors by PBA sector:</b>",
        "Direct emissions",
        "Agriculture-food",
        "Energy industry",
        "Heavy industry",
        "Manufacturing industry",
        "Services",
        "Transport services",
    ]

    for i, color in enumerate(colors):
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                legendgroup=i,
                showlegend=True,
                name=legend_names[i],
            )
        )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
    )


def fig_sankey_arrows(year, region, unit):
    """Builds sankey diagram.

    Parameters
    ----------
    year : int
    region : string
    unit : string, either Mt or t/cap

    Returns
    -------
    fig : figure
    """

    # Read data

    if unit == "t/cap":
        norm = feather.read_feather(DATA_PATH.joinpath("Results/norm_cap.feather"))
        pop = feather.read_feather(DATA_PATH.joinpath("Data/pop.feather"))
        unit = "tCO<sub>2</sub>eq/capita"
    elif unit == "Mt":
        norm = feather.read_feather(DATA_PATH.joinpath("Results/norm.feather"))
        unit = "MtCO<sub>2</sub>eq"
    else:
        raise ValueError(f"Invalid unit '{unit}'")

    ratio = norm.loc[region, year]

    data_sankey_path = DATA_PATH.joinpath(f"Results/Sankey_data/{region}/data{region}{year}.feather")
    data_sankey = feather.read_feather(data_sankey_path).replace(color_dict)

    node_list_path = DATA_PATH.joinpath(f"Results/Sankey_data/{region}/nodelist{region}{year}.feather")
    node_list = feather.read_feather(node_list_path)[0].values

    # Configurations
    height, width = 480, 1100
    top_margin, bottom_margin, left_margin, right_margin, pad = 60, 0, 10, 10, 10

    nodes, pad2 = Nodes(region, year, height, top_margin, bottom_margin, pad, ratio)

    if unit == "tCO<sub>2</sub>eq/capita":
        node = {
            "label": pd.DataFrame(nodes, index=node_list)["label t/cap"].replace(REGIONS).values,
            "pad": pad2,
            "thickness": 2,
            "color": "#00005A",
            "x": nodes["x"].values,
            "y": nodes["y"].values,
        }
        link = {
            "source": data_sankey["source"],
            "target": data_sankey["target"],
            "value": data_sankey["value"] * 1000000 / pop.loc[region].loc[year],
            "label": [f"{x:.1f} " + unit for x in data_sankey["value"].astype(float)],
            "color": data_sankey["color"],
        }

    else:
        node = {
            "label": pd.DataFrame(nodes, index=node_list)["label Mt"].replace(REGIONS).values,
            "pad": pad2,
            "thickness": 2,
            "color": "#00005A",
            "x": nodes["x"].values,
            "y": nodes["y"].values,
        }
        link = {
            "source": data_sankey["source"],
            "target": data_sankey["target"],
            "value": data_sankey["value"],
            "label": [f"{x:.1f} " + unit for x in data_sankey["value"].astype(float)],
            "color": data_sankey["color"],
        }

    # Create Sankey diagram
    sankey = go.Sankey(link=link, node=node, valueformat=".0f", valuesuffix=" " + unit, hoverinfo="none")

    fig = go.Figure(sankey)

    title_text = f"<b>Greenhouse gas footprint of {REGIONS[region]} in {year} (" + unit + ")<b>"

    # Update figure layout and traces
    fig.update_layout(
        title=title_text,
        font=dict(size=10, color="black"),
        paper_bgcolor="white",
        title_x=0.5,
        title_y=0.99,
        font_family="Arial",
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=left_margin, r=right_margin, t=top_margin, b=bottom_margin),
    )

    fig.update_traces(legendrank=10)

    # Add supplementary features
    add_arrows_and_labels(fig, year, region, unit)
    add_steps_and_legend(fig)

    return fig


def save_sankey():
    if not os.path.exists("Results/Sankey_figs"):
        os.mkdir("Results/Sankey_figs")
    if not os.path.exists("Results/Sankey_figs/MtCO2eq"):
        os.mkdir("Results/Sankey_figs/MtCO2eq")
    if not os.path.exists("Results/Sankey_figs/tCO2eq_per_capita"):
        os.mkdir("Results/Sankey_figs/tCO2eq_per_capita")
    for unit in ["Mt", "t/cap"]:
        for region in pd.read_excel("Data/regions.xlsx", index_col=0).sort_values(by="full name").index:
            for year in range(1995, 2020, 1):
                fig = fig_sankey_arrows(year, region, unit)

                if unit == "Mt":
                    if not os.path.exists("Results/Sankey_figs/MtCO2eq/" + REGIONS[region]):
                        os.mkdir("Results/Sankey_figs/MtCO2eq/" + REGIONS[region])
                    fig.write_image(
                        "Results/Sankey_figs/MtCO2eq/"
                        + REGIONS[region]
                        + "/sankey_Mt_"
                        + region
                        + "_"
                        + str(year)
                        + ".svg",
                        engine="orca",
                    )

                if unit == "t/cap":
                    if not os.path.exists("Results/Sankey_figs/tCO2eq_per_capita/" + REGIONS[region]):
                        os.mkdir("Results/Sankey_figs/tCO2eq_per_capita/" + REGIONS[region])
                    fig.write_image(
                        "Results/Sankey_figs/tCO2eq_per_capita/"
                        + REGIONS[region]
                        + "/sankey_tCO2eq_per_capita_"
                        + region
                        + "_"
                        + str(year)
                        + ".svg",
                        engine="orca",
                    )


def figpaper(year, region, unit):
    """Builds sankey diagram.

    Parameters
    ----------
    year : int
    region : string
    unit : string, either Mt or t/cap

    Returns
    -------
    fig : figure
    """

    # Read data

    if unit == "t/cap":
        norm = feather.read_feather(DATA_PATH.joinpath("Results/norm_cap.feather"))
        pop = feather.read_feather(DATA_PATH.joinpath("Data/pop.feather"))
        unit = "tCO<sub>2</sub>eq/capita"
    elif unit == "Mt":
        norm = feather.read_feather(DATA_PATH.joinpath("Results/norm.feather"))
        unit = "MtCO<sub>2</sub>eq"
    else:
        raise ValueError(f"Invalid unit '{unit}'")

    ratio = norm.loc[region, year]

    data_sankey_path = DATA_PATH.joinpath(f"Results/Sankey_data/{region}/data{region}{year}.feather")
    data_sankey = feather.read_feather(data_sankey_path).replace(color_dict)

    node_list_path = DATA_PATH.joinpath(f"Results/Sankey_data/{region}/nodelist{region}{year}.feather")
    node_list = feather.read_feather(node_list_path)[0].values

    # Configurations
    height, width = 480, 1100
    top_margin, bottom_margin, left_margin, right_margin, pad = 15, 0, 10, 10, 10

    nodes, pad2 = Nodes(region, year, height, top_margin, bottom_margin, pad, ratio)

    if unit == "tCO<sub>2</sub>eq/capita":
        node = {
            "label": pd.DataFrame(nodes, index=node_list)["label t/cap"].replace(REGIONS).values,
            "pad": pad2,
            "thickness": 2,
            "color": "#00005A",
            "x": nodes["x"].values,
            "y": nodes["y"].values,
        }
        link = {
            "source": data_sankey["source"],
            "target": data_sankey["target"],
            "value": data_sankey["value"] * 1000000 / pop.loc[region].loc[year],
            "label": [f"{x:.1f} " + unit for x in data_sankey["value"].astype(float)],
            "color": data_sankey["color"],
        }

    else:
        node = {
            "label": pd.DataFrame(nodes, index=node_list)["label Mt"].replace(REGIONS).values,
            "pad": pad2,
            "thickness": 2,
            "color": "#00005A",
            "x": nodes["x"].values,
            "y": nodes["y"].values,
        }
        link = {
            "source": data_sankey["source"],
            "target": data_sankey["target"],
            "value": data_sankey["value"],
            "label": [f"{x:.1f} " + unit for x in data_sankey["value"].astype(float)],
            "color": data_sankey["color"],
        }

    # Create Sankey diagram
    sankey = go.Sankey(link=link, node=node, valueformat=".0f", valuesuffix=" " + unit, hoverinfo="none")

    fig = go.Figure(sankey)

    title_text = f"<b>Greenhouse gas footprint of {REGIONS[region]} in {year} (" + unit + ")<b>"

    # Update figure layout and traces
    fig.update_layout(
        title=title_text,
        font=dict(size=10, color="black"),
        paper_bgcolor="white",
        title_x=0.5,
        title_y=0.99,
        font_family="Arial",
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=left_margin, r=right_margin, t=top_margin, b=bottom_margin),
    )

    fig.update_traces(legendrank=10)

    # Add supplementary features
    # add_arrows_and_labels(fig, year, region, unit)
    # add_steps_and_legend(fig)
    fig.write_image(
        "fig_paper/" + region + "_" + str(year) + unit[:1] + "_.svg",
        engine="orca",
    )

    return figpaper


# figpaper(2019, "AU", "t/cap")
# figpaper(2019, "BR", "t/cap")
# figpaper(2019, "CY", "t/cap")
# figpaper(1995, "RU", "Mt")
# figpaper(1995, "CN", "Mt")

# fig_sankey_arrows(1995, "FR", "t/cap")
