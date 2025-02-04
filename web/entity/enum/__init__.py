from enum import Enum

class UserStatusEnum(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]