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
import re
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


async def get_legislation(session, rep_name, add_to_ui_queue, error_queue):
    url = f"https://ohiohouse.gov/members/{rep_name}/legislation"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(create_formatted_json_msg("res_error", rep_name))
        error_queue.put(rep_name)
        return "Response Error"

    soup = BeautifulSoup(response, "html.parser")

    legislation_tables = soup.find_all("table", class_="member-legislation-table")

    table = None

    # Finding needed table
    for val in legislation_tables:
        caption = val.find("caption")

        if caption and "Primary Sponsored Bills" in caption.text:
            table = val

    if not table:
        return "No Primary Sponsored Bills Found"

    primary_legislation = []

    for tbody in table.find_all("tbody"):
        bill_num = tbody.find("a").text
        bill_title = tbody.find("td", class_="title-cell").text

        primary_legislation.append(bill_num + " " + bill_title)

    return "<newline>".join(primary_legislation)


async def get_image_url(session, rep_name, add_to_ui_queue, error_queue):
    url = f"https://ohiohouse.gov/members/directory?start=1&sort=LastName"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(create_formatted_json_msg("res_error", rep_name))
        error_queue.put(rep_name)
        return "Response Error"

    soup = BeautifulSoup(response, "html.parser")

    all_portraits = soup.find_all("div", class_="media-container-portrait")

    image_url = "Image not found"

    for div in all_portraits:
        name = div.find("div", class_="media-overlay-caption-text-line-1").text
        if (
            rep_name
            == name.strip().replace(" ", "-").replace(".", "").replace(",", "").lower()
        ):
            image_div = div.find("div", class_="media-thumbnail-image")
            image_url = re.search(r"url\((.*?)\)", image_div["style"]).group(1)

    formula_wrapped_url = f'=IMAGE("https://ohiohouse.gov{image_url}")'

    return formula_wrapped_url, f"https://ohiohouse.gov{image_url}"


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

    tasks = [
        get_legislation(session, rep_name, add_to_ui_queue, error_queue),
        get_image_url(session, rep_name, add_to_ui_queue, error_queue),
    ]

    # Run all the async functions concurrently for each rep
    add_to_ui_queue(create_formatted_json_msg("start_rep", rep_name))
    results = await asyncio.gather(*tasks)
    add_to_ui_queue(create_formatted_json_msg("finish_rep", rep_name))

    # Assign results to rep_obj
    rep_obj["legislation"] = results[0]
    (rep_obj["image_formula"], rep_obj["image_url"]) = results[1]

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
            await asyncio.sleep(4)
            await process_rep(
                session, error_queue.get(), add_to_ui_queue, result_queue, error_queue
            )

        # Adding corrected reps to peeople
        while not result_queue.empty():
            people.update(result_queue.get())

        people_json = create_json_list(people)

        await sendJson(websocket, people_json)
