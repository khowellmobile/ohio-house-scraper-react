from bs4 import BeautifulSoup  # type: ignore
import requests # type: ignore
import re

from utils import (
    get_representative_list,
    get_ai_prompt,
    create_formatted_json_msg,
    checkURLResponse,
    create_json_list,
)


def get_legislation(rep_name):
    url = f"https://ohiohouse.gov/members/{rep_name}/legislation"
    response = requests.get(url)

    if not response:
        print("Response Error")

    soup = BeautifulSoup(response.text, "html.parser")

    legislation_tables = soup.find_all("table", class_="member-legislation-table")

    # Finding needed table
    for val in legislation_tables:
        caption = val.find("caption")

        if caption and "Primary Sponsored Bills" in caption.text:
            table = val

    primary_legislation = []

    for tbody in table.find_all("tbody"):
        bill_num = tbody.find("a").text
        bill_title = tbody.find("td", class_="title-cell").text

        primary_legislation.append(bill_num + " " + bill_title)

    print("\n".join(primary_legislation))

def get_image_url(rep_name):
    url = f"https://ohiohouse.gov/members/directory?start=1&sort=LastName"
    response = requests.get(url)

    if not response:
        print("Response Error")

    soup = BeautifulSoup(response.text, "html.parser")

    all_portraits = soup.find_all("div", class_="media-container-portrait")

    image_url = "Image not found"

    for div in all_portraits:
        name = div.find("div", class_="media-overlay-caption-text-line-1").text
        if rep_name == name.strip().replace(" ", "-").replace(".", "").replace(",", "").lower():
            image_div = div.find("div", class_="media-thumbnail-image")
            image_url = re.search(r'url\((.*?)\)', image_div['style']).group(1)

    print(image_url)

    


def main():
    """ get_legislation("dontavius-l-jarrells") """
    get_image_url("dontavius-l-jarrells")


if __name__ == "__main__":
    main()
