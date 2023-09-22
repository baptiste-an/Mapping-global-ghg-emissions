import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np

df19 = pd.read_excel("datapaper.xlsx", index_col=[0, 1]).xs(2019, level=1).drop("World")

# Compute rankings for each method
df19["CB Rank"] = df19["CB total"].rank(ascending=False)
df19["CBk Rank"] = df19["CBk total"].rank(ascending=False)
df19["PB Rank"] = df19["PB"].rank(ascending=False)

# Extract the rank columns for visualization
df_rank = df19[["PB Rank", "CB Rank", "CBk Rank"]]
df_rank = df_rank.sort_values(by="PB Rank")


plt.figure(figsize=(11, 18))
pe = [path_effects.Stroke(linewidth=1, foreground="black"), path_effects.Normal()]


annot_array = df_rank.copy()

for col in df_rank.columns:
    value_col = col.split(" ")[0]
    if value_col != "PB":
        value_col += " total"

    for idx in df_rank.index:
        rank_val = df_rank.at[idx, col]
        footprint_val = df19.at[idx, value_col]
        annot_array.at[idx, col] = f"{rank_val:.0f} ({footprint_val:.1f} )"


# Create the heatmap WITHOUT a colorbar
ax = sns.heatmap(
    df_rank,
    cmap="viridis",
    annot=annot_array,
    fmt="s",
    linewidths=0.5,
    annot_kws={"color": "white", "path_effects": pe, "size": 17},
    cbar=False,
)


# Create a custom colorbar with a specific width
from mpl_toolkits.axes_grid1 import make_axes_locatable

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
cbar = plt.colorbar(ax.get_children()[0], cax=cax)
cbar.ax.tick_params(labelsize=16)


# plt.title('Region Rankings by Different Methods')

# cbar = ax.collections[0].colorbar


# Increase size of axis labels and title
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_xticklabels(ax.get_xticklabels(), fontsize=14)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=14)

plt.tight_layout()

plt.savefig("heatmap.svg")
plt.savefig("heatmap.png")
plt.savefig("heatmap.pdf")
plt.show()
