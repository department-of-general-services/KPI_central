from __future__ import annotations  # prevents NameError for typehints
from typing import List
import pyodbc
import sqlalchemy
from sqlalchemy.engine import URL, Row
from dynaconf import Dynaconf
import pandas as pd

from kpicentral.config import settings


class Archibus:
    """Client that interfaces with the Archibus database
    Attributes
    ----------
    engine: sqlalchemy.engine.Engine
        SQLAlchemy engine that manages the database connection
    """

    def __init__(
        self,
        conn_url: str = None,
        config: Dynaconf = settings,
    ) -> None:
        """Instantiates the FasterWeb class and connects to the database"""
        if not conn_url:
            conn_str = (
                "Driver={SQL Server};"
                f"Server={config.faster_web_server};"
                f"Database={config.faster_web_db};"
                "Trusted_Connection=yes;"
            )
            pyodbc.pool = False
            conn_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})
        self.engine = sqlalchemy.create_engine(conn_url)

    def execute_stmt(self, query_str: str) -> DatabaseRows:
        """Executes a SQL query against the FasterWeb database
        Parameters
        ----------
        query_str: str
            A string with valid SQL syntax
        fetch: FetchOpts
            How many rows should be fetched from the cursor, either all or
            just the first. Default is to return all.
        Returns
        -------
        DatabaseRows
            An instance of DatabaseRows with the results from the query
        """
        try:
            with self.engine.connect() as conn:
                query = sqlalchemy.text(query_str)
                rows = conn.execute(query).fetchall()
        except sqlalchemy.exc.ProgrammingError as error:
            raise error
        return DatabaseRows(rows)


class DatabaseRows:
    """A class that provides simplified access to the results of a SQL query
    Attributes
    ----------
    rows: List[Row]
        A list of SQLAlchemy Row instances that are returned by a query
    row_type: str
        The type of values included in each row, "columns" indicates that each
        row is a named tuple of the columns returned from a query, while "orm"
        indicates that each row is a named tuple of the orm models returned.
    cols: tuple
        A tuple of the names of the columns returned by the query
    """

    def __init__(self, rows: List[Row], row_type: str = "columns") -> None:
        """Inits the DatabaseRows class"""
        self.rows = rows
        self.row_type = row_type
        self.cols = rows[0]._fields

    @property
    def dataframe(self) -> pd.DataFrame:
        """Returns the rows as a pandas dataframe"""
        return pd.DataFrame(self.rows, columns=self.cols)

    @property
    def records(self) -> List[dict]:
        """Returns the rows as a list of dictionaries"""
        return [row._mapping for row in self.rows]
