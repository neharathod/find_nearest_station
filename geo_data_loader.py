# geo_data_loader.py
import os
import fiona
import geopandas as gpd

from zipfile import ZipFile
from io import BytesIO

from constants import *

# Extract the contents of kmz file
def extract_kml_from_kmz_file(kmz_file_path):
    """
    Extract contents from kmz file in parent directory of file
    Parameters:
        kmz_file_path: kmz file path to extract contents from
    Returns: None
    """
    with ZipFile(kmz_file_path, "r") as kmz:
        kmz.extractall(os.path.dirname(kmz_file_path))

# Create a GeoDataFrame object from kml file
def convert_kml_to_GDF(kml_file_path):
    """
    Create a GeoDataFrame object from a kml file.
    Parameters:
        kml_file_path: kml file path
    Returns: None
    """
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    with fiona.open(kml_file_path, "r", driver='KML') as kml_file:
        return gpd.GeoDataFrame.from_features(kml_file, crs=PROJECTED_CRS)
