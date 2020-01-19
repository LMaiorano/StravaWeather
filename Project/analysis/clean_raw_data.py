import pandas as pd
import datetime as dt
import os
from Project.data_load import LoadData

from Project.definitions import ACTIVITY_DATA_DIR, UI_GEN_DATA_DIR


class CleanRawData:

    @staticmethod
    def clean(data):
        #all shut down as this already happend for the data for the baseline calc
        # res = CleanRawData.remove_moving_time(data)
        # data.loc[:, 'date'] = data.loc[:, 'date'].map(CleanRawData.convert_to_dt)
        # res = CleanRawData.filter_date(data)
        return CleanRawData.group_by_date_seg(data)

    @staticmethod
    def filter_date(df, date_range=None):
        if date_range is None:
            date_range = [dt.datetime(2009, 1, 1), dt.datetime(2020, 1, 1)]
        return df[(date_range[0] <= df.loc[:, 'date']) & (df.loc[:, 'date'] <= date_range[1])]

    @staticmethod
    def remove_moving_time(df):
        return df.drop('moving_time', axis=1)

    @staticmethod
    def group_by_date_seg(df):
        #https: // datascience.stackexchange.com / questions / 29840 / how - to - count - grouped - occurrences
        ct = df.groupby(['date', 'segment_id']).size().to_frame('entries').reset_index()
        df = pd.merge(df, ct, on=['date', 'segment_id'])

        # Validation
        # valid = df.sort_values(by=['date', 'segment_id'])
        # valid = valid.drop(columns=['start_latlng', 'end_latlng'])

        return df.drop_duplicates().reset_index(drop=True)


    @staticmethod
    def convert_to_dt(string):
        return dt.datetime.strptime(string.split(' ')[0], '%Y-%m-%d')

    @staticmethod
    def date_to_str(datetime_object):
        date_list = str(datetime_object.date()).split('-')
        return date_list[0] + date_list[1] + date_list[2]


    @staticmethod
    def filter_data_parquet_file(file_load, file_save, range=None, ui_run=False):
        if ui_run:
            activity_dir = UI_GEN_DATA_DIR
        else:
            activity_dir = ACTIVITY_DATA_DIR

        # get file path
        tot_path = os.path.join(activity_dir, file_load)
        # print(tot_path)
        if file_load == 'ZH_5km_leaderboard_this_year_top10.csv':
            all_data = pd.read_csv(tot_path)
        else:
            all_data = pd.read_parquet(tot_path, 'auto', columns=['date', 'segment_id', 'end_latlng'])
        # print('laden gelukt')
        all_data.loc[:, 'date'] = all_data.loc[:, 'date'].map(CleanRawData.convert_to_dt)

        # print('data naar datetime')
        filtered_dates = CleanRawData.filter_date(all_data, date_range=range)
        all_data.loc[:, 'date'] = filtered_dates
        # print(all_data.isnull().any())
        # remove rows with NaN or NaT
        data_without_nan = all_data.dropna()
        # print(data_without_nan.isnull().any())

        # date to str
        dates_to_str = data_without_nan.loc[:, 'date'].map(CleanRawData.date_to_str)
        data_without_nan.loc[:, 'date'] = dates_to_str

        data_without_nan = CleanRawData.group_by_date_seg(data_without_nan)

        #set index right
        data_without_nan.reset_index(drop=True, inplace=True)

        # print(data_without_nan.head())

        # save file
        path = os.path.join(activity_dir, file_save)

        if file_load == 'ZH_5km_leaderboard_this_year_top10.csv':
            data_without_nan.to_csv(path)
        else:
            data_without_nan.to_parquet(path)

if __name__ == '__main__':
    crd = CleanRawData()

    load_path = os.path.join(ACTIVITY_DATA_DIR, 'filtered_this_year_data.parquet')
    filtered_data = pd.read_parquet(load_path, 'auto', columns=['date', 'segment_id', 'end_latlng'])
    grouped_data = crd.group_by_date_seg(filtered_data)

    print(grouped_data.head())
    grouped_data.to_parquet(load_path)

