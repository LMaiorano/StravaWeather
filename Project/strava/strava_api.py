# file to handle Strava api scraping

# https://github.com/marquies/strava-viz/blob/master/stravahr.py
# http://www.hainke.ca/index.php/s2018/08/23/using-the-strava-api-to-retrieve-activity-data/

# docs about authentication
# https://developers.strava.com/docs/authentication/

from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from Project.exceptions import RequestLimitException, StravaOtherError

from Project.definitions import CREDENTIALS_PATH
import yaml


class Api:

    def __init__(self, creds, user='api1'):
        """
        :param creds: dictionary of client_ID, client_secret, auth_token
        :type creds: dict
        """
        # some parameters are not hidden for test purposes
        self.__client_id = creds['client_ID']
        self.__client_secret = creds['client_secret']

        self.__activity_type = "riding"
        self.authorization_code = creds['auth_token']

        self.__user = user # Used only for writing new access/refresh tokens to file

        if creds['access_token'] is None: # First run with new auth_token
            self.__access_token = ""
            self.expires_at = datetime(2018, 12, 12)
            self.expires_in = ""
            self.__refresh_token = ""
            self.check_access_token_valid()

        else: # Load previous tokens
            self.__access_token = creds['access_token']
            self.expires_at = creds['expires_at']
            self.__refresh_token = creds['refresh_token']

    @staticmethod
    def init_request_session():
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.expires_at

    def get_access_token(self):
        return self.__access_token

    def get_refresh_token(self):
        return self.__refresh_token

    def check_access_token_valid(self):
        if self.authorization_code == "":  # never entered this loop, authorization was obtained manually
            print("Need authorization code first!")
        elif self.__access_token == "":
            self.request_access_token()
        else:
            if datetime.now() > self.expires_at:
                self.refresh_tokens()

    def refresh_tokens(self):
        # get new access tokens
        self.exchange_tokens("refresh_token")

    def request_access_token(self):
        # get first access token
        self.exchange_tokens("authorization_code")

    def exchange_tokens(self, grant_type):
        """
        :param grant_type: str that defines what type of request to do
        :return: access_token, refresh token, expiration time
        :rtype: str
        """

        # check grant type to decide what post request to do
        if grant_type == "refresh_token":
            code = "&refresh_token=" + self.__refresh_token
        elif grant_type == "authorization_code":
            code = "&code=" + self.authorization_code
        else:
            raise TypeError("invalid grant_type")

        # build url and post request
        base_url = "https://www.strava.com/api/v3/oauth/token?"
        url = base_url + "client_id=" + self.__client_id \
              + "&client_secret=" + self.__client_secret \
              + code + "&grant_type=" + grant_type
        session = self.init_request_session()
        result = session.post(url).json()

        # try to extract tokens, else raise keyError
        try:
            self.__access_token = result["access_token"]
            self.expires_in = result["expires_in"]
            self.__refresh_token = result["refresh_token"] ### This line was missing

        except KeyError as ke:
            print('Check authorization code and url', ke)

        # compute expiration time, include 30 second buffer
        self.expires_at = datetime.now() + timedelta(seconds=(int(self.expires_in) - 30))

        # Save Updated Credentials
        with open(CREDENTIALS_PATH, 'r') as f:
            creds = yaml.load(f, Loader=yaml.FullLoader)

        creds['Strava'][self.__user]['access_token'] = self.__access_token
        creds['Strava'][self.__user]['expires_at'] = self.expires_at
        creds['Strava'][self.__user]['refresh_token'] = self.__refresh_token
        creds['Strava'][self.__user]['auth_token'] = None # Delete token since can't be used anymore

        with open(CREDENTIALS_PATH, 'w') as f:
            new_creds = yaml.dump(creds, f)



    def explore_segments(self, latlong_bot_left, latlong_up_right):
        """
            :param latlong_bot_left: latitude and longitude of bottom left corner
            :type latlong_bot_left: tuple
            :param latlong_up_right: latitude and longitude of bottom right corner
            :type latlong_up_right: tuple
            :returns top 10 segments in rectangle between provided coordinates
            :rtype json
        """

        # check access_tokens
        self.check_access_token_valid()

        # construct url and header
        base_url = "https://www.strava.com/api/v3/segments/explore?"
        coordinates = "bounds=" + str(latlong_bot_left[0]) + "%2C%20" + str(latlong_bot_left[1]) + "%2C%20" \
                      + str(latlong_up_right[0]) + "%2C%20" + str(latlong_up_right[1])
        url = base_url + coordinates + "activity_type=" + self.__activity_type
        header = {"Authorization": "Bearer " + self.__access_token}

        # get response and check if limited
        session = self.init_request_session()
        response = session.get(url, headers=header)
        self.check_response(response)
        return response.json()

    def request_leaderboard(self, segment_id, page=1, date_range="this_year"):
        """
        :param segment_id: id number of segment
        :type segment_id: str
        :param page: page number of leaderboard
        :type page: int
        :param date_range:
        :type date_range: str
        :return: response of leaderboard request and T|F request limit exceeded
        :rtype: json, boolean
        """

        # check access_tokens
        self.check_access_token_valid()

        # create url and header
        base_url = "https://www.strava.com/api/v3/segments/" + str(segment_id) + "/leaderboard?date_range=" \
                   + date_range + "&page=" + str(page) + "&per_page=200"
        header = {"Authorization": "Bearer " + self.__access_token}

        if date_range == 'overall':
            base_url = "https://www.strava.com/api/v3/segments/" + str(segment_id) + "/leaderboard?" \
                   +  "page=" + str(page) + "&per_page=200"

        # get response and check if limited
        session = self.init_request_session()
        response = session.get(base_url, headers=header)
        self.check_response(response)
        return response.json()

    @staticmethod
    def check_response(response):
        header = response.headers
        if header["Status"][:3] == '429':
            raise RequestLimitException()
        elif header["Status"][:3] != '200':
            raise StravaOtherError()


