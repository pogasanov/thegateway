import logging
from decimal import Decimal

import requests
from gateway import Product, download_image

# pylint: disable=R0903
LOGGER = logging.getLogger(__name__)


class Magento:
    PRODUCT_TYPE_SINGLE = "single"
    PRODUCT_TYPE_CONFIGURABLE = "configurable"

    def __init__(self, BASE_URL, API_ACCESS_TOKEN):
        self.api_hostname = BASE_URL

        self.parsed_ids = set()
        self.default_tax = 23

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {API_ACCESS_TOKEN}"})

        self.base_media_url = self._get_base_media_url()
        self.attributes = self._get_possible_product_attributes()
        self.taxes = self._get_tax_rates()

    def _get_base_media_url(self):
        """
        Get base media url that will be used to download images.
        """
        response = self.session.get(f"{self.api_hostname}/rest/V1/store/storeConfigs")
        return response.json()[0]["base_media_url"]

    def _get_possible_product_attributes(self):
        """
        Get list of possible product attributes that will be used to get product variant of configurable products.
        """
        response = self.session.get(
            f"{self.api_hostname}/rest/V1/products/attributes", params={"searchCriteria[pageSize]": 9999},
        )
        response.raise_for_status()
        store_attributes = {}
        for att in response.json()["items"]:
            if att["options"]:
                store_attributes[att["attribute_id"]] = {
                    "code": att["attribute_code"],
                    "options": {o["value"]: o["label"] for o in att["options"]},
                }
        return store_attributes

    def _get_tax_rates(self):
        """
        Get list of tax rates and tax rules from magento. Tries to map every product tax class with
        corresponding tax rate. If product tax class has more than 1 tax rate, use default tax rate instead.
        """
        response = self.session.get(
            f"{self.api_hostname}/rest/V1/taxRates/search", params={"searchCriteria[pageSize]": 9999}
        )
        response.raise_for_status()
        tax_rates = {rate["id"]: rate["rate"] for rate in response.json()["items"]}

        response = self.session.get(
            f"{self.api_hostname}/rest/V1/taxRules/search", params={"searchCriteria[pageSize]": 9999}
        )
        response.raise_for_status()
        taxes = {}
        for rule in response.json()["items"]:
            if len(rule["tax_rate_ids"]) > 1:
                tax = self.default_tax
            else:
                tax = tax_rates[rule["tax_rate_ids"][0]]

            for product_tax_id in rule["product_tax_class_ids"]:
                if product_tax_id in taxes and taxes[product_tax_id] != self.default_tax:
                    taxes[product_tax_id] = self.default_tax
                else:
                    taxes[product_tax_id] = tax
        return taxes

    def build_products(self):
        """
        Returns a generator with products, grouped by variants
        Configurable products are products that has different variants
        Single products are products without variant
        We need to fetch configurable products first because single products include variants of configurable products,
        so to not overlap, we will exclude already returned products
        """
        yield from self._get_configurable_products()
        yield from self._get_single_products()

    def _get_configurable_products(self):
        """
        Returns a generator with configurable products. Each product is a list of corresponding variants.
        Saves all parsed ids of variants in `self.parsed_ids` so in future we will not refetch them.
        """
        for products, total in self._fetch_products(product_type=Magento.PRODUCT_TYPE_CONFIGURABLE):
            for i, product in enumerate(products, 1):
                LOGGER.info("Parsing CONFIGURABLE product %s/%s", i, total)

                variant_ids = product["extension_attributes"]["configurable_product_links"]
                variant_options = [
                    self.attributes[int(x["attribute_id"])]
                    for x in product["extension_attributes"]["configurable_product_options"]
                ]

                product_variants = []
                for variants, _ in self._fetch_products(ids=variant_ids):
                    for variant in variants:
                        prepared_variant = self._build_product_from_data(variant)
                        prepared_variant.variant_data = {
                            option["code"]: option["options"][
                                self._value_by_attribute_code(variant["custom_attributes"], option["code"])
                            ]
                            for option in variant_options
                        }
                        product_variants.append(prepared_variant)
                        self.parsed_ids.add(variant["id"])
                yield product_variants

    def _get_single_products(self):
        """
        Returns a generator with single products. Each product is a list of 1 variant.
        We exclude products that were already fetched with _get_configurable_products.
        """
        for products, total in self._fetch_products(product_type=Magento.PRODUCT_TYPE_SINGLE):
            total -= len(self.parsed_ids)
            for i, product in enumerate(products, 1):
                LOGGER.info("Parsing SINGLE product %s/%s", i, total)
                if product["id"] not in self.parsed_ids:
                    yield [self._build_product_from_data(product)]

    def _build_product_from_data(self, data):
        """
        Wrap magento data object to Product model.
        """
        return Product(
            name=data["name"],
            sku=data["sku"],
            price=Decimal(data["price"]),
            stock=self._fetch_product_stock(data["sku"]),
            vat_percent=self._get_product_tax(data),
            description=self._value_by_attribute_code(data["custom_attributes"], "description"),
            images=[self._fetch_product_image(i["file"], data["name"]) for i in data["media_gallery_entries"]],
        )

    @staticmethod
    def _value_by_attribute_code(items, attribute_code):
        """
        Try to find value of magento custom attribute using attribute code. Throws AttributeError if can't find.
        """
        try:
            return next(x["value"] for x in items if x["attribute_code"] == attribute_code)
        except StopIteration as exception:
            raise AttributeError from exception

    def _get_product_tax(self, product):
        """
        Check if product has tax details. If not, defaults to default_tax.
        """
        try:
            return self.taxes[int(self._value_by_attribute_code(product["custom_attributes"], "tax_class_id"))]
        except AttributeError:
            return self.default_tax

    def _fetch_products(self, **kwargs):
        """
        Returns a generator with list of products, paged by page_size.
        """
        page = 1
        page_size = 20

        response = self.session.get(
            f"{self.api_hostname}/rest/V1/products", params=self._requests_params(page_size, page, **kwargs),
        )
        response.raise_for_status()
        products = response.json()
        yield products["items"], products["total_count"]

        while products["total_count"] > page_size * page:
            page += 1
            response = self.session.get(
                f"{self.api_hostname}/rest/V1/products", params=self._requests_params(page_size, page, **kwargs),
            )
            response.raise_for_status()
            products = response.json()
            yield products["items"], products["total_count"]

    @staticmethod
    def _requests_params(page_size, page, product_type=None, ids=None):
        """
        Constructs request params for magento product search engine. Takes page size and current page.
        product_type can be 'simple', 'configurable', 'bundle'
        ids is a list of id of product that should be fetched.
        """
        params = {"searchCriteria[pageSize]": page_size, "searchCriteria[currentPage]": page}
        if product_type:
            params["searchCriteria[filter_groups][0][filters][0][field]"] = "type_id"
            params["searchCriteria[filter_groups][0][filters][0][condition_type]"] = "eq"
            params["searchCriteria[filter_groups][0][filters][0][value]"] = product_type
        if ids:
            params["searchCriteria[filter_groups][1][filters][0][field]"] = "entity_id"
            params["searchCriteria[filter_groups][1][filters][0][condition_type]"] = "in"
            params["searchCriteria[filter_groups][1][filters][0][value]"] = ",".join(map(str, ids))
        return params

    def _fetch_product_image(self, filepath, filename):
        """
        Returns a ResponseStream object for product image.
        """
        return download_image(f"{self.base_media_url}catalog/product{filepath}", filename)

    def _fetch_product_stock(self, product_sku):
        """
        Returns a product stock quantity.
        """
        response = self.session.get(f"{self.api_hostname}/rest/V1/stockItems/{product_sku}")
        response.raise_for_status()
        return Decimal(response.json()["qty"])
