#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""wheres_waldo setup script"""
from setuptools import setup

import versioneer

if __name__ == "__main__":
    setup(
        name="wheres_waldo",
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        zip_safe=False,
    )
