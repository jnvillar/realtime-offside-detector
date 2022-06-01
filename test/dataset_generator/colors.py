from test.dataset_generator.domain import Team, PlayerType
from utils import constants

FIELD_BOX_COLOR = constants.BGR_WHITE

TEAM_BOX_COLOR = {
    Team.TEAM_ONE: {PlayerType.FIELD_PLAYER: constants.BGR_RED, PlayerType.GOALKEEPER: constants.BGR_DARK_RED},
    Team.TEAM_TWO: {PlayerType.FIELD_PLAYER: constants.BGR_BLUE, PlayerType.GOALKEEPER: constants.BGR_DARK_BLUE},
    Team.REFEREE: {PlayerType.FIELD_PLAYER: constants.BGR_YELLOW}
}

TEAM_BOX_COLOR_LAST_DEFENSE = {
    Team.TEAM_ONE: constants.BGR_ORANGE,
    Team.TEAM_TWO: constants.BGR_CIAN
}

VP_SEGMENTS_COLOR = constants.BGR_GREEN