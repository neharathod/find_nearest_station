# constants.py

PRECISION = 4

# Replace 'EPSG:XXXX' with the appropriate UTM zone for your region
PROJECTED_CRS = 'EPSG:4326'

# Redis Config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Open Route Service API Key
ORS_API_KEY = '5b3ce3597851110001cf624889c2262aaa7c4533904b1107be0396d4'

API_KEY = "API_KEY"

# Define valid API keys
VALID_API_KEYS = ["KEY2", "KEY1"]

# Define rate limiting parameters
RATE_LIMIT_THRESHOLD = 10
RATE_LIMIT_EXPIRATION_SECONDS = 60

# Define the geographical bounds of the SEPTA train station dataset
SEPTA_VALID_LONGITUDE_RANGE = (-75.8, -74.8)
SEPTA_VALID_LATITUDE_RANGE = (39.51, 40.9)

# Define the geographical bounds of the DC Metro station dataset
DC_METRO_VALID_LONGITUDE_RANGE = (-77.5, -76.5)
DC_METRO_VALID_LATITUDE_RANGE = (38.5, 39.5)

# Define dataset keys
SEPTA_DATASET_KEY = "septa"
DC_METRO_DATASET_KEY = "dc_metro"

# File paths for datasets
SEPTA_KMZ_FILE_PATH = "/Users/neharathod/Documents/TUF/Gisual/dataset/SEPTARegionalRailStations2016.kmz"
SEPTA_DOC_KML_PATH = "/Users/neharathod/Documents/TUF/Gisual/dataset/doc.kml"

DC_METRO_KML_PATH = "/Users/neharathod/Documents/TUF/Gisual/dataset/Metro_Stations_Regional.kml"
