import requests  # type: ignore
import threading
import queue
import time
from bs4 import BeautifulSoup  # type: ignore
from google import genai  # type: ignore
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()
api_key = os.getenv("API_KEY")

API_KEY = api_key
client = genai.Client(api_key=API_KEY)

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


def run_scraper(add_to_ui_queue, formatSendCSV):
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

    people_queue, error_queue = batch_processor(rep_names, add_to_ui_queue)

    people = {}
    while not people_queue.empty():
        people.update(people_queue.get())

    print(people)

    while not error_queue.empty():
        print(error_queue.get())
        
    add_to_ui_queue("Finished Processing")
    add_to_ui_queue("stop_scraper")


def getInfo(rep_name):
    address_keywords = ["77", "High", "Street", "St.", "South", "S.", "Floor"]

    url = f"https://ohiohouse.gov/members/{rep_name}"
    response = requests.get(url)

    if checkURLResponse(response) != 0:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    divs = soup.find_all("div", class_="member-info-bar-module")

    home_town = address = phone_number = fax_number = "Not Listed"

    for module in divs:
        module_text = module.get_text()
        if "Hometown" in module_text:
            home_town = module.find("div", class_="member-info-bar-value").text.strip()

        if any(keyword in module_text for keyword in address_keywords):
            address_number_module = module.find_all(
                "div", class_="member-info-bar-value"
            )

            address = address_number_module[0].text.strip()
            phone_number = (
                address_number_module[1].text.strip().replace("Phone: ", "")
            )  # remove preceding "Phone: "
            fax_number = (
                address_number_module[2].text.strip().replace("Fax: ", "")
            )  # remove preceding "Fax: "

    return home_town, address, phone_number, fax_number


def getBio(rep_name, add_to_ui_queue, error_queue):

    url = f"https://ohiohouse.gov/members/{rep_name}/biography"
    response = requests.get(url)

    if checkURLResponse(response) != 0:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    bio_block = soup.find("div", class_="gray-block")

    if bio_block:
        bio_paragraphs = bio_block.find_all("p")

        if bio_paragraphs:
            combined_bio = " ".join(
                paragraph.text.strip() for paragraph in bio_paragraphs
            )

            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=ai_prompt_text + " " + combined_bio,
                )

            except Exception as e:
                print(f"Gemini Response Error: {e}")
                add_to_ui_queue(f"Gemini Response Error: Adding '{rep_name}' to error queue")
                error_queue.put(rep_name)
                return "AI Error"

            values = response.text.split("|")

            if len(values) < 4:
                add_to_ui_queue(f"Gemini Formatting Error. Adding '{rep_name}' to error queue")
                error_queue.put(rep_name)
                return "AI Error"

            return values[0], values[1], values[2], values[3]


def getCommittees(rep_name):
    url = f"https://ohiohouse.gov/members/{rep_name}/committees"
    response = requests.get(url)

    if checkURLResponse(response) != 0:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    media_captions = soup.find_all("div", class_="media-overlay-caption")

    committees = ", ".join(caption.text.strip() for caption in media_captions)

    return committees


def checkURLResponse(response):
    if response.status_code:
        if response.status_code != 200:
            print("Bad response code: ", response.status_code)
            return 1
        else:
            return 0
    else:
        return 0


# Process one rep and returns a person object
def process_rep(rep_name, result_queue, error_queue, add_to_ui_queue):
    rep_obj = {}

    def fetch_function_results(func, func_name, rep_name):
        if func_name == "getBio":
            rep_obj[func_name] = func(rep_name, add_to_ui_queue, error_queue)
        else:
            rep_obj[func_name] = func(rep_name)

    threads = [
        threading.Thread(
            target=fetch_function_results, args=(getInfo, "getInfo", rep_name)
        ),
        threading.Thread(
            target=fetch_function_results, args=(getBio, "getBio", rep_name)
        ),
        threading.Thread(
            target=fetch_function_results,
            args=(getCommittees, "getCommittees", rep_name),
        ),
    ]
    
    add_to_ui_queue(f"Starting Thread : {rep_name} at {getTime()}")
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    add_to_ui_queue(f"Finishing Thread : {rep_name} at {getTime()}")

    result_queue.put({rep_name: rep_obj})


def process_batch(batch, result_queue, error_queue, add_to_ui_queue):
    batch_threads = []

    for rep_name in batch:
        batch_thread = threading.Thread(
            target=process_rep,
            args=(rep_name, result_queue, error_queue, add_to_ui_queue),
        )
        batch_threads.append(batch_thread)
        batch_thread.start()
        time.sleep(3)

    for batch_thread in batch_threads:
        batch_thread.join()


def batch_processor(
    inputs, add_to_ui_queue, batch_size=15, total_batches=2, interval=60
):
    batches = [inputs[i : i + batch_size] for i in range(0, len(inputs), batch_size)]
    result_queue = queue.Queue()
    error_queue = queue.Queue()
    batch_threads = []

    for i in range(total_batches):
        if i < len(batches):
            batch = batches[i]
            add_to_ui_queue(f"Starting batch {i + 1}/{total_batches}...")

            batch_thread = threading.Thread(
                target=process_batch,
                args=(batch, result_queue, error_queue, add_to_ui_queue),
            )
            batch_thread.start()

            add_to_ui_queue(
                f"Waiting for {interval} seconds before starting the next batch..."
            )
            time.sleep(interval)

    for batch_thread in batch_threads:
        batch_thread.join()

    return result_queue, error_queue


def getTime():
    current_time = time.localtime()
    formatted_time = time.strftime("%H:%M:%S", current_time)

    return formatted_time


