from player_detector.player_detector import *
from player_finder.player_finder import *
from domain.status import *
from utils.constants import VideoConstants

override_config = {
    VideoConstants.video_1_Arsenal_Chelsea_107_122: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(109, 606), (963, 369)], [(495, 851), (1562, 410)]],
                'line_detection_angular_range': 90
            },
            'central_circle_axis': [[(894, 440), (1378, 440)], [(894, 440), (894, 347)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(122, 494), (373, 392)]
            },
            'kmeans': {
                'blur': False,
            }
        }
    },
    VideoConstants.video_2_Boca_Lanus_202_216: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(376, 1043), (894, 295)], [(753, 1076), (1096, 301)]]
            },
            'central_circle_axis': [[(919, 722), (1532, 722)], [(919, 722), (919, 571)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(519, 694), (686, 644)]
            },
            'background_subtraction': {
                'history': 500,
                'detect_shadows': False,
                'var_threshold': 100,
                'ignore_contours_smaller_than': 0.01,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
        }
    },
    VideoConstants.video_2_Boca_Lanus_383_392: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'hough_lines_threshold': 400,
                'vp_segments_first_frame': [[(542, 1055), (1115, 482)], [(980, 1069), (1434, 474)]]
            },
            'central_circle_axis': [[(919, 722), (1532, 722)], [(919, 722), (919, 571)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(224, 580), (199, 605)]
            },
            'kmeans': {
                'blur': False,
            }
        }
    },
    VideoConstants.video_3_Inter_Roma_55_67: {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.015,
                'debug_lines': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 10,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.005,
                'ignore_contours_bigger_than': 1,
            },
            'tophat': {
                'debug': True
            },
            'by_color': {
                'clicks': [(331, 521), (341, 439)],
                'ignore_contours_smaller_than': 0.05,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'adhoc': {
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.1,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'background_subtraction': {
                'history': 1,
                'detect_shadows': False,
                'var_threshold': 50,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
            'edges': {
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.04,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': False
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(132, 586), (800, 330)], [(456, 867), (1345, 341)]]
            },
            'central_circle_axis': [[(861, 557), (1392, 557)], [(861, 557), (861, 460)]]
        }
    },
    VideoConstants.video_3_Inter_Roma_147_158: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(308, 1031), (599, 296)], [(1466, 1036), (1185, 306)]]
            },
            'central_circle_axis': [[(861, 557), (1392, 557)], [(861, 557), (861, 460)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
        'player_detector': {
            'edges': {
                'parent_contour_only': False,
                'threshold1': 50,
                'threshold2': 70,
            },
            'by_color': {
                'clicks': [(167, 430), (423, 455)]
            }
        }
    },
    VideoConstants.video_4_Liverpool_Benfica_119_126: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1102, 987), (828, 266)], [(1606, 989), (1100, 306)]]
            },
            'central_circle_axis': [[(585, 579), (1147, 579)], [(585, 579), (585, 467)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(35, 373), (705, 617)]
            }
        }
    },
    VideoConstants.video_4_Liverpool_Benfica_422_432: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(826, 979), (557, 286)], [(1378, 989), (848, 289)]]
            },
            'central_circle_axis': [[(585, 579), (1147, 579)], [(585, 579), (585, 467)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(183, 520), (564, 570)]
            },
            'kmeans': {
                'blur': False,
            }
        }
    },
    VideoConstants.video_5_Napoli_Fiorentina_91_98: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1317, 1011), (846, 263)], [(1857, 968), (1181, 260)]]
            },
            'central_circle_axis': [[(143, 652), (848, 652)], [(143, 652), (143, 524)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(1276, 660), (663, 672)],
            },
            'kmeans': {
                # 'min_length_line_in_video_percentage': 0.02,
                'debug_lines': False,
                'debug': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 8,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.01,
                'ignore_contours_bigger_than': 1,
            },
            'edges': {
                'parent_contour_only': False,
                'threshold1': 50,
                'threshold2': 70,
            },
        }
    },
    VideoConstants.video_6_ManchesterCity_Brighton_539_547: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(426, 963), (1116, 85)], [(1028, 938), (1396, 52)]]
            },
            'central_circle_axis': [[(1638, 296), (1163, 278)], [(1638, 296), (1647, 194)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(765, 213), (657, 225)]
            }
        },
    },
    VideoConstants.video_7_Psg_Angers_103_110: {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'ignore_contours_smaller_than': 0.007,
                'klusters': 10,
                'blur': False,
            },
            'by_color': {
                'tolerance': 20,
                'ignore_contours_smaller_than': 0.02,
                'clicks': [(738, 468), (463, 755)]
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(706, 996), (898, 399)], [(1511, 997), (1253, 405)]]
            },
            'central_circle_axis': [[(446, 612), (815, 590)], [(446, 612), (437, 536)]]
        }
    },
    VideoConstants.video_7_Psg_Angers_156_167: {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'min_length_line_in_video_percentage': 0.01,
                'debug_lines': False,
                'blur': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 9,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.01,
                'ignore_contours_bigger_than': 1,
            },
            'by_color': {
                'tolerance': 20,
                'ignore_contours_smaller_than': 0.02,
                'clicks': [(322, 496), (632, 498)]
            }
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {

                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1392, 1037), (1107, 375)], [(1778, 1018), (1280, 394)]],
                'line_detection_angular_range': 90,
            },
            'central_circle_axis': [[(475, 597), (886, 581)], [(475, 597), (466, 512)]]
        }
    },
    VideoConstants.video_8_Roma_Ludogrets_503_510: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(896, 998), (1165, 200)], [(1461, 1026), (1469, 202)]],
                'hough_lines_threshold': 400,
                'line_detection_angular_range': 90,
                # Not detecting anything on this video. Tweak other parameters
            },
            'central_circle_axis': [[(1712, 474), (1112, 462)], [(1712, 474), (1713, 379)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
        'player_detector': {
            'by_color': {
                'clicks': [(305, 385), (554, 398)]
            }
        },
    },
    VideoConstants.video_9_BayernMunich_ViktoriaPlzen_515_524: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(821, 1047), (489, 149)], [(308, 1061), (257, 134)]]
            },
            'central_circle_axis': [[(389, 389), (847, 379)], [(389, 389), (384, 284)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(149, 414), (545, 394)]
            }
        },
    },
    VideoConstants.video_10_Italia_Alemania_78_94: {
        'player_detector': {
            'by_color': {
                'clicks': [(271, 581), (396, 733)],
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1124, 1039), (453, 405)], [(1549, 992), (718, 391)]],
                'line_detection_angular_range': 90,
            },
            'central_circle_axis': [[(389, 701), (998, 687)], [(389, 701), (386, 576)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'blur': False,
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 3,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_three, team_one, team_two]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
    },
    VideoConstants.video_10_Italia_Alemania_162_173: {
        'player_detector': {
            'by_color': {
                'clicks': [(378, 579), (709, 513)],
                'ignore_contours_smaller_than': 0.02,
            },
            'kmeans': {
                'blur': False,
            },
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(604, 1041), (1299, 362)], [(1095, 1057), (1584, 360)]],
                'hough_lines_threshold': 400,
            },
            'central_circle_axis': [[(713, 552), (1179, 550)], [(713, 552), (712, 456)]]
        }
    },
    VideoConstants.video_10_Italia_Alemania_548_555: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1141, 1007), (264, 419)], [(1392, 702), (643, 358)]]
            },
            'central_circle_axis': [[(713, 552), (1179, 550)], [(713, 552), (712, 456)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 3,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_three, team_one, team_two]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
        'player_detector': {
            'by_color': {
                'clicks': [(597, 392), (187, 684)],
                'ignore_contours_smaller_than': 0.02,
            }
        },
    },
    VideoConstants.video_11_Estudiantes_Patronato_380_392: {
        'player_detector': {
            'kmeans': {
                'ignore_contours_smaller_than': 0.005,
            },
            'by_color': {
                'clicks': [(290, 713), (276, 674)]
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(163, 1053), (1068, 444)], [(13, 532), (657, 246)]]
            },
            'central_circle_axis': [[(1905, 601), (1476, 567)], [(1905, 601), (1916, 471)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {

                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
    },
    VideoConstants.video_12_ManchesterCity_Sevilla_66_74: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(411, 1039), (1305, 306)], [(1148, 1075), (1641, 323)]],
                'line_detection_angular_range': 90
            },
            'central_circle_axis': [[(1918, 665), (1176, 626)], [(1918, 665), (1916, 510)]]
        },
        'player_detector': {
            'edges': {
                'parent_contour_only': False,
                'threshold1': 50,
                'threshold2': 70,
            },
            'by_color': {
                'clicks': [(396, 690), (383, 570)]
            },
        },
    },
    VideoConstants.video_13_Chelsea_Milan_38_44: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(648, 1061), (622, 244)], [(11, 1007), (361, 302)]],
                'line_detection_angular_range': 90
            },
            'central_circle_axis': [[(634, 481), (1171, 474)], [(634, 481), (630, 388)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(318, 409), (728, 404)]
            },
            'kmeans': {
                'blur': False,
            },
        },
    },
    VideoConstants.video_14_Psg_Olympique_156_164: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(1567, 1052), (670, 289)], [(1884, 703), (1200, 318)]]
            },
            'central_circle_axis': [[(29, 590), (507, 566)], [(29, 590), (22, 474)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(339, 467), (824, 494)]
            },
            'kmeans': {
                'blur': False,
            },
        },
    },
    VideoConstants.video_15_Valencia_Getafe_38_52: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(944, 1046), (930, 276)], [(1561, 1044), (1262, 491)]],
                # Not detecting anything on this video. Tweak other parameters
                'hough_lines_threshold': 300
            },
            'central_circle_axis': [[(931, 486), (1434, 486)], [(931, 486), (931, 394)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(125, 373), (386, 422)]
            }
        },
    },
    VideoConstants.video_16_RealMadrid_Shakhtar_20_29: {
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'debug_lines': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 10,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.008,
                'ignore_contours_bigger_than': 1,
            },
            'otsu': {

                'ignore_contours_smaller_than': 0.02,
                'ignore_contours_bigger_than': 1,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                # 'filter_contour_inside_other': True
            },
            'tophat': {
                'debug': True
            },
            'by_color': {
                'clicks': [(38, 412), (261, 400)],
                'ignore_contours_smaller_than': 0.05,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'adhoc': {
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.1,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'background_subtraction': {

                'history': 1,
                'detect_shadows': False,
                'var_threshold': 50,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
            'edges': {
                'threshold1': 10,
                'threshold2': 20,
                'ignore_contours_smaller_than': 0.04,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'parent_contour_only': False,
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(874, 1018), (157, 449)], [(1149, 911), (365, 433)]],
                'hough_lines_threshold': 400
            },
            'central_circle_axis': [[(424, 567), (886, 550)], [(424, 567), (421, 463)]]
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
    },
    VideoConstants.video_16_RealMadrid_Shakhtar_245_253: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(439, 1052), (416, 304)], [(921, 1043), (647, 301)]],
                'line_detection_angular_range': 90
            },
            'central_circle_axis': [[(424, 567), (886, 550)], [(424, 567), (421, 463)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(86, 432), (580, 470)]
            },
        },
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one]
                # smallest cluster = team 3, 2dn smallest = team 2 ...
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },

        },
    },
    VideoConstants.video_17_Celta_RealMadrid_112_122: {
        'player_sorter': {
            # bsas, automatic_by_color, by_color, kmeans
            'method': 'kmeans',
            'kmeans': {
                'only_unclassified_players': True,
                'median': False,
                'focused': False,
                'klusters': 2,
                # 'klusters_team': [team_three, team_two, team_one]  # smallest cluster = team 3, 2dn smallest = team 2 ...
                'klusters_team': [team_two, team_one],
                # smallest cluster = team 3, 2dn smallest = team 2 ...
                'blur': False,
            },
            'bsas': {
                'threshold': 0,
                'clusters': 2,
                'team_one': team_two,
                'team_two': team_one,
                'debug': False
            },
        },
        'player_detector': {
            # background_subtraction, edges, adhoc, by_color, kmeans, posta=otsu
            'detect_every_amount_of_frames': 1,
            'kmeans': {
                'green_background': False,
                'min_length_line_in_video_percentage': 0.020,
                'debug_lines': False,
                'color_percentage': (2 / 100),  # 5%
                'klusters': 10,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'ignore_contours_smaller_than': 0.007,
                'ignore_contours_bigger_than': 1,
            },
            'otsu': {

                'ignore_contours_smaller_than': 0.02,
                'ignore_contours_bigger_than': 1,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                # 'filter_contour_inside_other': True
            },
            'tophat': {
                'debug': True
            },
            'by_color': {
                'clicks': [(715, 328), (936, 581)],
                'ignore_contours_smaller_than': 0.02,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'adhoc': {

                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.1,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            },
            'background_subtraction': {

                'history': 1,
                'detect_shadows': False,
                'var_threshold': 50,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
            'edges': {
                'parent_contour_only': False,
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.04,
                'ignore_contours_bigger_than': 0.5,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': False
            }
        },
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(890, 779), (1785, 253)], [(1543, 1071), (1917, 656)]]
            },
            'central_circle_axis': [[(710, 485), (1072, 486)], [(710, 485), (710, 406)]]
        }
    },
    VideoConstants.video_18_Sevilla_Valladolid_29_38: {
        'vanishing_point_finder': {
            'method': 'hough',
            'hough': {
                'vp_segments_first_frame': [[(750, 1043), (737, 365)], [(174, 1029), (527, 400)]],
                'hough_lines_threshold': 400,
                'line_detection_angular_range': 90
            },
            'central_circle_axis': [[(936, 510), (1436, 510)], [(936, 510), (936, 429)]]
        },
        'player_detector': {
            'by_color': {
                'clicks': [(153, 445), (637, 621)]
            },
            'kmeans': {
                'blur': False,
            },
        },
    }
}
