from flask import Flask
from classes import Place, PlaceSchema
from flask_cors import CORS
from flask import request
import logging
from database import execute_sql
from bizlogic import default_search, fetch_settings, fetch_filters


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


@app.route("/default")
def get_default():
    return default_search(request.args.get("enums"))


@app.route("/settings")
def get_settings():
    return fetch_settings()


@app.route("/filters")
def get_filters():
    return fetch_filters()


if __name__ == "__main__":
    app.run(debug=True)
