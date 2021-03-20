# MEP API
MEP API is a very simple python package to scrape data on members of the European Parliament and outputs it in a neat JSON.

### Installation
Install this repository by using the following command:
```
pip install git+https://github.com/mgutmann/mep_api
```

### Usage
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
mep1.to_json("file.json") #writes json file to specified path
```