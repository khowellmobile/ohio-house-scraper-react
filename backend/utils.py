""" 
Ohio House Representatives Utils

This script holds various utility functions to be used throughout the scraper

Functions:
    def get_representative_list(): Scrapes for list of all Ohio Representatives
    async def checkURLResponse(response): Checks URL response for errors
    def getTime(): Formats the current time into hours, minutes, seconds
    def get_ai_prompt(combined_bio): Creates ai prompt to guide the AI
    def create_json_list(people_dict): Formats a dictionary of reps into json format
    
Libraries:
    BeautifulSoup: Helps format scraped pages
    requests: Used to handle http requests
    json: Used for formatting into json
    re: Used for pattern matching

Author: Kent Howell [khowellmobile@gmail.com]
Date: 2/18/2025
"""

from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
import time
import json
import re


def get_representative_list():
    """
    Scrapes the list of representatives from the Ohio House of Representatives website.

    Extracts and cleans the names of representatives, removing unwanted characters
    and converting the names to lowercase.

    Args:
        None

    Returns:
        list: A list of cleaned and formatted representative names.
    """
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
    """
    Checks the HTTP response status.

    Verifies whether the HTTP status code is 200 (OK). Returns `1` for non-200 status
    codes, indicating an error, and `0` for successful responses.

    Args:
        response (aiohttp.ClientResponse): The HTTP response to check.

    Returns:
        int: 1 if the response status is not 200, 0 if it is 200.
    """
    if response.status:
        if response.status != 200:
            return 1
        else:
            return 0
    else:
        return 0


def getTime():
    """
    Retrieves the current time formatted as HH:MM:SS.

    Uses the `time` module to get the current local time and formats it to a string
    in the format HH:MM:SS.

    Args:
        None

    Returns:
        str: The current time in HH:MM:SS format.
    """
    current_time = time.localtime()
    formatted_time = time.strftime("%H:%M:%S", current_time)

    return formatted_time

def create_json_list(people_dict):
    """
    Converts the dictionary of people data into a formatted JSON string.

    Iterates through the `people_dict`, cleans and standardizes each value by removing
    unwanted whitespace and newlines, and then converts the dictionary to a JSON string.

    Args:
        people_dict (dict): A dictionary containing people data to be formatted.

    Returns:
        str: A JSON-formatted string of the cleaned `people_dict`.
    """
    for key, val in people_dict.items():
        for sub_key, sub_val in val.items():
            val[sub_key] = re.sub(r"\s+", " ", sub_val).replace(", ,", "")
            val[sub_key] = re.sub(r"[\r\n\u2028\u2029]+", " ", sub_val)

    people_json = json.dumps(people_dict)

    people_json = re.sub(r"[\r\n\u2028\u2029]+", " ", people_json)

    return people_json


def create_formatted_json_msg(kind, rep_name):
    if kind == "start_rep":
        return f'{{"msg_type":"update", "rep_name":"{rep_name}", "msg":"Processing: {rep_name}"}}'
    elif kind == "finish_rep":
        return f'{{"msg_type":"update", "rep_name":"{rep_name}", "msg":"Finished Processing: {rep_name}"}}'
    elif kind == "res_error":
        return f'{{"msg_type":"error", "msg":"Error: Response Error. Adding {rep_name} to error queue"}}'
    elif kind == "ai_error":
        return f'{{"msg_type":"error", "msg":"Error: AI Format Error. Adding {rep_name} to error queue"}}'


def get_ai_prompt(combined_bio):
    """
    Generates an AI prompt for summarizing a representative's biography.

    The prompt provides specific instructions for summarizing various sections of a
    representative's biography (education, political experience, employment, community involvement).
    The biography is combined with the prompt to guide the AI.

    Args:
        combined_bio (str): The full biography of a representative to be summarized.

    Returns:
        str: The AI prompt concatenated with the biography.
    """
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
                c. If the term years are not specifically enumerated then do not include them
                d. If any section is missing, omit it and do not add extra commas. For example:
                    d1. "House of Representatives, Majority Whip, 2017-2021"
                    d2. "Columbus City Council, President"

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
                    a2. A degree should not be listed in Community Involvement, Employment History, and Education. It should only be listed in Education.
            2. Terms in the Ohio House or Senate, U.S. House or Senate, or City Council should only be listed under Political Experience
            3. Attending a college or university and any mention of a degree should only be listed under education.
            4. Multiple degrees are all put in the same bucket seperated by commas.
                a. E.g. "The Ohio State University, MS, Nursing, Toledo University, BS, Biology|||"
        
        Examples of summarizations to use for comparison:


        Output Instructions:
            1. The output should be a single line, with sections (education, political experience, employment, community involvement) separated by a pipe (|).
                a1. e.g. 'education | political experience | employment | community involvement'.
            2. If any section has no data, leave it empty (i.e., '||').
            3. If no biography is provided, return "||||".
            4. Ensure there are no extra commas or new line breaks. 
            5. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029" 
            6. Each output should contain exactly 3 pipe characters (|).
            
        Biography:"""

    return ai_prompt_text + " " + combined_bio
