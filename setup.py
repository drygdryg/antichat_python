# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

"""
:authors: drygdryg
:license: MIT
:copyright: (c) 2020 drygdryg
"""

version = '0.0.7'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='antichat',
    version=version,
    description='Simple forum.antichat.ru wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',

    author='drygdryg',
    author_email='drygdryg2014@yandex.com',
    url='https://github.com/drygdryg/antichat_python',
    download_url='https://github.com/drygdryg/antichat_python/archive/v{}.zip'.format(version),

    keywords='wrapper scraper antichat',

    packages=['antichat'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers'
    ]
)
