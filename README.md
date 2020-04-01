# Integrations

## The Gateway platform 
Our platform is a multivendor marketplace, built in-house. It's serverless & containerless FaaS on AWS. The back-end is 100% Python3.

### API

The Swagger UI for the API (development version) can be found at https://sma.dev.gwapi.eu

**Create a product**

| HTTP Method | Route              | Description |
| :---------: | ---------------------- | ---------------------- |
|   `POST`    | `/organizations​/{organization_id}​/products​`  |  [Create new product](https://public.the.gw/apidoc/index.html?url=https%3A//sma.dev.gwapi.eu/swagger.json#/Product/post_organizations__organization_guid__products__guid__)

---

##### The Product Object
`Product` is an object representing a product that belongs to a shop. It can also represent a delivery method, depending on the type. 

**Parameters**

| Parameter        |              Type               | Description                                                                                                              |
| ---------------- | :-----------------------------: | ------------------------------------------------------------------------------------------------------------------------ |
| **`activated`**  |             string              | Timestamp[^1] representing the UTC datetime of the product's most recent activation. Null means product is not activated |
| **`brief`**      |             string              | Short one line description of the product.                                                                               |
| **`created`**    |             string              |                                                                                                                          |
| **`data`**       |             object              | Miscelenious field for additional product data. TODO                                                                     |
| **`desc`**       |             string              | Detailed description of the product.                                                                                     |
| **`guid`**       |             string              | Unique identifier for the object.                                                                                        |
| **`images`**     |         Array of string         | List of image urls belonging to the object.                                                                              |
| **`name`**       |             string              | Name of the product                                                                                                      |
| **`owner_guid`** |             string              | Unique identifier of the retailer that owns the product.                                                                 |
| **`price`**      |   [VatPrice](#vatPriceObject)   |                                                                                                                          |
| **`pricing`**    |             string              | Unique identifier of a pricing object.                                                                                   |
| **`suppliers`**  |         Array of string         | List of unique identifiers of retailers currently selling the product                                                    |
| **`tags`**       |          Array of Tags          | List of Tag objects that are associated with the product.                                                                |
| **`timestamps`** | [Timestamps](#timestampsObject) |                                                                                                                          |
| **`type`**       |             string              | Type equals to 'default' if object is a normal product, or'delivery_method' if object is a delivery method.              |
| **`updated`**    |             string              | Timestamp[^1] respresenting the last UTC datetime whenthe object was edited.                                             |

<details>

  <summary>
  OPEN Example product object
  </summary>

```JSON
{
  "activated": "2019-09-24T12:52:18.249Z",
  "brief": "string",
  "created": "2019-09-24T12:52:18.249Z",
  "data": {},
  "desc": "string",
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "images": [
    "http://www.image-source.com/image-id/"
  ],
  "name": "A Product Name",
  "owner_guid": "4ka85f64-5717-4562-b3fc-2c063f66afa6",
  "price": {
    "base": {
      "unit": {
        "amount": 0,
        "vat": 0,
        "vat0": 0,
        "vat_percent": 0
      }
    },
    "cost": {
      "unit": {
        "amount": 0,
        "vat": 0,
        "vat0": 0,
        "vat_percent": 0
      }
    },
    "final": {
      "unit": {
        "amount": 0,
        "vat": 0,
        "vat0": 0,
        "vat_percent": 0
      }
    },
    "original": {
      "unit": {
        "amount": 0,
        "vat": 0,
        "vat0": 0,
        "vat_percent": 0
      }
    },
    "vat_class": 0
  },
  "pricing": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "suppliers": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ],
  "tags": [
    {
      "active": true,
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "images": [
        {
          "url": "string"
        }
      ],
      "name": "string",
      "owner": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "parent_guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "subtags": [
        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      ]
    }
  ],
  "timestamps": {
    "created": "2019-09-24T12:52:18.249Z"
  },
  "type": "string",
  "updated": "string"
}

```
</details>

---

### Other relevant objects

##### VatPrice object
| Parameter / Argument                                                                | Type   | Description                                                                     |
| ----------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------- |
| **`amount`** <span style="color:red; font-variant: small-caps">required</span>      | number | Number larger than 0 representing the price                                     |
| **`currency`** <span style="color:red; font-variant: small-caps">required</span>    | string | Should be `zl`                                                                  |
| **`vat`** <span style="color:red; font-variant: small-caps">required</span>         | number |                                                                             |
| **`vat0`** <span style="color:red; font-variant: small-caps">required</span>        | number |                                                                             |
| **`vat_percent`** <span style="color:red; font-variant: small-caps">required</span> | number | Number larger than 0 representing the value added tax. e.g. `23` would mean 23% |

---

### Creating new products with variants
To create products with variants, a variant tag must first be created. The variant tag will be the identfier allowing the system to know that these prodcuts are variants of each other.

#### Create new variant tag
| HTTP Method | Route              | Description |
| :---------: | ---------------------- | ---------------------- |
|   `POST`    | `/tags/`  |  [Create new variant tag](https://public.the.gw/apidoc/index.html?url=https%3A//sma.dev.gwapi.eu/swagger.json#/Tags/post_tags_)

##### Request payload
**Template**
```
{
  name: ""
  type: "variant"
}
```
**Properties of concern**
| Property | Type | Required | Example | Description
| :--------: | :--------:|:--------: |:--------: |:--------: |
| name | string | Yes|"Phone S6"| The name of the product variant |

**Example**
```
{
  name: "Phone S6"
  type: "variant"
}
```

##### Timestamps object
| Parameter / Argument                                        | Type   | Description                                                                    |
| ----------------------------------------------------------- | ------ | ------------------------------------------------------------------------------ |
| **`created`** <span style="color:lightgrey">optional</span> | string | Timestamp[^1] representing the UTC datetime when the object was first created. |

[^1]: Timestamp strings are always written in ISO 8601 datetime extended notation. (yyyy-mm-ddThh:mm:ss.ffffff	2008-09-15T15:53:00)

## Authentication
The authorization is a fixed -format JWT token with '{"iss": "shop:{shop_guid}", "organization_guid": "{shop_guid}"} signed with a per-shop shared secret HS256 key. There will be multiple vendors using each of the 3rd party platforms and each will probably have different credentials to those systems - we really haven't had time to look in to the 3rd party platform documentation so I don't have much info that isn't available with 10 seconds of googling, sorry! :/  

## Third party platforms

### Top priority
 - [x] IAI - @sunil.techwob
 - [ ] Retalia
 - [x] PrestaShop - @pogasanov
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


## Practicalities

> Commit early, commit often!

For each different integration, make a branch and a top level directory named after the 3rd party platform, e.g. `prestashop` or `magento` - and submit a pull request with a title `WIP: ...` as soon as you start.
