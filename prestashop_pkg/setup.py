#!/usr/bin/env python

from setuptools import setup

setup(
    name="prestashop",
    py_modules=["importers", "Runner"],
    install_requires=["jose", "simplejson", "click", "requests", "python-jose[cryptography]", "gateway"],
    python_requires=">=3.7",
    packages=["prestashop",],
)