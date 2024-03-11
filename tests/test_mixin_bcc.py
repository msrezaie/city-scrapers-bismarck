from datetime import datetime

import pytest
from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from dateutil.relativedelta import relativedelta
from scrapy.http import FormRequest, HtmlResponse
from scrapy.selector import Selector
from scrapy.spiders import Spider

from city_scrapers.mixins.bcc import BCCMixin


@pytest.fixture
def test_spider():
    class TestSpider(BCCMixin, Spider):
        name = "test_spider"
        agency = "Test Agency"
        cid = "123"

    return TestSpider()


def test_static_variables_enforcement():
    with pytest.raises(NotImplementedError) as e:

        class IncompleteSpider(BCCMixin, Spider):
            pass

    assert "must define the following static variable(s): agency, name, cid" in str(
        e.value
    )


def test_start_requests(test_spider):
    request_generator = test_spider.start_requests()
    request = next(request_generator)

    today = datetime.today()
    one_month_prior = today - relativedelta(months=1)
    one_year_ahead = today + relativedelta(months=6)
    meeting_date_from = one_month_prior.strftime("%m/%d/%Y")
    meeting_date_to = one_year_ahead.strftime("%m/%d/%Y")

    expected_url = f"{test_spider.base_url}?Keywords=&startDate={meeting_date_from}&enddate={meeting_date_to}&CID={test_spider.cid}&showPastEvents=false"  # noqa

    assert isinstance(request, FormRequest)
    assert request.url == expected_url
    assert request.method == "POST"
    assert "calendarView" in request.body.decode()


def test_parse_title(test_spider):
    # Mocking an HTML response
    html = "<li><span>Test Meeting Title</span></li>"
    response = HtmlResponse(
        url="http://example.com", body=html.encode("utf-8"), encoding="utf-8"
    )
    # Creating a selector for the mocked item
    item = Selector(response=response).css("li")
    title = test_spider._parse_title(item)
    assert title == "Test Meeting Title"


def test_parse_description(test_spider):
    html = '<li><p itemprop="description">Test Meeting Description</p></li>'
    response = HtmlResponse(url="http://example.com", body=html.encode("utf-8"))
    item = Selector(response=response).css("li")
    description = test_spider._parse_description(item)
    assert description == "Test Meeting Description"


def test_parse_classification(test_spider):
    assert test_spider._parse_classification("Commission Meeting") == COMMISSION
    assert test_spider._parse_classification("Board Meeting") == BOARD
    assert test_spider._parse_classification("Committee Meeting") == COMMITTEE
    assert test_spider._parse_classification("Council Meeting") == CITY_COUNCIL
    assert test_spider._parse_classification("Random Meeting") == NOT_CLASSIFIED


def test_parse_start(test_spider):
    html = '<li><span itemprop="startDate">2023-01-01T09:00:00</span></li>'
    response = HtmlResponse(url="http://example.com", body=html.encode("utf-8"))
    item = Selector(response=response).css("li")
    start = test_spider._parse_start(item)
    assert start == datetime(2023, 1, 1, 9, 0)


def test_parse_location(test_spider):
    html = """
    <span itemprop="location" itemscope="" itemtype="http://schema.org/Place">
        <span itemprop="name">
            <p>Tom Baker Meeting Room</p>
            <p>City/County Building</p>
            <p>221 N 5th St</p><p>Bismarck, ND 58501</p>
        </span>
        <span class="hidden" itemprop="address" itemscope="" itemtype="http://schema.org/PostalAddress">  # noqa
            <span itemprop="streetAddress">221 N. 5th Street</span>
        </span>
    </span>
    """
    response = HtmlResponse(url="http://example.com", body=html.encode("utf-8"))
    item = Selector(response=response)
    location = test_spider._parse_location(item)
    assert location == {
        "name": "Tom Baker Meeting Room",
        "address": "City/County Building, 221 N 5th St, Bismarck, ND 58501",
    }


def test_parse_location_alternate(test_spider):
    html = """
    <span itemprop="location" itemscope="" itemtype="http://schema.org/Place">
        <span itemprop="name">Event Location</span>
        <span class="hidden" itemprop="address" itemscope="" itemtype="http://schema.org/PostalAddress">  # noqa
            <span itemprop="streetAddress">4th Floor Mayor's Conference Room</span>
        </span>
    </span>
    """
    response = HtmlResponse(url="http://example.com", body=html.encode("utf-8"))
    item = Selector(response=response)
    location = test_spider._parse_location(item)
    assert location == {"name": "", "address": "4th Floor Mayor's Conference Room"}


def test_parse_links(test_spider):
    test_spider.agenda_link = {
        "title": "Agenda Center",
        "href": "https://example.com/agenda",
    }
    html = '<li><a href="/meeting/details">Meeting details</a></li>'
    response = HtmlResponse(url="http://example.com", body=html.encode("utf-8"))
    item = Selector(response=response).css("li")
    links = test_spider._parse_links(item)
    assert links == [
        {"title": "Agenda Center", "href": "https://example.com/agenda"},
        {
            "href": "https://www.bismarcknd.gov/meeting/details",
            "title": "Meeting details",
        },
    ]
