import os

import numpy as np
import pandas as pd

from Project.analysis import clean_raw_data as clean
from Project.analysis.clean_raw_data import CleanRawData as CRD
from Project.data_load import LoadData
from Project.definitions import BASELINE_DATA_DIR, UI_GEN_DATA_DIR


class BaselineGen():
    def __init__(self, full=True):
        if full:
            self.all_data = LoadData.get_filter_data_alltime()
        else:
            self.all_data = LoadData.get_filter_data_this_year()


    def sort_dataframe(self):

        crd = clean.CleanRawData()
        self.data_clean = crd.clean(self.all_data)
        data_filtered = self.data_clean[['date', 'segment_id', 'entries']]

        self.data_filtered  = data_filtered

    def debug_analy(self):
        file_path = os.path.dirname(__file__)
        final_path = file_path + '/data/data_filtered.parquet'
        data_filtered = pd.read_parquet(final_path)
        try:
            self.data_filtered = data_filtered
        except:
            # print(sys.traceback)
            print('failed')


    def count_number_of_entries_per_segment(self):
        # find all unique segments

        self.total_entries = self.data_filtered[['entries', 'segment_id']].groupby(['segment_id']).sum()['entries']

        # occur_seg = self.data_filtered['segment_id'].value_counts()
        # data_count = pd.DataFrame({'segment_id': occur_seg.index, 'entries': occur_seg.values})
        # data_count = data_count.sort_values('segment_id')
        # # set index to segment_id so the dataframes can be easier joined
        # self.count = data_count.set_index('segment_id')


    def time_segment_exists(self):
        # get max and min date per segment
        # most_recent_entry = self.data_filtered['date'].max()

        number_of_days = self.data_filtered[['date', 'segment_id']].groupby(['segment_id']).nunique()['date']
        self.days = number_of_days

    def final_data(self):
        # sort dataframe
        BaselineGen.sort_dataframe(self)

        # get both dataframes
        BaselineGen.count_number_of_entries_per_segment(self)
        BaselineGen.time_segment_exists(self)

        # creating last dataframe and filling it with averages
        data_final = pd.DataFrame()
        self.data_final = data_final.assign(average_entries_per_day=self.total_entries/self.days)


    def generate_baseline(self, alltime=True, ui_run=False): # Luigi
        if not alltime:
            data = LoadData.get_filter_data_this_year(columns=['date', 'segment_id', 'entries'])
        else:
            data = LoadData.get_filter_data_alltime(columns=['date', 'segment_id', 'entries'])

        data_gr = CRD.group_by_date_seg(data)
        baseline = data_gr[['entries', 'segment_id']].groupby(['segment_id']).mean()['entries'].to_frame('baseline').reset_index()

        # baseline['baseline'].describe()
        if ui_run:
            base_dir = UI_GEN_DATA_DIR
        else:
            base_dir = BASELINE_DATA_DIR


        if alltime:
            save_path = os.path.join(base_dir, 'alltime_daily_baseline.parquet')
        else:
            save_path = os.path.join(base_dir, 'this_year_daily_baseline.parquet')
        baseline.to_parquet(save_path)




class BaselineCompare:

    @staticmethod
    def compare(data, alltime_baseline=True):
        if alltime_baseline:
            baseline_df = LoadData.get_baseline_alltime()
        else:
            baseline_df = LoadData.get_baseline_this_year()

        # data = CRD.group_by_date_seg(data) # No longer necessary because already done in weather module

        normalized = baseline_df[['segment_id']].copy()
        ents_p_day_p_seg = data[['entries', 'segment_id']].groupby(['segment_id']).mean()['entries'].to_frame('avg_ent_p_day').reset_index()
        normalized = pd.merge(normalized, ents_p_day_p_seg, on=['segment_id'])
        normalized = pd.merge(normalized, baseline_df, on=['segment_id'])

        normalized['entries'] = ((normalized['avg_ent_p_day'] / normalized['baseline']) - 1 ) * 100
        normalized = normalized.drop(columns=['avg_ent_p_day', 'baseline'])


        return BaselineCompare.remove_outliers(normalized)

    @staticmethod
    def remove_outliers(comp_data, std_threshold=3):
        # keep only the ones that are within +3 to -3 standard deviations in the column 'entries'
        cleaned = comp_data[np.abs(comp_data.entries - comp_data.entries.mean()) <= (std_threshold * comp_data.entries.std())]

        return cleaned

def main():
    year_data = LoadData.get_filter_data_this_year(columns=['date', 'segment_id', 'entries'])
    comp = BaselineCompare.compare(year_data, alltime_baseline=True)

    cleaned = BaselineCompare.remove_outliers(comp)


    print(comp.describe())
    comp.to_parquet(os.path.join(BASELINE_DATA_DIR, 'past_yr_comparison.parquet'))


def gen_baseline():
    b = BaselineGen()
    b.generate_baseline(alltime=True)

def compare_baseline():
    year_data = LoadData.get_filter_data_this_year(columns=['date', 'segment_id', 'entries'])
    comp = BaselineCompare.compare(year_data, alltime_baseline=True)

    cleaned = BaselineCompare.remove_outliers(comp)

    print(comp.describe())
    comp.to_parquet(os.path.join(BASELINE_DATA_DIR, 'past_yr_comparison.parquet'))

if __name__ == '__main__':
    gen_baseline()
    compare_baseline()
