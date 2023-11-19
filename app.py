from flask import Flask
from classes import Place, PlaceSchema
from flask_cors import CORS
from flask import request
import logging
from database import execute_sql
from bizlogic import default_search, fetch_settings, fetch_filters, fetch_place


## config log file
logging.basicConfig(
    filename="app.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/default", methods=["POST"])
def get_default():
    filter_data = request.get_json()
    # Process the filter_data to extract enums, rails, airports, etc.
    # You might need to modify your default_search function to accept this new format.
    result = default_search(filter_data)
    return result


@app.route("/settings")
def get_settings():
    return fetch_settings()


@app.route("/filters/<string:userid>")
def get_filters(userid):
    return fetch_filters(userid)


@app.route("/places/<string:guid>")
def get_place(guid):
    return fetch_place(guid)


if __name__ == "__main__":
    app.run(debug=True)
