#!/usr/bin/env python

from setuptools import setup

setup(
    name="magento",
    py_modules=["importer", "runner"],
    install_requires=["gateway"],
    python_requires=">=3.7",
    packages=["magento"],
)
