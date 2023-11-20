from flask import Flask
from classes import Place, PlaceSchema
from flask_cors import CORS
from flask import request
import logging
from database import execute_sql
from bizlogic import default_search, fetch_settings, fetch_filters, fetch_place
from dotenv import load_dotenv
import highlight_io
from highlight_io.integrations.flask import FlaskIntegration
import os


load_dotenv()

## config log file
logging.basicConfig(
    filename="app.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
CORS(app)


# `instrument_logging=True` sets up logging instrumentation.
# if you do not want to send logs or are using `loguru`, pass `instrument_logging=False`
H = highlight_io.H(
	os.getenv("HIGHLIGHT_API_KEY"),
	integrations=[FlaskIntegration()],
	instrument_logging=True,
	service_name="collegetowns-api",
	service_version="git-sha",
)


@app.route("/")
def index():
    return "Test endpoint"


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


@app.route("/filters")
def get_filters():
    return fetch_filters()


@app.route("/places/<string:guid>")
def get_place(guid):
    return fetch_place(guid)


if __name__ == "__main__":
    app.run(debug=True)
