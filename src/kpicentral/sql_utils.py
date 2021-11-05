import pandas as pd
import sqlalchemy as db
import pyodbc
from private.config import config


def mssql_engine(
    username=config["username"], password=config["password"], server=config["server"]
):
    engine = db.create_engine(
        f"mssql+pyodbc://{config['username']}:{config['password']}@{config['server']}/DGS_Archibus?driver=SQL+Server"
    )
    return engine


def get_data_from_archibus(engine, db_name):
    query = f"SELECT * from DGS_Archibus.afm.{db_name};"
    archibus_df = pd.read_sql(query, engine)
    return archibus_df
