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


def entirely_within_fiscal_year(df):
    df = df.copy()
    # store year and month for both request and closure
    df["requested_cal_year"] = df["requested_dt"].dt.year
    df["requested_cal_month"] = df["requested_dt"].dt.month
    df["completed_cal_year"] = df["completed_dt"].dt.year
    df["completed_cal_month"] = df["completed_dt"].dt.month
    # store the years as numbers
    y_requested = pd.to_numeric(df["requested_cal_year"])
    y_closed = pd.to_numeric(df["completed_cal_year"])
    # compute the fiscal year of request & closure
    df["requested_fiscal_year"] = np.where(
        df["requested_cal_month"] >= 7, y_requested + 1, y_requested
    )
    df["completed_fiscal_year"] = np.where(
        df["completed_cal_month"] >= 7, y_closed + 1, y_closed
    )
    # drop the rows that straddle two fiscal years
    cond_both = df["requested_fiscal_year"] == df["completed_fiscal_year"]
    non_df = df[~cond_both]
    df = df[cond_both]
    # cast the type of the year
    df["fiscal_year"] = (
        pd.to_datetime(df["requested_fiscal_year"], format="%Y")
    ).dt.year
    df = df.drop(
        columns=[
            "requested_cal_year",
            "requested_cal_month",
            "completed_cal_year",
            "completed_cal_month",
            "requested_fiscal_year",
            "completed_fiscal_year",
        ]
    )
    return df, non_df


def add_fiscal_year(df, assign_fy_on="closure"):
    df = df.copy()
    if assign_fy_on == "closure":
        df["calendar_year"] = df["date_closed"].dt.year
        df["month"] = df["date_closed"].dt.month
    if assign_fy_on == "completion":
        df["calendar_year"] = df["completed_dt"].dt.year
        df["month"] = df["completed_dt"].dt.month
    if assign_fy_on == "request":
        df["calendar_year"] = df["requested_dt"].dt.year
        df["month"] = df["requested_dt"].dt.month
    c = pd.to_numeric(df["calendar_year"])
    df["fiscal_year"] = np.where(df["month"] >= 7, c + 1, c)
    df["fiscal_year"] = (pd.to_datetime(df["fiscal_year"], format="%Y")).dt.year
    df["fiscal_year"] = df["fiscal_year"].astype("Int64")
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


# def get_kpi_data(config, query_path):
#     # Get private credentials using dotenv system
#     server = config["SERVER"]
#     user = config["USER"]
#     password = config["PASSWORD"]
#     db = config["DB"]
#     # Connect to Archibus database
#     conn = pyodbc.connect(
#         f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={db};UID={user};PWD={password}"
#     )
#     cursor = conn.cursor()
#     # Open a file with our basic SQL query
#     fd = open(query_path, "r")
#     sqlFile = fd.read()
#     fd.close()

#     # Query the database
#     df = pd.read_sql(
#         sqlFile, conn, parse_dates=["date_requested", "date_completed", "date_closed"]
#     )
#     conn.close()
#     return df


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


def tidy_up_df(df):
    df = df.copy()
    df = df.rename(mapper={"prob_type": "problem_type"}, axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.dropna(subset=["wr_id", "problem_type"])
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    cond_valid = ~df["problem_type"].str.contains("TEST")
    df = df[cond_valid]
    df["status"] = df["status"].replace("A", "AA", regex=False)
    return df


def cast_dtypes(df):
    df = df.copy()
    df["wr_id"] = df["wr_id"].astype(int)
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
            "year",
            # "percent_pm",
            "pm_cm_ratio",
            "count_cm",
            "count_pm",
            "count_hvac",
        ]
    )
    for year in df["fiscal_year"].unique():
        results_dict = {}
        df_fy = df[df["fiscal_year"] == year]
        cond_pm = df_fy["is_pm"] == True
        count_pm = len(df_fy[cond_pm])
        count_hvac = len(df_fy)
        count_cm = count_hvac - count_pm
        results_dict["year"] = year
        # results_dict["percent_pm"] = (count_pm / count_hvac) * 100
        results_dict["pm_cm_ratio"] = count_pm / count_cm
        results_dict["count_pm"] = count_pm
        results_dict["count_cm"] = count_cm
        results_dict["count_hvac"] = count_hvac
        results_df = results_df.append(results_dict, ignore_index=True)
    results_df[["year", "count_cm", "count_pm", "count_hvac"]] = results_df[
        ["year", "count_cm", "count_pm", "count_hvac"]
    ].astype(int)
    return results_df.round(2)


def compute_kpi_table(df, label_for_KPI, label_for_totals):
    df = df.copy()
    table_df = df.groupby("fiscal_year")[["is_on_time"]].agg(["mean", "count"])
    table_df.columns = table_df.columns.droplevel(0)
    table_df["mean"] = table_df["mean"].apply(lambda x: round(x * 100, 2))
    table_df = table_df.rename(
        columns={"mean": label_for_KPI, "count": label_for_totals}
    )
    return table_df


def add_cm_benchmarks(row):
    ontime_in_7 = ["BUILDING", "DELIVERY", "INSPECTION", "OTHER-INTERNAL", "LOCK"]
    ontime_in_14 = [
        "BATHROOM",
        "CEILTILE",
        "DOOR",
        "ELECTRICAL",
        "FIXTURES",
        "LANDSCAPING",
        "OTHER-EXTERNAL",
        "PLUMBING",
        "SERVICE",
    ]
    ontime_in_21 = ["APPLIANCE", "CARPENTRY", "ELEVATOR", "PAINTING", "PREVENTIVE"]
    ontime_in_30 = ["HVAC", "WINDOW"]
    ontime_in_45 = [
        "AIR QUALITY",
        "ENVIRONMENTAL",
        "FENCE_GATE",
        "FIRE SUPPRESSION-PROTECTION",
        "FLOOR",
        "OVERHDDOOR",
        "SECURITY SYSTEMS",
    ]
    ontime_in_60 = ["DESIGN", "ROOF", "DUCT CLEANING"]
    if row["primary"] in ontime_in_7:
        row["benchmark"] = 7
    elif row["primary"] in ontime_in_14:
        row["benchmark"] = 14
    elif row["primary"] in ontime_in_21:
        row["benchmark"] = 21
    elif row["primary"] in ontime_in_30:
        row["benchmark"] = 30
    elif row["primary"] in ontime_in_45:
        row["benchmark"] = 45
    elif row["primary"] in ontime_in_60:
        row["benchmark"] = 60
    return row