import asyncio
import aiohttp
import queue
from bs4 import BeautifulSoup
from google import genai  # Assuming this supports async, or you can wrap it
import os
from dotenv import load_dotenv # type: ignore

## Gets text 
async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.text()
    
async def get_info(rep_name):
    address_keywords = ["77", "High", "Street", "St.", "South", "S.", "Floor"]

    url = f"https://ohiohouse.gov/members/{rep_name}"
    response = await fetch_data(session, url)
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
            phone_number = (
                address_number_module[1].text.strip().replace("Phone: ", "")
            )  # remove preceding "Phone: "
            fax_number = (
                address_number_module[2].text.strip().replace("Fax: ", "")
            )  # remove preceding "Fax: "

    return home_town, address, phone_number, fax_number


async def get_bio(rep_name, add_to_ui_queue, error_queue):

    url = f"https://ohiohouse.gov/members/{rep_name}/biography"
    response = await fetch_data(session, url)
    soup = BeautifulSoup(response, "html.parser")

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


async def get_committees(rep_name):
    url = f"https://ohiohouse.gov/members/{rep_name}/committees"
    response = await fetch_data(session, url)
    soup = BeautifulSoup(response, "html.parser")

    media_captions = soup.find_all("div", class_="media-overlay-caption")

    committees = ", ".join(caption.text.strip() for caption in media_captions)

    return committees

async def process_rep(rep_name, add_to_ui_queue, result_queue, error_queue):
    rep_obj = {}

    # Run all the async functions concurrently for each rep
    tasks = [
        get_info(rep_name),
        get_bio(rep_name),
        get_committees(rep_name)
    ]
    
    results = await asyncio.gather(*tasks)

    # Assign results to rep_obj
    rep_obj['hometown'], rep_obj['address'], rep_obj['phone'], rep_obj['fax'] = results[0]
    rep_obj['education'], rep_obj['politics'], rep_obj['employment'], rep_obj['community'] = results[1]
    rep_obj['committees'] = results[2]

    result_queue.put({rep_name: rep_obj})

async def process_batch(batch, session, add_to_ui_queue, result_queue, error_queue):
    tasks = []
    for rep_name in batch:
        task = asyncio.create_task(process_rep(rep_name, session, add_to_ui_queue, result_queue, error_queue))
        tasks.append(task)
    
    await asyncio.gather(*tasks)