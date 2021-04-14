#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_package_data(package):
    """
    Return all files under the root package, that are not in a package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return {package: filepaths}


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


name = "starlette-admin"
package_name = "starlette_admin"

setup(
    name=name,
    python_requires=">=3.7",
    version=get_version(package_name),
    url="https://github.com/accent-starlette/starlette-admin",
    license="MIT",
    description="Starlette Admin Site.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Stuart George",
    author_email="stuart@accentdesign.co.uk",
    packages=get_packages(package_name),
    package_data=get_package_data(package_name),
    install_requires=[
        'aiofiles',
        'itsdangerous',
        'jinja2',
        'python-multipart',
        'starlette-core'
    ],
    dependency_links=[
        'git+ssh://git@github.com/accent-starlette/starlette-core.git#egg=starlette-core-0.0.1'
    ],
    extras_require={
        "docs": [
            "mkdocs",
            "mkdocs-material",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
