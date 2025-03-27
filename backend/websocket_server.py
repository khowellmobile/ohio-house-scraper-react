"""
Ohio House Representatives Scraper Web Socket Server

This script handles creation and regulation of the websocket used for communicating
between the frontend and backend of the scraper. This file also handles communication between
The scraper itself and this file.

Functions:
    is_rate_limited(client_ip): Checks if the user surpases the rate limit.
    async def receive_from_frontend(websocket): Gets messages from front end to receive commands
    async def send_to_frontend(websocket): Sends messages to the front end from print_queue
    def add_to_ui_queue(text): Add messages to the print_queue (used as callback)
    async def sendJson(websocket, people_json): Sends final message to frontend and closes websocket
    async def run_scraper_handler(websocket): Runs scraper and sends progress updates to the frontend.
    async def handler(websocket): Handles WebSocket connection and manage scraping flow.
    async def start_server(): Starts the WebSocket server to listen for connections and handle scraping.

Libraries:
    asyncio: handles async functions.
    websockets: communication with front end.
    json: formatting of data.
    queue: used for holding messages for frontend.
    loggin: used to log the scraper runs for debugging.
    time: used to delay to make sure all messages have been sent
    re: used to pattern match for validation
    defaultdict: used to create dictionary for timestamps
    datetime: used to connection time stamps

Imports:
    houseScraper_async.py
        run_scraper: Used to start the scraper.
    utils.py
        get_representative_list: Used to get complete list of representatives.

Global Variables:
    print_queue: Holds messages to be sent to the front end.
    RATE_LIMIT: The number of requests users cna make in the time window
    RATE_LIMIT_WINDOW: Window size used for rate limiting
    request_timestamps: Dictionary of user connection timestamps
    BANNED_PATTERNS: List of patterns not allowed in messages


Author: Kent Howell [khowellmobile@gmail.com]
Date: 2/18/2025
Last Update: 3/27/2025
"""

import asyncio
import websockets  # type: ignore
import json
import queue
import logging
import time
import re
from collections import defaultdict
from datetime import datetime, timedelta

from houseScraper_async import run_scraper as run_scraper
from utils import get_representative_list


# This will hold the text updates for the frontend.
print_queue = queue.Queue()

# Rate Limiting Setup
RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 60
request_timestamps = defaultdict(list)


logging.basicConfig(
    filename="websocket.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BANNED_PATTERNS = [
    r"select",
    r"insert",
    r"update",
    r"drop",
    r"delete",
    r"script",
    r"eval",
    r"exec",
    r"alert",
    r"document",
    r"union",
    r"<!--",
    r"-->",
    r"base64",
    r"javascript",
    r"@import",
    r"@keyframes",
]


def is_rate_limited(client_ip):
    """
    Checks if a client IP has exceeded the rate limit within the time window.

    Args:
        client_ip (str): The IP address of the client trying to make a request.

    Returns:
        bool: True if the IP is rate-limited (exceeded the request limit), False otherwise.
    """
    current_time = datetime.now()

    # Get timestamps in window
    request_timestamps[client_ip] = [
        timestamp
        for timestamp in request_timestamps[client_ip]
        if current_time - timestamp < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]

    # Return true if rate is exceeded
    if len(request_timestamps[client_ip]) >= RATE_LIMIT:
        return True

    # If no exceeded, log time stamp and return False
    request_timestamps[client_ip].append(current_time)
    return False


async def receive_from_frontend(websocket):
    """
    Gets messages in json format from the front end

    Continuously waits for messages from the front end via the websocket. Once
    it gets a message it will handle the command properly

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the frontend.
    """
    while True:
        try:
            message = await websocket.recv()

            client_ip = websocket.remote_address[0]

            if is_rate_limited(client_ip):
                error_msg = json.dumps(
                    "Rate limit exceeded. Please wait before making another request."
                )
                await websocket.send(f'{{"msg_type":"error", "msg": {error_msg}}}')
                await websocket.close()
                return

            if any(
                re.search(pattern, message, re.IGNORECASE)
                for pattern in BANNED_PATTERNS
            ):
                raise ValueError("Malicious content detected in message.")

            msg_json = json.loads(message)

            if msg_json["msg_type"] == "command" and msg_json["msg"] == "start_scraper":
                fields = [field.strip() for field in msg_json["fields"]]
                asyncio.create_task(run_scraper_handler(websocket, fields))
                await send_to_frontend(websocket)
            elif (
                msg_json["msg_type"] == "command" and msg_json["msg"] == "get_rep_names"
            ):
                names = json.dumps(get_representative_list())
                json_return_msg = f'{{"msg_type":"data", "msg":{names}}}'
                await websocket.send(json_return_msg)
                await websocket.close()

        except websockets.exceptions.ConnectionClosed:
            # If the connection is closed, stop listening for messages
            print("WebSocket connection closed. Stopping message receiving.")
            break
        except ValueError as ve:
            print(f"Invalid message content: {ve}")
            break

        await asyncio.sleep(0.1)


async def send_to_frontend(websocket):
    """
    Sends updated to the frontend via a websocket

    Continuously checks global print_queue for new messages and sends them
    to the frontend via the passed websocket. Ensures there is no blocking
    and breaks loop when websocket is closed

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the frontend.
    """
    while True:
        try:
            # Try to get the next message from the queue (non-blocking)
            text = print_queue.get_nowait()

            # Try sending a message, catch ConnectionClosed exception if closed
            try:
                await websocket.send(text)
            except websockets.exceptions.ConnectionClosed:
                break

        except queue.Empty:
            pass

        await asyncio.sleep(0.1)


def add_to_ui_queue(text):
    """
    Function to add updates to the UI queue and print them.

    Adds messages to the global print_queue. This function can be
    passed to other files to faciliate printing to the front end

    Args:
        text: The message to be added to the queue
    """

    print_queue.put(text + "\n")


async def sendJson(websocket, people_json):
    """
    Sends one final message to the front via a websocket, waits a delay, then
    the websocket

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the front end
        people_json: The message to be sent. Should be in json format.
    """
    await websocket.send(people_json)
    time.sleep(3)
    await websocket.close()
    print("WebSocket Closed", "132")


async def run_scraper_handler(websocket, fields):
    """
    Run the scraper and sends progress updates to the frontend.

    Calls the scraper function and sends the resulting updates to the
    WebSocket. After completion, it adds a final "Finished" message to the queue.

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the frontend used to communicate to the front end.
    """
    try:
        await run_scraper(fields, add_to_ui_queue, sendJson, websocket)
        add_to_ui_queue('{"msg_type": "update", "msg": "Finished from websocket"}')
    except Exception as e:
        # Log the error and notify the client if error occurs
        logging.error(f"Error occurred while running scraper: {e}")
        error_msg = json.dumps(f"Error occurred: {e}. This error has been logged.")
        add_to_ui_queue(f'{{"msg_type": "error", "msg": {error_msg}}}')


async def handler(websocket):
    """
    Handle WebSocket connection and manage scraping flow.

    Receives connection and starts receiving and sending of messages
    to the frontend.

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the frontend used to send and receive messages from the front end.
    """

    client_ip = websocket.remote_address[0]

    print("Connection Made to: ", client_ip)

    logging.info(f"Connection made from IP: {client_ip}")

    receive_task = asyncio.create_task(receive_from_frontend(websocket))
    send_task = asyncio.create_task(send_to_frontend(websocket))

    await asyncio.gather(receive_task, send_task)


async def start_server():
    """
    Start the WebSocket server to listen for connections and handle scraping.

    Initializes the WebSocket server on port 50000 and continuously listens
    for incoming connections from the frontend to manage the scraping process.
    """
    server = await websockets.serve(handler, "localhost", 50000)
    print("WebSocket server running on ws://0.0.0.0:65432")
    await server.wait_closed()


if __name__ == "__main__":
    # Start the asyncio event loop to run the WebSocket server
    asyncio.run(start_server())
