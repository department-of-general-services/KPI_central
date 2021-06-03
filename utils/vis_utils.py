# import pyodbc  # for accessing the database directly
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
from pathlib import Path


def set_plot_params():
    """
    Sets default plotting options.
    Args:
        None
    Returns:
        None
    """
    sns.set_style("whitegrid", {"grid.linestyle": "--"})

    params = {
        "legend.fontsize": "large",
        "figure.figsize": (16, 6),
        "axes.labelsize": 16,
        "axes.labelweight": "regular",
        "axes.labelpad": 10.0,
        "axes.titlesize": 22,
        "axes.titleweight": "bold",
        "axes.titlepad": 15.0,
        "xtick.labelsize": "large",
        "ytick.labelsize": "large",
    }

    plt.rcParams.update(params)
    return


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker


def pointplot_with_barplot(
    data,
    x,
    point_y,
    bar_y,
    title,
    yaxis_freq_bar=25,
    yaxis_freq_point=50,
    ymax_point=105,
    ymax_bar=None,
    ylabel_point="",
    ylabel_bar="",
    xlabel="Fiscal Year",
    yticklabels=None,
    interval=4,
):
    data = data.copy()
    sns.set_style("white")

    ax1 = sns.barplot(data=data, x=x, y=bar_y, color="lightgrey", alpha=0.5)

    ax1.grid(False)
    if ymax_bar is None:
        ymax_bar = max(data[bar_y]) + (max(data[bar_y]) * 0.33)
    _ = ax1.set(ylim=(0, ymax_bar), xlabel=xlabel, ylabel=ylabel_bar)

    format = mdates.DateFormatter("%b-%y")
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    ax1.xaxis.set_major_formatter(format)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(yaxis_freq_bar))

    ax2 = ax1.twinx()
    ax2 = sns.pointplot(
        data=data,
        x=x,
        y=point_y,
        color="indianred",
    )
    ax2.set(title=title, ylabel=ylabel_point, ylim=(0, ymax_point))

    for point in [t for t in range(0, ymax_point) if t % yaxis_freq_point == 0]:
        plt.axhline(point, linestyle="--", alpha=0.25, color="grey")

    ax2.yaxis.set_major_locator(ticker.MultipleLocator(yaxis_freq_point))
    if yticklabels:
        ax2.set_yticklabels(yticklabels)

    ax2.yaxis.set_label_position("left")
    ax2.yaxis.tick_left()
    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()

    sns.despine()
    plt.show()


def simple_lineplot_from_df(
    df,
    title,
    x_label,
    y_label,
    yaxis_freq=25,
    x="calendar_month",
    y="percent_ontime",
    ymax=105,
    legend_labels=None,
    legend_anchor=(0, 0),
    xtup=None,
    interval=4,
):
    df = df.copy()
    sns.set_style("white")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    format = mdates.DateFormatter("%b-%y")
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    ax1.xaxis.set_major_formatter(format)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(yaxis_freq))

    ax1 = sns.lineplot(
        data=df,
        x=x,
        y=y,
    )

    ax1.axes.set_title(title, fontsize=22)
    ax1.set_xlabel(x_label, fontsize=18)
    ax1.set_ylabel(y_label, fontsize=18)
    ax1.xaxis.labelpad = 20

    _ = ax1.set(ylim=(0, ymax))

    if xtup is not None:

        _ = ax1.set(xlim=xtup)

    for year in df.index.year.unique():
        plt.axvline(
            pd.Timestamp(f"07-01-{year}"), linestyle="--", alpha=0.5, color="grey"
        )

    for point in [t for t in range(0, ymax) if t % yaxis_freq == 0]:
        plt.axhline(point, linestyle="--", alpha=0.25, color="grey")

    sns.despine()
    plt.show()


def set_plot_params(width, height):
    """
    Sets default plotting options.
    Args:
        None
    Returns:
        None
    """
    sns.set_style("whitegrid", {"grid.linestyle": "--"})

    params = {
        "legend.fontsize": "large",
        "figure.figsize": (width, height),
        "axes.labelsize": 18,
        "axes.labelweight": "regular",
        "axes.labelpad": 10.0,
        "axes.titlesize": 22,
        "axes.titleweight": "bold",
        "axes.titlepad": 15.0,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    }

    plt.rcParams.update(params)
    return