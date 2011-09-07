# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import rpc
import locale
from locale import localeconv

""" When ever the user will connect to the server through client the client will
    read all the userful values of the user's locale settings from the server and will update the
    LOCALE_CACHE dictionary. Then when the client needs the values it will be just returned
    form this LOCALE_CACHE.

    This is done because there may be the case if the user has modified the default locale date
    format from administration/Translations/Languages.

    For Example: if the user has 'en_US' set as his locale and 'en_US' has date format as '%m/%d/%Y'
    but he changes the date format to '%d/%m/%Y' from the menu specified above.So previously the gtk client
    was just setting the locale format inspite of the user's modification in the locale settings.

    Previously we just returned the user's locale format inspite of his modifications the modifications
    we not taken into account.

    fmt = locale.nl_langinfo(locale.D_FMT)
    for x,y in [('%y','%Y'),('%B',''),('%A','')]:
        fmt = fmt.replace(x, y)
     if not (fmt.count('%Y') == 1 and fmt.count('%m') == 1 and fmt.count('%d') == 1):
         return '%Y/%m/%d'
    return fmt
"""


LOCALE_CACHE = {
               'date_format':'%m/%d/%Y',
               'time_format':'%H:%M:%S',
               'grouping':[],
               'decimal_point':'.',
               'thousands_sep': ','
               }

def set_locale_cache(lang_data = {}):

    """ This function will set the LOCALE_CACHE dictionary to the
        values of the latest user locale settings.

        @param lang_data: The dictionary of values that has to be set.

     """
    try:
        if lang_data:
            if 'id' in lang_data:
                del lang_data['id']
            LOCALE_CACHE.update(lang_data)
    except:
        pass

def get_date_format():

    """ This function will return date format that the user has
        set/modified in the locale settings.

        @return: The date format of the user's set/ modified locale from the LOCALE_CACHE. """

    return str(LOCALE_CACHE.get('date_format','%m/%d/%Y'))

def get_datetime_format(with_date = False):

    """ This function will return date/datetime format
        that the user has set/modified in the locale settings.

        @param with_date: If True will return datetime format Else only the time format.

        @return: The date/datetime format of the user's set/ modified locale from the LOCALE_CACHE. """

    fmt = str(LOCALE_CACHE.get('time_format', '%H:%M:%S'))
    if with_date:
        return get_date_format() + ' ' + fmt
    return fmt


def get_lang_int_float_format(monetary=False):

    """ This function will return the values like thousands_separator, decimal_point,
        grouping, from the LOCALE_CACHE that the user has set/modified in the locale settings.

    @param monetary: IF True will will return the monetary_thousands separator.

    @return: The tuple (grouping, thousands_sep, decimal_point) """

    conv = localeconv()
    thousands_sep = LOCALE_CACHE.get('thousands_sep') or conv[monetary and 'mon_thousands_sep' or 'thousands_sep']
    decimal_point = LOCALE_CACHE.get('decimal_point')
    grouping      = LOCALE_CACHE.get('grouping')
    return (grouping, thousands_sep, decimal_point)

def group(value, monetary=False, grouping=False, thousands_sep=''):

    """ This function will convert the value in appropriate format after applying
        thousands_sep, grouping etc

        @param value:The value to be converted
        @param monetary:True or False by default False
        @param grouping:True or False by default False
        @param thousands_sep: The symbol to be applied at the thousand's place by default blank

        @return: The converted value"""

    grouping = eval(grouping)
    if not grouping:
        return (value, 0)

    result = ""
    seps = 0
    spaces = ""

    if value[-1] == ' ':
        sp = value.find(' ')
        spaces = value[sp:]
        value = value[:sp]

    while value and grouping:
        # if grouping is -1, we are done
        if grouping[0] == -1:
            break
        # 0: re-use last group ad infinitum
        elif grouping[0] != 0:
            #process last group
            group = grouping[0]
            grouping = grouping[1:]
        if result:
            result = value[-group:] + thousands_sep + result
            seps += 1
        else:
            result = value[-group:]
        value = value[:-group]
        if value and value[-1] not in "0123456789":
            # the leading string is only spaces and signs
            return value + result + spaces, seps
    if not result:
        return value + spaces, seps
    if value:
        result = value + thousands_sep + result
        seps += 1
    return result + spaces, seps

def format(percent, value, grouping=True, monetary=False):

    """ Format() will return the language-specific output for float values

        @param percent: The '%' symbol for float values.
        @param value: The value that has to be formated.
        @param grouping: True of False, by default False.
        @param monetary: True of False, by default False.

        @return: The converted value. """


    if percent[0] != '%':
        raise ValueError("format() must be given exactly one %char format specifier")

    lang_grouping, thousands_sep, decimal_point = get_lang_int_float_format(monetary)

    formatted = percent % value
    # floats and decimal ints need special action!
    if percent[-1] in 'eEfFgG':
        seps = 0
        parts = formatted.split('.')

        if grouping:
            parts[0], seps = group(parts[0], monetary=monetary, grouping=lang_grouping, thousands_sep=thousands_sep)

        formatted = decimal_point.join(parts)
        while seps:
            sp = formatted.find(' ')
            if sp == -1: break
            formatted = formatted[:sp] + formatted[sp+1:]
            seps -= 1
    elif percent[-1] in 'diu':
        if grouping:
            formatted = group(formatted, monetary=monetary, grouping=lang_grouping, thousands_sep=thousands_sep)[0]
    return formatted

def str2int(string):
    ''' Converts a string to an integer according to the locale settings
        that the user has in Administration/Translations/Languages.
    '''
    assert isinstance(string, basestring)
    return str2float(string, int)

def str2float(string, func=float):
    ''' Parses a string as a float according to the locale settings
    that the user has in Administration/Translations/Languages.
    '''
    assert isinstance(string, basestring)
    try:
        #First, get rid of the thousand separator
        ts = LOCALE_CACHE.get('thousands_sep')
        if ts:
            string = string.replace(ts, '')
        #next, replace the decimal point with a dot
        dd = LOCALE_CACHE.get('decimal_point')
        if dd:
            string = string.replace(dd, '.')
        #finally, parse the string
        return func(string)
    except:
        type = 'float'
        if func == int:
            type = 'integer'
        raise ValueError("%r does not represent a valid %s value" % (string,type))
