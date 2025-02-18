from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
import time
import json
import re


def get_representative_list():
    rep_names = []
    url = "https://ohiohouse.gov/members/directory?start=1&sort=LastName"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    rep_name_divs = soup.find_all("div", class_="media-overlay-caption-text-line-1")

    for div in rep_name_divs:
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
    ai_prompt_text = """ The following is a biography of a member of the Ohio State House of Representatives. Based on the biography, return a summarization following these instructions:

        Summarization Format:
            1. Education
                a. List educational background in the format: University, Degree, Area of Study.
                b. If any of the three sections are missing, omit that section and any commas. For example:
                    b1. "The Ohio State University, MS, Political Science"
                    b2. "Ohio University, BS, Nursing"

            2. Political Experience
                a. List political experience in the format: Organization, Role, Term.
                b. Include terms from any Ohio House or Senate, U.S. House or Senate, or City Council.
                c. If any section is missing, omit it and do not add extra commas. For example:
                    c1. "House of Representatives, Majority Whip, 2017-2021"
                    c2. "Columbus City Council, President"

            3.Employment History
                a. List past employment in the format: Organization, Role, Status.
                b. Include any business ventures like buying or starting companies.
                c. If any section is missing, omit it and do not add extra commas. For example:
                    c1. "JP Morgan Chase, Accountant, Formerly"
                    c2. "Bought Johns Company"
                    c3. "Started Columbus Mowing"

            4. Community Involvement
                a. List community involvement in the format: Organization, Role.
                b. This includes churches, local organizations, school boards, etc.
                c. If only the organization is available, list it alone. For example:
                    c1."Church of God"
                    c2."Neighborhood Watch, Captain"

        General Instructions for Summarization:
            1. Segments of information (jobs, terms in office, organizations) are only put in the category they most belong in.
                a. Examples include
                    a1. A term in the Ohio House should only be put into Political Experience and should not also be put into into community involvement.
                    a2. A degree should not be listed in Community Involvement, Employment History, and Education. It should only be listed in Education
            2. Terms in the Ohio House or Senate, U.S. House or Senate, or City Council should only be listed under Political Experience

        Output Instructions:
            1. The output should be a single line, with sections (education, political experience, employment, community involvement) separated by a pipe (|).
            2. If any section has no data, leave it empty (i.e., '||').
            3. If no biography is provided, return "||||".
            4. Ensure there are no extra commas or new line breaks. 
            5. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029" 
            
        Biography:
        """

    return ai_prompt_text + " " + combined_bio


def create_json_list(people_dict):
    for key, val in people_dict.items():
        for sub_key, sub_val in val.items():
            val[sub_key] = re.sub(r"\s+", " ", sub_val).replace(", ,", "")
            val[sub_key] = re.sub(r"[\r\n\u2028\u2029]+", " ", sub_val)

    people_json = json.dumps(people_dict)

    people_json = re.sub(r"[\r\n\u2028\u2029]+", " ", people_json)

    return people_json
