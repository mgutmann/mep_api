### MAIN FILE ###
# Contains the mep class and all package functions

# Imports
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import importlib.resources
import pkgutil
from tqdm import tqdm


class mep:

    def __init__(self, url=None, name=None, outgoing=False):
        if url != None:
            try: # Scrape MEP page
                home_r = requests.get(url)
                home_r.encoding = "utf-8"
            except Exception as error:
                return error
            # Assign basic properties
            self.url = home_r.url
            self.parl_id = self.url.split("/")[5]
            self.home_soup = BeautifulSoup(home_r.content, "html.parser")
        # Initialize properties
        self.outgoing = outgoing
        self.outdate = None
        self.meetings = None
        self.eu_party = None
        self.country = None
        self.national_party = None
        self.socials = None
        self.birthdate = None
        self.birthplace = None
        self.committees = None
        self.assistants = None
        self.history = None

    # This function collects basic personal data from the MEP's page
    # Properties it collects are either self-explanatory or have a comment
    def get_personal_data(self):
        self.name = self.home_soup.find(
            "span", class_="sln-member-name").text.strip()
        self.eu_party = self.home_soup.find(
            "h3", class_="erpl_title-h3 mt-1").text.strip()
        country_and_party = self.home_soup.find(
            "div", class_="erpl_title-h3 mt-1 mb-1").text.strip()
        self.country = country_and_party.split("-")[0].strip()
        self.national_party = country_and_party.split(
            "-")[1].split("(")[0].strip()
        self.history = [link.text[0] for link in self.home_soup.find_all("span", class_="t-x") if "parliamentary term" in link.text]
        # Dictionary of MEP social media accounts/email adresses
        self.socials = {element.text.strip(): element["href"] for element in self.home_soup.find_all(
            "a", attrs={"data-toggle": "tooltip"}) if element['class'] != ['mr-1', 'ml-1', 'mr-sm-2', 'ml-sm-0', 'mb-2']}
        # Unflipping email adresses, are stored flipped in Parliament Website's HTML
        if "Email" in self.socials:
            self.socials["Email"] = self.socials["Email"][::-1].replace("]ta[", "@").replace("]tod[", ".")[:-9]+"eu"
        elif "E-mail" in self.socials:
            self.socials["E-mail"] = self.socials["E-mail"][::-1].replace("]ta[", "@").replace("]tod[", ".")[:-9]+"eu"
        self.birthdate = self.home_soup.find(
            "time", class_="sln-birth-date")
        if self.birthdate != None: # Clean the birth date by removing blank spaces at the beginning and end of the string
            self.birthdate = self.birthdate.text.strip()
        self.birthplace = self.home_soup.find(
            "span", class_="sln-birth-place")
        if self.birthplace != None: # Clean the birth place by removing blank spaces at the beginning and end of the string
            self.birthplace = self.birthplace.text.strip()

    # Scrapes the committees of which the MEP is part
    def get_committees(self):
        committees = self.home_soup.find_all("div", class_="erpl_meps-status")
        committees_assignment = {status.find("h4").text: [
            committee.text for committee in status.find_all("a")] for status in committees}
        self.committees = committees_assignment

    # Scrapes names of listed assistants and consultants on MEP page
    def get_assistants(self):
        url_elements = self.url.split("/")[:-1]
        url_elements.append("assistants")
        assistants_url = "/".join(url_elements) # Creates url for the MEP's assistants webpage
        try:
            r = requests.get(assistants_url)
            r.encoding = "utf-8"
        except Exception as error:
            return error
        soup = BeautifulSoup(r.content, 'html.parser')
        self.assistants = [element.text.strip() for element in soup.find_all(
            "span", class_="erpl_assistant")]

    # Scrapes all of the MEP's reported meetings with special interest groups from the Parliament's website
    def get_meetings(self):
        meeting_list = []
        i = 1
        while True:
            try:
                r = requests.get(
                    "https://www.europarl.europa.eu/meps/en/loadmore-meetings/past/"+self.parl_id+"?slice="+str(i)) # Request returns five meetings, i=1 are the five latest, i=2, five before those, and so on
                r.encoding = "utf-8"
            except Exception as error:
                return error
            soup = BeautifulSoup(r.content, 'html.parser')
            page_meetings_soup = soup.find_all(
                "div", class_="erpl_meps-activity")
            if len(page_meetings_soup) == 0: # Checks the request result is not empty, if yes do not make any more requests, the loop reached the last "slice"
                break
            page_meetings_list = [{
                'title': meeting.find("span", class_="t-item").text.strip(),
                'location': meeting.find("span", class_="date").text.strip(),
                'date': meeting.find("time").text.strip(),
                'role': meeting.find("div", class_="erpl_report mt-1 mb-25"),
                'committee': meeting.find("a", class_="erpl_badge erpl_badge-committee"),
                'subject': meeting.find("div", class_="erpl_report mt-1 mb-25"),
                'interest_group': meeting.find("div", class_="erpl_rapporteur mb-25")
            } for meeting in page_meetings_soup] # Extract meeting information
            for meeting in page_meetings_list: # Format meeting information
                if meeting['committee'] != None:
                    meeting['committee'] = meeting['committee'].text.strip()
                if meeting["interest_group"] != None:
                    meeting["interest_group"] = [element.rstrip(",").strip() for element in meeting["interest_group"].text.split("\xa0\n\t\t\t\t\t\n\t\t\t\t\t\t")]
                if len(meeting['role'].text.split("-")) > 1:
                    meeting['role'] = meeting['role'].text.split("-")[0].strip()
                    meeting['subject'] = meeting['subject'].text.split("-")[1].strip()
                else:
                    meeting['role'] = meeting['role'].text.strip()
                    meeting['subject'] = None
                meeting_list.append(meeting)
            i += 1
            self.meetings = meeting_list

    # Run all scraping functions
    def scrape_all(self):
        self.get_personal_data()
        self.get_committees()
        self.get_assistants()
        self.get_meetings()

    # Return all scraped information in a dictionary
    def to_dict(self):
        data = {
            "url": self.url,
            "id": self.parl_id,
            "personal_info": {
                            "name": self.name,
                            "eu_party": self.eu_party,
                            "country": self.country,
                            "nat_party": self.national_party,
                            "social_media": self.socials,
                            "birthdate": self.birthdate,
                            "birthplace": self.birthplace
            },
            "committees": self.committees,
            "assistants": self.assistants,
            "meetings": self.meetings,
            "history": self.history,
            "outdate": self.outdate
        }
        return data

    # Output all scraped information to a .json file
    def to_json(self, outfile=None):
        data_json = json.dumps(self.to_dict(), ensure_ascii=False)
        if outfile == None:
            return data_json
        else:
            with open(outfile, 'w+', encoding="utf-8") as budget_json:
                budget_json.write(data_json)

# Collect infromation on all outgoing MEPs, which aren't listed with other MEPs
def scrape_outgoing_meps():
    r = requests.get("https://www.europarl.europa.eu/meps/en/incoming-outgoing/outgoing") # Page containing information on outgoing MEPs
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.content, "html.parser")
    outgoing_meps = {}
    reps = soup.find_all("div", class_="col-6 col-sm-4 col-md-3 col-lg-4 col-xl-3 text-center mb-3 erpl_member-list-item a-i") # List of HTML of representatives

    # Get the party abbreviations translations (parties are not listed with their full names on this page)
    with importlib.resources.path("mep_api", "euparty_abreviations.json") as data_path:
        with open(data_path, "r", encoding="utf-8") as abrevfile:
            abrevs = json.load(abrevfile)
    total = str(len(reps))

    progress=0
    for rep in tqdm(reps): # for each representative create an mep object and scrape information
        
        newmep = mep(outgoing=True)
        newmep.name = rep.find("div", class_="erpl_title-h5 t-item").text
        add_info = rep.find_all("div", class_="sln-additional-info")
        newmep.outdate = add_info[0].text.split(" ")[2]
        eu_party = add_info[1].text
        newmep.eu_party = abrevs[eu_party]
        newmep.country = add_info[2].text
        newmep.national_party = add_info[3].text
        newmep.url = rep.find("a", class_="erpl_member-list-item-content mb-2 t-y-block")["href"]
        newmep.parl_id = newmep.url.split("/")[-1]
        newmep.get_meetings()
        hist_r = requests.get(newmep.url)
        hist_r.encoding = "utf-8"
        hist_soup = BeautifulSoup(hist_r.content, "html.parser")

        newmep.history = []
        for ep in hist_soup.find("div", class_="erpl_accordion-item-content a-i-none show").find_all("span", class_="t-x"):
            newmep.history.append(ep.text.split(" ")[0][0])
        newmep.birthdate = hist_soup.find(
            "time", class_="sln-birth-date")
        if newmep.birthdate != None:
            newmep.birthdate = newmep.birthdate.text.strip()
        newmep.birthplace = hist_soup.find(
            "span", class_="sln-birth-place")
        if newmep.birthplace != None:
            newmep.birthplace = newmep.birthplace.text.strip()
        
        outgoing_meps[newmep.parl_id] = newmep.to_dict()
        progress += 1

    return outgoing_meps

# Function to scrape MEP information for all MEPs in a list of MEP URLs
def batch_scrape(url_list=None, outfile=None, add_outgoing=False):
    batch = {}
    if url_list != None:
        print("Collecting data on meps in submitted list.")
        total=len(url_list)
        for url in tqdm(url_list):
            rep = mep(url)
            rep.scrape_all()
            batch[str(rep.parl_id)] = rep.to_dict()
    if add_outgoing:
        print("Collecting data on outgoing meps.")
        outgoing_meps = scrape_outgoing_meps()
        for rep in tqdm(outgoing_meps):
            batch[rep] = outgoing_meps[rep]
    batch_json = json.dumps(batch, ensure_ascii=False)
    if outfile == None:
        return batch_json
    else:
        with open(outfile, "w+", encoding="utf-8") as outjson:
            outjson.write(batch_json)

# Get URLs for all MEPs from the parliament'slist of MEP page
def get_mep_urls():
    r = requests.get("https://www.europarl.europa.eu/meps/en/full-list/all")
    soup = BeautifulSoup(r.content, "html.parser")
    mep_url_list = [element["href"] for element in soup.find_all("a", class_="erpl_member-list-item-content mb-2 t-y-block")]
    for element in tqdm(soup.find_all("a", class_="erpl_member-list-item-content t-y-block")):
        mep_url_list.append(element["href"])
    return mep_url_list