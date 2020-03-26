# Integrations

## The Gateway platform 
Our platform is a multivendor marketplace, built in-house. It's serverless & containerless FaaS on AWS. The back-end is 100% Python3.

### API

The Swagger UI for the API (development version) can be found at https://sma.dev.gwapi.eu

## Authentication
The authorization is a fixed -format JWT token with '{"iss": "shop:{shop_guid}", "organization_guid": "{shop_guid}"} signed with a per-shop shared secret HS256 key. There will be multiple vendors using each of the 3rd party platforms and each will probably have different credentials to those systems - we really haven't had time to look in to the 3rd party platform documentation so I don't have much info that isn't available with 10 seconds of googling, sorry! :/  

## Third party platforms

### Top priority
 - [x] IAI - @sunil.techwob
 - [ ] Retalia
 - [x] PrestaShop - @poganasov
 - [ ] shoper.pl
 - [ ] SubiektGT

### Tier 2
 - [ ] Magento
 - [ ] IdoSell

### Tier 3
 - [ ] Selly
 - [ ] Sellingo / SellAssist
 - [ ] Selly
 - [ ] Forteca
 - [ ] ClickShop

## Process

### Step 1
First step would be importing product data from the 3rd party platform - at it's simplest this would be just 1 HTTP POST calls per product to /dashboard/webshop/{shop_guid}/products for most vendorsi. It's a bit more complicated for vendors that have multiple variants of same product (such as different sizes or colors) - then you would also need to create tags with type "variant" (POST /webshops/{shop_guid}/tags/) and add the tag guids to product's POST body. Also, if e.g. product images are not to be hotlinked - they must be re-uploaded to S3 either directly or via /uploads/ and /downloads/ endpoints in GW API

### Step 2
The second step is updating stock levels / inventory bidirectionally - this will be a bit more complex and we'll focus on that only after all the product data integrations have been implemented. In practice we will most likely create an additional endpoint that can be called via the Gateway API as a web hook.


## Implementation details

Each different platform integration should be a separate self-contained directory in this repository with the following restrictions.:

* There must be a `Dockerfile` on top level, that will build an image when run with `docker run -i` will prompt for token signing key, shop guid and credentials to third party platform.
* all tests must be in a subdirectory called tests/ 
* external libraries must be included in some standard way (e.g. setup.py, requirements.txt etc) for all external software instead of just hard-coding them in the Dockerfile (when applicable)



