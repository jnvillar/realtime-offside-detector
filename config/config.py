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
        'show_original': False,
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
        },
        'compare': False
    },
    'player_finder': {
        'debug': False
    },
    'team_classifier': {  # params for team classifier
        'method': 'by_parameter',
        'by_parameter': {  # params used in by parameter method
            'attacking_team': team_two
        },
        'by_ball_detection': {  # params used in by ball detection method
            'debug': False
        }
    },
    'player_sorter': {
        # bsas, automatic_by_color, by_color, kmeans
        'method': 'kmeans',
        'bsas': {
            'threshold': 0,
            'clusters': 2,
            'team_one': team_one,
            'team_two': team_two,
            'debug': False
        },
        'kmeans': {
            'debug': True,
            'only_unclassified_players': True,
            'median': False,
            'focused': False,
            'klusters': 2,
            # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            'klusters_team': [team_one, team_two]  # smallest cluster = team 3, 2dn smallest = team 2 ...
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
            'debug_lines': False,
            'debug': False,
            'color_percentage': (2 / 100),  # 5%
            'klusters': 8,
            'keep_contours_by_aspect_ratio': AspectRatio.taller,
            'ignore_contours_smaller_than': 0.01,
            'ignore_contours_bigger_than': 1,
        },
        'otsu': {
            'debug': True,
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
            'debug_lines': False,
            'debug': True,
            'history': 1,
            'detect_shadows': False,
            'var_threshold': 100,
            'ignore_contours_smaller_than': 0.01,
            'keep_contours_by_aspect_ratio': AspectRatio.taller
        },
        'edges': {
            'parent_contour_only': True,
            'debug': False,
            'threshold1': 10,
            'threshold2': 20,
            'ignore_contours_smaller_than': 0.04,
            'ignore_contours_bigger_than': 0.5,
            'keep_contours_by_aspect_ratio': AspectRatio.taller,
            'filter_contour_inside_other': False
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
        # opencv, distance, off
        'method': 'off',
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
            'calculate_every_x_amount_of_frames': 1,
            'max_number_of_candidate_lines': 100,
            'hough_lines_threshold': 500,
            'vp_segments_first_frame': None
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
