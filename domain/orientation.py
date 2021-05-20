from enum import Enum


class Orientation(Enum):
    def __init__(self, id):
        self.id = id

    left = 'left'
    right = 'right'

    def __str__(self):
        return self.id
