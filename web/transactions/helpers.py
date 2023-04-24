from transactions.models import LockedYear


def check_locked_year(current_year: int):
    if current_year <= 2015:
        return True
    try:
        LockedYear.objects.get(year=current_year, locked=True)
        return True
    except:
        return False
