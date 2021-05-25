from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *

default_config = {
    'analytics_conf': {
        'status': Status.inactive
    },
    'app': {
        'show_result': True,
        'stop_in_frame': 2,
        'resize': {
            'apply': False,
            'size_h': 500,
            'size_w': 500,
        }
    },
    'player_finder': {
        'debug': False
    },
    'team_classifier': {  # params for team classifier
        'method': 'by_parameter',
        'by_parameter': {  # params used in by parameter method
            'attacking_team': Team.team_river
        }
    },
    'player_sorter': {
        # bsas, automatic_by_color, by_color, kmeans
        'method': 'kmeans',
        'bsas': {
            'threshold': 0,
            'clusters': 2,
            'team_one': Team.team_boca,
            'team_two': Team.team_river,
            'debug': True
        },
        'kmeans': {
            'team_one': Team.team_boca,
            'team_two': Team.team_river,
            'debug': True,
            'only_unclassified_players': True,
            'median': False
        },
        'automatic_by_color': {
            Color.white.color_name: Team.team_river,
            Color.red.color_name: Team.team_river,
        }
    },
    'player_detector': {
        # background_subtraction, edges
        'method': 'edges',
        'background_subtraction': {
            'debug': False,
            'history': 100,
            'detect_shadows': False,
            'var_threshold': 50,
            'ignore_contours_smaller_than': 0.02,
            'keep_contours_by_aspect_ratio': AspectRatio.taller
        },
        'edges': {
            'debug': False,
            'threshold1': 50,
            'threshold2': 70,
            'ignore_contours_smaller_than': 0.04,
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
            'history': 1,
        }
    },
    'vanishing_point_finder': {
        # hough
        'method': 'hough',
        'hough': {
            'debug': True,
            'calculate_every_x_amount_of_frames': 10
        }
    },
    'offside_line_drawer': {
        'debug': False
    },
    'field_detector': {
        'debug': False,
        'method': 'green_detection'
    }
}
