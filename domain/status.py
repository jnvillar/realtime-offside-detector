from enum import Enum


class Status(Enum):
    def __init__(self, status):
        self.status = status

    active = "active"
    inactive = "inactive"
