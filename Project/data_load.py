import os
import pandas as pd

from Project.definitions import SEGMENT_DATA_DIR, ACTIVITY_DATA_DIR, BASELINE_DATA_DIR


class LoadData:

    @staticmethod
    def get_raw_data_alltime(columns=None):
        if columns == None:
            cols = ["segment_id", "date", "start_latlng", "end_latlng", "moving_time"]
        else:
            cols = columns
        path = os.path.join(ACTIVITY_DATA_DIR,
                            'Project_strava_final_generated_data_ZH_5km_full_leaderboard_overall.parquet')
        return pd.read_parquet(path, columns=cols)

    @staticmethod
    def get_filter_data_alltime(columns=None):
        if columns == None:
            cols = ["date", "segment_id" , "end_latlng"]
        else:
            cols = columns
        path = os.path.join(ACTIVITY_DATA_DIR,
                            'filtered_all_time_data.parquet')
        return pd.read_parquet(path, columns=cols)

    @staticmethod
    def get_filter_data_this_year(columns=None):
        if columns == None:
            cols = ["date", "segment_id", "end_latlng", "entries"]
        else:
            cols = columns
        path = os.path.join(ACTIVITY_DATA_DIR,
                            'filtered_this_year_data.parquet')
        return pd.read_parquet(path, columns=cols)

    @staticmethod
    def get_combined_data_this_year(columns=None):
        if columns == None:
            cols = ["date", "segment_id", "entries", "nearest_station", "Sun Score", "Rain Score", "Wind Score", "Extreme", "Overall"]
        else:
            cols = columns
        path = os.path.join(ACTIVITY_DATA_DIR,
                            'combined_this_year_data.parquet')
        return pd.read_parquet(path, columns=cols)

    @staticmethod
    def get_raw_data_year(columns=None):
        if columns == None:
            cols = ["segment_id", "date", "start_latlng", "end_latlng", "moving_time"]
        else:
            cols = columns
        path = os.path.join(BASELINE_DATA_DIR, '1_year_data.parquet')
        return pd.read_parquet(path, columns=cols)

    @staticmethod
    def get_segment_coords():
        path = os.path.join(SEGMENT_DATA_DIR, 'segments_ZH_5km.csv')
        df = pd.read_csv(path, usecols=['id', 'Start_coordinates', 'End_coordinates'])
        df.rename(columns={'id':'segment_id', 'Start_coordinates':'start_latlng',
                                'End_coordinates':'end_latlng'}, inplace=True)
        return df

    @staticmethod
    def get_baseline_alltime():
        path = os.path.join(BASELINE_DATA_DIR, 'alltime_daily_baseline.parquet')
        return pd.read_parquet(path)

    @staticmethod
    def get_baseline_this_year():
        path = os.path.join(BASELINE_DATA_DIR, 'this_year_daily_baseline.parquet')
        return pd.read_parquet(path)

if __name__ == '__main__':
    data = LoadData.get_combined_data_this_year()
    pd.set_option('display.width', 500)
    pd.set_option('display.max_columns', 10)
    print(f'Combined leaderboard and weather data, {data.shape[0]} entries \n', data.head(10))
