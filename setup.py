import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pyarubacloud",
    version="1.0.0",
    author="Aruba S.p.A.",
    author_email="luca.lasagni@staff.aruba.it",
    description="Python Interface to interact with ArubaCloud IaaS Service.",
    license="Apache License, Version 2.0",
    keywords="arubacloud.com cloud.it Cloud IaaS Api",
    url="https://github.com/Arubacloud/pyArubaCloud",
    packages=find_packages(),
    long_description="Python Interface to interact with ArubaCLoud IaaS Service.",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    install_requires=[
        'requests>=2.25.0',
        'jsonpickle>=2.0.0',
        'typing-extensions>=3.7.4;python_version<"3.8"',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-mock>=3.5.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
            'black>=20.8b1',
            'sphinx>=3.4.0',
        ]
    },
    python_requires='>=3.6',
)
