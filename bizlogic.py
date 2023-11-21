from functools import reduce
import logging
import json
from database import execute_sql
from classes import Place, PlaceSchema
import functools

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
            row["place2latitude"],
            row["place2longitude"],
            row["place2guid"].lower(),
        )
        if row["placename1"] not in processed:
            place = Place(
                row["placename1"],
                row["placeaddress1"],
                row["place1walkscore"],
                None,
                row["place1latitude"],
                row["place1longitude"],
                row["place1guid"].lower(),
            )

            processed[row["placename1"]] = place
            place.places.append(place2)
        else:
            processed[row["placename1"]].places.append(place2)

    place_schema = PlaceSchema()

    for k, v in processed.items():
        main_places.append(place_schema.dump(v))

    return main_places


def intersection(sets):
    logger.debug(sets)
    return reduce(set.intersection, sets)

@functools.lru_cache(maxsize=None)
def process_rail_enum():
    places = set()
    sql = "SELECT PlaceID FROM Places WHERE HasRails=1"
    json_data = execute_sql(sql)
    data = json.loads(json_data)
    for row in data:
        places.add(row["PlaceID"])

    return places

@functools.lru_cache(maxsize=None)
def process_place_enum(placeenum):
    places = set()
    sql = "SELECT DISTINCT PlaceID1 FROM PlacesDistancesView WHERE place2enum = ?"
    params = (placeenum,)
    json_data = execute_sql(sql, params)
    data = json.loads(json_data)
    for row in data:
        places.add(row["PlaceID1"])

    return places


def getmainplaces(placeenums):
    """
    For each enum in the list, get the ids of the main places
    Then find the intersection of those ids and return that list
    """

    enums = list(placeenums)

    places_list = []

    has_rail = False

    ## if TRAIN in placeenums then set HAS_RAIL = True and remove from list
    if "TRAIN" in enums:
        has_rail = True
        enums.remove("TRAIN")

    for placeenum in enums:
        places_list.append(process_place_enum(placeenum))

    ## if has rail then add rail places to list
    if has_rail:
        places_list.append(process_rail_enum())

    return list(intersection(places_list))


def default_search(filter):
    if not filter.get("enums"):
        sql = "select * from PlacesDistancesView ORDER BY place1walkscore DESC, placename1, distance;"
    else:
        enum_list = filter["enums"]
        placeids = getmainplaces(enum_list)[:100]

        ## if not places match then return empty list
        if not placeids:
            return []

        sql = """
        select * from PlacesDistancesView 
        WHERE place2enum in ({0}) AND placeid1 in ({1})
        ORDER BY place1walkscore DESC, placename1, distance;
        """
        ## list of quoted words
        sql = sql.format(
            ",".join(["'" + x + "'" for x in enum_list]),
            ",".join([str(x) for x in placeids]),
        )
        logger.debug(sql)

    json_data = execute_sql(sql)
    transformed_data = transform(json_data)
    return transformed_data


def fetch_settings():
    sql = "SELECT * FROM Brands ORDER BY BrandName ASC;"
    json_data = execute_sql(sql)
    data = json.loads(json_data)
    return data


def fetch_filters():
    sql = "SELECT enum from AvailableFilters ORDER BY enum ASC;"
    json_data = execute_sql(sql)
    data = [enum["enum"] for enum in json.loads(json_data)]

    return data


def fetch_place(guid):
    sql = "SELECT * FROM Places WHERE guidcolumn = ?"
    # Execute with parameter
    json_data = execute_sql(sql, [guid])
    data = json.loads(json_data)[0]
    return data


def fetch_filtergroups():
    sql = "SELECT * FROM AvailableFiltersView";
    json_data = execute_sql(sql)
    data = json.loads(json_data)
    return data
