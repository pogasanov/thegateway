# Prestashop importer

Python script that downloads all products from **prestashop** and uploads to **gateway**. Includes following fields:
* Name
* Description
* Short description
* Price
* Stock size
* SKU (reference in prestashop)
* VAT
* Images
* Variants

Requires following environment variables to be set before running script:
* `PRESTASHOP_BASE_URL` - Url of prestashop;
* `PRESTASHOP_API_KEY` - API key for prestashop. Follow with setup to know how retrieve it;
* `PRESTASHOP_LANGUAGE_ID` - Language id for desired language of products to be retrieved. For multilanguage prestashop sites only;
* `GATEWAY_BASE_URL` - Url of gateway;
* `GATEWAY_SHOP_ID` - Shop ID of gateway;
* `GATEWAY_SECRET` - Secret key for selected gateway shop id.

## Setup

### Script

```
pip install ./gateway ./prestashop
```

### Prestashop
1. Run `docker-compose up`
2. Visit https://127.0.0.1:8080
3. Follow up with prestashop installation. Fill up database:
    * Hostname: `db:3306`
    * Login `prestashop`
    * Password `prestashop`
    * Database name `prestashop`  
Save **email** and **password** for admin. 
4. Make sure https://127.0.0.1:8080 opens with dummy data
5. Run:
    ```
    docker-compose exec prestashop rm -R /var/www/html/install
    docker-compose exec prestashop mv -R /var/www/html/admin /var/www/html/admin1
    ```
6. Visit https://127.0.0.1:8080/admin1/ Use email and password from step 3.
7. Follow up with https://devdocs.prestashop.com/1.7/development/webservice/tutorials/provide-access/ describing process of enabling API.
Save **Key**
8. If Prestashop is using more then one language then `PRESTASHOP_LANGUAGE_ID` environmental variable should be set.
To find it go to: https://127.0.0.1:8080/admin1/ -> Improve -> International -> Localization -> Languages

## Running

```
python -m prestashop.Runner
```

Don't forget to setup environment variables!

## Uninstall

```
pip uninstall prestashop
pip uninstall gateway  # Optionally
```