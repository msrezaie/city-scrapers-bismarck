from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.bcc import BCCMixin

spider_configs = [
    {
        "class_name": "BisndBCCASpider",
        "name": "bisnd_bcc_a",
        "agency": "Bismarck City Commission - Administration",
        "cid": 52,
    },
    {
        "class_name": "BisndBCCBASpider",
        "name": "bisnd_bcc_ba",
        "agency": "Bismarck City Commission - Bismarck Airport",
        "cid": 54,
    },
    {
        "class_name": "BisndBCCBECSpider",
        "name": "bisnd_bcc_bec",
        "agency": "Bismarck City Commission - Bismarck Event Center",
        "cid": 85,
    },
    {
        "class_name": "BisndBCCPLSpider",
        "name": "bisnd_bcc_pl",
        "agency": "Bismarck City Commission - Bismarck Public Library",
        "cid": 55,
    },
    {
        "class_name": "BisndBCCCDCSpider",
        "name": "bisnd_bcc_cdc",
        "agency": "Bismarck City Commission - Central Dakota Communications Center (CenCom)",  # noqa
        "cid": 36,
    },
    {
        "class_name": "BisndBCCCASpider",
        "name": "bisnd_bcc_ca",
        "agency": "Bismarck City Commission - City Attorney",
        "cid": 59,
    },
    {
        "class_name": "BisndBCCPRBTSpider",
        "name": "bisnd_bcc_prbt",
        "agency": "Bismarck City Commission - City Pension & Retirement Board of Trustees",  # noqa
        "cid": 90,
    },
    {
        "class_name": "BisndBCCCSComSpider",
        "name": "bisnd_bcc_cscom",
        "agency": "Bismarck City Commission - Civil Service Commission",
        "cid": 91,
    },
    {
        "class_name": "BisndBCCCDSpider",
        "name": "bisnd_bcc_cd",
        "agency": "Bismarck City Commission - Community Development",
        "cid": 62,
    },
    {
        "class_name": "BisndBCCCDIBISpider",
        "name": "bisnd_bcc_cdib",
        "agency": "Bismarck City Commission - Community Development - Building Inspections",  # noqa
        "cid": 57,
    },
    {
        "class_name": "BisndBCCESpider",
        "name": "bisnd_bcc_e",
        "agency": "Bismarck City Commission - Engineering",
        "cid": 63,
    },
    {
        "class_name": "BisndBCCFSpider",
        "name": "bisnd_bcc_f",
        "agency": "Bismarck City Commission - Finance",
        "cid": 33,
    },
    {
        "class_name": "BisndBCCFEMSpider",
        "name": "bisnd_bcc_fem",
        "agency": "Bismarck City Commission - Fire - Emergency Management",
        "cid": 82,
    },
    {
        "class_name": "BisndBCCFDSpider",
        "name": "bisnd_bcc_fd",
        "agency": "Bismarck City Commission - Fire Department",
        "cid": 31,
    },
    {
        "class_name": "BisndBCCGMSSpider",
        "name": "bisnd_bcc_gms",
        "agency": "Bismarck City Commission - GIS / Maps",
        "cid": 67,
    },
    {
        "class_name": "BisndBCCHRSpider",
        "name": "bisnd_bcc_hr",
        "agency": "Bismarck City Commission - Human Resources",
        "cid": 69,
    },
    {
        "class_name": "BisndBCCIBSpider",
        "name": "bisnd_bcc_ib",
        "agency": "Bismarck City Commission - Intranet - BEAT",
        "cid": 87,
    },
    {
        "class_name": "BisndBCCIHRSpider",
        "name": "bisnd_bcc_ihr",
        "agency": "Bismarck City Commission - Intranet - Human Resources",
        "cid": 86,
    },
    {
        "class_name": "BisndBCCMCCSpider",
        "name": "bisnd_bcc_mcc",
        "agency": "Bismarck City Commission - Main City Calendar",
        "cid": 14,
    },
    {
        "class_name": "BisndBCCMCSpider",
        "name": "bisnd_bcc_mc",
        "agency": "Bismarck City Commission - Municipal Court",
        "cid": 72,
    },
    {
        "class_name": "BisndBCCPSpider",
        "name": "bisnd_bcc_p",
        "agency": "Bismarck City Commission - Police",
        "cid": 74,
    },
    {
        "class_name": "BisndBCCPHSpider",
        "name": "bisnd_bcc_ph",
        "agency": "Bismarck City Commission - Public Health",
        "cid": 76,
    },
    {
        "class_name": "BisndBCCPWSpider",
        "name": "bisnd_bcc_pw",
        "agency": "Bismarck City Commission - Public Works",
        "cid": 20,
    },
    {
        "class_name": "BisndBCCPWFSpider",
        "name": "bisnd_bcc_pwf",
        "agency": "Bismarck City Commission - Public Works - Forestry",
        "cid": 79,
    },
    {
        "class_name": "BisndBCCVFCSpider",
        "name": "bisnd_bcc_vfc",
        "agency": "Bismarck City Commission - Vision Fund Committee",
        "cid": 89,
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
                (BCCMixin, CityScrapersSpider),  # Base classes
                {**config},  # Attributes including name, agency, committee_id
            )
            # Register the class in the global namespace using its class_name
            globals()[class_name] = spider_class


create_spiders()
