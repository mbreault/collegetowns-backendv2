# database.py
import pyodbc
import os
import dotenv
import json
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def convert_to_json(data):
    """
    Use json.dumps with a handler to convert datetime to strings
    """

    def handler(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        else:
            raise TypeError(
                "Object of type {0} with value of {1} is not JSON serializable".format(
                    type(obj), repr(obj)
                )
            )

    return json.dumps(data, default=handler)


def connect_db():
    ## get db connection info from .env file
    server = os.getenv("AZURE_DB_SERVER")
    database = os.getenv("AZURE_DB_DATABASE")
    username = os.getenv("AZURE_DB_USERNAME")
    password = os.getenv("AZURE_DB_PASSWORD")

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + server + ";"
        "DATABASE=" + database + ";"
        "UID=" + username + ";"
        "PWD=" + password
    )
    return conn


def execute_sql(sql, params=None):
    """
    1.  Execute SQL
    2.  Get Column Names
    3.  Convert resultset to json.  This needs to include the column names
    """

    logger.debug(sql)

    conn = connect_db()
    cursor = conn.cursor()
    if params is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, params)
    column_names = [column[0] for column in cursor.description]
    data = cursor.fetchall()
    conn.close()

    # Convert data to json
    json_data = []
    for row in data:
        json_data.append(dict(zip(column_names, row)))

    return convert_to_json(json_data)
