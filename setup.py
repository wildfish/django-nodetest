import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Django NodeTest",
    version="0.0.1",
    author="Jonas Hagstedt",
    author_email="hagstedt@gmail.com",
    description=("Test your JavaScript client with Django."),
    license="BSD",
    keywords="testing, javascript",
    url="https://github.com/jonashagstedt/django-nodetest",
    packages=find_packages(),
    long_description=read('README.md'),
    include_package_data=True,
    install_requires=[
        "Django >= 1.6, < 1.9"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
)
