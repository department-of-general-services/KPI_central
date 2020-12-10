import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def fmd_line_plot(
    df,
    title,
    xlabel="Calendar Month",
    ylabel="Count of CMs Requested",
    yaxis_freq=25,
    x="calendar_month",
    y="percent_ontime",
    ymax=105,
    hue=None,
):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f"{title}", fontsize=18)

    format = mdates.DateFormatter("%b-%Y")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(format)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(yaxis_freq))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:,.0f}"))
    if hue:
        sns.lineplot(
            data=df,
            x=x,
            y=y,
            marker="o",
            color="red",
            ax=ax,
            hue=hue,
            palette="colorblind",
        )
    else:
        sns.lineplot(
            data=df, x=x, y=y, marker="o", color="red", ax=ax,
        )

    ax.set_xlabel(xlabel, size=14)
    ax.set_ylabel(ylabel, size=14)
    _ = ax.set(ylim=(0, ymax))
    _ = ax.set(
        xlim=(min(df[x]) - np.timedelta64(1, "M"), max(df[x]) + np.timedelta64(1, "M"))
    )

    for year in [2018, 2019, 2020, 2021]:
        for month in range(1, 13, 1):
            if month == 7:
                plt.axvline(
                    pd.Timestamp(f"{month}-01-{year}"),
                    linestyle="--",
                    alpha=0.5,
                    color="grey",
                )
            if month in (1, 4, 10):
                plt.axvline(
                    pd.Timestamp(f"{month}-01-{year}"),
                    linestyle="--",
                    alpha=0.15,
                    color="grey",
                )

    for point in [t for t in range(0, ymax) if t % yaxis_freq == 0]:
        plt.axhline(point, linestyle="--", alpha=0.25, color="grey")

    sns.despine()
    plt.show()
