#!/usr/bin/env python

from setuptools import setup

setup(
    name="gateway",
    py_modules=["gateway", "models", "utils"],
    install_requires=["jose", "simplejson", "click", "requests", "python-jose[cryptography]"],
    python_requires=">=3.7",
    packages=["gateway",],
)
