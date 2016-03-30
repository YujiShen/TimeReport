"""This module are functions to analyze data for plots or tables."""
from getdata import *

AGG_DICT = {'Sum': 'sum', 'Num': 'count', 'Std': 'std', 'Avg': 'mean', 'Min': 'min', 'Max': 'max', 'Median': 'median'}


def sleep_compare(base_day=None, range_days=7):
    """
    Analyze summary of today's sleep data and compared with previous days'
    :param base_day: a date string for comparison
    :param range_days: time range of previous days
    """
    if base_day is not None:
        end = str2datetime(base_day).replace(days=1).timestamp
        start = ts2datetime(end).replace(days=-range_days).timestamp
    else:
        sentence = 'this {0} days'.format(range_days)
        start, end = human_qr(sentence)
    dataframe = pd.DataFrame(index=['Bed Time', 'Up Time', 'Length'],
                             columns=['Today', 'v.s Yesterday', 'In {0} days'.format(range_days)])
    entries = get_sleep_data(start, end)
    data = pd.DataFrame(entries, columns=['from', 'to', 'delta'])

    # If base day and the date of last entry is not the same day
    # We do no have the data on base day
    if (base_day is not None) and (base_day != ts2str_level(data['to'].values[-1], 0)):
        print base_day
        return 'No data yet.'

    bed, last_bed = ts2str_hm(data['from'].values[-1]), ts2str_hm(data['from'].values[-2])
    dataframe.ix['Bed Time', 'Today'] = bed
    getup, last_getup = ts2str_hm(data['to'].values[-1]), ts2str_hm(data['to'].values[-2])
    dataframe.ix['Up Time', 'Today'] = getup
    bed_delta = sec2str(ts_cross_day(data['from'].values[-1]) - ts_cross_day(data['from'].values[-2]), True)
    getup_delta = sec2str(ts_cross_day(data['to'].values[-1]) - ts_cross_day(data['to'].values[-2]), True)
    dataframe.ix['Bed Time', 'v.s Yesterday'], dataframe.ix['Up Time', 'v.s Yesterday'] = bed_delta, getup_delta

    entry = data.iloc[-1, ]
    entry_str = sec2str(entry['delta'])
    last_entry = data.iloc[-2, ]
    delta = entry['delta'] - last_entry['delta']
    delta_str = sec2str(delta, True)
    dataframe.ix['Length', 'Today'], dataframe.ix['Length', 'v.s Yesterday'] = entry_str, delta_str

    len_rank = "#" + str(int(data.rank().delta.values[-1]))
    bed_rank = "#" + str(int(data['from'].map(lambda x: ts_cross_day(x)).rank().values[-1]))
    getup_rank = "#" + str(int(data['to'].map(lambda x: ts_cross_day(x)).rank().values[-1]))
    dataframe['In {0} days'.format(range_days)] = [bed_rank, getup_rank, len_rank]
    return dataframe


def get_pie_data(cut_data):
    """Provide percentage and average information of group and types for pie chart.
    :param cut_data: dataframe cut with start and end
    """
    num_date = len(cut_data.to.map(ts2date).unique()) - 1
    total_delta = cut_data.delta.sum()
    table = cut_data[['delta', 'group', 'type']].groupby(['group', 'type']).aggregate(np.sum)
    table_group = cut_data[['delta', 'group']].groupby(['group']).aggregate(np.sum)
    table_group = table_group.reset_index()
    table_group['type'] = '_Total'
    table = table.reset_index()
    table = pd.concat([table, table_group])
    table.sort_values(by=['group', 'delta'], inplace=True)
    table['pct'] = table.delta/total_delta
    table['pctStr'] = table['pct'].map(lambda x: str(round(x*100, 1)) + '%')
    table['rPct'] = table.apply(lambda x:
                                x['delta']*1.0/table_group.ix[table_group.group == x['group'], 'delta'].item(), axis=1)
    table['rPctStr'] = table['rPct'].map(lambda x: str(round(x*100, 1)) + '%')
    table['deltaStr'] = table['delta'].map(sec2str)
    table['avg'] = table['delta'].map(lambda x: sec2str(x * 1.0 / num_date))
    return table


def get_type_detail(data):
    """
    Aggregate data for each type to calculate its percentage and other statistics for type detailed table.
    :param data: (dataframe) cut data
    :return: (dataframe)
    """
    types = get_all_types()
    # Not using start, end in case of end have not happened yet
    days = len(get_datelist(data['from'].values[0], data.to.values[-1], 0))
    result = data.groupby(['group', 'type'])['delta'].agg(AGG_DICT)

    total_data = data.groupby('group')['delta'].agg(np.sum)
    total = data.delta.sum()
    result = result.reset_index()
    result = result.merge(types, on='type')
    result.sort_values(by=['order', 'Sum'], ascending=[True, False], inplace=True)
    result.fillna(value=0, inplace=True)

    result['In Pct'] = result.apply(lambda x: str(round(x['Sum']*100./total_data[x['group']], 1))+'%', axis=1)
    result['Pct'] = result.apply(lambda x: str(round(x['Sum']*100./total, 1))+'%', axis=1)
    result['Day Avg'] = result.apply(lambda x: x['Sum']*1./days, axis=1)
    result = result[['group', 'type', 'Pct', 'In Pct', 'Num', 'Sum', 'Avg', 'Day Avg', 'Std', 'Median', 'Min', 'Max']]
    result.ix[:, 5:] = result.ix[:, 5:].applymap(sec2str)

    result.rename(columns={'group': 'Group', 'type': 'Type', 'Num': 'Int', 'Avg': 'Int Avg'}, inplace=True)
    return result


def get_task_table(cut_data):
    """Aggregate data based on comments.
    :param cut_data: dataframe cut with start and end
    """
    data = cut_data.copy()
    result = data.ix[:, ('comment', 'type', 'group', 'delta')]
    result = result.groupby(['comment', 'type', 'group'])['delta'].agg(AGG_DICT)
    result.sort_values(by=['Sum'], inplace=True, ascending=False)
    result.fillna(value=0, inplace=True)
    result = result.reset_index()
    result.rename(columns={'comment': 'Task', 'type': 'Type', 'group': 'Group'}, inplace=True)
    result = result[['Group', 'Type', 'Task', 'Num', 'Sum', 'Avg', 'Std', 'Median', 'Min', 'Max']]
    result.ix[:, 4:] = result.ix[:, 4:].applymap(sec2str)
    return result


# TODO use OOD to combine data and plot into same class

def agg_level(start, end, cate, level, lst=None):
    """
    Aggregate and calculate descriptive statistics of data according to time frame.
    :param start: (int) unix timestamp.
    :param end: (int) unix timestamp.
    :param cate: (str) 'group' or 'type'.
    :param level: (int) time frame number.
    :param lst: (list) a list of group or type names.
    :return: (dataframe)
    """
    data = get_cut_level_dataframe(start, end, level)
    if lst is None:
        if cate == 'type':
            lst = data.type.unique()
        else:
            lst = data.group.unique()
    date_ind = ([start] + break_level(start, end, level))
    date_ind = map(lambda x: ts2str_level(x, level), date_ind)
    iterable = [date_ind, lst]
    multi_ind = pd.MultiIndex.from_product(iterable)
    data = data[['date_agg', cate, 'delta']].groupby(['date_agg', cate])['delta'].agg(AGG_DICT)
    # ind = data.index
    # data.index = pd.MultiIndex.from_tuples(ind.values)
    data = data.reindex(multi_ind, columns=['Num', 'Sum', 'Avg', 'Std', 'Median', 'Min', 'Max'], fill_value=0)
    data.index.names = ['date', cate]
    data = data.reset_index()
    data = data[['date', cate, 'Num', 'Sum', 'Avg', 'Std', 'Median', 'Min', 'Max']]
    data.fillna(value=0, inplace=True)
    return data
