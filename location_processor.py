# location_processor.py
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from shapely.geometry import Point
from constants import *
from redis_cache import RedisCache
from directions_api import DirectionsAPI
import logging

class LocationProcessor:
    def __init__(self, gdf_dict, septa_processing_queue, dc_metro_processing_queue):
        self.gdf_dict = gdf_dict
        self.septa_processing_queue = septa_processing_queue
        self.dc_metro_processing_queue = dc_metro_processing_queue

    # Check the user provided coordinates to identify the dataset to
    # serve API request from
    def get_valid_dataset_key(self, latitude, longitude):
        if self.is_valid_location(latitude, longitude, SEPTA_VALID_LATITUDE_RANGE, SEPTA_VALID_LONGITUDE_RANGE):
            return SEPTA_DATASET_KEY
        elif self.is_valid_location(latitude, longitude, DC_METRO_VALID_LATITUDE_RANGE, DC_METRO_VALID_LONGITUDE_RANGE):
            return DC_METRO_DATASET_KEY
        else:
            return None

    # Check if user provided location coordinates are within a valid range of the stations
    def is_valid_location(self, latitude, longitude, valid_latitude_range, valid_longitude_range):
        return valid_latitude_range[0] <= latitude <= valid_latitude_range[1] and \
               valid_longitude_range[0] <= longitude <= valid_longitude_range[1]

    # Fetch the nearest station for user requested location asynchronously
    async def process_location_async(self, location, dataset_key):
        location_key = f"{dataset_key}_location:{location}"

        redis_cache = RedisCache._instance

        try:
            # Check cache for the nearest station GeoJson object for user provided coordinates
            cached_result = redis_cache.get(location_key)
        except Exception as e:
            logging.error(f"Error accessing cache for location_key '{location_key}': {str(e)}")
            return {"status": "Error accessing cache", "result": None}

        if cached_result:
            return {"status": "Location result retrieved from cache", "result": cached_result}
        else:
            # Check if location is already being processed to prevent multiple instances
            # from processing the same location at a time
            processing_queue = self.get_dataset_queue(dataset_key)

            if location_key in processing_queue:
                # Wait to fetch result from cache if already being processed by another request
                while redis_cache.get(location_key) is None:
                    await asyncio.sleep(0.01)

                try:
                    cached_result = redis_cache.get(location_key)
                except Exception as e:
                    logging.error(f"Error accessing cache for location_key '{location_key}': {str(e)}")
                    return {"status": "Error accessing cache", "result": None}

                # Return result from the cache
                return {"status": "Location result retrieved from another's execution", "result": cached_result}

            else:
                # Fetch station GeoJson object from dataset

                # Add the current request being processed to appropriate queue
                processing_queue.add(location_key)
                try:
                    # Get the GDF object for the appropriate dataset
                    gdf = self.gdf_dict[dataset_key]
                    result = self.find_nearest_station(location[0], location[1], gdf, dataset_key)

                    try:
                        # Store key:value in redis on successful retrieval from dataset
                        redis_cache.set(location_key, result)
                    except Exception as e:
                        logging.error(f"Error storing result in cache for location_key '{location_key}': {str(e)}")

                    return {"status": "Location result retrieved", "result": result}

                finally:
                    # Remove location request from queue once processed completely
                    processing_queue.remove(location_key)

    # Process location request asynchronously
    def process_location_for_dataset(self, location, dataset_key):
        return asyncio.run(self.process_location_async(location, dataset_key))

    # Get the appropriate queue for the dataset being processed
    def get_dataset_queue(self, dataset_key):
        if dataset_key == SEPTA_DATASET_KEY:
            return self.septa_processing_queue
        elif dataset_key == DC_METRO_DATASET_KEY:
            return self.dc_metro_processing_queue
        else:
            return None

    # Function to create the GeoJson object for the nearest station from the GeoDataFrame object
    def find_nearest_station(self, latitude, longitude, gdf, dataset_key):
        if gdf is None:
            return {"error": "GeoDataFrame is not loaded for the dataset."}

        try:
            # Find the nearest station
            nearest_station = gdf.geometry.distance(Point(longitude, latitude)).idxmin()
            nearest_station_info = gdf.loc[nearest_station]

            start_location = [longitude, latitude]
            end_location = [nearest_station_info.geometry.x, nearest_station_info.geometry.y]

            # Get walking directions to the station
            directions_api = DirectionsAPI(api_key=ORS_API_KEY)
            walking_directions = directions_api.get_walking_directions(start_location, end_location)

            # Return the result in GeoJSON format
            geojson_result = {
                "type": "Feature",
                "properties": {
                    "name": nearest_station_info["Name"],
                    "distance": nearest_station_info.geometry.distance(Point(longitude, latitude)),
                    "walking_directions": walking_directions
                },
                "geometry": nearest_station_info.geometry.__geo_interface__
            }

            return geojson_result
        except Exception as e:
            logging.error(f"Error finding nearest station: {str(e)}")
            return {"error": "An error occurred while finding the nearest station."}
