"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

APP = ['BuildTool\\main.py']
DATA_FILES = []
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name="BuildTool",
    version="1.0",
    description="Python Build Tool to support {NS} builds/tests for Android an iOS",
    author="alexZaicev",
    author_email="alex.zaicef@gmail.com",
    packages="BuildTool",
    install_requires=["schedule"],
    long_description=long_description
)
