from Project.weather import WeatherModule

station_id = 344 # Voorschoten_dist = 215, Hoek_v_Holland_dist = 330,  Rotterdam_dist= 344
start_year = 2019
start_month = 1
start_day = 1
end_year = 2019
end_month = 1
end_day = 5

print(WeatherModule.build_weather_score_df(WeatherModule.scrape_KNMI(station_id, start_year, start_month, start_day, end_year, end_month, end_day)))
