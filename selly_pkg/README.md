# Selly importer

## Setup
* Requires following environmental variables to be set:
    * SELLY_API_ID -----------↓
    * SELLY_APP_KEY ---> API credentials
    * SELLY_SHOP_URL <- URL address of the shop "http://example.com"
    * GATEWAY_SHOP_ID <- GUID of shop
    * GATEWAY_SECRET <- Secret needed for authentication to the gateway API
* Requirement libraries should be installed by running:
```pip install ./gateway_pkg ./selly_pkg```

## Running
```
python -m selly
```

## Example data
Example responses from API are in `selly/tests/selly_responses.py` file
