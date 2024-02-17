from datetime import date

def get_formatted_date(d: date):
    return f'{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}'