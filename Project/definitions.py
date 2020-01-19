import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ACTIVITY_DATA_DIR = os.path.join(ROOT_DIR, 'analysis', 'reference_data', 'activities')
BASELINE_DATA_DIR = os.path.join(ROOT_DIR, 'analysis', 'Baseline', 'data')
SEGMENT_DATA_DIR = os.path.join(ROOT_DIR, 'strava', 'reference_data')
VISUAL_RESULTS_DIR = os.path.join(ROOT_DIR, 'results', 'visual_results')
UI_GEN_DATA_DIR = os.path.join(ROOT_DIR, 'results', 'ui_gen_data')
CREDENTIALS_PATH = os.path.join(ROOT_DIR, 'credentials.yml')