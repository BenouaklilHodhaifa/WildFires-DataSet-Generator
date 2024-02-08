class Gfed_year_out_of_bound_exception(Exception):
    def __init__(self, message):
        super().__init__(message)

class Gfed_request_exception(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code