from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='mep_api',
   version='0.1',
   description='A web scraping package for data on members of the European Parliament.',
   license="MIT",
   long_description=long_description,
   author='Michel Gutmann',
   url="http://www.github.com/mgutmann/mep_api",
   install_requires=['requests', 'beautifulsoup4'], #external packages as dependencies
)