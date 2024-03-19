from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class BisndMccSpider(CityScrapersSpider):
    name = "bisnd_mcc"
    agency = "Morton County Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.mortonnd.org/?Type=B_BASIC&SEC={8182F8B8-3783-4C56-B690-F78FEE7CAC95}"  # noqa
    ]
    title = "Morton County Commission Meeting"
    meeting_time = time(17, 30)
    location = {
        "address": "Morton County Commission Room",
        "name": "Morton County Courthouse, 210 2nd Ave NW, Mandan ND",
    }
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def parse(self, response):
        """
        Parse HTML table and extract meeting information. Due to a lack of info,
        we hardcode certain fields, like start time and title
        """
        for item in response.css("main[role='main'] table tbody tr:not(:first-child)"):
            start, description = self._first_col(item)
            if start is None:
                self.logger.warning("Invalid date format - skipping")
                continue
            # ignore meetings that are more than a year ago
            if start < datetime.now().replace(year=datetime.now().year - 1):
                self.logger.info(
                    f"Skipping meeting from {start} as it is more than a year ago"
                )
                continue
            meeting = Meeting(
                title=self.title,
                description=description,
                classification=COMMISSION,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _first_col(self, item):
        """Extract date of the meeting and any additional text from
        the first column of the table row. Date of the meeting is in
        "Month Day, Year" format."""
        col_str = item.css("td span::text").extract_first()
        description = ""

        # Parse text
        if col_str is None:
            self.logger.info("No text found in date column")
            return None, description
        col_words = col_str.split()
        if len(col_words) < 3:
            # date should always be first three words
            self.logger.info(f"Invalid date format: {col_words}")
            return None, description
        date_str = " ".join(col_words[:3])
        if len(col_words) > 3:
            # if there's any other text, use that as the description
            description = " ".join(col_words[3:])

        # parse date
        try:
            parsed_date = parse(date_str)
            # combine date and time
            parsed_date = datetime.combine(parsed_date.date(), self.meeting_time)
            return parsed_date, description
        except ValueError:
            self.logger.info(f"Invalid date format: {date_str}")
            return None, description

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for row in item.css("td:not(:first-child) a"):
            link = {
                "title": row.css("::text").extract_first(),
                "href": row.css("::attr(href)").extract_first(),
            }
            links.append(link)
        return links
