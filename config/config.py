from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *

default_config = {
    'analytics_conf': {
        'status': Status.inactive
    },
    'logger': {
        'status': Status.active
    },
    'screen_manager': {
        'debug_screen': 0,
    },
    'app': {
        'show_result': True,
        'show_players': True,
        'stop_in_frame': 1,
        'resize': {
            'apply': False,
            'size_h': 500,
            'size_w': 500,
        },
        'team_names': {
            team_one.id: "boca",
            team_two.id: "river",
        }
    },
    'player_finder': {
        'debug': False
    },
    'team_classifier': {  # params for team classifier
        'method': 'by_parameter',
        'by_parameter': {  # params used in by parameter method
            'attacking_team': team_two
        }
    },
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
            'focused': True,
            'klusters': 3,
            'klusters_team': {
                0: team_one,
                1: team_two,
                2: team_three,
            }
        },
        'automatic_by_color': {
            white.color_name: team_two,
            red.color_name: team_two
        }
    },
    'player_detector': {
        # background_subtraction, edges, adhoc,posta=by_color, otsu
        'method': 'otsu',
        'detect_every_amount_of_frames': 2,
        'otsu': {
            'debug': True,
            'ignore_contours_smaller_than': 0.06,
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
    'orientation_detector': {
        # methods: by_parameter, by_vanishing_point
        'method': 'by_vanishing_point',
        'by_parameter': {  # params used in by parameter method
            'orientation': Orientation.left
        },
    },
    'player_tracker': {
        # opencv, distance
        'method': 'distance',
        'opencv': {  # params used in by opencv method
            'tracker': 'kcf'
        },
        'distance': {
            'history': 2,
            'team_history': 3,
        }
    },
    'vanishing_point_finder': {
        'method': 'hough',
        'hough': {
            'debug': False,
            'calculate_every_x_amount_of_frames': 5
        }
    },
    'offside_line_drawer': {
        'debug': False
    },
    'field_detector': {
        'debug': False,
        'method': 'ground_pixels_detection'
    }
}
