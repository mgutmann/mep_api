# MEP API
MEP API is a very simple python package to scrape data on members of the European Parliament and output it in a neat JSON.

### Installation
Install this repository with pip:
```
pip install mep_api
pip install git+https://github.com/mgutmann/mep_api
```

### Usage

#### Scraping one MEP's information
To create an MEP object, import the package pass the URL of an MEP's EP home page. For instance:
```python
import mep_api
mep1 = mep_api.mep("https://www.europarl.europa.eu/meps/en/113892/ERIC_ANDRIEU/home")
```
Then you can add the information you want to the object:
```python
mep1.get_personal_data()
mep1.get_committees()
mep1.get_assistants()
```
or you can scrape everything at once:
```python
mep1.scrape_all()
```
You can then either get a JSON string containing all of the MEP's information and write to a file by running:
```python
mep1.to_json() #returns JSON string
mep1.to_json("file.json") #writes JSON file to specified path
```

#### Scraping multiple MEPs' information
It is possible to scrape data for multiple MEPs with a single line of code with `batch_scrape()` as follows:
```python
url_list = ["https://www.europarl.europa.eu/meps/en/113892/ERIC_ANDRIEU/home", "https://www.europarl.europa.eu/meps/en/124831/ISABELLA_ADINOLFI/home", "https://www.europarl.europa.eu/meps/en/28161/MARGRETE_AUKEN/home"]
mep_api.batch_scrape(url_list) #return JSON string
mep_api.batch_scrape(url_list, outfile="file.json") #writes JSON file to specified path
```
The `get_mep_urls()` function returns a list of all MEP home page URLs and makes collecting data on all MEPs at once easy. It is also possible to scrape available data for so-called "outgoing" MEPs, MEPs who have left the parliament during the current parliamentary term. To do so, it is sufficient to use the `batch_scrape()` function with the argument `add_outgoing = True` which is `False` by default. It is possible not to pass a `url_list` to the function to collect data only on outgoing MEPs. It is however not possible to collect data on single outgoing MEPs as of now.
```python
all_mep_urls = mep_api.get_mep_urls() #creates a list of all MEP URLS
mep_api.batch_scrape(all_mep_urls) #collects data on all current MEPs
mep_api.batch_scrape(all_mep_urls, add_outgoing=True) #collects data on all current MEPs and outgoing MEPs
mep_api.batch_scrape(add_outgoing=True) #collects data on outgoing MEPs
```
