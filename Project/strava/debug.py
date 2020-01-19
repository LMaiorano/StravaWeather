
import json
import os

from tqdm import tqdm


class DebugStrava():
    def __init__(self, api_obj):
        self.__api = api_obj


    def generate_requests(self, num_requests=600):
        for i in tqdm(range(num_requests)):
            response = self.__api.request_leaderboard(7932761)

    @staticmethod
    def save_response_to_file(response, directory):
        fname = f'401_unauthorized_response.json'
        filename = os.path.join(os.path.dirname(__name__), directory, fname)

        save_data = {}
        save_data['request'] = dict(response.request.headers)
        save_data['status_code'] = response.status_code
        save_data['reason'] = response.reason
        save_data['headers'] = dict(response.headers)
        save_data['text'] = response.text
        save_data['url'] = response.url

        with open(filename, 'w') as outfile:
            json.dump(save_data, outfile)


# Testbed for new exceptions
if __name__ == '__main__':
    file = './working_data/401_unauthorized_response.json'
    with open(file) as infile:
        unauth_resp = json.load(infile)
    print(unauth_resp)


