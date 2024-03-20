from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.mc import MCMixin

spider_configs = [
    {
        "agency": "City of Mandan - General",
        "category_id": 24,
        "name": "bisnd_mc_g",
        "class_name": "BisndMCGSpider",
    },
    {
        "agency": "City of Mandan - City Commission",
        "category_id": 26,
        "name": "bisnd_mc_cc",
        "class_name": "BisndMCCCSpider",
    },
    {
        "agency": "City of Mandan - Airport Authority",
        "category_id": 27,
        "name": "bisnd_mc_aa",
        "class_name": "BisndMCAASpider",
    },
    {
        "agency": "City of Mandan - Architectural Review Commission",
        "category_id": 28,
        "name": "bisnd_mc_arc",
        "class_name": "BisndMCARCSpider",
    },
    {
        "agency": "City of Mandan - Civil Service Commission",
        "category_id": 29,
        "name": "bisnd_mc_csc",
        "class_name": "BisndMCCSCSpider",
    },
    {
        "agency": "City of Mandan - Code Enforcement Appeals Board",
        "category_id": 30,
        "name": "bisnd_mc_ceab",
        "class_name": "BisndMCCEABSpider",
    },
    {
        "agency": "City of Mandan - Community Beautification Committee",
        "category_id": 31,
        "name": "bisnd_mc_cbc",
        "class_name": "BisndMCCBCSpider",
    },
    {
        "agency": "City of Mandan - Board of Equalization",
        "category_id": 32,
        "name": "bisnd_mc_boe",
        "class_name": "BisndMCBOESpider",
    },
    {
        "agency": "City of Mandan - Growth Fund Committee",
        "category_id": 33,
        "name": "bisnd_mc_gfc",
        "class_name": "BisndMCGFCSpider",
    },
    {
        "agency": "City of Mandan - Library Board of Trustees",
        "category_id": 34,
        "name": "bisnd_mc_lbot",
        "class_name": "BisndMCLBOTSpider",
    },
    {
        "agency": "City of Mandan - Parking Authority",
        "category_id": 35,
        "name": "bisnd_mc_pa",
        "class_name": "BisndMCPASpider",
    },
    {
        "agency": "City of Mandan - Planning and Zoning Commission",
        "category_id": 36,
        "name": "bisnd_mc_pazc",
        "class_name": "BisndMCPAZCSpider",
    },
    {
        "agency": "City of Mandan - Remediation Trust",
        "category_id": 37,
        "name": "bisnd_mc_rt",
        "class_name": "BisndMCRTSpider",
    },
    {
        "agency": "City of Mandan - Renaissance Zone Committee",
        "category_id": 38,
        "name": "bisnd_mc_rzc",
        "class_name": "BisndMCRZCSpider",
    },
    {
        "agency": "City of Mandan - Special Assessment Committee",
        "category_id": 39,
        "name": "bisnd_mc_sac",
        "class_name": "BisndMCSACSpider",
    },
    {
        "agency": "City of Mandan - Tree Board",
        "category_id": 40,
        "name": "bisnd_mc_tb",
        "class_name": "BisndMCTBSpider",
    },
    {
        "agency": "City of Mandan - Visitors Committee",
        "category_id": 41,
        "name": "bisnd_mc_vc",
        "class_name": "BisndMCVCSpider",
    },
    {
        "agency": "City of Mandan - Weed Board",
        "category_id": 42,
        "name": "bisnd_mc_wb",
        "class_name": "BisndMCWBSpider",
    },
]


def create_spiders():
    """
    Dynamically create spider classes using the spider_configs list
    and then register them in the global namespace. This approach
    is the equivalent of declaring each spider class in the same
    file but it is a little more concise.
    """
    for config in spider_configs:
        class_name = config.pop("class_name")
        # We make sure that the class_name is not already in the global namespace
        # Because some scrapy CLI commands like `scrapy list` will inadvertently
        # declare the spider class more than once otherwise
        if class_name not in globals():
            spider_class = type(
                class_name,
                (MCMixin, CityScrapersSpider),  # Base classes
                {**config},  # Attributes including name, agency, committee_id
            )
            # Register the class in the global namespace using its class_name
            globals()[class_name] = spider_class


create_spiders()
