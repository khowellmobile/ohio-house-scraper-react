# ohio-house-scraper-react
This project is a web scraper web application designed to collect detailed information about members of the Ohio House of Representatives.

It scrapes data such as:

- Hometown
- Contact information (address, phone, fax)
- Biography details (education, politics, employment, community involvement)
- Committees the representatives are part of
- Primary Legislation
- Headshot URLs

The application is built using a **React** frontend for the user interface and **Python** (with `aiohttp`, `asyncio`, `BeautifulSoup`, and **WebSocket**) for the backend scraper.

Click [here](https://wugtools.com/) for current hosting location
## Features
- **Real-time Scraping**: The scraper fetches data about each representative and sends status updates to the frontend using WebSockets.
- **Error Handling**: The scraper will retry errors on failed attempts and provide updates on the frontend.
- **Downloadable Output**: After scraping, the user can download the scraped data in a `.txt` format, formatted like as a tab delimited text file.
- **Batch Processing**: Representatives are processed in batches for efficiency and consistency.
- **AI Data Extraction**: Uses Gemini to extract data from the representatives biography.

## Tech Stack
- Front End
    - [React](https://react.dev/)
    - [Node.js](https://nodejs.org/en) (for package management)
    - Created using [create-react-app](https://github.com/facebook/create-react-app?tab=readme-ov-file)
- Back End
    - [Python](https://www.python.org/)
    - Packages used
        - [google-genai](https://ai.google.dev/)
        - [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
        - [websockets](https://websockets.readthedocs.io/en/stable/)
        - [aiohttp](https://docs.aiohttp.org/en/stable/)
        - [dotenv](https://pypi.org/project/python-dotenv/)
        - [requests](https://pypi.org/project/requests/)
- Hosting
    - AWS: [EC2](https://aws.amazon.com/pm/ec2/?gclid=Cj0KCQiA_NC9BhCkARIsABSnSTbwN1-G04mmv6p1qXeOHox1rsO1efCuAQdwr49LpMKGLXLXzEBOR8oaAjcbEALw_wcB&trk=36c6da98-7b20-48fa-8225-4784bced9843&sc_channel=ps&ef_id=Cj0KCQiA_NC9BhCkARIsABSnSTbwN1-G04mmv6p1qXeOHox1rsO1efCuAQdwr49LpMKGLXLXzEBOR8oaAjcbEALw_wcB:G:s&s_kwcid=AL!4422!3!467723097970!e!!g!!aws%20ec2!11198711716!118263955828) t2.micro
    - AMI: [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/?amazon-linux-whats-new.sort-by=item.additionalFields.postDateTime&amazon-linux-whats-new.sort-order=desc)
    - Webserver: [Nginix](https://nginx.org/)
- AI
    - Model: [Gemini 1.5 Flash](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-1.5-flash)

## Quick Start without Hosting
1. Install Python and Node (check tech stack above for links to their pages)
2. Setup a google gemini account and place your api key in a .env file in the backend folder named "API_KEY"
3. Setup virtual enviroment (recomended)

    Navigate to backend folder and run
    ```
    python -m venv venv
    ```
    Activate virtual enviroment
    ```
    source venv/bin/activate  # For macOS/Linux
    venv\Scripts\activate     # For Windows
    ```
4. Download Python Dependencies
    With virtual enviroment run
    ```
    pip install -r requirements.txt
    ```
5. Download React Dependencies
    Navigate to "ohio-house-scraper-app" in frontend folder and run
    ```
    npm install
    ```
6. Run application
    with your virtual enviroment activated and in the backend folder run
    ```
    python ./websocket_server.py
    ```
    In the "ohio-house-scraper-app" in frontend folder run
    ```
    npm start
    ```
7. The application should now open in local host. Ensure to change the IP address in Body.js and websocket_server.py to localhost.

## Notes and Caveats
- The application is still being worked on and imrpoved. As such the level of security, error handling, and interaction will increase over time.
- Only one user should be running the scraper at a time. The requests will quickly exceed the limits of the OhioHouse.gov website. There is a solution in place to rerun denied requests after a specified time but the time for the scraper to run will increase significantly.

    

