from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name="BuildTool",
    version="1.0",
    description="Python Build Tool to support {NS} builds/tests for Android an iOS",
    author="alexZaicev",
    author_email="alex.zaicef@gmail.com",
    packages="BuildTool",
    install_requires=["win10toast", "pync", "schedule"],
    long_description=long_description
)
