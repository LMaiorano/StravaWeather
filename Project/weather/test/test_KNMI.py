from Project.weather import WeatherModule

testdoc = WeatherModule.txt_to_pandas('test_documents/KNMI_scraper_testdocument.txt')
testresult = WeatherModule.scrape_KNMI(344, 2019, 12, 1, 2019, 12, 8)
assert testdoc.equals(testresult)
