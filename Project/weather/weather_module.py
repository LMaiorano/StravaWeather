import requests
import csv
import pandas as pd
import os

from Project.weather.station_selection import SelectStation

#stations in Zuid-Holland:
# 215: Voorschoten (Lat: 52.1333 N, Lon: 4.4333E)
# 330: Hoek van Holland (Lat: 51.98333 N, Lon: 4.1E )
# 344: Rotterdam (Lat: 51.95N, Lon: 4.1E)

class WeatherModule:

    @staticmethod
    def scrape_KNMI(stations, by, bm, bd, ey, em, ed, save=False, filename=None):
        if isinstance(stations, int):
            stations = [stations]

        Weather_URL = 'http://projects.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi'
        variables = 'FH:SQ:DR:M:R:S:O:Y'
        # variables = 'FH:SQ:DR' # WITHOUT EXTREME WEATHER
        bh = 8
        eh = 20
        Parameters = {
            'stns': stations,  # Which weather stations (colon separated)
            'vars': variables,  # Which weather parameters to get
            'byear': by,  # start year
            'bmonth': bm,  # start month
            'bday': bd,  # start day
            'bhour': bh,  # start hour
            'eyear': ey,  # end year
            'emonth': em,  # end month
            'eday': ed,  # end day
            'ehour': eh  # end hour
        }

        page = requests.get(url=Weather_URL, params=Parameters)
        filename='weather_temp.txt'
        WeatherModule.write_to_txt(filename, page.text)
        df = WeatherModule.txt_to_pandas(filename)
        os.remove(filename)
        return df

    @staticmethod
    def get_closest_station(LAT, LON):
        return SelectStation.get_closest_station(LAT, LON)

    @staticmethod
    def txt_to_pandas(file):
        with open(file) as textfile:
            reader = csv.reader(textfile)
            lines = []
            for line in reader:
                for i in range(len(line)):
                    line[i] = line[i].strip(' ')
                lines.append(line)
            df = pd.DataFrame(lines[20:], columns=lines[18])
            # df = pd.DataFrame(lines[15:], columns=lines[13]) # WITHOUT EXTREME WEATHER
            df = df.replace('', 0)
            df = df.astype(int)
            df = df.groupby('YYYYMMDD', as_index=False).sum()
        return df

    @staticmethod
    def write_to_txt(filename, data):
        with open(filename, 'w') as file:
            for line in data.split('\n'):
                file.write(line)

    @staticmethod
    def get_rain_score(day_score):
        if day_score == 0:
            result = 10
        elif day_score < 5:
            result = 9
        elif day_score < 10:
            result = 8
        elif day_score < 15:
            result = 7
        elif day_score < 20:
            result = 6
        elif day_score < 30:
            result = 5
        elif day_score < 40:
            result = 4
        elif day_score < 60:
            result = 3
        elif day_score < 80:
            result = 2
        elif day_score < 100:
            result = 1
        else:
            result = 0
        return result

    @staticmethod
    def build_weather_score_df(station_data):
        if not isinstance(station_data, pd.DataFrame):
            raise TypeError('station_data param should be of type df')

        ws = pd.DataFrame(columns=['Date', 'Sun Score', 'Rain Score', 'Wind Score', 'Extreme', 'Overall'])
        # ws = pd.DataFrame(columns=['Date', 'Sun Score', 'Rain Score', 'Wind Score', 'Overall']) # WITHOUT EXTREME
        ex_var = ['M', 'S', 'O', 'Y']
        ws['Date'] = round(station_data['YYYYMMDD'], 1)
        ws['Sun Score'] = round(station_data['SQ'] / 13, 0)
        ws['Rain Score'] = station_data['DR'].apply(WeatherModule.get_rain_score)
        ws['Wind Score'] = 10 - round((station_data['FH'] / (130 * 0.8360)) ** (2 / 3), 0)
        ws['Extreme'] = station_data[ex_var].sum(axis=1) >= 1
        ws['Overall'] = round((5 * ws['Sun Score'] + 5 * ws['Rain Score'] + 10 * ws['Wind Score']) / 20, 1)
        return ws

    @staticmethod
    def get_entries_score_type(dataframe, score_type, lower_bound, upper_bound):  # possible score_types: 'Sun Score', 'Rain
        # Score' 'Wind Score', 'Extreme', 'Overall'
        return dataframe[(dataframe[score_type] >= lower_bound) & (dataframe[score_type] <= upper_bound)]

    @staticmethod
    def get_df_with_preset(preset, dataframe):
        df = dataframe
        parameters = preset.keys()
        for param in parameters:
            low, up = preset[param]
            df = WeatherModule.get_entries_score_type(df, param, low, up)
        return df


if __name__ == "__main__":
    print(WeatherModule.scrape_KNMI(215, 2019, 1, 1, 2019, 12, 31))