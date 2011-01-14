import time
import datetime 
import locale

if not hasattr(locale, 'nl_langinfo'):
    def nl_langinfo(param):
        val = time.strptime('30/12/2004', '%d/%m/%Y')
        dt = datetime.datetime(*val[:-2])
        format_date = dt.strftime('%x')
        for x, y in [('30','%d'),('12','%m'),('2004','%Y'),('04','%Y')]:
            format_date = format_date.replace(x,y)
        return format_date
    locale.nl_langinfo = nl_langinfo


    if not hasattr(locale, 'D_FMT'):
        locale.D_FMT = None

