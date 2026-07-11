from datetime import datetime


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    return round(part / total * 100, 2) if total else 0


def parse_date(value):
    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue
    return None
