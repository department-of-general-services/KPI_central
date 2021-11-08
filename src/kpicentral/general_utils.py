import pandas as pd
import numpy as np
from datetime import datetime
import re

INT_COLS = [
    "wr_id",
    "fy_request",
    "fy_complete",
    "fy_close",
    "days_since_request",
    "weekdays_complete_to_close",
    "weekdays_since_completion",
    "completion_benchmark",
    "closure_benchmark",
]
BOOL_COLS = [
    "is_vendor_work",
    "not_completed_but_late",
    "not_closed_but_late",
    "is_on_time",
    "closed_on_time",
    "is_ratio_pm",
    "is_ratio_cm",
    "is_any_pm",
]


def set_pd_params():
    """
    Sets default Pandas options.

    Args:
        None
    Returns:
        None
    """
    pd.set_option("display.max_columns", 200)
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.min_rows", 100)
    pd.set_option("display.expand_frame_repr", True)
    return


def tidy_up_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(mapper={"prob_type": "problem_type"}, axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.dropna(subset=["wr_id", "problem_type"])
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.applymap(lambda x: np.nan if x == "NULL" else x)
    df["supervisor"] = df["supervisor"].apply(lambda x: "NULL" if x != x else x)
    cond_valid = ~df["problem_type"].str.contains("TEST")
    df = df[cond_valid]
    df["status"] = df["status"].replace("A", "AA", regex=False)
    return df


def clean_up_colnames(df_raw: pd.DataFrame, return_cols: list = None) -> pd.DataFrame:
    """Cleans a dataframe by standardizing column names, stripping
    whitespaces around string values, dropping rows with missing data
    (for certain cols)
    Args:
        df_raw (dataframe): Input dataframe
        na_cols (list): List of cols to check for missing values
        return_cols (list): List of cols to return, default returns all cols
    Returns:
        df (dataframe): Clean dataframe
    """
    # make a copy of the columns to return
    if return_cols:
        df = df_raw[return_cols].copy()
    else:
        df = df_raw.copy()
    # standardize col names
    df.columns = [col.strip() for col in df.columns]
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    df.columns = [col.replace("(", "") for col in df.columns]
    df.columns = [col.replace(")", "") for col in df.columns]
    df.columns = [col.replace("/", "_") for col in df.columns]
    # check for double underscores
    df.columns = [col.replace("__", "_") for col in df.columns]
    for colname in df.columns:
        if colname.startswith("unnamed"):
            df = df.drop(columns=[colname])
    return df


def cast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[INT_COLS] = df[INT_COLS].astype(float).astype("Int64")
    df[BOOL_COLS] = df[BOOL_COLS].astype(bool)
    df = df.replace("NULL", np.nan)
    df["supervisor"] = df["supervisor"].replace(np.nan, "NULL")
    return df


def drop_dupes(df: pd.DataFrame) -> pd.DataFrame:
    cond_1 = df["cf_notes"].str.contains(r"duplicate", re.IGNORECASE)
    cond_2 = df["status"].isin(["Can", "Clo", "R"])
    dupes = df[cond_1 & cond_2]
    df_deduped = df[~df["wr_id"].isin(dupes["wr_id"])]
    return df_deduped


def compute_pm_cm(df, grouping_var: str = "fy_complete"):
    df = df.copy().sort_values(grouping_var)
    results_df = pd.DataFrame(
        columns=[
            "pm_cm_ratio",
            "percent_pm",
            "count_cm",
            "count_pm",
            "count_hvac",
            grouping_var,
        ]
    )
    for fiscal_year in df[grouping_var].unique():
        print(fiscal_year)
        if pd.isna(fiscal_year):
            continue
        results_dict = {}
        df_fy = df[df[grouping_var] == fiscal_year]
        cond_pm = df_fy["is_pm"] is True
        count_pm = len(df_fy[cond_pm])
        count_hvac = len(df_fy)
        count_cm = count_hvac - count_pm
        results_dict[grouping_var] = fiscal_year
        results_dict["percent_pm"] = (count_pm / count_cm) * 100
        results_dict["pm_cm_ratio"] = f"{round((count_pm / count_cm), 2)}:1"
        results_dict["count_pm"] = count_pm
        results_dict["count_cm"] = count_cm
        results_dict["count_hvac"] = count_hvac
        results_df = results_df.append(results_dict, ignore_index=True)
    results_df[[grouping_var, "count_cm", "count_pm", "count_hvac"]] = results_df[
        [grouping_var, "count_cm", "count_pm", "count_hvac"]
    ].astype(int)
    return results_df.round(2)


def compute_kpi_table(
    df: pd.DataFrame,
    label_for_KPI: str,
    label_for_totals: str,
    grouping_var="fy_complete",
):
    df = df.copy()
    table_df = df.groupby(grouping_var)[["is_on_time"]].agg(["mean", "count"])
    table_df.columns = table_df.columns.droplevel(0)
    table_df["mean"] = table_df["mean"].apply(lambda x: round(x * 100, 2))
    table_df = table_df.rename(
        columns={"mean": label_for_KPI, "count": label_for_totals}
    )
    return table_df


def compute_pm_cm_by_month(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    df = df.copy().sort_values("date_closed")
    today = datetime.today()
    cond_current_fy = df["fy_complete"] == today.year
    cond_last_month = df["date_completed"] < end_date
    df = df[cond_current_fy & cond_last_month]
    df["year_month"] = df["date_completed"].dt.strftime("%b-%y")
    results_df = pd.DataFrame(
        columns=[
            "year_month",
            "pm_cm_ratio",
            "count_cm",
            "count_pm",
            "count_hvac",
        ]
    )
    for year_month in df["year_month"].unique():
        results_dict = {}
        df_ym = df[df["year_month"] == year_month]
        cond_pm = df_ym["is_pm"] is True
        count_pm = len(df_ym[cond_pm])
        count_hvac = len(df_ym)
        count_cm = count_hvac - count_pm
        results_dict["year_month"] = year_month
        results_dict["pm_cm_ratio"] = (count_pm / count_cm) * 100
        results_dict["count_pm"] = count_pm
        results_dict["count_cm"] = count_cm
        results_dict["count_hvac"] = count_hvac
        results_df = results_df.append(results_dict, ignore_index=True)
    results_df[["count_cm", "count_pm", "count_hvac"]] = results_df[
        ["count_cm", "count_pm", "count_hvac"]
    ].astype(int)
    return results_df.round(2)


def compute_kpi_table_by_month(
    df: pd.DataFrame,
    label_for_KPI: str = None,
    label_for_totals: str = None,
    current_fy: str = 2021,
    end_date: str = None,
    grouping: str = "date_closed",
) -> pd.DataFrame:
    df = df.copy()
    try:
        end_date = pd.to_datetime(end_date)
    except Exception:
        print(f"Date string {end_date} cannot be converted to a date.")
    # filter to current fy
    cond_current_fy = df["fiscal_year"] == current_fy
    cond_end_date = df[grouping] < end_date
    df = df[cond_current_fy & cond_end_date]
    table_df = (
        df[["wr_id", grouping, "is_on_time"]]
        .resample("M", on=grouping)
        .agg({"is_on_time": "mean", "wr_id": "count"})
    )
    table_df["year_month"] = table_df.index.strftime("%b-%y")
    table_df["is_on_time"] = table_df["is_on_time"].apply(lambda x: round(x * 100, 2))
    table_df = table_df.rename(
        columns={"is_on_time": label_for_KPI, "wr_id": label_for_totals}
    )
    return table_df


def compute_is_on_time(
    days_to_completion: pd.Series, benchmark: pd.Series
) -> pd.Series:
    return days_to_completion <= benchmark


def choose_pms_or_cms(df: pd.DataFrame, selection: str = ""):
    """Simplifies the interactive notebook by letting the
    user use a dropdown to pick whether to look at PMs or CMs.
    """
    df = df.copy()
    assert selection in ["PMs", "CMs", "All WRs"]
    # this defines which problem types are considered PMs
    pm_list = [
        "PREVENTIVE_GENERAL",
        "PREVENTIVE_HVAC",
    ]
    # filter data to PM types only
    cond_pm = df["primary_type"].isin(pm_list)

    # apply filter conditions
    if selection == "PMs":
        df_filt = df[cond_pm].copy()
        # the benchmark for all PMs is 21 days
        df_filt["benchmark"] = 21
    elif selection == "CMs":
        df_filt = df[~cond_pm].copy()
    elif selection == "All WRs":
        df_filt = df.copy()
    # store is_on_time variable
    df_filt = df_filt.dropna(subset=["days_to_completion", "benchmark"])
    df_filt["is_on_time"] = compute_is_on_time(
        df_filt["days_to_completion"], df_filt["benchmark"]
    )
    return df_filt


def trim_small_groups(
    df: pd.DataFrame,
    col: str,
    n_mode: bool = False,
    threshold=None,
    n: int = None,
):
    """
    Filters a df so that the result contains only a discrete number of
    values in a specified categorical column. Returns a filtered df that
    contains either:
    - Only those rows in the df that fall into the n most numerous
        categories (if n_mode = True)
    - Only those rows in the df that fall into an arbitrary number of
        categories that meet a row-count threshold (if n_mode = False)
    Args:
        df (pandas df): The dataframe to filter
        col (str): the column we want to use to remove values
        n_mode (bool): If true, the function takes the number of groups to return (n). If false,
                       then the function ignores n and takes the minimum value groups must
                       contain to be included (threshold).
        threshold (int): the threshold number of rows a value must have to remain
        n (int): the desired number of groups to return
    Returns:
        df_filtered (pandas df): A Pandas dataframe with nrows equal to or less than df.
    """
    df = df.copy()  # ensures the original data isn't modified
    if n_mode:
        to_include_list = (
            df[col].value_counts()[0:n].index.tolist()
        )  # list of top n categories
        df_filtered = df[df[col].isin(to_include_list)]  # filter
    else:
        # list of categories above threshold
        to_include_list = df[col].value_counts()[lambda x: x > threshold].index.tolist()
        df_filtered = df[df[col].isin(to_include_list)]  # filter
    return df_filtered
