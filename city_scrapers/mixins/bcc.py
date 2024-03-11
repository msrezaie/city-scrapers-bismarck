import logging
from datetime import datetime

from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta
from scrapy.http import FormRequest


class BCCMixinMeta(type):
    """
    Metaclass that enforces the implementation of required static
    variables in child classes that inherit from BismarckCCMixin.
    """

    def __init__(cls, name, bases, dct):
        required_static_vars = ["agency", "name", "cid"]
        missing_vars = [var for var in required_static_vars if var not in dct]

        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise NotImplementedError(
                f"{name} must define the following static variable(s): {missing_vars_str}."  # noqa
            )
        super().__init__(name, bases, dct)


class BCCMixinMeta(CityScrapersSpider, metaclass=BCCMixinMeta):
    """
    Spider mixin for Bismarck City Commission in Bismarck ND. This mixin
    is intended to be used as a base class for spiders that scrape meeting
    data from the city's website.
    """

    host = "https://www.bismarcknd.gov"
    base_url = f"{host}/calendar.aspx"
    agenda_link = {
        "title": "Agenda Center",
        "href": f"{host}/AgendaCenter/Search/?term=&CIDs=all&startDate=&endDate=&dateRange=&dateSelector=",  # noqa
    }
    timezone = "America/Chicago"
    name = None
    agency = None
    cid = None  # calendar ID, used to target specific committee

    def start_requests(self):
        """
        Prepare and send a POST request with form data to get meetings.
        On the webpage, search requests typically include several other
        pieces of form data (eg. "__RequestVerificationToken"
        and "__VIEWSTATE") typical for a ASP Web Forms site. However,
        in this agency's case, it appears the server does not seem to require
        them.
        """
        # Calculate dates for one month prior and one year ahead
        today = datetime.today()
        one_month_prior = today - relativedelta(months=1)
        one_year_ahead = today + relativedelta(months=6)

        # Format dates as "MM/DD/YYYY"
        meeting_date_from = one_month_prior.strftime("%m/%d/%Y")
        meeting_date_to = one_year_ahead.strftime("%m/%d/%Y")

        # build form data
        form_data = {
            "calendarView": "list",
        }

        # build headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"  # noqa
        }

        # build the URL
        url = f"{self.base_url}?Keywords=&startDate={meeting_date_from}&enddate={meeting_date_to}&CID={self.cid}&showPastEvents=false"  # noqa
        yield FormRequest(
            url, method="POST", headers=headers, formdata=form_data, callback=self.parse
        )

    def parse(self, response):
        """
        Parse a list of meetings from the response.
        """
        items = response.css(".calendar > ol > li")
        for item in items:
            title = self._parse_title(item)
            start_date = self._parse_start(item)
            if not start_date:
                # Assume items with no start_date aren't valid meeting items
                self.log(f'No start date found for "{title}"', level=logging.WARNING)
                continue
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source="https://www.bismarcknd.gov/calendar.aspx",
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("span::text").get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        desc = item.css("p[itemprop='description']::text").get()
        return desc if desc else ""

    def _parse_classification(self, title):
        """Generate classification based on meeting title.
        "commission meeting" generally indicates a regular
        meeting of the city commission.
        """
        if not title:
            return NOT_CLASSIFIED
        clean_title = title.lower()
        if "commission meeting" in clean_title:
            return COMMISSION
        if "board" in clean_title:
            return BOARD
        elif "committee" in clean_title:
            return COMMITTEE
        elif "council" in clean_title:
            return CITY_COUNCIL
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_date_time = item.css("span[itemprop='startDate']::text").get()
        if not start_date_time:
            return None
        return datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, item):
        """Parse location. Addresses are formatted in several
        different ways in the HTML so account for different
        configurations as best we can.
        """
        name_parts = item.css("span[itemprop='location'] > span[itemprop='name'] > p")
        address_parts = item.css(
            "span[itemprop='address'] > span[itemprop='streetAddress']::text"
        )
        if not name_parts and not address_parts:
            return {"name": "TBD", "address": ""}
        name = ""
        address = ""
        if name_parts:
            if len(name_parts) > 1:
                name = name_parts[0].css("::text").get()
                address = ", ".join(name_parts[1:].css("::text").getall())
            else:
                name = name_parts.css("::text").get()
        if not address and address_parts:
            address = address_parts.get()
        if not name and address_parts:
            address = address_parts.get()
        return {"name": name, "address": address}

    def _parse_links(self, item):
        """Parse or generate links."""
        links = [self.agenda_link]
        details_link = item.css("a")
        if not details_link:
            return links
        href = details_link.css("a::attr(href)").get()
        absolute_href = f"{self.host}{href}" if href else ""
        title = details_link.css("a::text").get()
        meeting_details = {
            "href": absolute_href,
            "title": title if title else "Meeting details",
        }
        links.append(meeting_details)
        return links
