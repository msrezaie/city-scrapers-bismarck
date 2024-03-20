from datetime import datetime

import pytest
from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)

from city_scrapers.mixins.mc import MCMixin


class TestMCMixin:
    @pytest.fixture
    def mixin(self):
        # Setup a basic instance of the mixin
        # Ensure the required static vars are set
        class TestSpider(MCMixin):
            name = "test_spider_mc"
            agency = "test_agency"
            category_id = 100

        return TestSpider()

    def test_mixin_initialization_requires_vars(self):
        # Testing that the mixin raises NotImplementedError if required
        # static vars are not defined
        with pytest.raises(NotImplementedError) as exc_info:

            class InvalidSpider(MCMixin):
                pass  # Missing required vars

        assert "must define the following static variable(s)" in str(
            exc_info.value
        ), "Mixin should raise NotImplementedError for missing required static variables."  # noqa

    def test_start_requests_url_format(self, mixin):
        # Test if the start_requests method builds the URL correctly
        requests = list(mixin.start_requests())
        assert requests, "start_requests should yield at least one Request"
        url = requests[0].url
        assert mixin.base_url in url, "The base_url should be part of the request URL"
        assert (
            str(mixin.category_id) in url
        ), "The category_id should be part of the request URL"
        assert "Events?$filter=categoryId+in+(" in url, "URL filter format is incorrect"

    def test_parse_classification(self, mixin):
        # Test various classifications based on category name
        assert mixin._parse_classification("City Council Meeting") == CITY_COUNCIL
        assert mixin._parse_classification("Board Meeting") == BOARD
        assert mixin._parse_classification("Commission Meeting") == COMMISSION
        assert mixin._parse_classification("Committee Meeting") == COMMITTEE
        assert mixin._parse_classification("Other Meeting") == NOT_CLASSIFIED

    def test_parse_start(self, mixin):
        # Test the start date and time parsing
        start = "2024-03-12T09:00:00Z"
        parsed_start = mixin._parse_start(start)
        assert isinstance(
            parsed_start, datetime
        ), "Parsed start should be a datetime object"
        assert (
            parsed_start.year == 2024
            and parsed_start.month == 3
            and parsed_start.day == 12
        ), "Parsed date does not match expected values"

    def test_parse_location(self, mixin):
        # Test location parsing with complete details
        location = {
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Mandan",
            "state": "ND",
            "zipCode": "58554",
        }
        parsed_location = mixin._parse_location(location)
        assert (
            parsed_location["address"] == "123 Main St, Suite 100, Mandan, ND, 58554"
        ), "Parsed address does not match expected format"

        # Test with minimal details
        location_minimal = {
            "address1": "123 Main St",
            "address2": "",
            "city": "",
            "state": "",
            "zipCode": "",
        }
        parsed_location_minimal = mixin._parse_location(location_minimal)
        assert (
            parsed_location_minimal["address"] == "123 Main St"
        ), "Parsed address should handle minimal details correctly"

    def test_parse_links(self, mixin):
        # Test links parsing with some published files
        item_with_files = {
            "publishedFiles": [
                {
                    "name": "Agenda",
                    "fileId": "12345",
                },
                {
                    "name": "Minutes",
                    "fileId": "67890",
                },
            ]
        }
        parsed_links = mixin._parse_links(item_with_files)
        assert len(parsed_links) == 2, "Should parse all published files into links"
        assert (
            parsed_links[0]["title"] == "Agenda"
        ), "First link title does not match expected value"
        assert (
            "fileId=12345" in parsed_links[0]["href"]
        ), "First link href does not contain correct fileId"
