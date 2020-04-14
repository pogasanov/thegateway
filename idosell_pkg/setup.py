#!/usr/bin/env python

from setuptools import setup

setup(
    name="idosell",
    py_modules=["importers", "Runner"],
    install_requires=["requests", "click", "gateway"],
    python_requires=">=3.7",
    packages=["idosell"],
)
