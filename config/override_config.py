from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *
from utils.constants import VideoConstants

override_config = {
    VideoConstants.video_1_Arsenal_Chelsea_107_122: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(109, 606), (963, 369)], [(495, 851), (1562, 410)]]
            }
        }
    },
    VideoConstants.video_2_Boca_Lanus_202_216: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'hough_lines_threshold': 400,
                'vp_segments_first_frame': [[(376, 1043), (894, 295)], [(753, 1076), (1096, 301)]]
            }
        }
    },
    VideoConstants.video_2_Boca_Lanus_383_392: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'hough_lines_threshold': 400,
                'vp_segments_first_frame': [[(542, 1055), (1115, 482)], [(980, 1069), (1434, 474)]]
            }
        }
    },
    VideoConstants.video_3_Inter_Roma_55_67: {
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
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(132, 586), (800, 330)], [(456, 867), (1345, 341)]]
            }
        }
    },
    VideoConstants.video_3_Inter_Roma_147_158: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(308, 1031), (599, 296)], [(1466, 1036), (1185, 306)]]
            }
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'debug': False,
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            }
        },
    },
    VideoConstants.video_4_Liverpool_Benfica_119_126: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1102, 987), (828, 266)], [(1606, 989), (1100, 306)]]
            }
        }
    },
    VideoConstants.video_4_Liverpool_Benfica_422_432: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(826, 979), (557, 286)], [(1378, 989), (848, 289)]]
            }
        }
    },
    VideoConstants.video_6_Napoli_Fiorentina_91_98: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1317, 1011), (846, 263)], [(1857, 968), (1181, 260)]]
            }
        }
    },
    VideoConstants.video_7_Psg_Angers_103_110: {
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
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(706, 996), (898, 399)], [(1511, 997), (1253, 405)]]
            }
        }
    },
    VideoConstants.video_7_Psg_Angers_156_167: {
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
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'debug': False,
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1392, 1037), (1107, 375)], [(1778, 1018), (1280, 394)]]
            }
        }
    },
    VideoConstants.video_10_Italia_Alemania_78_94: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1124, 1039), (453, 405)], [(1549, 992), (718, 391)]]
            }
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'debug': False,
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 3,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_three, team_one, team_two]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            }
        },
    },
    VideoConstants.video_10_Italia_Alemania_162_173: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(604, 1041), (1299, 362)], [(1095, 1057), (1584, 360)]]
            }
        }
    },
    VideoConstants.video_10_Italia_Alemania_548_555: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1141, 1007), (264, 419)], [(1392, 702), (643, 358)]]
            }
        }
    },
    VideoConstants.video_11_Estudiantes_Patronato_380_392: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(163, 1053), (1068, 444)], [(13, 532), (657, 246)]]
            }
        }
    },
    VideoConstants.video_12_ManchesterCity_Sevilla_66_74: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(411, 1039), (1305, 306)], [(1148, 1075), (1641, 323)]]
                # Not detecting anything on this video. Tweak other parameters
            }
        }
    },
    VideoConstants.video_13_Chelsea_Milan_38_44: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(648, 1061), (622, 244)], [(11, 1007), (361, 302)]]
            }
        }
    },
    VideoConstants.video_14_Psg_Olympique_156_164: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1567, 1052), (670, 289)], [(1884, 703), (1200, 318)]]
            }
        }
    },
    VideoConstants.video_15_Valencia_Getafe_38_52: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(944, 1046), (930, 276)], [(1561, 1044), (1262, 491)]]
                # Not detecting anything on this video. Tweak other parameters
            }
        }
    },
    VideoConstants.video_17_Celta_RealMadrid_112_122: {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'method': 'kmeans',
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.015,
                'debug_lines': False,
                'debug': False,
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
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(890, 779), (1785, 253)], [(1543, 1071), (1917, 656)]]
            }
        }
    },
    VideoConstants.video_18_Sevilla_Valladolid_29_38: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(750, 1043), (737, 365)], [(174, 1029), (527, 400)]]
                # Not detecting anything on this video. Tweak other parameters
            }
        }
    },
    VideoConstants.video_19_RealMadrid_Shakhtar_20_29: {
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
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(874, 1018), (157, 449)], [(1149, 911), (365, 433)]]
            }
        }
    },
    VideoConstants.video_19_RealMadrid_Shakhtar_245_253: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(439, 1052), (416, 304)], [(921, 1043), (647, 301)]]
            }
        }
    },
    VideoConstants.video_20_BayernMunich_ViktoriaPlzen_515_524: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(821, 1047), (489, 149)], [(308, 1061), (257, 134)]]
            }
        }
    },
    VideoConstants.video_21_Roma_Ludogrets_503_510: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(896, 998), (1165, 200)], [(1461, 1026), (1469, 202)]]
                # Not detecting anything on this video. Tweak other parameters
            }
        }
    },
    VideoConstants.video_22_ManchesterCity_Brighton_539_547: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(426, 963), (1116, 85)], [(1028, 938), (1396, 52)]]
                # Not detecting very well on this video. Tweak other parameters
            }
        }
    },
}
