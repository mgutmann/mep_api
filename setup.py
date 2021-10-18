from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='mep_api',
   version='0.1',
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
   packages=['mep_api'],
   package_data={'mep_api': ['euparty_abreviations.json']},
   python_requires=">=3.7",
   install_requires=['requests', 'beautifulsoup4', 'tqdm'], #external packages as dependencies
)