# WordPress WooCommerce
[About WooCommerce](https://woocommerce.com/my-dashboard/)

## Setup RestApi
1. Go to admin panel `<your-domain.com>/wp-admin` and login
2. Go to `WooCommerce` **>** `Settings` then go to `Advanced`, then `Legacy API`. Check `Enable the legacy REST API` and save.
3. Now (still in `Advanced` tab) go to `REST API` and click `Add key`
4. Fill the form and `Generate API key`
5. What we need is `Consumer key` and `Consumer secret`

[Tutorial with images](https://sgwebpartners.com/how-to-use-woocommerce-api/) (Only step  1 and 2)

## Setup test environment
 1. Run `docker-compose up`
 2. Go to `http://localhost:8000` in order to setup admin user
 3. Run `ngrock http 8000` (requires [ngrock](https://ngrok.com/)) and and copy address ex. _`http://a41bcc60.ngrok.io`_
 5. Go to `http://localhost:8000/wp-admin/options-permalink.php` and set `Common Settings` other than `Plain`
 4. Go to `http://localhost:8000/wp-admin/options-general.php` and set  `WordPress Address (URL)` and `Site Address (URL)` with ngrock address and save. Now your page should be working on ngrock address
 6. Go to `Plugins` > `Add New` and install WooCommerce
 7. Setup RestApi (above)
 8. Done!