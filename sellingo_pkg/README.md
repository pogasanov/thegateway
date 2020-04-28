# Sellingo importer
## Status
For now we don't have any example production-like data,
so this importer was written on self made products.
It should be tested and changed if needed after getting some example data.  
## Info
Sellingo doesn't have an API but it can be integrated with Sellasist which has one. 
## Setup
* Requires following environmental variables to be set:
    * SELLINGO_API_URL <- url of sellasist API (https://demo2137.sellasist.pl/api/v1)
    * SELLINGO_API_KEY <- API key from sellasist
    * GATEWAY_SHOP_ID <- GUID of shop
    * GATEWAY_SECRET <- Secret needed for authentication to the gateway API
* Requirement libraries should be installed by running:
```pip install ./gateway_pkg ./sellingo_pkg```

## Running
```
python -m sellingo
```

## Getting API Key
On Sellasist admin (https://demo2137.sellasist.pl/admin/
go to `Integracje/Klucze API` then click `DODAJ KLUCZ`