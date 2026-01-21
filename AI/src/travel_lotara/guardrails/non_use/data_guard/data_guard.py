from enum import Enum

class DataAccessMode(Enum):
    READ = "read"
    WRITE = "write"


class DataGuard:
    def __init__(self, mode: DataAccessMode):
        self.mode = mode

    def ensure_write_allowed(self):
        if self.mode != DataAccessMode.WRITE:
            raise PermissionError("Write access not allowed")
