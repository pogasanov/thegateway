#!/usr/bin/env python

from setuptools import setup

setup(
    name="shoper",
    py_modules=["importers", "runner"],
    install_requires=[
        "jose",
        "simplejson",
        "click",
        "requests",
        "python-dotenv",
        "python-jose[cryptography]",
        "gateway",
    ],
    python_requires=">=3.7",
    package_dir={"shoper": "shoper"},
    package_data={"shoper": ["tests/*.json"]},
    packages=["shoper",],
)
