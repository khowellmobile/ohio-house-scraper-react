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
    getTime,
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
    async with session.get(url) as response:

        if await checkURLResponse(response) != 0:
            print(f"Error: Received a non-200 status code {response.status} for {url}")
            return None

        return await response.text()


# Fetch representative information
async def get_info(session, rep_name, add_to_ui_queue, error_queue):
    address_keywords = ["77", "High", "Street", "St.", "South", "S.", "Floor"]
    url = f"https://ohiohouse.gov/members/{rep_name}"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(f"Error: Response Error. Adding {rep_name} to error queue")
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
    url = f"https://ohiohouse.gov/members/{rep_name}/biography"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(f"Error: Response Error. Adding {rep_name} to error queue")
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


# Fetch committees information
async def get_committees(session, rep_name, add_to_ui_queue, error_queue):
    url = f"https://ohiohouse.gov/members/{rep_name}/committees"
    response = await fetch_data(session, url)

    if not response:
        add_to_ui_queue(f"Error: Response Error. Adding {rep_name} to error queue")
        error_queue.put(rep_name)
        return "Response Error", "Response Error", "Response Error", "Response Error"

    soup = BeautifulSoup(response, "html.parser")

    media_captions = soup.find_all("div", class_="media-overlay-caption")

    committees = ", ".join(caption.text.strip() for caption in media_captions)

    return committees


# Process each representative concurrently
async def process_rep(session, rep_name, add_to_ui_queue, result_queue, error_queue):
    rep_obj = {}

    # Run all the async functions concurrently for each rep
    tasks = [
        get_info(session, rep_name, add_to_ui_queue, error_queue),
        get_bio(session, rep_name, add_to_ui_queue, error_queue),
        get_committees(session, rep_name, add_to_ui_queue, error_queue),
    ]
    add_to_ui_queue(f"Processing: {rep_name}")
    results = await asyncio.gather(*tasks)
    add_to_ui_queue(f"Finished Processing: {rep_name}")

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
    tasks = []
    for rep_name in batch:
        task = asyncio.create_task(
            process_rep(session, rep_name, add_to_ui_queue, result_queue, error_queue)
        )
        tasks.append(task)
        await asyncio.sleep(3)

    await asyncio.gather(*tasks)


async def create_run_batches(
    rep_names, batch_size, add_to_ui_queue, result_queue, error_queue, session
):
    total_batches = len(rep_names) // batch_size + (
        1 if len(rep_names) % batch_size else 0
    )

    tasks = []  # List to hold tasks

    for i in range(total_batches):
        batch = rep_names[i * batch_size : (i + 1) * batch_size]

        add_to_ui_queue(f"Starting batch {i + 1}/{total_batches}...")

        # Start the batch processing in a new task
        task = asyncio.create_task(
            process_batch(session, batch, add_to_ui_queue, result_queue, error_queue)
        )
        tasks.append(task)

        # Wait 60 seconds before launching the next batch
        if i < total_batches - 1:
            add_to_ui_queue(f"Waiting 60 seconds to launch next batch...")
            await asyncio.sleep(60)

    # Wait for all tasks to finish
    await asyncio.gather(*tasks)


# Main runner function (handling session and batches)
async def run_scraper(add_to_ui_queue, sendJson, websocket):
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
            add_to_ui_queue("Starting to process response and format errors...")

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
