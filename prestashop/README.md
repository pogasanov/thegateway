# Prestashop importer

## Setup

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

## Running

### Locally
1. Make sure prestashop docker-compose is running `docker-compose up`
2. Find prestashop internal ip
    ```
    docker network ls
    # ...
    # 2e2c5239cfab        prestashop_default        bridge              local
    # ...
    
    docker network inspect prestashop_default
    # ...
    #        "Containers": {
    # ...
    #            "a4806d1b1392c9a5c72853e1096a731c990ad62758bd508ee6a2da211a35d3a6": {
    #                "Name": "prestashop_prestashop_1",
    #                "EndpointID": "8aa2f54f62df6a26de0d4a5bee56cd90cd77b6dae8a29f9ff5638d26fdac21cc",
    #                "MacAddress": "02:42:ac:1c:00:03",
    #                "IPv4Address": "172.28.0.3/16",
    #                "IPv6Address": ""
    #            }
    #        },
    # ...
    ```
3. Run script using network name and internal ip
```
docker run --network prestashop_default --env PRESTASHOP_BASE_URL=http://172.28.0.3 -it prestashop-importer
```

**Note - On prestashop install it will save shop url as `http://127.0.0.1:8080`. When script runs from docker network, it will be constantly redirected to that url instead of internal (http://127.28.0.1 in my example). You will need to fix database table row in `ps_shop_url` to your ip address.**