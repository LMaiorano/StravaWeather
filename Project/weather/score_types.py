from Project.data_load import LoadData
from Project.weather.weather_module import WeatherModule

# WEATHER_PRESET_DICT is a dictionary of different weather_types, which can be updated if needed
WEATHER_PRESET_DICT = {'low': {'Overall': (0, 3.4)},
                       'medium': {'Overall': (3.4, 6.9)},
                       'high': {'Overall': (6.9, 10)},
                       'no_rain': {'Rain Score': (10, 10)},
                       'little_wind': {'Wind Score': (8, 10)},
                       'ideal': {'Wind Score': (8, 10), 'Sun Score': (8, 10), 'Rain Score': (10, 10)}
                       }

if __name__ == '__main__':
    # To get a dataframe following a certain preset, following function needs to be run:

    assigned_data = LoadData.get_combined_data_this_year()
    df = WeatherModule.get_df_with_preset(WEATHER_PRESET_DICT['low'], assigned_data)
    print(df)

