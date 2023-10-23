from marshmallow import Schema, fields


class Place:
    def __init__(self, name, address, walkscore, distance):
        self.name = name
        self.address = address
        self.walkscore = walkscore
        self.distance = distance
        self.places = []


class PlaceSchema(Schema):
    name = fields.Str()
    address = fields.Str()
    walkscore = fields.Int()
    distance = fields.Float()
    places = fields.Nested("self", many=True)
