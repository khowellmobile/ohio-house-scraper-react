from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
import time
import json


def get_representative_list():
    """rep_names = ["munira-abdullahi", "darnell-t-brewer", "karen-brownlee"]"""
    rep_names = []
    url = "https://ohiohouse.gov/members/directory?start=1&sort=LastName"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    rep_name_divs = soup.find_all("div", class_="media-overlay-caption-text-line-1")

    for div in rep_name_divs[:30]:
        # Use re.sub in future
        rep_names.append(
            div.text.strip().replace(" ", "-").replace(".", "").replace(",", "").lower()
        )

    return rep_names


async def checkURLResponse(response):
    if response.status:
        if response.status != 200:
            return 1
        else:
            return 0
    else:
        return 0


def getTime():
    current_time = time.localtime()
    formatted_time = time.strftime("%H:%M:%S", current_time)

    return formatted_time


def get_ai_prompt(combined_bio):
    ai_prompt_text = """

    The text at the end of this prompt is a biography for a memeber Ohio State House of Representatives. Using the biography return a summarization of the biography. The summarization format and notes on each section is described next.

    Summarization format and information:

    1. A comma delimited list of their education.
        a. The list should follow the format 'University, Degree, Area of Study'.
        b. If one of the three sections is not specified then leave it blank. In this case do not include the comma either. This means the list could be "University, Degree", "Degree, Area of Study", Etc.
        c. Here is an example of what a representatives list might look like "The Ohio State University, MS, Political Science, Ohio University, BS, Nursing"
    2. A comma delimited list of their past political experience. 
        a. The list should follow the format 'Organization, Role, Term'
        b. If one of the three sections is not specified then leave it blank. In this case do not include the comma either. This means the list could be "Organization, Term", "Role, Term", Etc.
        c. The political experience can include Previous Terms in the house or senate of anywhere and city councils.
        d. Here is an example of what a representatives list might look like "House of Representatives, Majority Whip, 2017-2021, Columbus City Council, Gahanna City Council, President"
    3. A comma delmited list of their employment history.
        a. The list should follow the format 'Organization, Role, Status'.
        b. If one of the three sections is not specified then leave it blank. In this case do not include the comma either. This means the list could be "Organization, Status", "Role, Status", Etc.
        c. Include any instances of buying, selling, or starting businesses
        d. Here is an example of what a representatives list might look like "JP Morgan Chase, Accountant, Formerly, Bought Johns Company, Started Columbus Mowing"
    4. A comma delimited list of their community involvement. This includes churches, local organizations, school boards, etc.
        a. The list should follow the format 'Organization, role'.
        b. It is possible that only an organization is listed. If so then include the organziation. E.g. "Church of God"
        c. Here is an example of what a representatives list might look like "Member of General Church, Neighborhood Watch, Captain"

    Listed next in any general instructions for generating the lists and the total output.

    1. The total output should be a list delimited by "|". Where each section (education, politcal history, employment history, community involvement) makes up an element in the list
    2. If a biography does not mention a section then do not include it. In this case still delimit the section. E.g. if a rep does not have employement history "Education list|Political history list||Community involvement list" would be the format of the output
    3. If no text for the bio is provided then return "||||"
    4. No new line operators or instances of the string ", ," should exist in the response 

    Biography:
    """

    return ai_prompt_text + " " + combined_bio


def create_json_list(people_dict):
    people_json = json.dumps(people_dict)

    return people_json
