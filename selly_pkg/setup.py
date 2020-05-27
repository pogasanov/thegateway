#!/usr/bin/env python

from setuptools import setup

setup(
    name="selly",
    py_modules=["importer", "runner", "utils"],
    install_requires=["requests", "markdownify", "click", "gateway"],
    python_requires=">=3.7",
    packages=["selly"],
    entry_points="""
        [console_scripts]
        selly=selly.runner:cli
    """,
)
