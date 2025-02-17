import asyncio
import websockets  # type: ignore
import json
import queue

from houseScraper_async import run_scraper


# This will hold the text updates for the frontend.
print_queue = queue.Queue()


async def send_to_frontend(websocket):
    """Send updates to the frontend via WebSocket."""
    while True:
        try:
            # Try to get the next message from the queue (non-blocking)
            text = print_queue.get_nowait()
            if text == "stop_scraper":
                break
            await websocket.send(text)
        except queue.Empty:
            pass
        await asyncio.sleep(0.1)  # To prevent busy-waiting


def add_to_ui_queue(text):
    """Function to add updates to the UI queue and print them."""
    print_queue.put(text + "\n")


async def sendJson(websocket, people_json):
    await websocket.send(people_json)


async def run_scraper_and_send_updates(websocket):
    """Run the scraper and send progress updates."""
    await run_scraper(add_to_ui_queue, sendJson, websocket)
    add_to_ui_queue("Finished from websocket")


async def handler(websocket):
    """WebSocket connection handler."""
    print("Connection Made")

    start_message = await websocket.recv()
    print(f"Received from frontend: {start_message}")

    if start_message == "start_scraping":
        print("Starting scraper...")
        asyncio.create_task(run_scraper_and_send_updates(websocket))
        await send_to_frontend(websocket)


async def start_server():
    """Start the WebSocket server."""
    server = await websockets.serve(handler, "0.0.0.0", 50000)
    print("WebSocket server running on ws://0.0.0.0:50000")
    await server.wait_closed()


if __name__ == "__main__":
    # Start the asyncio event loop to run the WebSocket server
    asyncio.run(start_server())
