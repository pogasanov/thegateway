# Sellingo importer

## Setup
* Requires following environmental variables to be set:
    * SELLINGO_EXPORT_FILE_PATH <- File path of exported xlsx file.
    * GATEWAY_SHOP_ID <- GUID of shop
    * GATEWAY_SECRET <- Secret needed for authentication to the gateway API
    * SELLINGO_SHOP_URL <- url of the shop on sellingo (by default it's sellingo demo shop url "https://demo.sellingo.pl/")
* Requirement libraries should be installed by running:
```pip install ./gateway_pkg ./sellingo_pkg```

## Running
```
python -m sellingo
```

## Example data
Example exported data of products from sellingo demo shop is in examples/sellingo.xlsx

## Exporting product data
To export product data go to admin panel (https://demo.sellingo.pl/admin)
and login with your admin credentials. 
Then click `Eksport produktów` under `Asortyment` on the top menu.
Then on the next site click `EKSPORTUJ DANE DO PLIKU XLSX` button.
After a while downloading will start.
![Products export](sellingo%20export.png)