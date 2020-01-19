import os
import sys
import time
from datetime import datetime

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib import colors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Project.analysis  import BaselineCompare, CleanRawData
from Project.data_load import LoadData
from Project.definitions import VISUAL_RESULTS_DIR, CREDENTIALS_PATH
from Project.visualization.custom_libs import gmplot


class GoogleHeatmap:
    def __init__(self, results_dir=VISUAL_RESULTS_DIR,weatherType='Sunny Test'):
        """
        :var results_dir: **RELATIVE** path to directory to save results, use '\\..\\' as required
        """
        self.__map_cntr = (52.011821, 4.359605) # Delft
        self.__map_type = 'roadmap'
        self.__results_dir = results_dir

        if weatherType[-5:] == '.html':
            weather_name = weatherType[:-5]
        else:
            weather_name = weatherType

        self.__weather_type = weather_name

        for old, new in {' ':'_', ':':'', '/':'_'}.items():
            weather_name = weather_name.replace(old, new)
        weather_name ='weather_' + weather_name + '_google_map'
        self.__html_name = weather_name + '.html'

    def extract_lat_lon_weight(self, dataframe):
        if "pytest" not in sys.modules:
            seg_df = LoadData.get_segment_coords()
            # Add weights column
            dataframe = pd.merge(dataframe, seg_df, on='segment_id')



        # V2: retain entries column for use with weights
        start_df = dataframe[["start_latlng", "entries"]].copy()
        start_df.rename(columns={'start_latlng':'LatLon',
                                 'entries':'Weight'},
                        inplace=True)

        end_df = dataframe[["end_latlng", "entries"]].copy()
        end_df.rename(columns={'end_latlng': 'LatLon',
                                 'entries': 'Weight'},
                      inplace=True)


        data = pd.concat([start_df, end_df], sort=True).sort_values(by=['LatLon']).reset_index(drop=True)
        data[['LAT', 'LON']] = data['LatLon'].str[1:-1].str.split(',', expand=True).astype(float)
        data = data.drop(columns=['LatLon'])


        # Assign Latitudes and Longitudes as Series objects
        latitudes = data['LAT']
        longitudes = data['LON']
        weights = data['Weight']

        # Set map center
        self.__map_cntr = (latitudes.mean(), longitudes.mean())

        del dataframe, start_df, end_df
        return latitudes, longitudes, weights, data


    def gen_googlemap(self, dataframe, zoom_level=9, threshold=10, radius=10, gradient=None,
                      opacity=0.6, maxIntensity=None, dissipating=True, map_type='roadmap'):
        # https://developers.google.com/maps/documentation/javascript/heatmaplayer
        self.__map_zoom = zoom_level
        self.__map_type = map_type
        self.html_path = os.path.join(self.__results_dir, self.__html_name)

        # Google Maps API key from Luigi GCP Account:
        API_file_path = CREDENTIALS_PATH
        with open(API_file_path, 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            api_key = cfg['Google']['key']

        latitudes, longitudes, weights, _ = self.extract_lat_lon_weight(dataframe)

        gmap = gmplot.GoogleMapPlotter(self.__map_cntr[0], self.__map_cntr[1], self.__map_zoom)
        gmap.apikey = api_key
        gmap.heatmap(latitudes, longitudes, weights, threshold, radius, gradient, opacity, maxIntensity, dissipating)

        # Generate the heatmap into an HTML file
        gmap.draw(self.html_path, mapType=self.__map_type, weatherType=self.__weather_type)

        return self.html_path



    def screenshot(self, img_name='screenshot', headless=True):
        date_time = datetime.now().strftime("%m%d%y_%H-%M-%S")
        image_name = img_name + "_" + date_time
        image_name += f'_{self.__map_type}'

        self.img_path = os.path.join(VISUAL_RESULTS_DIR, image_name+".png")

        # print(image_name)

        chrome_options = Options()
        if headless:
            width = 1920
            height =1080
            chrome_options.add_argument('--headless')
            chrome_options.add_argument(f'window-size={width}x{height}')

        DRIVER = 'chromedriver'
        driver = webdriver.Chrome(DRIVER, options=chrome_options)

        selenium_html_path = 'file:' + os.path.join(os.getcwd(), self.__results_dir, self.__html_name)

        driver.get( selenium_html_path )
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.CLASS_NAME, "gmnoprint")))

        time.sleep(1)
        driver.save_screenshot(self.img_path)
        driver.quit()



class ComparisonHeatmap:

    @staticmethod
    def group_by(df):
        df['entries'] = df.groupby(['LAT'])['LON'].transform('count')
        return df.drop_duplicates(['LAT', 'LON']).reset_index(drop=True)


    @staticmethod
    def load_sample_data():
        test_data = os.path.join(os.path.dirname(__file__), 'test/reference_data/ZH_5km_leaderboard_this_year_top10.csv')
        test_df = pd.read_csv(test_data)
        df = CleanRawData.group_by_date_seg(test_df)

        date_start = '2019-06-01'
        date_end =  '2019-06-02'
        single_day = df[(df['date'] > date_start) & (df['date'] < date_end)]

        latlon_df = GoogleHeatmap.extract_lat_lon_weight(GoogleHeatmap(), single_day)[3]
        return latlon_df

    @staticmethod
    def transform_to_ddegrees(coord_tuple):
        # ONE TIME USE for generation of background image

        # page 44
        E = coord_tuple[0]
        N = coord_tuple[1]

        # Parameters
        lon_0 = 0  # Longitude of natural origin
        a = 6378137.0  # Ellipsoid [m]
        FE = 0  # False Easting [m]
        FN = 0  # False Northing [m]

        D = (FN - N) / a
        rlat = np.pi / 2 - 2 * np.arctan(np.exp(D))  # [Rad]
        rlon = (E - FE) / a + lon_0  # [Rad]

        lat = rlat / np.pi * 180
        lon = rlon / np.pi * 180

        return round(lat, 2), round(lon, 2)


    @staticmethod
    def combine_segs_weights_latlon(seg_weights_df):
        seg_df = LoadData.get_segment_coords()

        # Add weights column
        seg_df = pd.merge(seg_df, seg_weights_df, on='segment_id')

        start_df = seg_df[["start_latlng", "entries"]].copy()
        start_df.rename(columns={'start_latlng': 'LatLon',
                                 'entries': 'Weight'},
                        inplace=True)

        end_df = seg_df[["end_latlng", "entries"]].copy()
        end_df.rename(columns={'end_latlng': 'LatLon',
                               'entries': 'Weight'},
                      inplace=True)

        data = pd.concat([start_df, end_df], sort=True).sort_values(by=['Weight']).reset_index(drop=True)
        data[['LAT', 'LON']] = data['LatLon'].str[1:-1].str.split(',', expand=True).astype(float)
        data = data.drop(columns=['LatLon'])

        data = data.dropna()

        return data


    @staticmethod
    def forceAspect(ax,aspect):
        im = ax.get_images()
        extent =  im[0].get_extent()
        ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)




    def gen_map(self, seg_weights_df, weatherType='SunnyTest', savefig=False, results_dir=VISUAL_RESULTS_DIR, cbarZeroed=True):
        # Convert [seg_id, weights]_df to [Lat, Lon, Weight]_df
        LatLonWeight_df = self.combine_segs_weights_latlon(seg_weights_df)

        # Background Image:
        png = os.path.join(os.path.dirname(__file__), 'ZH_ww_background_sq.png')
        zh_image = mpimg.imread(png)
        qgis_bounds = [(426037.9063, 6724262.4089), (575068.9736, 6873293.4762)]
        img_b = []
        for corner in qgis_bounds:
            img_b.append(self.transform_to_ddegrees(corner))


        if cbarZeroed:
            norm = colors.DivergingNorm(vcenter=0)
        else:
            norm = colors.DivergingNorm(vcenter=LatLonWeight_df['Weight'].mean())

        scatter = LatLonWeight_df.plot(kind='scatter', x='LON', y='LAT', alpha=0.4, c='Weight',
                                  cmap=plt.get_cmap('coolwarm'), norm=norm, figsize=(10,8), colorbar=True)
        scatter.imshow(zh_image, extent=[img_b[0][1], img_b[1][1], img_b[0][0], img_b[1][0]], alpha=0.8)
        self.forceAspect(scatter, aspect=1)

        plt.title(weatherType, fontsize=16)
        plt.xlabel("Latitude", fontsize=14)
        plt.ylabel("Longitude", fontsize=14)

        f = plt.gcf()
        cbar_ax = f.get_axes()[1]
        cbar_ax.set_ylabel('[%] Percent Deviation from Baseline', fontsize=14)


        if savefig:
            for old, new in {':':'', '+':'', '&':'', ' |':'_', ' [':'', ' ]':'', ' ':'_'}.items():
                weatherType = weatherType.replace(old, new)

            path = os.path.join(results_dir, weatherType + '_map.png')
            plt.savefig(path, dpi=900, bbox_inches='tight')

        plt.show()



if __name__ == '__main__':
    year_data = LoadData.get_filter_data_this_year()
    data = BaselineCompare.compare(year_data)

    h = ComparisonHeatmap()
    h.gen_map(data, weatherType='All Weather, full year', savefig=True, cbarZeroed=True)

    g = GoogleHeatmap()
    g.gen_googlemap(data)


