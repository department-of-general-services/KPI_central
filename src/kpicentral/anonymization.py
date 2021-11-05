import numpy as np
import pandas as pd


def split_names(row):
    if "." in row["supervisor"]:
        full_name = row["supervisor"].split(".")
        row["supervisor_fname"] = full_name[0]
        row["supervisor_lname"] = full_name[1]
    if row["supervisor"] == "NULL":
        row["supervisor_fname"] = "NULL"
        row["supervisor_lname"] = "NULL"
    return row

def replace_names(df, faker):
    # empty string values as nan
    df["supervisor"] = df["supervisor"].replace("NULL", np.nan)
    # name replacement dictionary
    fname_replacements = {
        name: faker.first_name().upper().replace(" ", "")
        for name in df["supervisor_fname"].unique()
        if name is not np.nan
    }
    lname_replacements = {
        name: faker.last_name().upper().replace(" ", "")
        for name in df["supervisor_lname"].unique()
        if name is not np.nan
    }

    # apply replacement
    df = df.replace(
        {"supervisor_fname": fname_replacements, "supervisor_lname": lname_replacements}
    )
    df["supervisor_anon"] = df["supervisor_fname"] + "." + df["supervisor_lname"]
    df = df.drop(columns=["supervisor_fname", "supervisor_lname"])
    return df