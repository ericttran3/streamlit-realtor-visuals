# config.py
from pathlib import Path
import os

# Base paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = BASE_DIR / "data" / "realtor"

# Data files
DATA_FILES = {
    "country": DATA_DIR / "RDC_Inventory_Core_Metrics_Country_History.csv",
    "state": DATA_DIR / "RDC_Inventory_Core_Metrics_State_History.csv",
    "metro": DATA_DIR / "RDC_Inventory_Core_Metrics_Metro_History.csv",
    "county": DATA_DIR / "RDC_Inventory_Core_Metrics_County_History.csv",
    "zip": DATA_DIR / "RDC_Inventory_Core_Metrics_Zip_History.csv"
}

# Available metrics for visualization
METRICS = [
    ("active_listing_count", "Active Listing Count"), 
    ("new_listing_count", "New Listing Count"),
    ("pending_listing_count", "Pending Listing Count"),
    ("total_listing_count", "Total Listing Count"),
    ("pending_ratio", "Pending Ratio"),
    ("median_listing_price", "Median Listing Price"),
    ("average_listing_price", "Average Listing Price"),
    ("median_square_feet", "Median Square Feet"),
    ("median_listing_price_per_square_foot", "Price per Square Foot"),
    ("median_days_on_market", "Median Days on Market"),
    ("price_increased_count", "Price Increased Count"),
    ("price_reduced_count", "Price Reduced Count"),
]

# Default selections
DEFAULT_METRIC = "median_listing_price"
DEFAULT_GEO_LEVEL = "State"
DEFAULT_STATE = "California"

# Geo Mappings
GEO_MAPPINGS = {
    "Country": {
        "id_col": None,
        "name_col": "country",
        "display_name": "Country"
    },
    "State": {
        "id_col": "state_id",  # This should match your CSV column name
        "name_col": "state",   # This should match your CSV column name
        "display_name": "State"
    },
    "Metro": {
        "id_col": "cbsa_code",
        "name_col": "cbsa_title",
        "display_name": "Metro Area"
    },
    "County": {
        "id_col": "county_fips",
        "name_col": "county_name",
        "display_name": "County"
    },
    "Zip": {
        "id_col": "postal_code",
        "name_col": "zip_name",
        "display_name": "ZIP Code"
    }
}

GEO_LEVELS = list(GEO_MAPPINGS.keys())


# Chart properties configuration
CHART_PROPERTIES = {
    "height": 300,
    "width": 'container',
    "title_font_size": 16,
    "subtitle_font_size": 12,
    "subtitle_color": "gray",
    "color": "black"
}

# State to FIPS code mapping
STATE_TO_FIPS = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09',
    'DE': '10', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18',
    'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25',
    'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32',
    'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47',
    'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55',
    'WY': '56', 'DC': '11'
}


# Constants and Mappings
STATE_FIPS = {
    'Alabama': 1, 'Alaska': 2, 'Arizona': 4, 'Arkansas': 5, 'California': 6,
    'Colorado': 8, 'Connecticut': 9, 'Delaware': 10, 'District of Columbia': 11,
    'Florida': 12, 'Georgia': 13, 'Hawaii': 15, 'Idaho': 16, 'Illinois': 17,
    'Indiana': 18, 'Iowa': 19, 'Kansas': 20, 'Kentucky': 21, 'Louisiana': 22,
    'Maine': 23, 'Maryland': 24, 'Massachusetts': 25, 'Michigan': 26,
    'Minnesota': 27, 'Mississippi': 28, 'Missouri': 29, 'Montana': 30,
    'Nebraska': 31, 'Nevada': 32, 'New Hampshire': 33, 'New Jersey': 34,
    'New Mexico': 35, 'New York': 36, 'North Carolina': 37, 'North Dakota': 38,
    'Ohio': 39, 'Oklahoma': 40, 'Oregon': 41, 'Pennsylvania': 42,
    'Rhode Island': 44, 'South Carolina': 45, 'South Dakota': 46,
    'Tennessee': 47, 'Texas': 48, 'Utah': 49, 'Vermont': 50, 'Virginia': 51,
    'Washington': 53, 'West Virginia': 54, 'Wisconsin': 55, 'Wyoming': 56
}

COUNTRY_MAPPING = {'United States': 840}
