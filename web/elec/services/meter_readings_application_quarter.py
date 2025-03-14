import calendar
from datetime import date, timedelta

from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


def get_application_quarter(current_date: date):
    current_year, current_quarter = quarter(current_date)
    last_day_of_current_quarter = last_day_of_quarter(current_year, current_quarter)

    # the reference date is in the last 10 days of its quarter
    # this means the wanted quarter is the reference date's quarter
    if (last_day_of_current_quarter - current_date).days <= 10:
        application_quarter = current_quarter
        application_year = current_year
    else:
        application_quarter = current_quarter - 1 if current_quarter > 1 else 4
        application_year = current_year if current_quarter > 1 else current_year - 1

    return application_year, application_quarter


def quarter(date: date):
    return date.year, (date.month - 1) // 3 + 1


def first_day_of_quarter(year, quarter):
    first_month = (quarter - 1) * 3 + 1
    return date(year, first_month, 1)


def last_day_of_quarter(year, quarter):
    last_month = quarter * 3
    last_day = calendar.monthrange(year, quarter * 3)[1]
    return date(year, last_month, last_day)


def get_application_deadline(current_date: date, year: int, quarter: int):
    quarter_last_day = last_day_of_quarter(year, quarter)
    deadline = quarter_last_day + timedelta(days=15)
    days_to_deadline = (deadline - current_date).days

    if days_to_deadline < 0:
        status = ElecMeterReadingApplication.CRITICAL
    elif days_to_deadline <= 10:
        status = ElecMeterReadingApplication.HIGH
    else:
        status = ElecMeterReadingApplication.LOW

    return deadline, status
