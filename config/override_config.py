from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *

override_config = {
    '9_Udinese-Cagliari_35_41': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'debug': True,
                'klusters': 20,
                'color_percentage': (1 / 100),  # 5%
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.06,
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
    },
    '12_ManchesterCity-Sevilla_415_425': {
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
            'kmeans': {
                'debug': False,
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 3,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'automatic_by_color': {
                white.color_name: team_two,
                red.color_name: team_two
            }
        },
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'debug': False,
                'klusters': 15,
                'color_percentage': (1 / 100),  # 5%
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.045,
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
