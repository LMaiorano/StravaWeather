# Imports
import os
import sys
import art
import pandas as pd
import datetime as dt
import Project.visualization as visuals
import Project.strava as strava
import Project.analysis as analysis
from Project.data_load import LoadData
import Project.weather as weather
import webbrowser
from Project.exceptions import *

from Project.definitions import UI_GEN_DATA_DIR, VISUAL_RESULTS_DIR



def print_id(*args, id=0, **kwargs):
    print(id*'\t', *args, **kwargs, sep='')


class Controller:
    def __init__(self):
        pass


    @staticmethod
    def select_option(options, prompt='Please select an option:', indent=0, allow_default=False):
        print_id(prompt, id=indent)
        for key, value in options.items():
            print_id(f'{key}: {value}', id=indent)

        while True:
            try:
                txt = indent*'\t'+'> '
                sel = input(txt)
                if sel.lower() == 'q':
                    raise QuitUI
                elif sel.lower() == 'm':
                    raise MainMenUI
                if allow_default:
                    if sel == '':
                        option = 1
                        break
                option = int(sel)

                if option in options.keys():
                    break
                else:
                    raise KeyError

            except (QuitUI, MainMenUI):
                print()
                raise
            except:
                print_id('not a valid option', id=indent+1)

        return option

    @staticmethod
    def select_yn(prompt='Do ...? (y/n):', indent=0):
        while True:
            try:
                txt = indent*'\t'+prompt+' '
                sel = input(txt)
                if sel.lower() == 'q':
                    raise QuitUI
                elif sel.lower() == 'm':
                    raise MainMenUI
                elif sel.lower() == 'y' :
                    return True
                elif sel.lower() == 'n' or sel == '':
                    return False
                else:
                    raise Exception

            except (QuitUI, MainMenUI):
                print()
                raise
            except:
                print_id('not a valid option', id=indent+1)

    # -------------- UI ACTIONS ------------------------
    def ui_select_mode(self, lvl):
        modes = {1:'Weather Comparison', 2:'Data Gen Pipeline'}
        mode = self.select_option(modes, prompt='Please select a mode:', indent=lvl)
        return mode

    def ui_select_weather_score(self, lvl):
        presets = list(weather.WEATHER_PRESET_DICT.keys())
        prompt_options = {}
        for i, option in enumerate(presets):
            option = option.replace('_', ' ')
            prompt_options[i+1] = option.capitalize()
        prompt_options[0] = "Custom Score"

        selection = self.select_option(prompt_options, prompt='Please select a weather type:', indent=lvl)
        if selection == 0:
            score = self.ui_input_cust_score(indent=lvl)
        else:
            score = weather.WEATHER_PRESET_DICT[presets[selection - 1]]
        return score, prompt_options[selection]

    def ui_select_strava_scope(self, lvl):
        options = {1: 'Today (Runtime: ~45min)', 2: 'This Week', 3:'This Month', 4:'This Year', 5:'All Time (Runtime: ~35hrs)', 0:'SKIP (Recommended)'}
        selection = self.select_option(options, prompt='Define date range to scrape activity data:', indent=lvl)
        scopes = {1:'today', 2:'this_week', 3:'this_month', 4:'this_year', 5:'overall', 0:None}
        return scopes[selection]

    def ui_input_cust_score(self, indent=0):
        score_params = ['Sun Score', 'Rain Score', 'Wind Score']
        score = {}

        try:
            txt = (indent + 1) * '\t' + 'Title of custom score: '
            title = input(txt)
            if title.lower() == 'q':
                raise QuitUI
            elif title.lower() == 'm':
                raise MainMenUI
            score['Title'] = title

        except (QuitUI, MainMenUI):
            print()
            raise

        print_id('Enter score (0 - 10) for each parameter bound, or <Enter> to skip', id=indent)
        for param in score_params:
            print_id(f'Parameter "{param}":', id=indent+1)
            bounds = []
            skip = False
            for bound in ['Low:  ', 'High: ']:
                while True:
                    try:
                        txt = (indent+2) * '\t'+ bound
                        sel = input(txt)
                        if sel.lower() == 'q':
                            raise QuitUI
                        elif sel.lower() == 'm':
                            raise MainMenUI
                        elif sel == '': # Enter is pressed
                            raise SkipParamException
                        elif float(sel) >= 0. and float(sel) <= 10.:
                            if bound == 'High: ' and float(sel) < bounds[0]:
                                raise ValueError
                            bounds.append(round(float(sel), 1))
                            break # Goto Next bound
                        else:
                            raise Exception

                    except (QuitUI, MainMenUI):
                        print()
                        raise
                    except SkipParamException:
                        skip = True
                        break
                    except ValueError:
                        print_id('Must be >= "Low" score', id=indent+3)
                    except:
                        print_id('Enter a value between 0 and 10', id=indent+3)

                if skip:
                    break # Skip this parameter

            if len(bounds) == 2:
                score[param] = tuple(bounds)

        return score


    # ---------------- PROGRAM FUNCTIONS ----------------------
    def load_full_data(self):
        raw_data_alltime = LoadData.get_raw_data_alltime()
        return analysis.CleanRawData.clean(raw_data_alltime)


    def scrape_strava(self, scope='today'):
        s = strava.StravaModule(coordinates_csv='ZH_5km.csv', disable_pbars=True)
        s.load_existing_segment_df(segments_csv='segments_ZH_5km.csv')
        s.multi_user_build_all_leaderboards(date_range=scope, save_dir=UI_GEN_DATA_DIR)
        raw_data_file = s.combine_user_leaderboards(date_range=scope, leaderboard_dir=UI_GEN_DATA_DIR)

        crd = analysis.CleanRawData()
        t = dt.date.today()
        date_range = [dt.datetime(2009, 1, 1), dt.datetime(t.year, t.month, t.day)]
        crd.filter_data_parquet_file(raw_data_file, raw_data_file, range=date_range, ui_run=True)


    def calculate_baseline(self):
        # Uses previously scraped activity data, no time to refactor for parameters
        b = analysis.BaselineGen()
        b.generate_baseline(ui_run=True)
        print(f'Baseline generated, results saved to: {UI_GEN_DATA_DIR}')


    def scrape_weather(self):
        return weather.WeatherModule.scrape_KNMI(215, 2019, 1, 1, 2019, 12, 31)


    def assign_weather_score(self):
        # Only runs on pre-generated full year 2019 data
        data = LoadData.get_filter_data_this_year()
        out = analysis.AssignWeatherScore.assign_scores(data)
        return out


    # ------------ Plotting -------------
    def validate_plot(self, df, html_filename='plot_validation'):
        gv = visuals.GoogleHeatmap(results_dir=VISUAL_RESULTS_DIR, weatherType=html_filename)
        return gv.gen_googlemap(dataframe=df) # Returns filepath to html heatmap

    def plot_results(self, df, weather_type='SunnyDays', save_fig=False, cbar_zero=True):
        hm = visuals.ComparisonHeatmap()
        hm.gen_map(df, weatherType=weather_type, savefig=save_fig, results_dir=VISUAL_RESULTS_DIR, cbarZeroed=cbar_zero)

    def open_heatmap(self, file_path):
        '''Open html in browser'''
        heatmap_url = 'file://'+file_path
        os.system(f"start {heatmap_url}")

