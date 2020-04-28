#!/usr/bin/env python

from setuptools import setup

setup(
    name="sellingo",
    py_modules=["importer", "runner"],
    install_requires=["requests", "markdownify", "gateway"],
    python_requires=">=3.7",
    packages=["sellingo"],
)
