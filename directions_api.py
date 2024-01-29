# directions_api.py
import openrouteservice
from pyproj import Transformer
from shapely.geometry import Point
from constants import *
import logging

class DirectionsAPI:
    def __init__(self, api_key):
        # Create a client to talk to the OpenRouteService API
        self.client = openrouteservice.Client(key=api_key)

    # Function to get walking directions using OpenRouteService
    def get_walking_directions(self, start_location, end_location):
        """
        Given the start location and end location as a tuple of (latitude, longitude) coords
        Returns:
            A list of textual walking instructions from start location to end location.
        """
        # Create a transformer for coordinate transformation
        transformer = Transformer.from_crs("EPSG:4326", PROJECTED_CRS, always_xy=True)

        # Transform start and end locations
        start_location_proj = Point(transformer.transform(*start_location))
        end_location_proj = Point(transformer.transform(*end_location))

        coords = [start_location_proj.coords[0], end_location_proj.coords[0]]

        try:
            directions = self.client.directions(coordinates=coords, profile='foot-walking', format='geojson')
            # Extract textual directions
            steps = directions['features'][0]['properties']['segments'][0]['steps']
            instructions = [step['instruction'] for step in steps]

            return instructions
        except openrouteservice.exceptions.ApiError as e:
            logging.error(f"Error from OpenRouteService API: {e}")
            return None
