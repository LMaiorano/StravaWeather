import pandas as pd
from Project.weather import WeatherModule

file = 'test_documents/KNMI_scraper_testdocument.txt'
df = WeatherModule.txt_to_pandas(file)

assert type(df) == pd.DataFrame
assert not df.empty

print('Visual Testing:')
print(df)
