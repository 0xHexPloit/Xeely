from enum import Enum


class XXEAttackType(Enum):
    FILE_DISCLOSURE = "FILE_DISCLOSURE"
    DIRECTORY_LISTING = "DIRECTORY_LISTING"
    RCE = "RCE"
    SSRF = "SSRF"
