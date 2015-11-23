"""Main module to combine functions into complete services"""

from db import *
from time_api import *
from note import *
from plot_func import *
import argparse


def update_db():
    """Insert last two days' entries in aTimeLogger into database."""
    mysql_switch(1)
    time_token = get_time_token()
    new_entries = get_new_intervals(time_token)
    insert_intervals(new_entries)
    mysql_switch(0)
    print "Update complete!"


def rebuild_table(table):
    """
    Empty all entries in passed table and reinsert current data into table.
    This function is used when history or types are edited.
    :param table: A string of table name in database, 'types' or 'intervals'
    """
    empty_db(table)
    mysql_switch(1)
    time_token = get_time_token()
    echo = 'Please correct your table name!'
    if table == 'types':
        types = get_types(time_token)
        insert_types(types)
        echo = "Rebuild types complete!"
    elif table == 'intervals':
        intervals = get_all_intervals(time_token)
        insert_types(intervals)
        echo = "Rebuild intervals complete!"
    mysql_switch(0)
    print echo


def rebuild_db(op='truncate'):
    """
    Rebuild the whole database.
    :param op: the option when empty the database, 'truncate' (default) or 'drop'
    """
    mysql_switch(1)
    if op == 'truncate':
        empty_db()
    else:
        empty_db(op)
        create_all_tables()
    time_token = get_time_token()
    types = get_types(time_token)
    intervals = get_all_intervals(time_token)
    insert_all(types, intervals)
    mysql_switch(0)
    print "Rebuild database complete!"


def daily_report(date=None):
    """
    Generate daily report in Evernote.
    Report content: 1.Date info, 2.Sleep table, 3.Group pie chart, 4.Task table.
    :param date: A string of date in the format 'YYYYMMDD', default None for yesterday.
    """
    mysql_switch(1)
    if date:
        start, end = str2level_range(date, 0)
        date_info = day_info(date)
    else:
        start, end = human_qr('last 1 days')
        date_info = day_info()
    title = ts2str_level(start, 0)
    sleep_table_plot(sleep_compare(date))
    last_cut = get_cut_level_dataframe(start, end, 0)
    group_pie_plot(last_cut)
    task_data = get_task_table(last_cut)

    dev_token, note_store = connect_note()

    # in case of early date with zero task
    if task_data.shape[0] != 0:
        task_table_plot(task_data)
        resources = create_resources(['img/sleep_table.png', 'img/group_pie.png', 'img/task_table.png'])
        headings = ['1. Good Morning!', '2. What\'s up?', '3. How are things going?']
        widths = [500, None, None]
    else:
        resources = create_resources(['img/sleep_table.png', 'img/group_pie.png'])
        headings = ['1. Good Morning!', '2. What\'s up?']
        widths = [500, None]
    # create_daily_note(dev_token, note_store, title, date_info, resources, headings, widths)
    create_note(dev_token, note_store, 0, title, resources, headings, widths, date_info)
    mysql_switch(0)
    print "Generate daily report for {0}!".format(title)


def weekly_report(week=None):
    """
    Generate weekly report in Evernote.
    Report content: 1.Group pie chart, 2.Type table, 3.Group stacked bar chart, 4. Type grid chart, 5. Sleep plot.
    :param week: A string of week number in the format 'YYYYWww', e.g '2015W07'. Default None for last week.
    """
    mysql_switch(1)
    if week:
        start, end = str2level_range(week, 1)
    else:
        start, end = human_qr('last 1 week')
    start_date = ts2datetime(start).strftime('%b %d')
    end_date = ts2datetime(end).strftime('%b %d')
    title = ts2datetime(start).strftime("%Y Week%V ({0} - {1})".format(start_date, end_date))

    cut_data = get_cut_dataframe(start, end)
    group_pie_plot(cut_data)
    type_data = get_type_detail(cut_data)
    type_table_plot(type_data)
    agg_data_group = agg_level(start, end, 'group', 0)
    group_barh_plot(agg_data_group, 0)
    agg_data_type = agg_level(start, end, 'type', 0)
    type_bar_grid_plot(agg_data_type, 0)
    sleep_data = get_sleep_dataframe(start, end)
    sleep_plot(sleep_data)

    dev_token, note_store = connect_note()
    resources = create_resources(['img/group_pie.png', 'img/type_table.png', 'img/group_bar.png',
                                  'img/type_bar_grid.png', 'img/sleep_plot.png'])
    headings = ['1. Group Overview', '2. Type Detail', '3. Group Trends', '4. Type Trends', '5. Sleep Trends']
    widths = [None] * 5
    # create_weekly_note(dev_token, note_store, title, resources, headings, widths)
    create_note(dev_token, note_store, 1, title, resources, headings, widths)
    mysql_switch(0)
    print "Generate weekly report for {0}!".format(title)


def monthly_report(month=None):
    """
    Generate monthly report in Evernote.
    Report content: 1.Group pie chart, 2.Type table, 3.Group stacked bar chart, 4. Type grid chart, 5. Sleep plot.
    :param month: A string of month number in the format 'YYYYMmm', e.g '2015M02'. Default None for last month.
    """
    mysql_switch(1)
    if month:
        start, end = str2level_range(month, 2)
    else:
        start, end = human_qr('last 1 month')
    title = ts2datetime(start).strftime("%Y Month%m")

    cut_data = get_cut_dataframe(start, end)
    group_pie_plot(cut_data)
    type_data = get_type_detail(cut_data)
    type_table_plot(type_data)
    agg_data_group = agg_level(start, end, 'group', 1)
    group_barh_plot(agg_data_group, 1)
    agg_data_type = agg_level(start, end, 'type', 1)
    type_bar_grid_plot(agg_data_type, 1)
    sleep_data = get_sleep_dataframe(start, end)
    sleep_plot(sleep_data)

    dev_token, note_store = connect_note()
    resources = create_resources(['img/group_pie.png', 'img/type_table.png', 'img/group_bar.png',
                                  'img/type_bar_grid.png', 'img/sleep_plot.png'])
    headings = ['1. Group Overview', '3. Type Detail', '2. Group Trends', '4. Type Trends', '5. Sleep Trends']
    widths = [None] * 5
    create_note(dev_token, note_store, 2, title, resources, headings, widths)
    mysql_switch(0)
    print "Generate monthly report for {0}!".format(title)


def gen_report(level=0, date=None):
    """
    Report wrapper function.
    :param level: An integer for different time levels. 0: daily (default), 1: weekly, 2: monthly.
    :param date: A string to specify date/week/month.
    """
    if level == 0:
        daily_report(date)
    elif level == 1:
        weekly_report(date)
    elif level == 2:
        monthly_report(date)


def test_func():
    """Test function"""
    mysql_switch(1)
    start, end = human_qr('last 1 week')
    # cut_data = get_cut_dataframe(start, end)
    # group_pie_plot(cut_data)
    # day_cut_data = get_cut_day_dataframe(start, end)
    # agg_data = agg_level(start, end, 'type', 0)
    # types = get_type_order('Health').type
    # agg_line_plot(agg_data, 'type', 0, lst=types, smooth=False)
    # sleep_data = get_sleep_dataframe(start, end)
    # sleep_plot(sleep_data)
    # agg_data = agg_level(start, end, 'group', 0)
    # group_barh_plot(agg_data, 0)
    agg_data = agg_level(start, end, 'type', 0)
    type_bar_grid_plot(agg_data, 0)
    mysql_switch(0)


def main():
    # Add argument to program for more flexible console control
    parser = argparse.ArgumentParser(description='Report system actions.')
    parser.add_argument("-o", "--operation", choices=['re', 'db'], default='re', help="choose operation (default: re)")
    parser.add_argument("-u", "--update", type=int, choices=[0, 1], help="update or rebuild db")
    parser.add_argument("-l", "--level", type=int, default=0, choices=[0, 1, 2],
                        help="choose the report level (default: 0)")
    parser.add_argument("-d", "--date", help="Specify date/week/month for report. "
                                             "Day: '19970215'; Week: '1999W05'; Year: '2010M02'")
    args = parser.parse_args()
    if args.operation == 're':
        update_db()
        gen_report(args.level, args.date)
    else:
        if args.update == 0:
            update_db()
        else:
            rebuild_db()


if __name__ == '__main__':
    main()
    # test_func()
