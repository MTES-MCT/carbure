
from transactions.models import LockedYear

def check_locked_year(current_year: int):
    locked_years = LockedYear.objects.order_by('year').filter(locked=True)
    if locked_years.count() == 0 : return False

    try:
        locked_years.get(year = current_year)
        return True
    except:
        return (True if current_year < locked_years.first().year else False)
