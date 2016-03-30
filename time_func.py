"""This module defines helper functions to get/transform datetime object."""
import arrow
from datetime import datetime
from datetime import timedelta

SEC_HOUR = 60 * 60.
SEC_DAY = SEC_HOUR * 24
STR2LEVEL = {"days": 0, "weeks": 1, "months": 2}
LEVEL2STR = {0: "days", 1: "weeks", 2: "months"}
# TODO Build TZINFO global parameter

def fmt_cal_str(cal_string):
    """
    Format calendar range string to the STR2LEVEL acceptable form.
    :param cal_string: A string for calendar range, unformed.
    :return: A lowercase plural string.
    """
    cal_string = cal_string.lower()
    cal_string = cal_string if cal_string[-1] == 's' else cal_string+'s'
    return cal_string


def quick_range(current=True, shift=0, unit='days'):
    """
    Return some simple default time ranges in unix timestamp.
    Example
        yesterday = (False, 0, 'days')
        (True, 2, 'weeks') = current week + last week
        (False, 2, 'weeks') = last week + last last week
        When need relative time range to today, using (False, n, 'days')
    :param current: time range has finished or not.
    :param shift: shift for time unit
    :param unit: days/weeks/months/years
    :return: (int) start, (int) end
    """
    now = arrow.get(datetime.now(), 'US/Eastern')
    current = 0 if current else 1
    # build arguments for arrow.replace()
    end_arg = {unit: current*(-1)}
    start_arg = {unit: shift*(-1)}
    end = now.replace(**end_arg)
    start = end.replace(**start_arg)

    start = start.floor(unit[:-1]).timestamp
    end = end.ceil(unit[:-1]).timestamp + 1
    return start, end


def human_qr(phrase):
    """
    Translate human phrase into the arguments of quick_range()
    :param phrase: A string to represent a time range in English (e.g. 'last two weeks').
    :return: (int) start, (int) end
    """
    current, shift, unit = phrase.split(" ")
    current = True if current == 'this' or current == 'these' else False
    shift = int(shift) - 1
    unit = fmt_cal_str(unit)
    start, end = quick_range(current, shift, unit)
    return start, end


def str2datetime(date_string, tzinfo='US/Eastern'):
    """
    Transform a date string into Arrow datetime object.
    :param date_string: A string of date (e.g. "20150112").
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: Arrow datetime
    """
    date_time = arrow.get(date_string, "YYYYMMDD", tzinfo=tzinfo)
    return date_time


def str2ts(date_string, tzinfo='US/Eastern'):
    """
    Transform a date string into unix timestamp (beginning of the date).
    :param date_string: a date string in form of "YYYYMMDD".
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: (int) unix timestamp
    """
    timestamp = str2datetime(date_string, tzinfo=tzinfo).timestamp
    return timestamp


def str2range(date_string1, date_string2, tzinfo='US/Eastern'):
    """
    Get unix timestamps for two date string as a range, not including the second date.
    :param date_string1: a date string in form of "YYYYMMDD".
    :param date_string2: a date string in form of "YYYYMMDD".
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: (int) start, (int) end
    """
    start = str2ts(date_string1, tzinfo=tzinfo)
    end = str2ts(date_string2, tzinfo=tzinfo)
    return start, end


def str2level_range(date_string, level, tzinfo='US/Eastern'):
    """
    Get start and end unix timestamps for given date string.
        Day: "YYYYMMDD", e.g. "20151225"
        Week: "YYYYWww", e.g. "2011W08"
        Month: "YYYYMmm", e.g. "2000M03"
    :param date_string: a date string.
    :param level: An integer for different time levels.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: (int) start, (int) end
    """
    start = None
    unit = LEVEL2STR[level]
    replace_arg = {unit: 1}
    if level == 0:
        start = str2ts(date_string, tzinfo=tzinfo)
    elif level == 1:
        start = parse_week_number(date_string, tzinfo).timestamp
    elif level == 2:
        return week_of_month(date_string, tzinfo)
    end = ts2datetime(start, tzinfo=tzinfo).replace(**replace_arg).timestamp
    return start, end


def week_of_month(month_str, tzinfo='US/Eastern'):
    year, month = month_str.split('M')
    # every 4th of that month will in the first week for that month
    month_4th = arrow.get(year+month+"04", "YYYYMMDD", tzinfo=tzinfo)
    week_start = month_4th.floor('week').timestamp
    week_end = month_4th.replace(months=+1).replace(weeks=-1).ceil('week').timestamp+1
    return week_start, week_end


def ts2datetime(timestamp, tzinfo='US/Eastern'):
    """
    Get Arrow datetime object from unix timestamp
    :param timestamp: A integer of unix timestamp.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: Arrow datetime
    """
    return arrow.get(timestamp).to(tzinfo)


def ts2date(timestamp, tzinfo='US/Eastern'):
    """
    Get Arrow date object from unix timestamp
    :param timestamp: A integer of unix timestamp.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: Arrow date
    """
    return ts2datetime(timestamp, tzinfo).date()


def ts2str_level(timestamp, level, tzinfo='US/Eastern'):
    """
    Transform unix timestamp into date string.
    :param level: (int) time frame number
    :param timestamp: A integer of unix timestamp.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: (str) describes its time frame.
    """
    date_time = ts2datetime(timestamp, tzinfo)
    date_string = None
    if level == 0:
        date_string = date_time.strftime('%Y%m%d')
    elif level == 1:
        date_string = date_time.strftime('%YW%V')
    elif level == 2:
        date_string = date_time.strftime('%YM%m')
    return date_string


def ts2str_hm(timestamp, tzinfo='US/Eastern'):
    """
    Transform unix timestamp into string of hour and minute at the time.
    :param timestamp: A integer of unix timestamp.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: A string in form of "HH:mm".
    """
    return ts2datetime(timestamp, tzinfo).format("HH:mm")


def sec2str(duration, sign=False):
    """
    Transform duration in seconds into readable duration.
    :param duration: duration in seconds
    :param sign: Boolean, whether or not add sign to result string
    :return: string format of duration
    """
    positive = True if duration >= 0 else False
    td = timedelta(seconds=abs(duration))
    day = td.days
    hour = td.seconds/3600
    minute = (td.seconds/60) % 60
    time_str = str(minute) + 'm'
    if hour != 0:
        time_str = str(hour) + 'h ' + time_str
    if day != 0:
        time_str = str(day) + 'd ' + time_str
    if sign:
        if not positive:
            time_str = '-' + time_str
        else:
            time_str = '+' + time_str
    return time_str


def ts_cross_day(timestamp, tzinfo='US/Eastern'):
    """
    Make timestamps in the last night and next day before dawn comparable for sleep analysis.
        Transform a time before 20:00 into next day in seconds, and after 20:00 into one day in seconds.
    :param timestamp: A integer of unix timestamp.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: An integer of time in in seconds.
    """
    date_time = ts2datetime(timestamp, tzinfo=tzinfo)
    hour = int(date_time.format("H"))
    minute = int(date_time.format("m"))
    second = int(date_time.format("s"))
    if hour < 20:
        hour += 24
    result = hour * 3600 + minute * 60 + second
    return result


def get_datelist(start, end, level):
    """
    Generate a a relative date span list between given timestamp according to levels.
    Used in plot function for x-axis date.
    :param start: integer of unix timestamp.
    :param end: integer of unix timestamp.
    :param level: An integer for different time levels.
    :return: a list of datetime object.
    """
    start, end = ts2datetime(start), ts2datetime(end - 1)
    unit = LEVEL2STR[level][:-1]
    result = [s.date() for s, e in arrow.Arrow.span_range(unit, start, end)]
    return result


def day_info(date_string=None):
    """
    Generate a string to describe the date, default yesterday.
    :param date_string: A date string in form of "YYYYMMDD".
    :return: A string of date description.
    """
    if date_string:
        date = str2datetime(date_string)
    else:
        date = ts2datetime(human_qr('last 1 day')[0])
    day = int(date.strftime('%j'))
    suffix = ""
    if 1 <= day % 10 <= 3:
        if day % 100 not in [11, 12, 13]:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
    else:
        suffix = "th"
    next_year = date.replace(years=1).floor('year')
    rest_days = (next_year - date).days - 1
    if rest_days > 1:
        strings = date.strftime('Today is %A, %b. %d,  Week %V, the %j{0} day of %Y. '
                                'There are {1} days left in the year.'.format(suffix, rest_days))
    else:
        strings = date.strftime('Today is %A, %b. %d,  Week %V, the %j{0} day of %Y. '
                                'There is {1} day left in the year.'.format(suffix, rest_days))
    return strings


def parse_week_number(week_str, tzinfo='US/Eastern'):
    """
    Parse week number string into the monday of that week
    :param week_str: (string) describe weeks, e.g. "1991W05".
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :return: datetime
    """
    try:
        year, week = week_str.split('W')
        # every 4 Jan will in the first week (ISO)
        week_01 = arrow.get(year+"0104", "YYYYMMDD", tzinfo=tzinfo).floor('week')
        monday = week_01.replace(weeks=int(week)-1)
        return monday
    except ValueError:
        print "Please input week number in the form of '1990W05'."


def break_level(start, end, level, tzinfo='US/Eastern'):
    """
    Return a list of unix timestamp break the start and end time according to given time frame.
    start and end are not included.
    :param tzinfo: A string for timezone, default is 'US/Eastern'.
    :param start: integer of unix timestamp.
    :param end: integer of unix timestamp.
    :param level: int of time frame
    :return: list of unix timestamp
    """
    start_time = ts2datetime(start, tzinfo=tzinfo)
    end_time = ts2datetime(end, tzinfo=tzinfo)
    break_points = []
    if level == 0:
        break_points = arrow.Arrow.range('day', start_time, end_time)[1:-1]
    else:
        replace_arg = {LEVEL2STR[level]: 1}
        if (level == 1 and start_time.isocalendar()[:2] == end_time.isocalendar()[:2]) or \
                (level == 2 and start_time.strftime("%Y%m") == end_time.strftime("%Y%m")):
            pass
        else:
            point = start_time
            while True:
                point = point.replace(**replace_arg).floor(LEVEL2STR[level][:-1])
                if point >= end_time:
                    break
                break_points.append(point)
    break_points = [x.timestamp for x in break_points]
    return break_points


def get_days_of_month(start, end):
    ts_list = [start] + break_level(start, end, 2) + [end]
    date_list = map(lambda x: ts2date(x), ts_list)
    days_list = []
    for n in range(len(date_list)-1):
        days_list.append((date_list[n+1]-date_list[n]).days)
    return days_list
