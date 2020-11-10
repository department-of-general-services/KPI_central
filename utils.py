import pandas as pd
import numpy as np
import re


def glue_date_time(df, date_col, time_col, dt_col_name):
    """
    Given a dataframe where date and time information is stored in separate columns,
    take the date and time and fuse them together into a single valid datetime.
    Note that we assume that the time information in a date column is present (not blank)
    but incorrect, as is the case in DGS Archibus data.

    Args:
        df (pandas df): A df with date and time columns to be glued
        date_col (str): The name of the column in df containing the date information.
                        This column should have a dtype of datetime64.
        time_col (str): The name of the column in df containing the time information
                        This column should have a dtype of datetime64.
        dt_col_name (str): The name of the resulting, glued, datetime column

    Returns:
        df (pandas df): A new dataframe with the original date and time columns
                        removed and replaced with the glued, complete datetime column.
    """
    df = df.copy()  # ensures the original data isn't modified
    # Here we separate the df into the part we can glue and the part we can't;
    # we do this so that we can avoid dropping rows where date_col is null, which we still need.
    df_y = df[df[date_col].notna()]  # select the rows where the date col is valid
    df_n = df[df[date_col].isna()]  # select the rows where the date col is null

    # convert date and time cols to formatted strings
    df_y["date_str"] = df_y[date_col].apply(
        lambda x: x.strftime("%m/%d/%Y") if not pd.isnull(x) else ""
    )
    df_y["time_str"] = df_y[time_col].apply(
        lambda x: x.strftime("%H:%M:%S") if not pd.isnull(x) else ""
    )
    # concatenate the date and time strings
    df_y["temp"] = df_y["date_str"] + " " + df_y["time_str"]
    # convert concatenated string into a complete datetime
    df_y[dt_col_name] = df_y["temp"].apply(
        lambda x: pd.to_datetime(x, format="%m/%d/%Y %H:%M:%S", errors="coerce")
    )
    df_y = df_y.drop(columns=["temp", "date_str", "time_str", date_col, time_col])

    # include the rows where the date col was null
    df = pd.concat([df_y, df_n], sort=False)
    return df


def add_fiscal_year(df):
    df = df.copy()
    df["calendar_year"] = df["requested_dt"].dt.year
    df["month"] = df["requested_dt"].dt.month
    c = pd.to_numeric(df["calendar_year"])
    df["fiscal_year"] = np.where(df["month"] >= 7, c + 1, c)
    df["fiscal_year"] = (pd.to_datetime(df["fiscal_year"], format="%Y")).dt.year
    return df


def entirely_in_fiscal_year(df):
    df = df.copy()
    df["requested_cal_year"] = df["requested_dt"].dt.year
    df["requested_cal_month"] = df["requested_dt"].dt.month
    df["closed_cal_year"] = df["date_closed"].dt.year
    df["closed_cal_month"] = df["date_closed"].dt.month
    y_requested = pd.to_numeric(df["requested_cal_year"])
    y_closed = pd.to_numeric(df["closed_cal_year"])
    df["requested_fiscal_year"] = np.where(
        df["requested_cal_month"] >= 7, y_requested + 1, y_requested
    )
    df["closed_fiscal_year"] = np.where(
        df["closed_cal_month"] >= 7, y_closed + 1, y_closed
    )
    cond_both = df["requested_fiscal_year"] == df["closed_fiscal_year"]
    df = df[cond_both]
    df["fiscal_year"] = (
        pd.to_datetime(df["requested_fiscal_year"], format="%Y")
    ).dt.year
    df = df.drop(
        columns=[
            "requested_cal_year",
            "requested_cal_month",
            "closed_cal_year",
            "closed_cal_month",
            "requested_fiscal_year",
            "closed_fiscal_year",
        ]
    )
    return df


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


def compute_days_to_completion(df):
    df = df.copy()
    # compute days to completion
    df["days_to_completion"] = df.apply(
        lambda x: (x["completed_dt"] - x["requested_dt"]) / np.timedelta64(1, "D"),
        axis=1,
    ).round(2)
    # set the index
    df = df.set_index(keys="requested_dt", verify_integrity=False, drop=False)
    return df


def tidy_up_wr(df):
    df = df.copy()
    df = df.dropna(subset=["wr_id"])
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df["wr_id"] = df["wr_id"].astype(int).astype(str)
    df = df.rename(mapper={"prob_type": "problem_type"}, axis=1)
    cond_valid = ~df["problem_type"].str.contains("TEST")
    df = df[cond_valid]
    df["status"] = df["status"].replace("A", "AA", regex=False)
    return df


def drop_dupes(df):
    cond_1 = df["cf_notes"].str.contains(r"duplicate", re.IGNORECASE)
    cond_2 = df["status"].isin(["Can", "Clo", "R"])
    dupes = df[cond_1 & cond_2]
    df_deduped = df[~df["wr_id"].isin(dupes["wr_id"])]
    return df_deduped
