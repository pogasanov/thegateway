#!/usr/bin/env python

from setuptools import setup

setup(
    name="wordpress",
    py_modules=["importers", "runner"],
    install_requires=["woocommerce", "gateway"],
    python_requires=">=3.7",
    packages=["wordpress"],
)
