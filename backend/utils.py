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

    for div in rep_name_divs[:30]:
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
    ai_prompt_text = """ Included at the end of this prompt is a biography. The biography should be broken into segments of information (check section 1. to see examples of a segment of information).
Once the biography is broken down into segments these segments should be sorted into 1 of 5 buckets (check section 2. for information on buckets and sorting). Once the 
information is sorted into the appropriate buckets the output needs to be summarized, formatted, and returned.

Section 1. (Segments of information)
    Defintion of a segment of information: A segment of information is a collection of words that describe a membership/participation to 
        an organization, job, degree, or term in office.
    Examples of segments of information include:
        a. His educational background includes a BA, in Urban Studies
        b. He received a Master of Legal Studies from Cleveland State University School of Law
        c. Kyle has served on the Executive Committee of several Civic and Community Organizations including the Cleveland Chapter of the NAACP
        d. National Association of Community Health Workers
        e. Rep. Dane served as an award-winning public school teacher for three decades
        f. as well as a Parma councilman for nearly two decades
        g. Rep. Smith joined the Ohio House of Representatives in 2023 and is now serving his second term
        h. State Representative John Doe is serving his second term in the Ohio House of Representatives.

Section 2. (Buckets and sorting)
    Definition of a bucket: A collection of segments of information that are related by a topic
    Buckets:
        1. Education: This bucket includes any segments of information pertaining to a degree.
            1a. Examples include
                a. His educational background includes a BA, in Urban Studies
                b. He received a Master of Legal Studies from Cleveland State University School of Law
                c. She holds a degree in Social Work from Indiana University
                d. They earned a Masters degree from MIT
            1b. Look for keywords such as degree, university, Masters, Bachelors, PhD, Studied
        2. Political Experience: This bucket includes any segments of information pertaining to a term in office for Senate, House, or City Council
            2a. Examples include
                a. Rep. Smith joined the Ohio House of Representatives in 2023 and is now serving his second term
                b. State Representative John Doe is serving his second term in the Ohio House of Representatives.
                c. During his previous service in the House, his peers elected him Majority Whip and he chaired two standing committees. 
            2b. Look for keywords such as term, council, house of representatives, sentate, city council, elected
            2c. ONLY terms on a city countil, senate, or house of representatives are included here. Awards and Commitees are not sorted into this bucket.
        3. Employment History: This bucket includes any segments of information pertaining to employment and starting/selling/buying companies
            3a. Examples include
                a. He went on to serve as Southwest Ohio Outreach Director for For Ohios Future Action Fund
                b. The family works together to operate SFIA Enterprises
                c. Badger Run Berries, Sarahs company
            3b. Look for keywords such as works, bought, sold, company, worked, employed
        4. Commmunity Involvement: This bucket contains segments of information pertaining to communities, volunteering, churches, and extracurricular organizations
            4a. Examples include
                a. Belongs to St. Pauls Church
                b. The Does are parishioners of Sts. Constantine and Helen Greek Orthodox Church
                c. Patrols her neighborhood as a member of the neighborhood watch
            4b. Look for keywords such as belongs to and helps with, volunteers
        5. Other: This bucket contains segments of information that do not fall into one of the previous 4 buckets.
            5a. Examples unclude
                a. Claggett has been married to his wife for more than 27 years and they reside in Newark where they raised two children.
                b. and is currently in the process of writing his Masters theses. 
                c. He worked to expand school choice and empower parents to be active participants in their childs education regardless of income or circumstance.
            5b. This bucket may also include segments of information that describe another segment. Such as what they wanted to do or goals they had while serving a term
                or participating in an organization
    Sorting:
        1. Each segment of information should get sorted into a single bucket. A segment of information should not be placed into two buckets.
        2. If you feel a segment could belong in two buckets put it in the bucket it most belongs to.
        3. Not all buckets will be full as the bio may not have information that would sort into a bucket

Section 3. (formatting and summarization)
    Once all segments are sorted into buckets each segment should be summarized into a certain format. There is a summarization format that corresponds to each bucket.
    The formats are as listed below
    1. Education
        Format: University, Degree, Area of Study
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. The Ohio State University, MS, Political Science
            b. Ohio University, BS, Nursing
            c. Ohio Unviersity, BS
            d. The Ohio State University, Political Science
        Example of entire bucket:
            a. Kent State University, BS, Visual Journalism, United States Naval War College, Command and Staff Program, University of Toledo, MS
    2. Political Experience
        Format: Organization, Role, Term
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. Ohio House of Representatives, Majority Whip
            b. Ohio House of Representatives, Speaker, 2017-2020
            c. Ohio Senate, 2015-Preset
            d. Columbus City Council
        Example of entire bucket once summarized:
            a. Ohio House of Representatives, Speaker, 2017-2020, Ohio Senate, 2015-2017, Columbus City Council
    3. Employment
        Format: Organization, Role, Status
        If a section of the format is not listed then omit that section and any commas.
        If a company was bought/sold/started the summarization should be "Action, Company Name"
        Examples of segment summarization:
            a. McDonalds, Manager, Former
            b. Chase Bank, Analyst
            c. Started Scotts Mowing
            d. B&H Cleaning, CEO, Current
        Example of entire bucket:
            a. B&H Cleaning, CEO, Current, Started Scotts Mowing, Chase Bank, Analyst
    4. Community Involvement
        Format: Organization, Role
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. St. Pauls Church, Pastor
            b. Neighborhood Watch
            c. Columbus for Hunger, Member
            d. Soup Kitchen
        Example of entire bucket:
            a. St. Pauls Church, Pastor, Neighborhood Watch, Columbus for Hunger, Member, Soup Kitchen
    5. Other
        Segments of information in this bucket do not need formatting

Section 4. (Final Ouput)
    Notes about output: 
        1. Bucket 5 should be left out of the final output and not considered beyond this point
        2. Create a list of buckets 1 through 4 delimited by a pipe (|). 
        3. Buckets are ordered "Education | Political Experience | Employment | Community Involvement"
        3. If a bucket is empty still delimit it eg. ("||")
        4. Each output should have exactly 3 pipes regardless of if buckets are empty or not. eg ("|||")
        5. Here is an example of what a final output might look like
            "Kent State University, BS, Visual Journalism, University of Toledo, MS|Ohio Senate, 2015-2017, Columbus City Council|Started Scotts Mowing, Chase Bank, Analyst|St. Pauls Church, Pastor"
        6. Ensure there are no extra commas or new line breaks. 
        7. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029"
        IMPORTANT 8. Return ONLY the pipe delimited list. Do NOT add any thing to the response. 
            8a. Example of incorrect response by adding something to the list would be "Here is the list as requested: |||"
            8b. Example of incorrect response would be "Here's a breakdown of the biography into segments, sorted into buckets, summarized, and formatted according to your specifications: |||"
            8c. Example of a correct response "Kent State University|||St. Pauls Church"

Section 5. (Biography)
    Biography:"""

    return ai_prompt_text + " " + combined_bio


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
        return f'{{"msg_type":"update", "msg":"Processing: {rep_name}"}}'
    elif kind == "finish_rep":
        return f'{{"msg_type":"update", "msg":"Finished Processing: {rep_name}"}}'
    elif kind == "res_error":
        return f'{{"msg_type":"error", "msg":"Error: Response Error. Adding {rep_name} to error queue"}}'
    elif kind == "ai_error":
        return f'{{"msg_type":"error", "msg":"Error: AI Format Error. Adding {rep_name} to error queue"}}'
