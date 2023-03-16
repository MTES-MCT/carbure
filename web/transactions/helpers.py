
from transactions.models import LockedYear

def check_locked_year(current_year: int, locked_years = None):

    if current_year <= 2015 : return True

    try:
        if locked_years :
            locked_years.get(year = current_year)
        else :
            LockedYear.objects.get(year = current_year, locked = True)
        return True
    except:
        return False