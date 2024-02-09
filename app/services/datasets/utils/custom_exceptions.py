class GFED_YearNotAvailableException(Exception):
    def __init__(self, message):
        super().__init__(message)

class GFED_RequestException(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code