import requests
from bs4 import BeautifulSoup
import json


class mep:

    def __init__(self, url):
        self.url = url
        self.parl_id = self.url.split("/")[5]
        self.meetings = None
        self.name = None
        self.eu_party = None
        self.country = None
        self.national_party = None
        self.socials = None
        self.birthdate = None
        self.birthplace = None
        self.committees = None
        self.assistants = None
        self.history = None
        try:
            home_r = requests.get(self.url)
            home_r.encoding = "utf-8"
        except Exception as error:
            return error
        self.home_soup = BeautifulSoup(home_r.content, "html.parser")

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
        self.socials = {element.text.strip(): element["href"] for element in self.home_soup.find_all(
            "a", attrs={"data-toggle": "tooltip"}) if element['class'] != ['mr-1', 'ml-1', 'mr-sm-2', 'ml-sm-0', 'mb-2']}
        self.socials["E-mail"] = self.socials["E-mail"][::-1].replace("]ta[", "@").replace("]tod[", ".")[:-9]+"eu"
        self.birthdate = self.home_soup.find(
            "time", class_="sln-birth-date").text.strip()
        self.birthplace = self.home_soup.find(
            "span", class_="sln-birth-place").text.strip()

    def get_committees(self):
        committees = self.home_soup.find_all("div", class_="erpl_meps-status")
        committees_assignment = {status.find("h4").text: [
            committee.text for committee in status.find_all("a")] for status in committees}
        self.committees = committees_assignment

    def get_assistants(self):
        url_elements = self.url.split("/")[:-1]
        url_elements.append("assistants")
        assistants_url = "/".join(url_elements)
        try:
            r = requests.get(assistants_url)
            r.encoding = "utf-8"
        except Exception as error:
            return error
        soup = BeautifulSoup(r.content, 'html.parser')
        self.assistants = [element.text.strip() for element in soup.find_all(
            "span", class_="erpl_assistant")]

    def get_meetings(self):
        meeting_list = []
        i = 1
        while True:
            try:
                r = requests.get(
                    "https://www.europarl.europa.eu/meps/en/loadmore-meetings/past/"+self.parl_id+"?slice="+str(i))
                r.encoding = "utf-8"
            except Exception as error:
                return error
            soup = BeautifulSoup(r.content, 'html.parser')
            page_meetings_soup = soup.find_all(
                "div", class_="erpl_meps-activity")
            if len(page_meetings_soup) == 0:
                break
            page_meetings_list = [{
                'title': meeting.find("span", class_="t-item").text.strip(),
                'location': meeting.find("span", class_="date").text.strip(),
                'date': meeting.find("time").text.strip(),
                'role': meeting.find("div", class_="erpl_report mt-1 mb-25"),
                'committee': meeting.find("a", class_="erpl_badge erpl_badge-committee"),
                'subject': meeting.find("div", class_="erpl_report mt-1 mb-25"),
                'interest_group': [element.rstrip(",") for element in meeting.find("div", class_="erpl_rapporteur mb-25").text.strip().split("\xa0\n\t\t\t\t\t\n\t\t\t\t\t\t")]
            } for meeting in page_meetings_soup]
            for meeting in page_meetings_list:
                if meeting['committee'] != None:
                    meeting['committee'] = meeting['committee'].text.strip()
                if len(meeting['role'].text.split("-")) > 1:
                    meeting['role'] = meeting['role'].text.split("-")[0].strip()
                    meeting['subject'] = meeting['subject'].text.split("-")[1].strip()
                else:
                    meeting['role'] = meeting['role'].text.strip()
                    meeting['subject'] = None
                meeting_list.append(meeting)
            i += 1
            self.meetings = meeting_list

    def scrape_all(self):
        self.get_personal_data()
        self.get_committees()
        self.get_assistants()
        self.get_meetings()

    def to_json(self, outfile=None):
        data = {
            "url": self.url,
            "id": self.parl_id,
            "personal_info": {
                            "name": self.name,
                            "eu_party": self.eu_party,
                            "country": self.country,
                            "nat_part": self.national_party,
                            "social_media": self.socials,
                            "birthdate": self.birthdate,
                            "birthplace": self.birthplace
            },
            "committees": self.committees,
            "assistants": self.assistants,
            "meetings": self.meetings,
            "history": self.history
        }
        data_json = json.dumps(data, ensure_ascii=False)
        if outfile == None:
            return data_json
        else:
            with open(outfile, 'w+', encoding="utf-8") as budget_json:
                budget_json.write(data_json)