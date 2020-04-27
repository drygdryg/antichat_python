# -*- coding: utf-8 -*-
from setuptools import setup

"""
:authors: drygdryg
:license: MIT
:copyright: (c) 2020 drygdryg
"""

version = '0.0.1'

setup(
    name='antichat',
    version=version,
    description='Simple forum.antichat.ru wrapper',

    author='drygdryg',

    keywords='wrapper scraper antichat',

    packages=['antichat'],
    python_requires='>=3.5',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
