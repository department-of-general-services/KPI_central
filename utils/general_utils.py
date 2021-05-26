import pandas as pd
import numpy as np
from datetime import datetime
import re


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


def tidy_up_df(df):
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


def cast_dtypes(df):
    df = df.copy()
    df["wr_id"] = df["wr_id"].astype(int)
    df = df.replace("NULL", np.nan)
    df["supervisor"] = df["supervisor"].replace(np.nan, "NULL")
    return df


def drop_dupes(df):
    cond_1 = df["cf_notes"].str.contains(r"duplicate", re.IGNORECASE)
    cond_2 = df["status"].isin(["Can", "Clo", "R"])
    dupes = df[cond_1 & cond_2]
    df_deduped = df[~df["wr_id"].isin(dupes["wr_id"])]
    return df_deduped


def consolidate_prob_types(row):
    leave_alone_types = [
        "AIR QUALITY",
        "APPLIANCE",
        "CEILTILE",
        "DUCT CLEANING",
        "ELEVATOR",
        "FENCE_GATE",
        "FIRE SUPPRESSION-PROTECTION",
        "FLOOR",
        "LOCK",
        "OVERHDDOOR",
        "ROOF",
        "SNOW_REMOVAL",
        "WINDOW",
    ]
    hvac_types = [
        "BOILER",
        "CHILLERS",
        "COOLING TOWERS",
        "HVAC|INFRASTRUCTURE",
        "HVAC INFRASTRUCTURE",
        "HVAC|HEATING OIL",
        "HVAC|INSPECTION",
        "HVAC|REPAIR",
        "HVAC|REPLACEMENT",
        "HVAC",
    ]
    pm_types = [
        "BUILDING INTERIOR INSPECTION",
        "BUILDING PM",
        "GENERATOR PM",
        "HVAC|PM",
        "PREVENTIVE MAINT",
        "INSPECTION",
        "FUEL INSPECTION",
    ]
    other_types = ["OTHER", "RAMPS", "STEPS", "RAILSTAIRSRAMP"]
    if row["problem_type"] in leave_alone_types:
        row["primary"] = row["problem_type"]
    elif row["problem_type"] in hvac_types:
        row["primary"] = "HVAC"
    elif row["problem_type"] in pm_types:
        row["primary"] = "PREVENTIVE"
    elif row["problem_type"] == "BATHROOM_FIXT":
        row["primary"] = "BATHROOM"
    elif row["problem_type"] in ["BUILDING EXTERIOR"]:
        row["primary"] = "BUILDING"
    elif row["problem_type"] in ["CARPENTRY", "WALL"]:
        row["primary"] = "CARPENTRY"
    elif row["problem_type"] in ["DELIVERY", "_DELIVERY"]:
        row["primary"] = "DELIVERY"
    elif row["problem_type"] == "DESIGN/RENOVATION":
        row["primary"] = "DESIGN"
    elif row["problem_type"] in ["PEDESTRIAN DOORS", "DOOR"]:
        row["primary"] = "DOOR"
    elif row["problem_type"].startswith("ELEC") or row["problem_type"] == "OUTLETS":
        row["primary"] = "ELECTRICAL"
    elif row["problem_type"].startswith("ENVIR") or row["problem_type"] == "ASBESTOS":
        row["primary"] = "ENVIRONMENTAL"
    elif row["problem_type"] in ["LAWN", "LANDSCAPING"]:
        row["primary"] = "LANDSCAPING"
    elif row["problem_type"] in ["PAINT", "PAINTING"]:
        row["primary"] = "PAINTING"
    elif row["problem_type"].startswith("PLUMB"):
        row["primary"] = "PLUMBING"
    elif row["problem_type"].startswith("SECURITY SYSTEMS"):
        row["primary"] = "SECURITY SYSTEMS"
    elif row["problem_type"].startswith("SERV"):
        row["primary"] = "SERVICE"
    elif row["problem_type"] in other_types and "GATEKEEPER" in str(row["role_name"]):
        row["primary"] = "OTHER-EXTERNAL"
    elif row["problem_type"] in other_types and not "GATEKEEPER" in str(
        row["role_name"]
    ):
        row["primary"] = "OTHER-INTERNAL"
    return row


def compute_pm_cm(df, PM_list):
    df = df.copy().sort_values("fiscal_year")
    results_df = pd.DataFrame(
        columns=[
            "fy_request",
            # "percent_pm",
            "pm_cm_ratio",
            "count_cm",
            "count_pm",
            "count_hvac",
        ]
    )
    for fiscal_year in df["fiscal_year"].unique():
        results_dict = {}
        df_fy = df[df["fiscal_year"] == fiscal_year]
        cond_pm = df_fy["is_pm"] == True
        count_pm = len(df_fy[cond_pm])
        count_hvac = len(df_fy)
        count_cm = count_hvac - count_pm
        results_dict["fiscal_year"] = fiscal_year
        results_dict["pm_cm_ratio"] = (count_pm / count_cm) * 100
        results_dict["count_pm"] = count_pm
        results_dict["count_cm"] = count_cm
        results_dict["count_hvac"] = count_hvac
        results_df = results_df.append(results_dict, ignore_index=True)
    results_df[["fiscal_year", "count_cm", "count_pm", "count_hvac"]] = results_df[
        ["fiscal_year", "count_cm", "count_pm", "count_hvac"]
    ].astype(int)
    return results_df.round(2)


def add_fiscal_year(df, assign_fy_on):
    df = df.copy()
    if assign_fy_on == "Closed":
        df["calendar_year"] = df["date_closed"].dt.year
        df["month"] = df["date_closed"].dt.month
    elif assign_fy_on == "Completed":
        df["calendar_year"] = df["date_completed"].dt.year
        df["month"] = df["date_completed"].dt.month
    elif assign_fy_on == "Requested":
        df["calendar_year"] = df["date_requested"].dt.year
        df["month"] = df["date_requested"].dt.month
    c = pd.to_numeric(df["calendar_year"])
    df["fiscal_year"] = np.where(df["month"] >= 7, c + 1, c)
    df["fiscal_year"] = (pd.to_datetime(df["fiscal_year"], format="%Y")).dt.year
    df["fiscal_year"] = df["fiscal_year"].astype("Int64")
    return df


def compute_kpi_table(df, label_for_KPI, label_for_totals, grouping_var="fiscal_year"):
    df = df.copy()
    table_df = df.groupby(grouping_var)[["is_on_time"]].agg(["mean", "count"])
    table_df.columns = table_df.columns.droplevel(0)
    table_df["mean"] = table_df["mean"].apply(lambda x: round(x * 100, 2))
    table_df = table_df.rename(
        columns={"mean": label_for_KPI, "count": label_for_totals}
    )
    return table_df


def compute_pm_cm_by_month(df, PM_list, end_date):
    df = df.copy().sort_values("date_closed")
    today = datetime.today()
    cond_current_fy = df["fiscal_year"] == today.year
    cond_last_month = df["date_closed"] < end_date
    df = df[cond_current_fy & cond_last_month]
    df["year_month"] = df["date_closed"].dt.strftime("%b-%y")
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
        cond_pm = df_ym["is_pm"] == True
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
    df,
    label_for_KPI=None,
    label_for_totals=None,
    current_fy=2021,
    end_date=None,
    grouping="date_closed",
):
    df = df.copy()
    try:
        end_date = pd.to_datetime(end_date)
    except Exception:
        print(f"Date string {end_date} cannot be converted to a date.")
    # filter to current fy
    cond_current_fy = df["fiscal_year"] == current_fy
    cond_end_date = df["date_closed"] < end_date
    df = df[cond_current_fy & cond_end_date]
    table_df = (
        df[["wr_id", "date_closed", "is_on_time"]]
        .resample("M", on=grouping)
        .agg({"is_on_time": "mean", "wr_id": "count"})
    )
    table_df["year_month"] = table_df.index.strftime("%b-%y")
    table_df["is_on_time"] = table_df["is_on_time"].apply(lambda x: round(x * 100, 2))
    table_df = table_df.rename(
        columns={"is_on_time": label_for_KPI, "wr_id": label_for_totals}
    )
    return table_df


def compute_is_on_time(days_to_completion, benchmark):
    return days_to_completion <= benchmark


def duration_in_days(df, new_col_name: str, start_col: str, end_col: str):
    df = df.copy()
    # compute days to completion
    df[new_col_name] = df.apply(
        lambda x: (x[end_col] - x[start_col]) / np.timedelta64(1, "D"),
        axis=1,
    ).round(2)
    return df


def choose_pms_or_cms(df, selection: str = ""):
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