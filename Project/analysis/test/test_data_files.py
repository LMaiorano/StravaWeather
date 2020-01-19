import unittest
from Project.data_load import LoadData


class Datafiltertest(unittest.TestCase):

    def setUp(self):
        self.this_year_data = LoadData.get_filter_data_this_year()
        self.all_time_data = LoadData.get_filter_data_alltime()

    def test_filter_date(self):

        def filter_year(string):
            return string[:4]

        # this year
        dates_this_year = self.this_year_data['date'].map(filter_year)
        contains_years_this_year = dates_this_year.isin(['2019', '2020'])

        # all time
        dates_all_time = self.all_time_data['date'].map(filter_year)
        contains_years_all_time = dates_all_time.isin(['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020'])

        self.assertTrue(contains_years_this_year.all())
        self.assertTrue(contains_years_all_time.all())



