# Magento product importer

Python script that downloads all products from **magento** and uploads to **gateway**. Includes following fields:
* Name
* Description
* Short description
* Price
* Stock size
* SKU
* VAT
* Images
* Variants

Includes **simple** and **configurable** products.

Requires following environment variables to be set before running script:
* `MAGENTO_BASE_URL` - Url of magento shop;
* `MAGENTO_API_ACCESS_TOKEN` - API key for magento. Follow with setup to know how retrieve it;
* `GATEWAY_BASE_URL` - Url of gateway;
* `GATEWAY_SHOP_ID` - Shop ID of gateway;
* `GATEWAY_SECRET` - Secret key for selected gateway shop id.

API docs - https://devdocs.magento.com/guides/v2.3/rest/bk-rest.html

## Setup

### Script

```
pip install ./gateway_pkg ./magento_pkg
```

### Magento

On ubuntu 19.10, elasticshop docker container was throwing error `Invalid kernel settings. Elasticsearch requires at least: vm.max_map_count = 262144`.  
To fix this, run `sudo sysctl -w vm.max_map_count=262144`

Register on magento marketplace - https://marketplace.magento.com/ It will be required to install sample data. Follow with https://devdocs.magento.com/guides/v2.3/install-gde/prereq/connect-auth.html

Admin username:
* user
* bitnami1

1. Run `docker-compose up`
2. Visit http://127.0.0.1
3. Wait a little bit for magento to install
4. **[Optional]** Install sample data. Expect it will require public and private access key from magento marketplace. **It will take some time.**
    ```
    docker-compose exec magento php /opt/bitnami/magento/htdocs/bin/magento sampledata:deploy -vvv
    docker-compose exec magento php /opt/bitnami/magento/htdocs/bin/magento setup:upgrade -vvv
    docker-compose exec magento chown -R bitnami:daemon /opt/bitnami/magento/htdocs
    ```
4. Make sure http://127.0.0.1 opens with dummy data
5. Generate ACCESS_TOKEN, following https://devdocs.magento.com/guides/v2.3/get-started/authentication/gs-authentication-token.html#integration-tokens Follow **integration token** generation and store **ACCESS TOKEN** as `MAGENTO_API_ACCESS_TOKEN` environment variable.

## Running

```
python -m magento
```

Don't forget to setup environment variables!

## Uninstall

```
pip uninstall magento
pip uninstall gateway  # Optionally
```