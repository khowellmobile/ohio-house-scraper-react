import asyncio
import websockets
import json
import time


# Simulate scraper function
async def run_scraper(websocket):
    # Simulate scraping pages with progress updates
    results = []
    for i in range(1, 6):  # Simulating 5 pages of data
        await asyncio.sleep(1)  # Simulate scraping delay
        results.append(f"Page {i} scraped")
        # Send progress update to the frontend
        await websocket.send(f"Progress: Scraping page {i} of 5")

    # Simulate file creation (e.g., after scraping completes)
    file_content = "Scraped data content...\n" + "\n".join(results)

    # Send the completed file content to the frontend
    await websocket.send(f"Scraping complete! Sending file: scraped_data.txt")
    await websocket.send(file_content)


# WebSocket server handler
async def handler(websocket):
    print("New connection received!")

    # Wait for the start signal from the client
    start_message = await websocket.recv()
    print(f"Received from frontend: {start_message}")

    if start_message == "start_scraping":
        print("Starting the scraper...")
        # Run the scraper and send progress updates
        await run_scraper(websocket)


# Start the WebSocket server
async def start_server():
    server = await websockets.serve(handler, "localhost", 65432)
    print("WebSocket server running on ws://localhost:65432")
    await server.wait_closed()


# Run the server
if __name__ == "__main__":
    asyncio.run(start_server())
