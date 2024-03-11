from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.bisnd_bcc import BisndBCCASpider

# Setup for spider
test_response = file_response(
    join(dirname(__file__), "files", "bisnd_bcc_a.html"),
    url="https://www.bismarcknd.gov/calendar.aspx?Keywords=&startDate=02/04/2024&enddate=09/04/2024&CID=52&showPastEvents=false",  # noqa
)
spider = BisndBCCASpider()

freezer = freeze_time("2024-03-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

# Assuming the first item in parsed_items is the one we're interested in based on the CSV data  # noqa
item = parsed_items[0]


def test_title():
    assert item["title"] == "Bismarck-Burleigh Commissions Committee"


def test_description():
    assert item["description"] == ""


def test_start():
    assert item["start"] == datetime(2024, 2, 6, 16, 0)


def test_end():
    assert item["end"] is None


def test_id():
    assert (
        item["id"]
        == "bisnd_bcc_a/202402061600/x/bismarck_burleigh_commissions_committee"
    )


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": "Tom Baker Meeting Room",
        "address": "City/County Building, 221 N 5th St, Bismarck, ND 58501",
    }


def test_source():
    assert item["source"] == "https://www.bismarcknd.gov/calendar.aspx"


def test_links():
    expected_links = [
        {
            "title": "Agenda Center",
            "href": "https://www.bismarcknd.gov/AgendaCenter/Search/?term=&CIDs=all&startDate=&endDate=&dateRange=&dateSelector=",  # noqa
        },
        {
            "href": "https://www.bismarcknd.gov/Calendar.aspx?EID=7227&month=3&year=2024&day=4&calType=0",  # noqa
            "title": "More Details",
        },
    ]
    assert item["links"] == expected_links


def test_classification():
    assert item["classification"] == COMMITTEE


def test_all_day():
    assert item["all_day"] is False
