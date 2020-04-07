#!/usr/bin/env python

from setuptools import setup

setup(
    name="prestashop",
    py_modules=["importers", "Runner"],
    install_requires=["jose", "simplejson", "click", "requests", "python-jose[cryptography]"],
    python_requires=">=3.7",
)
