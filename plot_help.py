import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from time_func import SEC_HOUR, SEC_DAY
from db import connect_db

plt.ioff()
PALETTE_12 = ["#CB5E1C", "#34A002", "#D63EC6", "#6FCECE",
              "#D09340", "#FF859B", "#F9E401", "#7F59CC",
              "#ED1F22", "#824D2C", "#2F589D", "#3C6034"]


def bar_width(level):
    width = None
    if level == 0:
        width = 0.8
    elif level == 1:
        width = 0.8 * 7
    elif level == 2:
        width = 0.8 * 30
    return width


def get_palette():
    """Return the hexadecimal color code in a dictionary."""
    cnx, cursor = connect_db()
    query = """select name, color from types"""
    cursor.execute(query)
    color = cursor.fetchall()
    cnx.close()
    color = {x[0]: '#' + format(x[1], 'x') for x in color}
    return color


def date_formatter(ax_value, pos):
    """Format the axis date labels. Add month abbr if date is first day of the month.
    :param pos: position of tick
    :param ax_value: (list) list of values of x axis.
    """
    date = mdates.num2date(ax_value)
    date_str = date.strftime('%d')
    if date.day == 1 and pos:
        date_str = date.strftime('%b-%d')
    return date_str


def format_date(ax, ax_value, level, which='x'):
    """
    Set the axis (date) for different length of value list.
    :param ax: (axis) x axis.
    :param ax_value: (list) list of values of axis.
    :param level: (int) time frame number.
    :param which: (str) x|y, x or y axis
    :return: (axis)
    """
    date_num = mdates.date2num(ax_value)
    length = len(date_num)
    axis = ax.xaxis
    if which == 'y':
        axis = ax.yaxis
    if level == 0:
        if length > 120:
            # only month ticks in the bottom
            axis.set_major_locator(mdates.MonthLocator())
            axis.set_major_formatter(mdates.DateFormatter('%b'))
        elif length > 30:
            # week in bottom, month in top
            axis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
            axis.set_major_formatter(mdates.DateFormatter('%V'))
            axis.set_minor_locator(mdates.MonthLocator())
            axis.set_minor_formatter(mdates.DateFormatter('%b'))
            ax.tick_params(axis=which, which='minor', labeltop=True, labelbottom=False)
            if which == 'y':
                ax.tick_params(axis=which, which='minor', labelright=True, labelleft=False)
            ax.grid(b=True, which='major', color='w')
            ax.grid(b=True, which='minor', color='w', linestyle='--')
        else:
            # day in bottom, week in top
            axis.set_major_locator(ticker.FixedLocator(date_num))
            axis.set_major_formatter(ticker.FuncFormatter(date_formatter))
            axis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
            axis.set_minor_formatter(mdates.DateFormatter('%V'))
            ax.tick_params(axis=which, which='minor', labeltop=True, labelbottom=False)
            if which == 'y':
                ax.tick_params(axis=which, which='minor', labelright=True, labelleft=False)
    elif level == 1:
        # week in bottom, month on top
        axis.set_major_locator(ticker.FixedLocator(date_num))
        axis.set_major_formatter(mdates.DateFormatter('%V'))
        axis.set_minor_locator(mdates.MonthLocator())
        axis.set_minor_formatter(mdates.DateFormatter('%b'))
        ax.tick_params(axis=which, which='minor', labeltop=True, labelbottom=False)
        if which == 'y':
            ax.tick_params(axis=which, which='minor', labelright=True, labelleft=False)
        ax.grid(b=True, which='major', color='w')
        ax.grid(b=True, which='minor', color='w', linestyle='--')
    elif level == 2:
        # month in bottom
        axis.set_major_locator(ticker.FixedLocator(date_num))
        axis.set_major_formatter(mdates.DateFormatter('%b'))


def time_formatter(y, pos):
    """Format the axis time labels.
    :param y: (list) list of values of y axis.
    :param pos: position of tick
    """
    if y >= SEC_DAY and pos:
        y = y % SEC_DAY if y != SEC_DAY else 0
    tick = '{:0>2}:{:0>2}'.format(int(y / SEC_HOUR), int((y % SEC_HOUR) / 60))
    return tick


def format_time(ax, y_ax):
    """
    Format the time ticks in y axis into hour and half hour.
    :param ax: (axis) y axis.
    :param y_ax: (list) list of value of y axis.
    :return: (axis)
    """
    ymax, ymin = y_ax.max(), y_ax.min()
    major_ticks = range(int(ymin - (ymin % SEC_HOUR)), int(ymax + SEC_HOUR), int(SEC_HOUR))
    minor_ticks = range(int(major_ticks[0] + SEC_HOUR / 2), major_ticks[-1] - 1, int(SEC_HOUR))
    ax.yaxis.set_minor_locator(ticker.FixedLocator(minor_ticks))
    ax.yaxis.set_major_locator(ticker.FixedLocator(major_ticks))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
