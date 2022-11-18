from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *

override_config = {
    '19_RealMadrid-Shakhtar_20_29': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'debug_lines': False,
                'debug': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 10,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.008,
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
        }
    },
    '7_Psg-Angers_103_110': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.01,
                'debug_lines': False,
                'debug': True,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 9,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.01,
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
        }
    },
    '7_Psg-Angers_156_167': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.01,
                'debug_lines': False,
                'debug': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 9,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.01,
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
        }
    },
    '3_Inter-Roma_55_67': {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.015,
                'debug_lines': False,
                'debug': True,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 10,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.005,
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
        }
    }
}
