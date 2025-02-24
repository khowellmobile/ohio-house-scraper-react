""" 
Ohio House Representatives Scraper

This script handles scraping the OhioHouse.gov website for information about the representatives.
The list of rep names are split into batches of 15 that are then run concurrently. A batch is started
every 60 seconds. Updates are sent to the front end throughout scraping.

Functions:
    async def fetch_data(session, url): Fetches HTML content for a given URL asynchronously.
    async def get_info(session, rep_name, add_to_ui_queue, error_queue): Fetches representative 
        information (hometown, address, phone, fax).
    async def get_bio(session, rep_name, add_to_ui_queue, error_queue): Fetches representative biography 
        details and process using AI.
    async def get_committees(session, rep_name, add_to_ui_queue, error_queue): Fetches representative 
        committee memberships.
    async def process_rep(session, rep_name, add_to_ui_queue, result_queue, error_queue): Processes each 
        representative's data concurrently.
    async def process_batch(session, batch, add_to_ui_queue, result_queue, error_queue): Process a batch 
        of representatives concurrently.
    async def create_run_batches(rep_names, batch_size, add_to_ui_queue, result_queue, error_queue, session): 
        Splits the representative list into batches and process each batch sequentially. 
    async def run_scraper(add_to_ui_queue, sendJson, websocket): Main function to run the scraper and 
        send the results to the frontend.
    
Libraries:
    asyncio: handles async functions
    aiohttp: handles async requests
    BeautifulSoup: Helps format scraped pages
    queue: Used for holding messages for frontend
    os, load_dontenv:Uused for environment variables

Author: Kent Howell [khowellmobile@gmail.com]
Date: 2/18/2025
"""

import asyncio
import aiohttp  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from google import genai  # Assuming this supports async, or you can wrap it
import queue
import os
from dotenv import load_dotenv  # type: ignore

from utils import (
    get_representative_list,
    get_ai_prompt,
    create_formatted_json_msg,
    checkURLResponse,
    create_json_list,
)

# Getting ai client
load_dotenv()
api_key = os.getenv("API_KEY")

API_KEY = api_key
client = genai.Client(api_key=API_KEY)


# Asynchronous fetch for getting html content
async def fetch_data(session, url):
    """
    Fetch HTML content for a given URL asynchronously.

    Sends a GET request to the URL, checks the response status, and returns
    the HTML content if successful. Returns None if the response is not valid.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        url (str): The URL to fetch data from.

    Returns:
        str: The HTML content of the page or None if the request fails.
    """
    async with session.get(url) as response:

        if await checkURLResponse(response) != 0:
            print(f"Error: Received a non-200 status code {response.status} for {url}")
            return None

        return await response.text()


# Fetch representative information
async def get_info(session, rep_name, add_to_ui_queue, error_queue):
    """
    Fetch representative information (hometown, address, phone, fax).

    Scrapes the representative's page for personal details like hometown,
    address, phone number, and fax number. Returns default values if not found.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        rep_name (str): The name of the representative whose details are being fetched.
        add_to_ui_queue (function): A callback function to send updates to the frontend.
        error_queue (queue.Queue): A queue to store names of representatives with errors.

    Returns:
        tuple: Hometown, address, phone number, and fax number of the representative.
    """
    address_keywords = ["77", "High", "Street", "St.", "South", "S.", "Floor"]
    url = f"https://ohiohouse.gov/members/{rep_name}"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(create_formatted_json_msg("res_error", rep_name))
        error_queue.put(rep_name)
        return "Response Error", "Response Error", "Response Error", "Response Error"

    soup = BeautifulSoup(response, "html.parser")

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
            phone_number = address_number_module[1].text.strip().replace("Phone: ", "")
            fax_number = address_number_module[2].text.strip().replace("Fax: ", "")

    return home_town, address, phone_number, fax_number


# Fetch bio details
async def get_bio(session, rep_name, add_to_ui_queue, error_queue):
    """
    Fetch representative biography details and process using AI.

    Scrapes the representative's biography and uses AI to process and format it.
    Returns error messages or the processed details if successful.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        rep_name (str): The name of the representative whose biography is being fetched.
        add_to_ui_queue (function): A function to send updates to the frontend.
        error_queue (queue.Queue): A queue to store names of representatives with errors.

    Returns:
        tuple: Biography-related details (education, politics, employment, community).
    """
    url = f"https://ohiohouse.gov/members/{rep_name}/biography"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(create_formatted_json_msg("res_error", rep_name))
        error_queue.put(rep_name)
        return "Response Error", "Response Error", "Response Error", "Response Error"

    soup = BeautifulSoup(response, "html.parser")

    bio_block = soup.find("div", class_="gray-block")

    if bio_block:
        bio_paragraphs = bio_block.find_all("p")

        if bio_paragraphs:
            combined_bio = " ".join(
                paragraph.text.strip() for paragraph in bio_paragraphs
            )

            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-1.5-flash",
                    contents=get_ai_prompt(combined_bio),
                )
            except Exception as e:
                print(f"Gemini Response Error: {e}")
                add_to_ui_queue(create_formatted_json_msg("ai_error", rep_name))
                error_queue.put(rep_name)
                return "AI Error", "AI Error", "AI Error", "AI Error"

            values = response.text.split("|")

            if len(values) < 4:
                add_to_ui_queue(create_formatted_json_msg("ai_error", rep_name))
                error_queue.put(rep_name)
                return "AI Error", "AI Error", "AI Error", "AI Error"

            return values[0], values[1], values[2], values[3]

    return "Bio Not Found", "Bio Not Found", "Bio Not Found", "Bio Not Found"


# Fetch committees information
async def get_committees(session, rep_name, add_to_ui_queue, error_queue):
    """
    Fetch representative committee memberships.

    Scrapes the representative's committees and returns a list of their names.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        rep_name (str): The name of the representative whose committee info is being fetched.
        add_to_ui_queue (function): A function to send updates to the frontend.
        error_queue (queue.Queue): A queue to store names of representatives with errors.

    Returns:
        str: A comma-separated list of committees the representative is a member of.
    """
    url = f"https://ohiohouse.gov/members/{rep_name}/committees"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(create_formatted_json_msg("res_error", rep_name))
        error_queue.put(rep_name)
        return "Response Error"

    soup = BeautifulSoup(response, "html.parser")

    media_captions = soup.find_all("div", class_="media-overlay-caption")

    committees = ", ".join(caption.text.strip() for caption in media_captions)

    return committees


# Process each representative concurrently
async def process_rep(session, rep_name, add_to_ui_queue, result_queue, error_queue):
    """
    Process each representative's data concurrently.

    Collects information about a representative's details (bio, committees, contact info) and
    formats them into a dictionary. Sends updates to the frontend as it processes.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        rep_name (str): The name of the representative to process.
        add_to_ui_queue (function): A function to send updates to the frontend.
        result_queue (queue.Queue): A queue to store results of the scraping.
        error_queue (queue.Queue): A queue to store names of representatives with errors.

    Returns:
        None
    """
    rep_obj = {}

    # Run all the async functions concurrently for each rep
    tasks = [
        get_info(session, rep_name, add_to_ui_queue, error_queue),
        get_bio(session, rep_name, add_to_ui_queue, error_queue),
        get_committees(session, rep_name, add_to_ui_queue, error_queue),
    ]
    add_to_ui_queue(create_formatted_json_msg("start_rep", rep_name))
    results = await asyncio.gather(*tasks)
    add_to_ui_queue(create_formatted_json_msg("finish_rep", rep_name))

    print(rep_name)

    # Assign results to rep_obj
    rep_obj["hometown"], rep_obj["address"], rep_obj["phone"], rep_obj["fax"] = results[
        0
    ]
    (
        rep_obj["education"],
        rep_obj["politics"],
        rep_obj["employment"],
        rep_obj["community"],
    ) = results[1]
    rep_obj["committees"] = results[2]

    result_queue.put({rep_name: rep_obj})


# Process a batch of representatives concurrently
async def process_batch(session, batch, add_to_ui_queue, result_queue, error_queue):
    """
    Process a batch of representatives concurrently.

    Processes a list of representatives by calling `process_rep` for each. Each
    batch is processed in parallel, with a 3-second delay between each representative.

    Args:
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.
        batch (list): A list of representative names to process.
        add_to_ui_queue (function): A function to send updates to the frontend.
        result_queue (queue.Queue): A queue to store results of the scraping.
        error_queue (queue.Queue): A queue to store names of representatives with errors.

    Returns:
        None
    """
    tasks = []
    for rep_name in batch:
        task = asyncio.create_task(
            process_rep(session, rep_name, add_to_ui_queue, result_queue, error_queue)
        )
        tasks.append(task)

        # Sleep to avoid resource exhaustion errors
        await asyncio.sleep(3)

    await asyncio.gather(*tasks)


async def create_run_batches(
    rep_names, batch_size, add_to_ui_queue, result_queue, error_queue, session
):
    """
    Split the representative list into batches and process each batch sequentially.

    Divides the list of representatives into smaller batches and processes each
    batch with a 60-second wait between starting to process each batch.

    Args:
        rep_names (list): List of representative names to process.
        batch_size (int): The size of each batch of representatives.
        add_to_ui_queue (function): A function to send updates to the frontend.
        result_queue (queue.Queue): A queue to store results of the scraping.
        error_queue (queue.Queue): A queue to store names of representatives with errors.
        session (aiohttp.ClientSession): The aiohttp session used for sending requests.

    Returns:
        None
    """
    total_batches = len(rep_names) // batch_size + (
        1 if len(rep_names) % batch_size else 0
    )

    tasks = []  # List to hold tasks

    for i in range(total_batches):
        batch = rep_names[i * batch_size : (i + 1) * batch_size]

        add_to_ui_queue(
            f'{{"msg_type": "update", "msg": "Starting batch {i + 1}/{total_batches}..."}}'
        )

        # Start the batch processing in a new task
        task = asyncio.create_task(
            process_batch(session, batch, add_to_ui_queue, result_queue, error_queue)
        )
        tasks.append(task)

        # Wait 60 seconds before launching the next batch
        if i < total_batches - 1:
            add_to_ui_queue(
                '{"msg_type": "update", "msg": "Waiting 60 seconds to launch next batch..."}'
            )
            await asyncio.sleep(60)

    # Wait for all tasks to finish
    await asyncio.gather(*tasks)


# Main runner function (handling session and batches)
async def run_scraper(add_to_ui_queue, sendJson, websocket):
    """
    Main function to run the scraper and send the results to the frontend.

    Initializes the session, processes the batches of representatives,
    formats the results, and sends the data to the frontend.

    Args:
        add_to_ui_queue (function): A function to send updates to the frontend.
        sendJson (function): A function to send the final JSON to the frontend.
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection to the frontend.

    Returns:
        None
    """
    rep_names = get_representative_list()

    async with aiohttp.ClientSession() as session:
        result_queue = queue.Queue()
        error_queue = queue.Queue()

        await create_run_batches(
            rep_names, 15, add_to_ui_queue, result_queue, error_queue, session
        )

        people = {}
        while not result_queue.empty():
            people.update(result_queue.get())

        if not error_queue.empty():
            add_to_ui_queue(
                '{"msg_type": "update", "msg": "Starting to process errors..."}'
            )

        while not error_queue.empty():
            await process_rep(
                session, error_queue.get(), add_to_ui_queue, result_queue, error_queue
            )
            await asyncio.sleep(4)

        # Adding corrected reps to peeople
        while not result_queue.empty():
            people.update(result_queue.get())

        people_json = create_json_list(people)

        await sendJson(websocket, people_json)
