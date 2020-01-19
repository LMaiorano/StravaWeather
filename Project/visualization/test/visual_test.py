import filecmp
import pytest
import os

import pandas as pd

from Project.visualization.visual_module import GoogleHeatmap


def test_create_heatmap():
    test_data = os.path.join(os.path.dirname(__file__), 'reference_data/reference_data_n=31.csv')
    test_df = pd.read_csv(test_data)
    heatmap_name = 'test_heatmap'
    reference_html = 'reference_data/reference_heatmap_w_weights.html'

    colors = ['rgba(0,0,255,0)',
              'rgba(92,18,163,1)',
              'rgba(127,25,128,1)',
              'rgba(159,31,96,1)',
              'rgba(202,40,53,1)',
              'rgba(255,51,0,1)']
    colors2 = ['rgba(0,0,255,0)',
               'rgba(0,255,0,1)',
               'rgba(255,255,0,1)',
               'rgba(255,156,64,1)',
               'rgba(255,0,0,1)']
    blwhrd = ['rgba(74,111,227,1)',
              'rgba(133,149,225,1)',
              'rgba(181,187,227,1)',
              'rgba(226,226,226,0)',
              'rgba(230,175,185,1)',
              'rgba(224,123,145,1)',
              'rgba(211,63,106,1)']

    htmap = GoogleHeatmap(results_dir='', weatherType=heatmap_name)
    htmap.gen_googlemap(test_df)

    # Shallow=False ensures that files must be exactly the same
    assert filecmp.cmp(htmap.html_path, os.path.join(os.path.dirname(__file__), reference_html), shallow=False)

    # Clean directory
    os.remove(htmap.html_path)
    del test_df, heatmap_name, htmap

@pytest.mark.xfail
def test_take_screenshot_NL():

    ref_html = 'reference_data/reference_heatmap_n=31.html'
    img_name = 'test_screenshot'

    ref_html = os.path.join(os.path.dirname(__file__), ref_html)


    htmap = GoogleHeatmap(weatherType=ref_html, results_dir='')
    htmap.screenshot(img_name=img_name)

    try:
        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), htmap.img_path),
                           os.path.join(os.path.dirname(__file__), 'reference_data/reference_img_n=31.png'), shallow=False)

    finally:
        # Clean directory
        os.remove(htmap.img_path)
        del ref_html, img_name, htmap

#
# #
# def test_sandbox():
#     data_loc = os.path.join(os.path.dirname(__file__), 'reference_data/segments_ZH_5km.csv')
#     test_df = pd.read_csv(data_loc)
#
#     name = 'ZH_segments'
#     output_dir = os.path.join('..', 'results')
#     htmap = Heatmap(results_dir=output_dir, weatherType=name)
#     htmap.build_heatmap(test_df, zoom_level=10, threshold=10, radius=20, gradient=None, opacity=0.6, dissipating=True)
#
#     image_name = name
#     # htmap.screenshot(image_name=image_name, satellite=True, sat_labels=False)

#     print(htmap.img_path)
#     # CleanUp
#     # os.remove(htmap.html_path)
# #
#
