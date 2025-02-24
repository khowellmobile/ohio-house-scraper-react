""" 
Ohio House Representatives Scraper Web Socket Server

This script handles creation and regulation of the websocket used for communicating
between the frontend and backend of the scraper. This file also handles communication between
The scraper itself and this file.

Functions:
    async def send_to_frontend(websocket): Sends messages to the front end from print_queue
    def add_to_ui_queue(text): Add messages to the print_queue (used as callback)
    async def sendJson(websocket, people_json): Sends final message to frontend and closes websocket
    async def run_scraper_handler(websocket): Runs scraper and sends progress updates to the frontend.
    async def handler(websocket): Handles WebSocket connection and manage scraping flow.
    async def start_server(): Starts the WebSocket server to listen for connections and handle scraping.

Libraries:
    asyncio: handles async functions
    websockets: communication with front end
    json: formatting of data
    queue: used for holding messages for frontend

Author: Kent Howell [khowellmobile@gmail.com]
Date: 2/18/2025
"""

import asyncio
import websockets  # type: ignore
import json
import queue
import logging

from houseScraper_async_full import run_scraper as run_scraper_full
from houseScraper_async_partial import run_scraper as run_scraper_partial


# This will hold the text updates for the frontend.
print_queue = queue.Queue()


logging.basicConfig(
    filename="websocket.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def receive_from_frontend(websocket):
    while True:
        try:
            message = await websocket.recv()

            msg_json = json.loads(message)

            if msg_json["msg_type"] == "command" and msg_json["msg"] == "start_full_scraper":
                print("Starting scraper...")
                asyncio.create_task(run_scraper_handler(websocket, True))
                await send_to_frontend(websocket)
            elif msg_json["msg_type"] == "command" and msg_json["msg"] == "start_partial_scraper":
                print("Starting scraper...")
                asyncio.create_task(run_scraper_handler(websocket, False))
                await send_to_frontend(websocket)

        except websockets.exceptions.ConnectionClosed:
            # If the connection is closed, stop listening for messages
            print("WebSocket connection closed. Stopping message receiving.")
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
                # If the WebSocket is closed, stop trying to send messages
                print("WebSocket is closed. Stopping sending messages.")
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
    Sends one final message to the front via a websocket and
    closes the websocket

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the front end
        people_json: The message to be sent. Should be in json format.
    """
    await websocket.send(people_json)
    await websocket.close()


async def run_scraper_handler(websocket, run_full):
    """
    Run the scraper and sends progress updates to the frontend.

    Calls the scraper function and sends the resulting updates to the
    WebSocket. After completion, it adds a final "Finished" message to the queue.

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection
        to the frontend used to communicate to the front end.
    """
    try:
        if run_full:
            await run_scraper_full(add_to_ui_queue, sendJson, websocket)
        else:
            await run_scraper_partial(add_to_ui_queue, sendJson, websocket)
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
    server = await websockets.serve(handler, "localhost", 65432)
    print("WebSocket server running on ws://0.0.0.0:50000")
    await server.wait_closed()


if __name__ == "__main__":
    # Start the asyncio event loop to run the WebSocket server
    asyncio.run(start_server())
