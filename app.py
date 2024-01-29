# app.py
import os
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

from constants import *
from location_processor import LocationProcessor
from redis_cache import RedisCache
from authentication import Authentication
from geo_data_loader import extract_kml_from_kmz_file, convert_kml_to_GDF

app = Flask(__name__)
CORS(app)

redis_cache = RedisCache()

# Get the current working directory
current_directory = os.getcwd()

# Set up logging
log_file_path = os.path.join(current_directory, 'app.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO)

# Processing queues for each dataset
septa_processing_queue = set()
dc_metro_processing_queue = set()

# GeoDataFrames for each dataset
gdf_dict = {
    SEPTA_DATASET_KEY: None,
    DC_METRO_DATASET_KEY: None
}

# Create GDF for Septa and DC Metro datasets
def load_datasets():
    """
    Load datasets as GeoDataFrame objects
    """
    try:
        extract_kml_from_kmz_file(SEPTA_KMZ_FILE_PATH)
        gdf_dict[SEPTA_DATASET_KEY] = convert_kml_to_GDF(SEPTA_DOC_KML_PATH)
    except Exception as e:
        logging.error(f"Error loading SEPTA GeoDataFrame: {str(e)}")

    try:
        gdf_dict[DC_METRO_DATASET_KEY] = convert_kml_to_GDF(DC_METRO_KML_PATH)
    except Exception as e:
        logging.error(f"Error loading DC Metro GeoDataFrame: {str(e)}")

    return gdf_dict

# Load datasets for Septa and DC Metro
load_datasets()

location_processor = LocationProcessor(gdf_dict, septa_processing_queue, dc_metro_processing_queue)
authentication = Authentication()

# Expose functionality as an API
@app.route('/find_nearest_station', methods=['GET'])
@authentication.authenticate_and_rate_limit
def find_nearest_station_api():
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))

        #Round latitude and longitude to the specified precision
        rounded_latitude = round(latitude, PRECISION)
        rounded_longitude = round(longitude, PRECISION)
    except (TypeError, ValueError):
        logging.error("Invalid latitude or longitude in the request.")
        return jsonify({"error": "Invalid latitude or longitude"}), 400

    # Check if location in a valid range
    dataset_key = location_processor.get_valid_dataset_key(latitude, longitude)
    if dataset_key is None:
        logging.error("Invalid coordinates for any dataset.")
        return jsonify({"error": "There are no stations in your vicinity."})

    # Find the nearest station
    result = location_processor.process_location_for_dataset((rounded_latitude, rounded_longitude), dataset_key)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
