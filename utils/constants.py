

class VideoConstants:
    video_1_Arsenal_Chelsea_107_122 = "1_Arsenal-Chelsea_107_122.mp4"
    video_2_Boca_Lanus_202_216 = "2_Boca-Lanus_202_216.mp4"
    video_2_Boca_Lanus_383_392 = "2_Boca-Lanus_383_392.mp4"
    video_3_Inter_Roma_55_67 = "3_Inter-Roma_55_67.mp4"
    video_3_Inter_Roma_147_158 = "3_Inter-Roma_147_158.mp4"
    video_4_Liverpool_Benfica_119_126 = "4_Liverpool-Benfica_119_126.mp4"
    video_4_Liverpool_Benfica_422_432 = "4_Liverpool-Benfica_422_432.mp4"
    video_5_Napoli_Fiorentina_91_98 = "5_Napoli-Fiorentina_91_98.mp4"
    video_6_ManchesterCity_Brighton_539_547 = "6_ManchesterCity-Brighton_539_547.mp4"
    video_7_Psg_Angers_103_110 = "7_Psg-Angers_103_110.mp4"
    video_7_Psg_Angers_156_167 = "7_Psg-Angers_156_167.mp4"
    video_8_Roma_Ludogrets_503_510 = "8_Roma-Ludogrets_503_510.mp4"
    video_9_BayernMunich_ViktoriaPlzen_515_524 = "9_BayernMunich-ViktoriaPlzen_515_524.mp4"
    video_10_Italia_Alemania_78_94 = "10_Italia-Alemania_78_94.mp4"
    video_10_Italia_Alemania_162_173 = "10_Italia-Alemania_162_173.mp4"
    video_10_Italia_Alemania_548_555 = "10_Italia-Alemania_548_555.mp4"
    video_11_Estudiantes_Patronato_380_392 = "11_Estudiantes-Patronato_380_392.mp4"
    video_12_ManchesterCity_Sevilla_66_74 = "12_ManchesterCity-Sevilla_66_74.mp4"
    video_13_Chelsea_Milan_38_44 = "13_Chelsea-Milan_38_44.mp4"
    video_14_Psg_Olympique_156_164 = "14_Psg-Olympique_156_164.mp4"
    video_15_Valencia_Getafe_38_52 = "15_Valencia-Getafe_38_52.mp4"
    video_16_RealMadrid_Shakhtar_20_29 = "16_RealMadrid-Shakhtar_20_29.mp4"
    video_16_RealMadrid_Shakhtar_245_253 = "16_RealMadrid-Shakhtar_245_253.mp4"
    video_17_Celta_RealMadrid_112_122 = "17_Celta-RealMadrid_112_122.mp4"
    video_18_Sevilla_Valladolid_29_38 = "18_Sevilla-Valladolid_29_38.mp4"

    def all(self):
        return [v for k, v in VideoConstants.__dict__.items() if k[:1] != '_' and k != 'all']


# Colors RGB
RGB_RED = (255, 0, 0)
RGB_BLUE = (0, 0, 255)
RGB_GREEN = (0, 255, 0)

# Colors BGR
BGR_WHITE = (255, 255, 255)
BGR_RED = (0, 0, 255)
BGR_DARK_RED = (0, 40, 100)
BGR_ORANGE = (0, 165, 255)
BGR_BLUE = (255, 0, 0)
BGR_DARK_BLUE = (100, 40, 0)
BGR_CIAN = (255, 255, 0)
BGR_YELLOW = (0, 255, 255)
BGR_GREEN = (0, 255, 0)

# Key ASCII codes (dec)
DELETE_KEY_CODE = [8, 127]
RETURN_KEY_CODE = 13
ESC_KEY_CODE = 27
SPACE_KEY_CODE = 32
LEFT_ARROW_KEY_CODE = 123
RIGHT_ARROW_KEY_CODE = 124

ONE_KEY_CODE = 49
TWO_KEY_CODE = 50
THREE_KEY_CODE = 51
NINE_KEY_CODE = 57

Y_KEY_CODE = 121
N_KEY_CODE = 110
