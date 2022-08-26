import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.core.reshape.merge import merge
from pandas.io.pytables import Fixed
from matplotlib import colors as mcolors, rc_params
import seaborn as sns
import plotly.offline as pyo
import plotly.graph_objs as go

from dash import html, dcc, Output, Input, State, callback, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import uuid


class PlaybackSliderAIO(html.Div):
    class ids:
        play = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "button",
            "aio_id": aio_id,
        }
        play_icon = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "i",
            "aio_id": aio_id,
        }
        slider = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "slider",
            "aio_id": aio_id,
        }
        interval = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "interval",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self, button_props=None, slider_props=None, interval_props=None, aio_id=None
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        button_props = button_props.copy() if button_props else {}
        slider_props = slider_props.copy() if slider_props else {}
        interval_props = interval_props.copy() if interval_props else {}

        button_props["active"] = False

        super().__init__(
            [
                dbc.Button(
                    html.I(id=self.ids.play_icon(aio_id)),
                    id=self.ids.play(aio_id),
                    **button_props
                ),
                dcc.Slider(id=self.ids.slider(aio_id), **slider_props),
                dcc.Interval(id=self.ids.interval(aio_id), **interval_props),
            ]
        )

    @callback(
        Output(ids.play(MATCH), "active"),
        Output(ids.play_icon(MATCH), "className"),
        Output(ids.interval(MATCH), "disabled"),
        Input(ids.play(MATCH), "n_clicks"),
        State(ids.play(MATCH), "active"),
    )
    def toggle_play(clicks, curr_status):
        if clicks:
            text = "fa-solid fa-play" if curr_status else "fa-solid fa-pause"
            return not curr_status, text, curr_status
        return curr_status, "fa-solid fa-play", not curr_status

    @callback(
        Output(ids.slider(MATCH), "value"),
        Input(ids.play(MATCH), "active"),
        Input(ids.interval(MATCH), "n_intervals"),
        State(ids.slider(MATCH), "min"),
        State(ids.slider(MATCH), "max"),
        State(ids.slider(MATCH), "step"),
        State(ids.slider(MATCH), "value"),
    )
    def start_playback(play, interval, min, max, step, value):
        if not play:
            raise PreventUpdate

        new_val = value + step
        if new_val > max:
            new_val = min

        return new_val


from dash import Dash, html, callback, Output, Input, dcc
import dash_bootstrap_components as dbc

df = pd.read_excel("regions.xlsx")
dictreg = dict(zip(df["region"], df["full name"]))
norm = pd.read_csv("norm.csv", index_col=0)


app = Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
)
server = app.server

app.layout = html.Div(
    [
        # html.H4(""),
        # html.P("region"),
        dcc.Dropdown(
            id="slct",
            # options=[dict(zip(df['region'],df['full name']))],
            options=[
                {"label": "Australia", "value": "AU"},
                {"label": "Austria", "value": "AT"},
                {"label": "Belgium", "value": "BE"},
                {"label": "Brazil", "value": "BR"},
                {"label": "Bulgaria", "value": "BG"},
                {"label": "Canada", "value": "CA"},
                {"label": "China", "value": "CN"},
                {"label": "Croatia", "value": "HR"},
                {"label": "Cyprus", "value": "CY"},
                {"label": "Czech Republic", "value": "CZ"},
                {"label": "Denmark", "value": "DK"},
                {"label": "Estonia", "value": "EE"},
                {"label": "Finland", "value": "FI"},
                {"label": "France", "value": "FR"},
                {"label": "Germany", "value": "DE"},
                {"label": "Great Britain", "value": "GB"},
                {"label": "Greece", "value": "GR"},
                {"label": "Hungary", "value": "HU"},
                {"label": "India", "value": "IN"},
                {"label": "Indonesia", "value": "ID"},
                {"label": "Ireland", "value": "IE"},
                {"label": "Italy", "value": "IT"},
                {"label": "Japan", "value": "JP"},
                {"label": "Latvia", "value": "LV"},
                {"label": "Lithuania", "value": "LT"},
                {"label": "Luxembourg", "value": "LU"},
                {"label": "Malta", "value": "MT"},
                {"label": "Mexico", "value": "MX"},
                {"label": "Netherlands", "value": "NL"},
                {"label": "Norway", "value": "NO"},
                {"label": "Poland", "value": "PL"},
                {"label": "Portugal", "value": "PT"},
                {"label": "Romania", "value": "RO"},
                {"label": "Russia", "value": "RU"},
                {"label": "Slovakia", "value": "SK"},
                {"label": "Slovenia", "value": "SI"},
                {"label": "South Africa", "value": "ZA"},
                {"label": "South Korea", "value": "KR"},
                {"label": "Spain", "value": "ES"},
                {"label": "Sweden", "value": "SE"},
                {"label": "Switzerland", "value": "CH"},
                {"label": "Taiwan", "value": "TW"},
                {"label": "Turkey", "value": "TR"},
                {"label": "United States", "value": "US"},
                {"label": "RoW Africa", "value": "WF"},
                {"label": "RoW America", "value": "WL"},
                {"label": "RoW Asia and Pacific", "value": "WA"},
                {"label": "RoW Europe", "value": "WE"},
                {"label": "RoW Middle East", "value": "WM"},
            ],
            multi=False,
            value="CN",
            style={"width": "40%"},
        ),
        dcc.Graph(id="graph"),
        # html.P("year"),
        PlaybackSliderAIO(
            aio_id="bruh",
            slider_props={
                "min": 1995,
                "max": 2019,
                "step": 1,
                "value": 1995,
                "marks": {str(year): str(year) for year in range(1995, 2020, 1)},
            },
            button_props={"className": "float-left"},
            interval_props={"interval": 2000},
        ),
        # html.Div(id="text"),
    ]
)


@app.callback(
    Output("graph", "figure"),
    # Output("text", "children"),
    Input(PlaybackSliderAIO.ids.slider("bruh"), "value"),
    Input("slct", "value"),
)
def fig_sankey(year, region):

    height = 450
    width = 1100
    top_margin = 50
    bottom_margin = 0
    left_margin = 50
    right_margin = 50
    pad = 10

    nodes = pd.read_csv(
        "Sankeys/" + region + "/nodes" + region + str(year) + ".txt", index_col=0
    )

    def node_y(node, white, color):
        pos = nodes["position"].loc[node]
        df = nodes.reset_index().set_index(["position", "index"]).loc[pos]["value"]
        total = nodes.reset_index().set_index("position").loc["0. ges"]["value"].sum()
        if pos == "0. ges":
            df = df.reindex(["CO2", "CH4", "N2O", "SF6"])
        elif pos == "1. imp region":
            df = df.reindex(
                pd.Index([region]).union(
                    df.index.sort_values().drop(region), sort=False
                )
            )
        elif pos == "2. imp/dom":
            df = df.sort_values(ascending=False)
        elif pos == "3. primaire":
            df = df.reindex(
                pd.Index([region + " - Households"])
                .union(
                    df.loc[df.index.str[:2] == region].index.drop(
                        region + " - Households"
                    ),
                    sort=False,
                )
                .union(df.loc[df.index.str[:2] != region].index, sort=False)
            )
        elif pos == "4. cap/ci":
            df = df.reindex(["Households ", "Intermediate cons", "Capital formation"])
        elif pos == "5. depenses":
            df = df.reindex(
                [
                    "Households direct emissions",
                    "Households",
                    "Government",
                    "Other",
                    "Exportations",
                ]
            )
            #############!!!!!Exports
        elif pos == "6. exp region":
            df = df.reindex(
                [
                    "Transport",
                    "Logement",
                    "Nourriture",
                    "Autres biens et services",
                    "Divertissements",
                    "Textiles",
                    "Education",
                    "Santé",
                    "Africa ",
                    "Asia ",
                    "Europe ",
                    "Middle East ",
                    "North America ",
                    "Oceania ",
                    "South America ",
                ]
            )
        return (
            len(df.loc[:node]) / (len(df) + 1) * white
            + (df.loc[:node][:-1].sum() + df.loc[node] / 2) / total * color
        )

    data_sankey = pd.read_csv(
        "Sankeys/" + region + "/data" + region + str(year) + ".txt", index_col=0
    )

    ratio = norm.loc[region].loc[str(year)]

    size = height - top_margin - bottom_margin
    n = len(nodes.reset_index().set_index("position").loc["6. exp region"])
    pad2 = (size - ratio * (size - n * pad)) / (n)
    color = (size - (n) * pad2) / size
    white = ((n) * pad2) / size

    nodes = nodes.assign(
        x=lambda d: d["position"].replace(
            dict(
                zip(
                    [
                        "0. ges",
                        "1. imp region",
                        "2. imp/dom",
                        "3. primaire",
                        "4. cap/ci",
                        "5. depenses",
                        "6. exp region",
                        "tbd",
                    ],
                    ([0.001, 0.09, 0.20, 0.34, 0.58, 0.75, 0.88, 0.999]),
                )
            )
        ),
        y=lambda d: [node_y(i, white, color) for i in d.index],
    )

    nodes["x"].loc["Other"] = 0.75
    nodes["x"].loc[
        "Transport",
        "Logement",
        "Nourriture",
        "Autres biens et services",
        "Divertissements",
        "Textiles",
        "Education",
        "Santé",
    ] = (
        1 - 0.001
    )

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
        "label": nodes["label"].replace(dictreg),
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
        title="Greenhouse gas footprint of "
        + dictreg[region]
        + " in "
        + str(year)
        + " (Mt CO2eq)",
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
    return fig
    # fig.write_image("SankeyFR" + str(year) + ".pdf", engine="orca")
    # fig.write_image("SankeyFR" + str(year) + ".svg", engine="orca")


# app.run_server(debug=False)

if __name__ == "__main__":
    app.run_server(debug=False)
