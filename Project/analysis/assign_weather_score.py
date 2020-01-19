from Project.weather.weather_module import WeatherModule
from Project.data_load import LoadData
import json
import pandas as pd
from Project.definitions import ACTIVITY_DATA_DIR
import os


class AssignWeatherScore:

    @staticmethod
    def assign_scores(df):
        df['date'] = df['date'].apply(lambda x: int(x))
        coordinate_station_dict = AssignWeatherScore.get_station_dict(df)
        df['nearest_station'] = df.end_latlng.map(coordinate_station_dict)
        merged_data = AssignWeatherScore.merge_entries_with_weather(df, [344, 215])
        res = merged_data.drop(columns=['end_latlng'])
        return res

    @staticmethod
    def convert_str_to_int(string):
        return int(string)

    @staticmethod
    def get_station_dict(df):
        unique_coordinates = df.end_latlng.unique()
        res_dict = {}
        for coordinate in unique_coordinates:
            res_dict[coordinate] = AssignWeatherScore.find_nearest_weather_station(coordinate)
        return res_dict

    @staticmethod
    def find_nearest_weather_station(latlng):
        latlong = json.loads(latlng)  # we could choose to go for an average of the start and end coordinates
        return WeatherModule.get_closest_station(latlong[0], latlong[1])

    @staticmethod
    def merge_entries_with_weather(leaderboard_df, station_ids):
        full_df = pd.DataFrame()
        for station_id in station_ids:
            entries_df = leaderboard_df[leaderboard_df['nearest_station'] == station_id]
            weather_df = WeatherModule.build_weather_score_df(WeatherModule.scrape_KNMI(station_id, 2019, 1, 1, 2020, 1, 1))
            weather_df = weather_df.rename(columns={'Date': 'date'})
            total_df = pd.merge(left=entries_df, right=weather_df, on='date')
            full_df = full_df.append(total_df, ignore_index=True)
        return full_df


if __name__ == "__main__":
    leaderboard_data = LoadData.get_filter_data_this_year()
    print('data loaded')
    print(leaderboard_data.info())
    assigned_data = AssignWeatherScore.assign_scores(leaderboard_data)
    print('\n assigned all data')
    print(assigned_data.info())

    path = os.path.join(ACTIVITY_DATA_DIR, 'combined_this_year_data.parquet')
    # assigned_data.to_parquet(path)  # commented to prevent unwanted overwriting of data files
    retrieved_data = pd.read_parquet(path)
    print('\n retrieved data')
    print(list(retrieved_data.columns))
    print(retrieved_data.info())
