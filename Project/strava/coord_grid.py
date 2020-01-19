# https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
import os
from functools import wraps
from time import time

import numpy as np
import pandas as pd
import shapefile as shp


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            print(f'Total execution time: {end_ if end_ > 0 else 0} ms')
    return _time_it


@measure
def generate_coord_grid(shape_file, save_file):

    def read_shapefile(shp_path):
        """
        Read a shapefile into a Pandas dataframe with a 'coords'
        column holding the geometry information. This uses the pyshp
        package
        """
        assert os.path.exists(shp_path), "Input file does not exist."

        sf = shp.Reader(shp_path)
        fields = [x[0] for x in sf.fields][1:]
        records = sf.records()
        shps = [s.points for s in sf.shapes()]
        df = pd.DataFrame(columns=fields, data=records)
        df = df.assign(coords=shps)
        return df

    def transform_to_ddegrees(coord_tuple):
        #page 44
        E = coord_tuple[0]
        N = coord_tuple[1]

        # Parameters
        lon_0 = 0       # Longitude of natural origin
        a = 6378137.0       # Ellipsoid [m]
        FE = 0   # False Easting [m]
        FN = 0   # False Northing [m]

        D = (FN - N) / a
        rlat = np.pi/2 - 2*np.arctan(np.exp(D))  # [Rad]
        rlon = (E - FE) / a + lon_0              # [Rad]

        lat = rlat / np.pi * 180
        lon = rlon / np.pi * 180

        return (lat, lon)

    # Open ShapeFile to Pandas DF
    coords_df = read_shapefile(shape_file)

    # Split single coords column into individual corners SW,NW,NE,SE,end
    coords = pd.Series(coords_df['coords'])
    corners = pd.DataFrame.from_dict(dict(zip(coords.index, coords.values))).T
    del coords      # Memory Management
    corners.columns = ['SW', 'NW', 'NE', 'SE', 'end']
    corners = corners.drop(['NW', 'SE', 'end'], axis=1)

    coords_df = coords_df.drop(['coords'], axis=1)
    coords_df = pd.concat([coords_df, corners], axis=1)
    del corners      # Memory Management

    ## Convert Coordinates to decimal degrees
    coords_df['SW'] = coords_df['SW'].swifter.apply(transform_to_ddegrees)
    coords_df['NE'] = coords_df['NE'].swifter.apply(transform_to_ddegrees)


    ## Split Dataframe into lat and lon of each corner
    lat_lon = pd.Series(coords_df['SW'])
    SW_lat_lon = pd.DataFrame.from_dict(dict(zip(lat_lon.index, lat_lon.values))).T
    SW_lat_lon.columns = ['SW_lat', 'SW_lon']

    lat_lon = pd.Series(coords_df['NE'])
    NE_lat_lon = pd.DataFrame.from_dict(dict(zip(lat_lon.index, lat_lon.values))).T
    NE_lat_lon.columns = ['NE_lat', 'NE_lon']
    del lat_lon

    coords_out = pd.concat([coords_df['id'], SW_lat_lon, NE_lat_lon], axis=1)
    del SW_lat_lon, NE_lat_lon

    # Sort
    coords_out = coords_out.sort_values(by=['SW_lat', 'SW_lon'], ascending=True)

    # Write to CSV:
    coords_out.to_csv(save_file, index=False)
    return coords_out


def main(shape_file, csv_out):
    generate_coord_grid(shape_file, csv_out)


if __name__ == '__main__':
    shp_loc = './reference_data/shape_files/WGS84_Pseudo-Mercator/NL_1km.shp'
    csv = './reference_data/csv_grids/NL_1km.csv'

    main(shp_loc, csv)
