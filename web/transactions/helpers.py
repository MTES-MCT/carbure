
from transactions.models import LockedYear

def check_locked_year(current_year: int):
    try:
        locked_years = LockedYear.objects.order_by('year').filter(locked=True)
    except:
        # print("NO LOCKED YEAR")
        return False

    try:
        locked_years.get(year = current_year)
        # print("CURRENT YEAR LOCKED")
        return True
    except:
        print(locked_years.first().year)
        if (current_year < locked_years.first().year):
            # print("CURRENT YEAR LOCKED")
            return True
    
    return False