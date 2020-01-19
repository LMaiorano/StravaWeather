# Imports

import sys
import webbrowser

import art
import pandas as pd

from Project.analysis import BaselineCompare
from Project.weather import WeatherModule
from Project.control import Controller, print_id
from Project.data_load import LoadData
from Project.definitions import UI_GEN_DATA_DIR
from Project.exceptions import MainMenUI, QuitUI


def main():
    ctrl = Controller()

    print( art.text2art('StravaWeather') )


    # Execution of terminal UI
    while True:
        lvl = 0
        print('-----------------------------------------------------')
        print('At any menu:')
        print('\t"m" => Return to Main Menu')
        print('\t"q" => Quit program')
        print()

        try:
            mode = ctrl.ui_select_mode(lvl)
            if mode == 1:
                print()
                print('------ Mode: Weather Comparison ------')
                while True:
                    lvl = 1
                    print()

                    # Get weather score
                    preset_params, preset_name = ctrl.ui_select_weather_score(lvl)
                    if preset_name == 'Custom Score':
                        preset_name = preset_params.pop('Title')

                    print_id(f'-- Using "{preset_name}" to select activity data --', id=lvl+1)
                    print_id(f'WeatherScore(s) = {preset_params}', id=lvl+1)
                    print()

                    # Load activities of the weather score
                    df = LoadData.get_combined_data_this_year()
                    data_selection = WeatherModule.get_df_with_preset(preset_params, df)

                    if data_selection.empty:
                        print_id('Unfortunately, no activities match this weather score.', id=lvl+1)
                        continue

                    # Compare data to baseline
                    data_selection = BaselineCompare.compare(data_selection, alltime_baseline=True)

                    # Select plot type
                    plot_type = ctrl.select_option({1:'Default', 2:'Verification'}, prompt='Select a plot type:',
                                                   indent=lvl+1, allow_default=True)
                    # Default Matplotlib
                    if plot_type == 1:
                        save = ctrl.select_yn("Save Plot to .png (long runtime)? (y/n): ", indent=lvl+1)

                        # Create Title for Plot
                        score_str = ''
                        for param in preset_params:
                            # score_str += f'{param.split()[0]}: {preset_params[param][0]}-{preset_params[param][1]} | '
                            score_str += '%s %g-%g | ' % (param.split()[0], preset_params[param][0], preset_params[param][1])
                        score_str = score_str[:-3]
                        w_type = preset_name.upper() + ': [ ' + score_str +' ]'

                        # Create plot
                        ctrl.plot_results(data_selection, weather_type=w_type, save_fig=save, cbar_zero=True)

                    # Google heatmap for validation
                    else:
                        print_id("Opening Google Heatmap in browser for manual verification of activities' geo-locations", id=lvl+1)
                        heatmap_path = ctrl.validate_plot(data_selection, html_filename=preset_name)
                        webbrowser.open(heatmap_path)




            elif mode == 2:
                lvl = 1
                print()
                print('------ Mode: Data Gen Pipeline ------')
                # Request Strava scrape scope
                if ctrl.select_yn('Scrape Strava data? (y/n):', indent=lvl):
                    scope = ctrl.ui_select_strava_scope(lvl+1)
                    if scope:
                        print_id('Scraping Zuid-Holland activity data from Strava. See logfile for detailed progress', id=lvl+1)
                        print()
                        ctrl.scrape_strava(scope)

                        print_id(f'*Note: manually check <*_segments_skipped_*.csv> for segments that '
                                 f'were unable to be scraped.', id = lvl+1)
                        print_id(f'Results in <{UI_GEN_DATA_DIR}\>', id=lvl + 1)
                        print_id(f'---- Strava Scrape Complete.', id=lvl+1)

                    if scope == 'overall':
                        # Generate Baseline
                        if ctrl.select_yn('Generate baseline? (y/n):', indent=lvl):
                            ctrl.calculate_baseline()

                # Scrape Weather Data
                if ctrl.select_yn('Scrape KNMI weather data? (y/n):', indent=lvl):
                    print_id('This is purely for demonstration. This function is embedded in '
                             '"Combine Strava and Weather data"', id=lvl+1)
                    print(ctrl.scrape_weather().head())
                    print()

                # Combine weather + activities
                if ctrl.select_yn('Combine Strava and Weather data? (y/n):', indent=lvl):
                    pd.set_option('display.max_columns', None)
                    print_id("Scraping data from weather stations and combining with activities", id=lvl+1)
                    print(ctrl.assign_weather_score().sort_values(by=['segment_id']).head())

                print()
                print('------ Data Gen Pipeline complete ------')
                print()
                print()

        except QuitUI:
            print('Quitting StravaWeather...')
            sys.exit()

        except MainMenUI:
            continue

# Run
if __name__ == '__main__':
    # Uncomment main() for real program
    main()

    # ------ Use this for debugging --------


