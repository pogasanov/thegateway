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