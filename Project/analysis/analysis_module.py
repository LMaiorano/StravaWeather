import pandas as pd
from Project.visualization.visual_module import GoogleHeatmap
from Project.strava.strava_module import StravaModule
from Project.weather.weather_module import WeatherModule
import os


class AnalysisModule:
    def __init__(self):
        self.__reference_data_dir = os.path.join(os.path.dirname(__file__), 'reference_data')
        self.__leaderboard_raw = self.load_leaderboard_raw()
        # self.__leaderboard_raw = pd.read_csv(os.path.join(os.path.dirname(__name__), '..', 'strava/working_data/ZH_5km_leaderboard_6358823_8530719.csv'))
        # self.__all_time_df = pd.read_csv('./reference_data/activities/all_time.csv')
        # self.__gradient_activities = pd.read_csv('./reference_data/activities/activities_compared.csv')

    def get_leaderboard_raw(self):
        return self.__leaderboard_raw

    def load_leaderboard_raw(self, columns=None):
        if columns is None:
            cols = ["segment_id", "date", "start_latlng", "end_latlng", "moving_time"]
        else:
            cols = columns
        path = os.path.join(self.__reference_data_dir, 'activities',
                            'Project_strava_final_generated_data_ZH_5km_full_leaderboard_overall.parquet')
        return pd.read_parquet(path, columns=cols)

    def baseline_generation(self):
        '''
        :return: Calculate a baseline segment intensity --> 'reference_data/activities/baseline.csv'
        This will represent the average usage intensity of each segment over the past few years.
        '''
        raise NotImplementedError()

    def compare_with_baseline(self):
        '''
        For every day in the requested time frame, compare all segments' intensity to the baseline.
        This will result in a positive or negative percentage (gradient), where 0% is no change.
        Can be a One-Time action
        :return: DF of all days, all activities, with gradient. Saved to CSV
        '''
        raise NotImplementedError()

    def activities_with_weather(self, weather_score):
        '''
        :return: Combine activities from all days with same weather score.
        The data will be sourced from all days in the given time frame, which meet the same weather score requirements.
        '''
        raise NotImplementedError()

    def visualize(self, output_filename):
        '''
        :return: Generate Heatmap, of activity locations, using gradient as weight
        '''
        # Heatmap.build_heatmap()
        raise NotImplementedError()

if __name__ == '__main__':
    anal = AnalysisModule()
    df = anal.get_leaderboard_raw()
    print(df.head())