import requests  # type: ignore
import threading
import queue
import time
from bs4 import BeautifulSoup  # type: ignore
from google import genai  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

from utils import (
    get_representative_list,
    checkURLResponse,
    getTime,
    get_ai_prompt,
    create_json_list,
)

# Getting ai client
load_dotenv()
api_key = os.getenv("API_KEY")

API_KEY = api_key
client = genai.Client(api_key=API_KEY)


def run_scraper(add_to_ui_queue, sendJson, websocket):

    rep_names = get_representative_list()

    people_queue, error_queue = batch_processor(rep_names, add_to_ui_queue)

    people = {}
    while not people_queue.empty():
        people.update(people_queue.get())

    while not error_queue.empty():
        print(error_queue.get())

    people_json = create_json_list(people)
    sendJson(websocket, people_json)


# Proceeses all batches and returns queue containing information and errors
def batch_processor(
    rep_names, add_to_ui_queue, batch_size=15, total_batches=2, interval=60
):
    batches = [
        rep_names[i : i + batch_size] for i in range(0, len(rep_names), batch_size)
    ]

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

    add_to_ui_queue("Finished Processing")
    add_to_ui_queue(f"stop_scraper {getTime()}")
    print(f"stop_scraper {getTime()}")

    return result_queue, error_queue


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


def process_rep(rep_name, result_queue, error_queue, add_to_ui_queue):
    rep_obj = {}

    def fetch_function_results(func, func_name, rep_name):
        if func_name == "getInfo":
            (hometown, address, phone, fax) = func(rep_name)
            rep_obj["hometown"] = hometown
            rep_obj["address"] = address
            rep_obj["phone"] = phone
            rep_obj["fax"] = fax
        elif func_name == "getBio":
            (education, politics, employment, community) = func(
                rep_name, add_to_ui_queue, error_queue
            )
            rep_obj["education"] = education
            rep_obj["politics"] = politics
            rep_obj["employment"] = employment
            rep_obj["community"] = community
        else:
            rep_obj["committees"] = func(rep_name)

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

    for thread in threads:
        thread.start()
    add_to_ui_queue(f"Starting Threads: {rep_name} at {getTime()}")

    for thread in threads:
        thread.join()
    add_to_ui_queue(f"joining Threads: {rep_name} at {getTime()}")
    print(f"thread join at {getTime()}")

    result_queue.put({rep_name: rep_obj})


def getInfo(rep_name):
    address_keywords = ["77", "High", "Street", "St.", "South", "S.", "Floor"]

    url = f"https://ohiohouse.gov/members/{rep_name}"
    response = requests.get(url)

    if checkURLResponse(response) != 0:
        return "Response Error", "Response Error", "Response Error", "Response Error"

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
        return "Response Error", "Response Error", "Response Error", "Response Error"

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
                    contents=get_ai_prompt(combined_bio),
                )

            except Exception as e:
                print(f"Gemini Response Error: {e}")
                add_to_ui_queue(
                    f"Gemini Response Error: Adding '{rep_name}' to error queue"
                )
                error_queue.put(rep_name)
                return "AI Error", "AI Error", "AI Error", "AI Error"

            values = response.text.split("|")

            if len(values) < 4:
                add_to_ui_queue(
                    f"Gemini Formatting Error. Adding '{rep_name}' to error queue"
                )
                error_queue.put(rep_name)
                return "AI Error", "AI Error", "AI Error", "AI Error"

            return values[0], values[1], values[2], values[3]

    return "Bio Not Found", "Bio Not Found", "Bio Not Found", "Bio Not Found"


def getCommittees(rep_name):
    url = f"https://ohiohouse.gov/members/{rep_name}/committees"
    response = requests.get(url)

    if checkURLResponse(response) != 0:
        return "Response Error"

    soup = BeautifulSoup(response.content, "html.parser")

    media_captions = soup.find_all("div", class_="media-overlay-caption")

    committees = ", ".join(caption.text.strip() for caption in media_captions)

    return committees
