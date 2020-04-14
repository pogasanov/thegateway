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
pip install ./gateway_pkg ./prestashop_pkg
```

### Prestashop
1. Run `docker-compose up`
2. Make sure https://127.0.0.1:8080 opens with dummy data
3. When setup ends visit https://127.0.0.1:8080/admin-dev/
4. Login with credentials:
    * Email `admin@admin.com`
    * Password `admin`
5. Follow up with https://devdocs.prestashop.com/1.7/development/webservice/tutorials/provide-access/ describing process of enabling API.
Save **Key**
6. Setup International setting to your liking
7. If Prestashop is using more then one language  then `PRESTASHOP_LANGUAGE_ID` environmental variable should be set.
To find it go to: https://127.0.0.1:8080/admin-dev/ -> Improve -> International -> Localization -> Languages

## Running

```
python -m prestashop
```

Don't forget to setup environment variables!

## Uninstall

```
pip uninstall prestashop
pip uninstall gateway  # Optionally
```