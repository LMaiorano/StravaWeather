import argparse
import datetime as dt
import logging
import ntpath
import os
import sys
import time


import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))  # This must come before the next two imports
from Project.strava.strava_api import Api
from Project.exceptions import RequestLimitException, StravaOtherError

from Project.definitions import CREDENTIALS_PATH

# noinspection PyUnresolvedReferences,PyPep8
class StravaModule:

    def __init__(self, coordinates_csv='ZH_5km.csv',
                 re_generate_segments=False,
                 log_file='./logs/strava_module.log',
                 print_log_statements=False,
                 verbose=False, disable_pbars=False):

        self.__disable_pbars = disable_pbars # Print Progress bars

        self.__leaderboard_df_columns = ["segment_id", "date", "start_latlng", "end_latlng", "moving_time"]
        self.__region = ntpath.basename(coordinates_csv)[:-4]
        coordinates_csv_path = os.path.join(os.path.dirname(__file__), 'reference_data', 'csv_grids', coordinates_csv)
        self.__coordinates = pd.read_csv(coordinates_csv_path)
        self.__leaderboards = pd.DataFrame(columns=self.__leaderboard_df_columns)
        if re_generate_segments:
            self.__segments = pd.DataFrame()
        else:
            self.load_existing_segment_df()

        # Initialize api's
        self.__api_objs = {}
        self.__api_segments = {}
        self.__api_leaderboard_complete = {}
        self.__api_leaderboard_df = {}
        self.__api_completed_segments = {}
        self.__api_skipped_segments = {}
        self.__api_leftoff_pg = {}
        self.__api_segment_leaderboard_df = {}


        if re_generate_segments:
            self.__api = self.setup_api_instance(user='api_1')[0]
        else:
            self.setup_api_accounts()
            self.__api = self.__api_objs['api_1']  # Default api used to scrape segments

        # Setup Logging:
        self.setup_logging(log_file, print_log_statements, verbose)

    @staticmethod
    def setup_logging(log_file, print_log_statements, verbose):
        def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
            """Handler for unhandled exceptions that will write to the logs"""
            if issubclass(exc_type, KeyboardInterrupt):
                # call the default excepthook saved at __excepthook__
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            logging.getLogger().critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

        if not os.path.exists('./logs'):
            os.makedirs('./logs')
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_file,
                            filemode='w')

        sys.excepthook = handle_unhandled_exception

        parser = argparse.ArgumentParser(description='StravaModule using APIs to collect data segment leaderboard data')
        parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        args = parser.parse_args()
        if print_log_statements:  # Print log messages to console as well
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        if args.verbose or verbose:
            logging.getLogger().setLevel(logging.DEBUG)

            # Disable annoying logs of each 'GET' or 'POST'
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)

    @staticmethod
    def setup_api_instance(user='api_1'):
        with open(CREDENTIALS_PATH, 'r') as cred:
            creds = yaml.load(cred, Loader=yaml.FullLoader)['Strava']
        accounts = [*creds]  # Unpack to a list of users (strings)
        api = Api(creds[user], user=user)
        return api, accounts

    def setup_api_accounts(self):
        """
        Use number of accounts in credentials_path file to determine how to split the segments.
        Allows more users to be created and simply be added to credentials_path file
        :return:
        """
        _, accounts = self.setup_api_instance(user='api_1')  # List of available api user accounts
        # print(f'Using {len(accounts)} Strava api accounts')

        # Create api instances based on number of accounts in credentials_path file
        for i, user in enumerate(accounts):
            self.__api_objs[user] = self.setup_api_instance(user=user)[0]

            # List of segment IDs to be handled by each user
            self.__api_segments[user] = np.array_split(self.__segments, len(accounts))[i]
            self.__api_segments[user] = self.__api_segments[user]['id'].to_list()

            self.__api_leaderboard_complete[user] = False
            self.__api_leaderboard_df[user] = pd.DataFrame(columns=self.__leaderboard_df_columns)

            self.__api_completed_segments[user] = set()
            self.__api_skipped_segments[user] = set()

            # Used to keep track of last page visited before request limited
            self.__api_leftoff_pg[user] = 1
            self.__api_segment_leaderboard_df[user] = pd.DataFrame(columns=self.__leaderboard_df_columns)

    def load_existing_segment_df(self, segments_csv='segments_ZH_5km.csv'):
        fpath = os.path.join(os.path.dirname(__file__), 'reference_data', segments_csv)
        self.__segments = pd.read_csv(fpath)
        self.__segments = self.__segments.astype({'id': 'int64'})

    # ******************* SIMPLE CLASS GET METHODS ****************************
    def get_sample_data(self, num=10):
        return self.generate_sample_data(num)

    def get_leaderboard(self):
        return self.__leaderboards

    def get_segments(self):
        return self.__segments

    # ********************* SEGMENT DATAFRAME *********************************
    def build_segment_df(self):
        """
        :rtype: df
        :return: df with segment data
        """
        num_squares = len(self.__coordinates.index)
        scraped_squares = []
        for i in tqdm(range(num_squares), disable=self.__disable_pbars):
            try:
                coordinates = self.df_idx_get_coordinates(i)
                square_df = self.scrape_segments(coordinates[0], coordinates[1])
                scraped_squares.append(self.__coordinates.id[i])
                self.__segments = self.__segments.append(square_df, ignore_index=True)

            except RequestLimitException:
                logging.info(f'API limit reached, completed {len(scraped_squares)} grid squares so far')
                i -= 1
                self.api_sleep()

        # skipped_segs_set type of segment_id to int64, needed for build_leaderboard method
        self.__segments = self.__segments.astype({'id': 'int64'})

    def scrape_segments(self, latlong_bot_left, latlong_up_right):
        segments = self.__api.explore_segments(latlong_bot_left, latlong_up_right)
        return self.segments_to_df(segments)

    @staticmethod
    def segments_to_df(segments):
        """
            :type segments: json
            :return: segment ID's and segment coordinates, segment length
            :rtype df
            """
        # setup
        data = {'id': [], 'distance': [], 'start_latlng': [], 'end_latlng': []}

        for segment in segments['segments']:
            for item in ['id', 'distance', 'start_latlng', 'end_latlng']:
                data[item].append(segment[item])

        return pd.DataFrame(data)

    def df_idx_get_coordinates(self, coord_idx):
        SW_lat = round(self.__coordinates.SW_lat[coord_idx], 4)
        SW_lon = round(self.__coordinates.SW_lon[coord_idx], 4)
        NE_lat = round(self.__coordinates.NE_lat[coord_idx], 4)
        NE_lon = round(self.__coordinates.NE_lon[coord_idx], 4)
        SW = (SW_lat, SW_lon)
        NE = (NE_lat, NE_lon)
        return SW, NE

    # ******************* LEADERBOARD DATAFRAME *******************************
    @staticmethod
    def leaderboard_to_df(leaderboard):
        """
        *********** CONVERTS JSON TO PANDAS DF ******************
        :type leaderboard: strava json
        :param leaderboard:
        :return: leaderboard df with date and moving time, unfiltered!
        :rtype df
        """

        data = {'date': [], 'moving_time': []}
        for entry in leaderboard['entries']:
            new_date = dt.datetime.strptime(entry['start_date'], '%Y-%m-%dT%H:%M:%SZ')
            data['date'].append(new_date)
            data['moving_time'].append(entry['moving_time'])
        return pd.DataFrame(data)

    @staticmethod
    def api_sleep():
        time_max_req = (dt.datetime.now().minute, dt.datetime.now().second)
        min_to_reset = 15 - (time_max_req[0] % 15)
        logging.info(f'Sleeping for {min_to_reset} minutes until API reset')
        time.sleep(min_to_reset * 60)

    def scrape_leaderboard(self, segment_id, page, date_range='this_year', api_obj=None):
        if api_obj is None:
            api_obj = self.__api
        leaderboard = api_obj.request_leaderboard(segment_id, page, date_range)

        return self.leaderboard_to_df(leaderboard)

    # ---------------------MULTI-USER APPROACH ------------------------------
    @staticmethod
    def append_page(existing_df, segment_id, leaderboard_df, start_coordinates, end_coordinates):
        # add columns with segment ID and coordinates to df
        leaderboard_df = leaderboard_df.assign(segment_id=segment_id,
                                               start_latlng=[start_coordinates for i in leaderboard_df.index],
                                               end_latlng=[end_coordinates for i in leaderboard_df.index])
        new_df = existing_df.append(leaderboard_df, ignore_index=True, sort=True)
        return new_df

    def export_leaderboard_df(self, dataframe, save_directory, date_range):
        """
        :param dataframe: Leaderboard dataframe
        :type dataframe: Pandas df
        :param save_directory: Relative path to directory where to save csv file
        :param date_range: Range of dates
        :return:
        """
        if len(dataframe.index) >= 1:
            segment_id_range = f'{int(dataframe.segment_id[0])}_{int(dataframe.segment_id[dataframe.index[-1]])}'
            fname = f'{self.__region}_leaderboard_{segment_id_range}_{date_range}.csv'
            save_location = os.path.join(os.path.dirname(__name__), save_directory, fname)
            dataframe.to_csv(save_location, index=False)

    def write_skipped_segments_to_file(self, user, skipped_segs_set, save_directory, date_range):
        """Write the list to csv file."""
        if len(skipped_segs_set) > 0:
            fname = f'{self.__region}_{user}_segments_skipped_{date_range}.csv'
            filename = os.path.join(os.path.dirname(__name__), save_directory, fname) #Use __name__ so main.py can acces local files
            with open(filename, "w") as outfile:
                for entry in list(skipped_segs_set):
                    outfile.write(str(entry))
                    outfile.write("\n")

    def single_segment_leaderboard(self, segment_id, user, date_range='this_year'):
        """
        For a given segment, build the leaderboard df
        :return: segment leaderboard df
        """
        # Retrieve segment coordinates from segment_df
        start_coordinates = self.__segments.set_index('id').loc[segment_id, 'Start_coordinates']
        end_coordinates = self.__segments.set_index('id').loc[segment_id, 'End_coordinates']

        # Get next page to scrape (1 if new segment)
        pg_start = self.__api_leftoff_pg[user]

        # Get number of pages ********************
        try:
            leaderboard_json = self.__api_objs[user].request_leaderboard(segment_id, page=1, date_range=date_range)
            page_count = int(np.ceil(leaderboard_json['entry_count'] / 200))

        except RequestLimitException:
            logging.info(f'Request limit reached when determining num pgs of segment '
                         f'(User {user}, segment {segment_id})')
            raise  # Re-raises exception for calling function to switch to next user

        logging.debug(f'Resuming segment {segment_id} on page {pg_start}')
        try:
            for i in range(pg_start, page_count + 1):
                page_leaderboard_df = self.scrape_leaderboard(segment_id, page=i, api_obj=self.__api_objs[user],
                                                              date_range=date_range)
                self.__api_segment_leaderboard_df[user] = self.append_page(self.__api_segment_leaderboard_df[user],
                                                                           segment_id,
                                                                           page_leaderboard_df,
                                                                           start_coordinates,
                                                                           end_coordinates)
                self.__api_leftoff_pg[user] = i + 1

            # Cleanup after all pages complete
            self.__api_leftoff_pg[user] = 1
            result = self.__api_segment_leaderboard_df[user].copy()
            self.__api_segment_leaderboard_df[user] = pd.DataFrame(columns=self.__leaderboard_df_columns)

        except RequestLimitException:
            logging.info(f'Request limit reached on page {self.__api_leftoff_pg[user]} of {page_count}. '
                         f'(User {user}, segment {segment_id})')
            raise  # Re-raises exception for calling function to switch to next user

        else:
            return result

    def multi_user_build_all_leaderboards(self, date_range='this_year', save_dir='working_data'):
        """
        Multi-user method to get all leaderboard data, based on build_leaderboard_df
        """
        # Re-initialize to ensure using correct segments and attributes
        self.setup_api_accounts()

        api_users = [*self.__api_objs]

        logging.info(f'Starting multi-user building of leaderboards, using {len(api_users)} API accounts')
        while True:
            quarter_start = dt.datetime.now().minute // 15  # mark which 15min period

            # Iterate through available api users
            for user in api_users:

                # User finished, all leaderboards complete
                if self.__api_leaderboard_complete[user]:
                    logging.debug(f'User: {user} already complete, skipping to next')
                    continue

                # User not yet finished
                else:
                    logging.info(f'---- Switch to API User {user}. '
                                 f'Resuming from page {self.__api_leftoff_pg[user]} ---')

                    for segment in tqdm(self.__api_segments[user], disable=self.__disable_pbars):

                        if segment not in self.__api_completed_segments[user]:
                            logging.debug(f'Retrieving segment {segment}')

                            try:
                                seg_leaderboard = self.single_segment_leaderboard(segment, user, date_range=date_range)

                                # Add segment leaderboard to user leaderboard
                                self.__api_leaderboard_df[user] = pd.concat(
                                    [self.__api_leaderboard_df[user], seg_leaderboard], axis=0, ignore_index=True,
                                    sort=True)

                                # Save segment as completed
                                self.__api_completed_segments[user].add(segment)



                            except RequestLimitException:
                                percent = len(self.__api_completed_segments[user]) / \
                                          len(self.__api_segments[user]) * 100
                                logging.info(f'{round(percent, 1)}% complete, '
                                             f'{len(self.__api_completed_segments[user])} of '
                                             f'{len(self.__api_segments[user])} segments. '
                                             f'(User {user}, segment {segment})')
                                break  # Move on to next user

                            except StravaOtherError:
                                logging.info(f'Strava response not 200. Skipping segment. '
                                             f'(User {user}, segment {segment})')
                                self.__api_completed_segments[user].add(segment)
                                self.__api_skipped_segments[user].add(segment)

                            except: # ANY OTHER ERROR
                                logging.exception(f'Unexpected exception occurred. Skipping segment. '
                                                  f'(User {user}, segment {segment})')
                                self.__api_completed_segments[user].add(segment)
                                self.__api_skipped_segments[user].add(segment)

                    if len(self.__api_segments[user]) == len(self.__api_completed_segments[user]):
                        logging.info(f'******************{user} completed all segments ************************')

                        # Mark user as complete
                        self.__api_leaderboard_complete[user] = True

                        # Export data to files
                        self.export_leaderboard_df(self.__api_leaderboard_df[user], save_dir, date_range)
                        self.write_skipped_segments_to_file(user, self.__api_skipped_segments[user],
                                                            save_dir, date_range)

                        # Overwrite dataframe to clear memory
                        self.__api_leaderboard_df[user] = None

            # Determine if all leaderboards are collected
            if all(self.__api_leaderboard_complete.values()):
                break

            # Determine if the 15min mark has been passed
            quarter_end = dt.datetime.now().minute // 15
            if quarter_start == quarter_end:
                self.api_sleep()

        logging.info("All users' leaderboards complete.")

    def combine_user_leaderboards(self, leaderboard_dir='working_data', date_range='this_year'):
        # find data files
        data_files = []
        leaderboard_path = os.path.join(os.path.dirname(__name__), leaderboard_dir)
        for file in os.listdir(leaderboard_path):
            if file.startswith(self.__region+'_leaderboard') and file.endswith(date_range+'.csv'):
                file_path = os.path.join(os.path.dirname(__name__), leaderboard_dir, file)
                data_files.append(file_path)

        if len(data_files) == 0:
            return

        full_leaderboard = pd.DataFrame(columns=self.__leaderboard_df_columns)

        # Combine into df
        for file in tqdm(data_files, disable=self.__disable_pbars):
            file_df = pd.read_csv(file)
            # DO NOT DROP DUPLICATES, different users may have the same results
            full_leaderboard = pd.concat([full_leaderboard, file_df], sort=True).reset_index(drop=True)


        filename = self.__region + '_full_leaderboard_' + date_range + '.parquet'
        outfile = os.path.join(leaderboard_path, filename)
        for file in data_files:
            os.remove(file)

        self.save_to_parquet(full_leaderboard, outfile)
        return filename

    # ***************************** GENERATE SAMPLE DATA *******************************
    def generate_sample_data(self, n):
        data = {"segment_ID": [i for i in range(n)],
                "date": [dt.datetime(2019, np.random.randint(1, 12), np.random.randint(1, 28)) for i in range(1, n+1)],
                "start_coordinates": [[52.01 - i / 100, 4.32 + i / 100] for i in range(n)],
                "end_coordinates": [[52.1 - i / 100, 4.35 + i / 100] for i in range(n)],
                "entries": [np.random.randint(50, 500) for i in range(n)]}
        df = pd.DataFrame(data, columns=self.__leaderboard_df_columns)
        return df

    def dev_example_dataset(self, n=10, filename='dev_example_data'):
        ex_data = self.generate_sample_data(n)
        ex_data.to_csv(filename + '_n=' + str(n) + '.csv')

    @staticmethod
    def save_to_parquet(dataframe, filename):
        dataframe.to_parquet(filename)

    def select_skipped_segments(self, skipped_seg_csv):
        skipped_segs = []
        with open(skipped_seg_csv, 'r') as f:
            lines = f.readlines()
            for seg in lines:
                skipped_segs.append(seg)
        self.__segments = self.__segments.loc[self.__segments['id'].isin(skipped_segs)]


def main():
    s = StravaModule(coordinates_csv='ZH_5km.csv')
    s.load_existing_segment_df(segments_csv='segments_ZH_5km.csv')

    s.multi_user_build_all_leaderboards(date_range='overall')
    s.combine_user_leaderboards(date_range='overall')

if __name__ == '__main__':
    main()

