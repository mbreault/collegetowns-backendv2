from flask import Flask
import pyodbc
import os
import dotenv
import json
from classes import Place, PlaceSchema

app = Flask(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()


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


def execute_sql(sql):
    """
    1.  Execute SQL
    2.  Get Column Names
    3.  Convert resultset to json.  This needs to include the column names
    """

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql)
    column_names = [column[0] for column in cursor.description]
    data = cursor.fetchall()
    conn.close()

    # Convert data to json
    json_data = []
    for row in data:
        json_data.append(dict(zip(column_names, row)))

    return convert_to_json(json_data)


def transform(data):
    """
    The data has multiple lines of restaurants (place2) for each college (place1)
    Get a distinct list of places1 and then makes a list of places2 for each place1
    """
    # Get distinct list of places1
    main_places = []
    processed = {}
    for row in json.loads(data):
        place2 = Place(
            row["placename2"],
            row["placeaddress2"],
            row["place2walkscore"],
            row["distance"],
        )
        if row["placename1"] not in processed:
            place = Place(
                row["placename1"], row["placeaddress1"], row["place1walkscore"], None
            )

            processed[row["placename1"]] = place
            place.places.append(place2)
        else:
            processed[row["placename1"]].places.append(place2)

    place_schema = PlaceSchema()

    for k, v in processed.items():
        main_places.append(place_schema.dump(v))

    return main_places


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/default")
def get_default():
    json_data = execute_sql("select top 10 * from PlacesDistancesView")
    transformed_data = transform(json_data)
    return transformed_data


@app.route("/places")
def get_places():
    return execute_sql("select * from places")


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


if __name__ == "__main__":
    app.run(debug=True)
