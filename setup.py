from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='mep_api-mgutmann',
   version='0.2',
   description='A web scraping package for data on members of the European Parliament.',
   license="MIT",
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='Michel Gutmann',
   author_email="mich.gutmann@gmail.com",
   url="http://www.github.com/mgutmann/mep_api",
   classifier=[
	"Programming Language :: Python :: 3",
	"Licence :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
   ],
   packages=['resources'],
   py_modules=['mep_api'],
   package_data={'resources': ['eu_party_abreviations.json']},
   python_requires=">=3.6",
   install_requires=['requests', 'beautifulsoup4'], #external packages as dependencies
)