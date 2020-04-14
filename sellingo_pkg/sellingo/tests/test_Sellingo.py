import os

import numpy as np
import pandas as pd
import pytest
from gateway import Product
from markdownify import markdownify as md
from sellingo.importer import Sellingo


@pytest.fixture()
def mock_df():
    filepath = os.path.join(os.path.dirname(__file__), "sellingo_mock_data.csv")
    return pd.read_csv(filepath)


@pytest.fixture()
def importer():
    return Sellingo("abc", "http://123.456.789.0/")


def test_fill_empty_ids(mock_df, importer):
    filled_data_frame = importer._fill_empty_ids(mock_df)
    groups = filled_data_frame.groupby("new_id")
    assert groups.ngroups == 2
    ids = filled_data_frame["new_id"]
    assert ids[ids == 13].count() == 4
    assert ids[ids == 14].count() == 3


@pytest.mark.parametrize("value,expected", [(np.nan, True), ("test", False), (123, False), (21.37, False)])
def test_is_value_non(value, expected, importer):
    assert importer._is_value_nan(value) == expected


def test_get_images_from_images_string(importer, mock_df):
    images_string = mock_df.iloc[0]["images"]
    images_urls = importer._Sellingo__get_images_from_images_string(images_string)
    expected_images_urls = [
        "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135681.jpg",
        "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135722.jpg",
        "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135763.jpg",
    ]
    assert sorted(images_urls) == sorted(expected_images_urls)


def test_get_initial_product(importer, mock_df):
    initial_product = mock_df.iloc[0]
    expected_product = Product(
        name=initial_product.title,
        price=initial_product.price_brutto,
        vat_percent=initial_product.vat,
        description_short="",
        description=md(initial_product.text),
        images_urls=[
            "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135681.jpg",
            "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135722.jpg",
            "http://123.456.789.0/public/upload/catalog/product/13/minigallery/original_13973135763.jpg",
        ],
    )
    assert importer._Sellingo__get_initial_product(initial_product) == expected_product


@pytest.mark.parametrize(
    "variant,expected",
    [
        ("Rozmiar:Rozmiar M#Kolor:pepitka", {"size": "M", "color": "pepitka"}),
        ("Rozmiar:Rozmiar M#Kolor:pepitka#Rozmiar:Rozmiar L#Kolor:pepitka", {"size": "L", "color": "pepitka"}),
        (
            "Rozmiar:Rozmiar M#Kolor:pepitka#Rozmiar:Rozmiar L#Kolor:pepitka#Rozmiar:Rozmiar XL#Kolor:pepitka",
            {"size": "XL", "color": "pepitka"},
        ),
    ],
)
def test_get_variant_data(variant, expected, importer):
    assert importer._Sellingo__get_variant_data(variant) == expected


def test_get_variant(importer, mock_df):
    initial_product: Product = importer._Sellingo__get_initial_product(mock_df.iloc[0])
    variant = mock_df.iloc[1]
    expected_product = Product(
        name=initial_product.name,
        price=variant.price_brutto,
        vat_percent=initial_product.vat_percent,
        stock=variant.quantity,
        description=initial_product.description,
        description_short=initial_product.description_short,
        images_urls=initial_product.images_urls,
        variant_data={"size": "M", "color": "pepitka"},
    )
    assert importer._Sellingo__get_variant(variant, initial_product) == expected_product
