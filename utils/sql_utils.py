import pandas as pd
import sqlalchemy as db
import pyodbc
from private.config import config
# from utils.general_utils import clean_report


def mssql_engine(
    username=config["username"], password=config["password"], server=config["server"]
):
    engine = db.create_engine(
        f"mssql+pyodbc://{config['username']}:{config['password']}@{config['server']}/DGS_Archibus?driver=SQL+Server"
    )
    return engine


def get_data_from_archibus(engine):
    query = "SELECT * from DGS_Archibus.afm.dash_benchmarks;"
    archibus_df = pd.read_sql(query, engine)
    return archibus_df
