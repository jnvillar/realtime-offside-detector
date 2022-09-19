from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *

override_config = {
    '12_ManchesterCity-Sevilla_415_425': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'debug': False,
                'klusters': 15,
                'least_predominant_colors': 5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.03,
                'ignore_contours_bigger_than': 1,
            },
            'otsu': {
                'debug': False,
                'ignore_contours_smaller_than': 0.02,
                'ignore_contours_bigger_than': 1,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                # 'filter_contour_inside_other': True
            },
            'tophat': {
                'debug': True
            },
            'by_color': {
                'debug': False,
                'ignore_contours_smaller_than': 0.05,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'adhoc': {
                'debug': False,
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.1,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'background_subtraction': {
                'debug': False,
                'history': 1,
                'detect_shadows': False,
                'var_threshold': 50,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
            'edges': {
                'debug': True,
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.04,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            }
        },
    }
}
