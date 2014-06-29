#!/usr/bin/env python

import modelo

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = []

packages = [
    "modelo",
    "modelo.model",
    "modelo.trait",
]

setup(
    name="modelo",
    version=modelo.__version__,
    description="Simple models independent of SQL/ORM.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/modelo",
    install_requires=requires,
    packages=packages,
    license="BSD",
    classifiers=(
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ),
)
