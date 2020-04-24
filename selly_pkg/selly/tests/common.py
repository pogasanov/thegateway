import base64
import json

import responses
from selly.tests.selly_responses import *

DUMMY_TOKEN = "TEST"
DUMMY_SELLY_URL = "http://example.com"
API_ID = 2137
APP_KEY = "QUFBQUFBQUFBQQ=="
HEX_DIGEST = "b35a830efa0c0cf39737a95083e229745e1cc9213e7a05af8e4efc29ea491d26"


def chain_list_of_lists(list_of_lists):
    return [y for x in list_of_lists for y in x]


def prepare_response(args, response):
    return {
        "method": responses.GET,
        "url": f"{DUMMY_SELLY_URL}/apig?token={DUMMY_TOKEN}&{args}",
        "body": base64.b64encode(json.dumps(response).encode()),
    }


def add_responses():
    responses.add(**prepare_response("table=produkty", PRODUCTS))
    responses.add(**prepare_response("table=produkty_wlasciwosci", DETAILS))
    responses.add(**prepare_response("table=produkty_warianty", VARIANTS))
    responses.add(**prepare_response("table=produkty_atrybuty", ATTRIBUTES))
    responses.add(**prepare_response("table=produkty_atrybuty_grupy", ATTRIBUTES_GROUPS))
    responses.add(**prepare_response("table=produkty_warianty_atrybuty", VARIANTS_ATTRIBUTES))
    responses.add(**prepare_response("table=produkty_zdjecia", IMAGES))
