import pytest
import os
from Project.weather import WeatherModule
import pandas as pd

def ref_files(f_name):
    path = os.path.join(os.path.dirname(__file__), 'test_documents', f_name)
    return path


def test_knmi():

    f_path = ref_files('KNMI_scraper_testdocument.txt')
    testdoc = WeatherModule.txt_to_pandas(f_path)
    testresult = WeatherModule.scrape_KNMI(344, 2019, 12, 1, 2019, 12, 8)
    assert testdoc.equals(testresult)


def test_txt_to_pandas():

    file = ref_files('KNMI_scraper_testdocument.txt')
    df = WeatherModule.txt_to_pandas(file)

    assert type(df) == pd.DataFrame
    assert not df.empty
