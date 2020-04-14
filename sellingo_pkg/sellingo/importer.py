import numpy as np
import olefile
import pandas as pd
from markdownify import markdownify as md

from gateway.models import Product


# pylint: disable=too-few-public-methods
class Sellingo:
    def __init__(self, filepath, shop_url):
        self.shop_url = shop_url
        self.filepath = filepath
        self.data_frame = None
        self.products_count = 0
        self.current_product_index = 0
        self.products = dict()

    @staticmethod
    def _read_file(filepath) -> pd.DataFrame:
        with open(filepath, "rb") as file:
            ole = olefile.OleFileIO(file)
            if ole.exists("Workbook"):
                stream = ole.openstream("Workbook")
                return pd.read_excel(stream, engine="xlrd")
            raise IOError

    @staticmethod
    def _fill_empty_ids(data_frame):
        """
        File exported by Sellingo looks like this:

        1;Base product;...
         ;Variant of base product;...

         ;Another variant of base product;...
        2;Another base product;...
         ;Variant of another base product;...

        So in order to easier group product variants with product this function creates new_id,
        which is assigned to both base product and its variants.
        :param data_frame:
        :return:
        """
        data_frame["new_id"] = data_frame["ID produktu"]
        data_frame["new_id"] = data_frame["new_id"].dropna().diff()
        data_frame.loc[0, "new_id"] = data_frame.loc[0, "ID produktu"]
        data_frame["new_id"] = data_frame["new_id"].fillna(0).cumsum()
        data_frame["new_id"] = data_frame["new_id"].astype({"new_id": "int32"})
        return data_frame

    @staticmethod
    def _is_value_nan(value):
        try:
            return np.isnan(value)
        except TypeError:
            return False

    def __get_images_from_images_string(self, images_string):
        """
        Example value of images string from Sellingo file looks like this:

        'public/upload/catalog/product/13/minigallery/original_13973135681.jpg;
        public/upload/catalog/product/13/minigallery/original_13973135722.jpg'

        So this function splits it and appends shop url at the beginning

        :param images_string:
        :return:
        """
        return [f"{self.shop_url}{url}" for url in images_string.split(";")]

    def __get_initial_product(self, initial_product: pd.Series) -> Product:
        images = (
            self.__get_images_from_images_string(initial_product.images)
            if not self._is_value_nan(initial_product.images)
            else []
        )
        name = initial_product.title
        price = initial_product.price_brutto
        vat = initial_product.vat
        description = md(initial_product.text) if not self._is_value_nan(initial_product.text) else ""
        description_short = md(initial_product.textshort) if not self._is_value_nan(initial_product.textshort) else ""
        return Product(
            name=name,
            price=price,
            vat_percent=vat,
            description_short=description_short,
            description=description,
            images_urls=images,
        )

    @staticmethod
    def __get_variant_data(variants):
        variant_data_list = variants.split("#")[-2:]
        variant_data = dict()
        for variant_data_element in variant_data_list:
            variant_data_value = variant_data_element.split(":")
            variant_data_value[0] = variant_data_value[0].replace("Rozmiar", "size")
            variant_data_value[0] = variant_data_value[0].replace("Kolor", "color")
            variant_data_value[1] = variant_data_value[1].replace("Rozmiar ", "")
            variant_data[variant_data_value[0]] = variant_data_value[1]
        return variant_data

    def __get_variant(self, variant: pd.Series, initial_product: Product) -> Product:
        variant_images = (
            self.__get_images_from_images_string(variant.images)
            if not self._is_value_nan(variant.images)
            else initial_product.images_urls
        )
        variant_name = variant.title if not self._is_value_nan(variant.title) else initial_product.name
        variant_price = variant.price_brutto if not np.isnan(variant.price_brutto) else initial_product.price
        variant_description = md(variant.text) if not self._is_value_nan(variant.text) else initial_product.description
        variant_description_short = (
            md(variant.textshort) if not self._is_value_nan(variant.textshort) else initial_product.description_short
        )
        variant_vat = variant.vat if not self._is_value_nan(variant.vat) else initial_product.vat_percent
        variant_stock = variant.quantity
        variant_data = self.__get_variant_data(variant.variants)
        return Product(
            name=variant_name,
            price=variant_price,
            vat_percent=variant_vat,
            stock=variant_stock,
            description=variant_description,
            description_short=variant_description_short,
            images_urls=variant_images,
            variant_data=variant_data,
        )

    def _set_variant(self, variant_data: pd.Series, initial_product: Product, product_id: int):
        variant = self.__get_variant(variant_data, initial_product)
        self.products[product_id].append(variant)

    def _parse_to_product(self, element: pd.DataFrame):
        self.current_product_index += 1
        print(f"Importing: {self.current_product_index} / {self.products_count}")
        initial_product = self.__get_initial_product(element.iloc[0])
        product_id = element.iloc[0].new_id
        initial_variants = element.iloc[1:]
        self.products[product_id] = []
        initial_variants.apply(self._set_variant, args=(initial_product, product_id), axis=1)

    def _parse_df(self):
        grouped_df = self.data_frame.groupby("new_id")
        self.products_count = grouped_df.ngroups
        grouped_df.apply(self._parse_to_product)

    def build_products(self):
        input_data_frame = self._read_file(self.filepath)
        self.data_frame = self._fill_empty_ids(input_data_frame)
        self._parse_df()
        return list(self.products.values())
