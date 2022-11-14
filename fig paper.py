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
from general_functions import *

df = pd.read_excel("regions.xlsx")
dictreg = dict(zip(df["region"], df["full name"]))

if not os.path.exists("Sankeys"):
    os.mkdir("Sankeys")
pio.orca.config.executable = "C:/Users/andrieba/anaconda3/pkgs/plotly-orca-1.2.1-1/orca_app/orca.exe"
pio.orca.config.save()
pio.kaleido.scope.mathjax = None  # ne sert à rien car mathjax ne fonctionne pas
pyo.init_notebook_mode()

pathexio = "Data/"


plt_rcParams()


def data_table():
    data = pd.DataFrame()
    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"

        Yk = feather.read_feather(pathIOT + "Yk.feather").unstack()
        Yk.index.names = ["region cons", "sector cons"]
        L = feather.read_feather(pathIOT + "L.feather")
        L.columns.names = ["region cons", "sector cons"]
        L.index.names = ["region prod", "sector prod"]
        Lk = feather.read_feather(pathIOT + "Lk.feather")
        Lk.columns.names = ["region cons", "sector cons"]
        Lk.index.names = ["region prod", "sector prod"]

        S_imp = pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
        S_imp.index.names = ["region prod", "sector prod"]

        SL = L.mul(S_imp, axis=0).sum()
        SL.index.names = ["region cons", "sector cons"]
        SLY = Yk.mul(SL, axis=0).sum().unstack()

        SLk = Lk.mul(S_imp, axis=0).sum()
        SLk.index.names = ["region cons", "sector cons"]
        SLkY = Yk.mul(SLk, axis=0).sum().unstack()

        D_pba = (
            pd.read_csv(
                pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/D_pba.txt",
                delimiter="\t",
                header=[0, 1],
                index_col=[0],
            )
            .loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
            .groupby(level="region")
            .sum()
        )
        D_pba.index.names = ["region cons"]

        F_hh = (
            pd.read_csv(
                pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/F_Y.txt",
                delimiter="\t",
                header=[0, 1],
                index_col=[0],
            )
            .loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
            .groupby(level="region")
            .sum()
        )
        F_hh.index.names = ["region cons"]

        df = pd.DataFrame()
        df["pba"] = D_pba + F_hh
        df["cba"] = SLY.loc[["CFC", "Government", "Households", "NCF", "NPISHS"]].sum() + F_hh
        df["cbaK with NCF"] = SLkY.loc[["Government", "Households", "NPISHS", "NCF"]].sum() + F_hh
        df["cbaK without NCF"] = SLkY.loc[["Government", "Households", "NPISHS"]].sum() + F_hh

        df.loc["World"] = df.sum()
        pop = feather.read_feather("pop.feather")[i]
        pop.loc["World"] = pop.sum()
        df = df.div(pop, axis=0)
        df = df.sort_values(by="pba")

        data[i] = df.unstack()
    feather.write_feather(data, "data_table.feather")
    return data


data_t = feather.read_feather("data_table.feather").unstack(level=0) / 1000


def data():
    data = pd.DataFrame()
    for i in range(1995, 2020, 1):
        pathIOT = pathexio + "EXIO3/IOT_" + str(i) + "_pxp/"

        Yk = feather.read_feather(pathIOT + "Yk.feather").unstack()
        Yk.index.names = ["region cons", "sector cons"]
        L = feather.read_feather(pathIOT + "L.feather")
        L.columns.names = ["region cons", "sector cons"]
        L.index.names = ["region prod", "sector prod"]
        Lk = feather.read_feather(pathIOT + "Lk.feather")
        Lk.columns.names = ["region cons", "sector cons"]
        Lk.index.names = ["region prod", "sector prod"]

        S_imp = pd.read_csv(
            pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/S.txt",
            delimiter="\t",
            header=[0, 1],
            index_col=[0],
        ).loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
        S_imp.index.names = ["region prod", "sector prod"]

        SL = L.mul(S_imp, axis=0).sum()
        SL.index.names = ["region cons", "sector cons"]
        SLY = Yk.mul(SL, axis=0).sum().unstack()

        SLk = Lk.mul(S_imp, axis=0).sum()
        SLk.index.names = ["region cons", "sector cons"]
        SLkY = Yk.mul(SLk, axis=0).sum().unstack()

        D_pba = (
            pd.read_csv(
                pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/D_pba.txt",
                delimiter="\t",
                header=[0, 1],
                index_col=[0],
            )
            .loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
            .groupby(level="region")
            .sum()
        )
        D_pba.index.names = ["region cons"]

        F_hh = (
            pd.read_csv(
                pathexio + "EXIO3/IOT_" + str(i) + "_pxp/impacts/F_hh.txt",
                delimiter="\t",
                header=[0, 1],
                index_col=[0],
            )
            .loc["GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"]
            .groupby(level="region")
            .sum()
        )
        F_hh.index.names = ["region cons"]

        df = pd.DataFrame()
        df["pba"] = D_pba + F_hh
        df["cba"] = SLY.loc[["CFC", "Government", "Households", "NCF", "NPISHS"]].sum() + F_hh
        df["cbaK"] = SLkY.loc[["Government", "Households", "NPISHS"]].sum() + F_hh
        df["cba hh direct"] = SLY.loc["Households"] + F_hh
        df["cbaK hh direct"] = SLkY.loc["Households"] + F_hh
        df["cba hh"] = SLY.loc["Households"]
        df["cbaK hh"] = SLkY.loc["Households"]
        df.loc["World"] = df.sum()
        pop = feather.read_feather("pop.feather")[i]
        pop.loc["World"] = pop.sum()
        df = df.div(pop, axis=0)
        df = df.sort_values(by="pba")

        data[i] = df.unstack()
    feather.write_feather(data, "data.feather")
    return data


data = feather.read_feather("data.feather")
# pba, cba, cbaK, cbaK without NCF !!!!!!!!!!!!!!!!!!!!!!!

# for i in data.swaplevel().unstack().index:
#     df = data.swaplevel().unstack().loc[i].unstack().T
#     fig, axes = plt.subplots(1, figsize=(5, 5))
#     axes.plot(df.div(df[1995], axis=0).T)


# for i in data.swaplevel().unstack().index:
#     df = data.swaplevel().unstack().loc[i].unstack().T
#     fig, axes = plt.subplots(1, figsize=(5, 5))
#     axes.plot(df.div(df.loc["cba"], axis=1).T)

# Vendredi matin
# pop 2019
# hh from IPCC
# ajouter Net capital formation pour calcul noeuds RoW (exemple CN cap 1995)


# # Il faut dire quelque chose de la proportionnalité entre pays
# # Par exemple comparer cbaK hh et cba China US, il y a un facteur 2
# # Ca mais pas satisfaisant :

fig, axes = plt.subplots(1, figsize=(10, 15))
k = 0
dictcol = {
    "pba": "white",
    "cba": "black",
    "cbaK": "red",
    "cba hh direct": "green",
    "cbaK hh direct": "orange",
    "cba hh": "gray",
    "cbaK hh": "pink",
}
df = data[2019].unstack().T
for i in df.index[:-1]:
    plt.vlines(x=df.loc[i].loc["pba"], ymin=k, ymax=k + 6, axes=axes)
    axes.annotate(i, xy=(df.loc[i].loc["pba"], k - 3))
    for j in df.columns:
        axes.scatter(df[j].loc[i], k, color=dictcol[j])
        plt.hlines(
            y=k,
            xmin=min(df.loc[i].loc["pba"], df[j].loc[i]),
            xmax=max(df.loc[i].loc["pba"], df[j].loc[i]),
            linewidth=0.5,
            ls="dashed",
            color=dictcol[j],
        )
        k += 1
    k += 1


fig, axes = plt.subplots(1, figsize=(10, 15))
k = 0
dictcol = {
    "pba": "white",
    "cba": "black",
    "cbaK": "red",
    "cba hh direct": "green",
    "cbaK hh direct": "orange",
    "cba hh": "gray",
    "cbaK hh": "pink",
}
df = data[1995].unstack().T.sort_values(by="cba")
for i in df.index[:-1]:
    plt.vlines(x=df.loc[i].loc["cba"], ymin=k, ymax=k, axes=axes)
    axes.annotate(i, xy=(df.loc[i].loc["cba"], k))
    for j in ["cbaK"]:
        axes.scatter(df[j].loc[i], k, color=dictcol[j])
        plt.hlines(
            y=k,
            xmin=min(df.loc[i].loc["cba"], df[j].loc[i]),
            xmax=max(df.loc[i].loc["cba"], df[j].loc[i]),
            linewidth=0.5,
            ls="dashed",
            color=dictcol[j],
        )
        k += 1
    k += 1


fig, axes = plt.subplots(1, figsize=(10, 15))
k = 0
dictcol = {
    "pba": "white",
    "cba": "black",
    "cbaK": "red",
    "cba hh direct": "green",
    "cbaK hh direct": "orange",
    "cba hh": "gray",
    "cbaK hh": "pink",
}
df = data[1995].unstack().T.sort_values(by="cba")
for i in df.index[:-1]:
    plt.vlines(x=df.loc[i].loc["cba"], ymin=k, ymax=k, axes=axes)
    axes.annotate(i, xy=(df.loc[i].loc["cba"], k))
    for j in ["cbaK"]:
        axes.scatter(df[j].loc[i], k, color=dictcol[j])
        plt.hlines(
            y=k,
            xmin=min(df.loc[i].loc["cba"], df[j].loc[i]),
            xmax=max(df.loc[i].loc["cba"], df[j].loc[i]),
            linewidth=0.5,
            ls="dashed",
            color=dictcol[j],
        )
        k += 1
    k += 1
