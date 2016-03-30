
import statsmodels.api as sm
from matplotlib.table import Table
import seaborn as sns
import itertools
from analysis import *
from plot_help import *

plt.ioff()


def sleep_len_plot(ax, data, plot='line', smooth=True):
    """
    Plot the sleep data based on uncut entries with Lowess smoothing.
    :param ax: figure axis.
    :param data: (dataframe) sleep data.
    :param plot: (str) 'line' default or 'bar'.
    :param smooth: (bool) use Lowess smoothing or not.
    :return: (axis)
    """
    x_ax = list(data.date)
    y = data['delta'].map(lambda x: x / SEC_HOUR)
    y_median = np.median(np.array(y))
    if smooth:
        lowess = sm.nonparametric.lowess(y, range(len(x_ax)), frac=1 / len(data) ** 0.5)
        y = lowess[:, 1]
    # fig, ax = plt.subplots(1, figsize=(12, 3))
    if plot == 'bar':
        ax.bar(x_ax, y, width=1, align='center')
    else:
        ax.plot(x_ax, y, linewidth=2.5)
        ax.axhline(y_median, linestyle='--', zorder=1)
    format_date(ax, x_ax, 0)
    ax.grid(b=True, which='minor', linestyle='--', linewidth=1.5)
    ax.grid(b=True, which='major', linestyle='-', linewidth=1.5)
    ax.tick_params(axis='both', which='both', labelsize=12)
    ax.set_title("Time in bed", fontdict={"fontsize": 14, "fontweight": 'bold'}, y=1.06)
    return ax
    # fig.savefig('img/sleep_{0}'.format(plot), bbox_inches='tight', dpi=200)


def sleep_time_plot(ax, data, bed=True, smooth=True):
    """
    Plot the sleep bed or wake up time based on uncut entries with Lowess smoothing.
    :param ax: figure axis.
    :param data: (dataframe) sleep data.
    :param bed: (bool) True default for bed time, False for woke up time.
    :param smooth: (bool) use Lowess smoothing or not.
    :return: (axis)
    """
    x_ax = list(data.date)
    if bed:
        y = data['from'].map(ts_cross_day)
        title = 'Went to bed'
    else:
        y = data['to'].map(ts_cross_day)
        title = 'Woke up'
    y_median = np.median(np.array(y))
    if smooth:
        lowess = sm.nonparametric.lowess(y, range(len(x_ax)), frac=1 / len(data) ** 0.5)
        y = lowess[:, 1]
    # fig, ax = plt.subplots(1, figsize=(12, 3))
    ax.plot(x_ax, y, linewidth=2.5)
    ax.axhline(y_median, linestyle='--', zorder=1)
    format_time(ax, y)
    format_date(ax, x_ax, 0)
    ax.grid(b=True, which='minor', linestyle='--', linewidth=1.5)
    ax.grid(b=True, which='major', linestyle='-', linewidth=1.5)
    ax.tick_params(axis='both', which='both', labelsize=12)
    ax.set_title(title, fontdict={"fontsize": 14, "fontweight": 'bold'}, y=1.06)
    return ax
    # fig.savefig('img/sleep_time_{0}'.format(suffix), bbox_inches='tight', dpi=200)


def sleep_plot(data, smooth=False):
    """
    Plot the sleep time and sleep length, save in png file.
    :param data: (dataframe) sleep data.
    :param smooth: (bool) use Lowess smoothing or not.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1)
    sleep_time_plot(ax1, data, smooth=smooth)
    sleep_len_plot(ax2, data, smooth=smooth)
    sleep_time_plot(ax3, data, bed=False, smooth=smooth)
    fig.set_tight_layout(True)
    fig.savefig('img/sleep_plot', bbox_inches='tight', dpi=200)


def group_pie_plot(data):
    """
    Plot pie chart of data aggregated by groups, save in png file.
    :param data: (dataframe) cut data.
    """
    pie_data = get_pie_data(data)
    pie_data = pie_data[(pie_data['type'] == '_Total')]
    pie_data.sort_values(by='delta', inplace=True, ascending=False)
    pie_data['label'] = pie_data.apply(
        lambda row: '%s\n%s' % (row['group'], row['pctStr']) if row['pct'] > 0.05 else "", axis=1)

    palette = get_palette()
    color = [palette[x] for x in pie_data.group]
    # explode = (1 - pie_data['pct']) ** 15 / 10

    fig, axs = plt.subplots(1, 2, figsize=(14, 7))
    ax, ax1 = axs
    ax1.axis('off')
    wedges, texts = ax.pie(pie_data.delta, startangle=270, colors=color,
                           counterclock=False, labels=pie_data.label, labeldistance=0.6,
                           wedgeprops={'edgecolor': None, 'linewidth': 1.5},
                           textprops={'color': 'white'}, radius=1.2)

    for t, pct in zip(texts, pie_data.pct):
        t.set_size(pct ** 0.5 * 40)
        t.set_horizontalalignment('center')
        t.set_weight('bold')
    for w, c in zip(wedges, color):
        w.set_edgecolor(c)

    pie_table = pie_data[['group', 'pctStr', 'deltaStr', 'avg']]
    tbl = ax1.table(cellText=pie_table.as_matrix(),
                    cellLoc='center',
                    colWidths=[0.15, 0.2, 0.3, 0.25],
                    colLabels=['Group', 'Pct', 'Duration', 'Avg'],
                    loc='center')

    nrow, ncol = pie_table.shape
    nrow += 1
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(20)
    cell_dict = tbl.get_celld()

    for i, j in itertools.product(range(nrow), range(ncol)):
        cell = cell_dict[(i, j)]
        cell.set_height(0.09)
        cell.set_edgecolor('gray')
        cell.set_linewidth(1)
        text = cell_dict[(i, j)].get_text()
        text.set_family('DINPro')
        text.set_weight('medium')
        if i == 0:
            cell.set_height(0.07)
            text.set_weight('bold')
            text.set_color('white')
            cell.set_facecolor('gray')
            text.set_family('Verdana')
            text.set_fontsize(13)
        if j == 0 < i:
            cell.set_facecolor(color[i - 1])
            cell.set_edgecolor(color[i - 1])
            text.set_family('Verdana')
            text.set_color('white')
            text.set_weight('bold')
            text.set_fontsize(13)

    fig.subplots_adjust(left=0, bottom=0, right=1, top=1,
                        wspace=0, hspace=0)
    fig.savefig('img/group_pie', dpi=200)


def agg_line_plot(agg_data, cate, level, fmla='Sum',
                  lst=None, smooth=True, end=None):
    """
    Plot aggregated line plot for groups or types, save in png file.
    :param agg_data: (dataframe) aggregated data according to time frame.
    :param cate: (str) 'group' or 'type'.
    :param level: (int) time frame number.
    :param fmla: (str) name of statistics in AGG_DICT.
    :param lst: (list) name of types or groups
    :param smooth: (bool) use Lowess smoothing or not.
    :param end: use when end is not correct for higher levels.
    """
    start = str2level_range(agg_data['date'].values[0], level)[0]
    if end is None:
        end = str2level_range(agg_data['date'].values[-1], level)[1]
    if lst is None:
        if cate == 'type':
            lst = agg_data.type.unique()
        else:
            lst = agg_data.group.unique()
    fig, ax = plt.subplots(1, figsize=(15, 5))
    x_ax = get_datelist(start, end, level)

    np.random.shuffle(PALETTE_12)
    colors = sns.color_palette(PALETTE_12)

    for ind, item in enumerate(lst):
        data = agg_data[agg_data[cate] == item]
        if fmla == 'Day Avg':
            y = data['Sum'].map(lambda value: value / SEC_HOUR)
            days_list = get_days_of_month(start, end)
            y = y / days_list
        elif fmla == 'Num':
            y = data['Num']
        else:
            y = data[fmla].map(lambda value: value / SEC_HOUR)
        if smooth:
            x = np.arange(len(y))
            lowess = sm.nonparametric.lowess(y, x, frac=1 / data.shape[0] ** 0.5)
            y = lowess[:, 1]
        color = colors[ind]
        ax.plot(x_ax, y, label=item, color=color, linewidth=2.5)

    format_date(ax, x_ax, level)
    ax.legend(loc='best', prop={'size': 13, 'weight': 'bold'})
    fig.savefig('agg_line', bbox_inches='tight', dpi=200)


def group_barh_plot(agg_data, level):
    """
    Horizontal group bar plot, with percentage in the bar.
    :param agg_data: aggregated group data.
    :param level: time frame number.
    """
    start = str2level_range(agg_data['date'].values[0], level)[0]
    end = str2level_range(agg_data['date'].values[-1], level)[1]
    data = agg_data.merge(get_group_order())
    x_ax = get_datelist(start, end, level)
    agg_total = data[['date', 'Sum']].groupby('date').aggregate(np.sum)
    groups = data.sort_values(by=['order']).group.unique()

    fig, ax = plt.subplots(1, figsize=(15, 5))
    palette = get_palette()
    bottom = np.zeros(len(x_ax))
    width = bar_width(level)
    patch_handles = []
    pct = []
    for group in groups:
        bar_data = data[data.group == group].copy()
        pct.append(bar_data['Sum'].values * 100. / agg_total['Sum'].values)
        bar_data['pct'] = pct[-1]
        patch_handles.append(ax.barh(x_ax, bar_data['pct'], left=bottom, height=width,
                                     align='center', label=group, edgecolor=palette[group],
                                     color=palette[group]))
        bottom += bar_data.pct
    pct = np.array(pct).reshape(len(groups), len(x_ax))
    ax.invert_yaxis()
    # go through all of the bar segments and annotate
    for j in xrange(len(patch_handles)):
        for i, patch in enumerate(patch_handles[j].get_children()):
            # if the bar is higher than 5%, add text on it
            if pct[j, i] > 5:
                bl = patch.get_xy()
                x = 0.5 * patch.get_width() + bl[0]
                y = 0.5 * patch.get_height() + bl[1]
                t = ax.text(x, y, "%d" % (pct[j, i]), color='w', ha='center', va='center')
                t.set_weight('bold')
    format_date(ax, x_ax, level, which='y')
    ax.set_xlim((0, 100))
    x_major_ticks = range(0, 101, 10)
    ax.xaxis.set_major_locator(ticker.FixedLocator(x_major_ticks))
    ax.tick_params(axis='x', which='major', labeltop=True, labelbottom=False)
    ax.tick_params(axis='both', which='both', labelsize=12)
    ax.legend(loc='lower left', bbox_to_anchor=(-0.01, -0.15),
              handletextpad=0.2, ncol=9, prop={'size': 13, 'weight': 'bold'})
    fig.savefig('img/group_bar', bbox_inches='tight', dpi=200)


def type_barh_plot(ax, data, group, level):
    """
    Plot horizontal bar plot for given group's types, return axis.
    :param ax: axis to plot.
    :param data: aggregated type data.
    :param group: group name for title.
    :param level: time frame number.
    """
    start = str2level_range(data['date'].values[0], level)[0]
    end = str2level_range(data['date'].values[-1], level)[1]
    x_ax = get_datelist(start, end, level)
    types = data.sort_values(by=['order']).type.unique()
    palette = get_palette()
    # fig, ax = plt.subplots(1, figsize=(15, 5))
    bottom = np.zeros(len(x_ax))
    width = bar_width(level)
    patch_handles = []
    pct = []
    for ind, tpy in enumerate(types):
        bar_data = data[data.type == tpy].copy()
        # noinspection PyTypeChecker
        if all(bar_data['Sum'] == 0):
            pct.append([0.0]*len(x_ax))
            continue
        pct.append(bar_data['Sum'].values / SEC_HOUR)
        bar_data['bar'] = pct[-1]
        patch_handles.append(ax.barh(x_ax, bar_data.bar, height=width, align='center',
                             left=bottom, label=tpy, edgecolor=palette[tpy], color=palette[tpy]))
        bottom += bar_data.bar
    tallest_bar = max(bottom)
    pct = np.array(pct).reshape(len(types), len(x_ax))
    ax.invert_yaxis()
    for j in xrange(len(patch_handles)):
        for i, patch in enumerate(patch_handles[j].get_children()):
            # if the bar is higher than 5% of highest bar, add text on it
            if pct[j, i]/tallest_bar > 0.05:
                bl = patch.get_xy()
                x = 0.5 * patch.get_width() + bl[0]
                y = 0.5 * patch.get_height() + bl[1]
                t = ax.text(x, y, "%.1f" % (pct[j, i]), color='w', ha='center', va='center')
                t.set_weight('bold')
    format_date(ax, x_ax, level, which='y')
    ax.tick_params(axis='both', which='both', labelsize=12)
    # ax.set_xlim(0, tallest_bar*1.05)
    ax.legend(loc='lower left', bbox_to_anchor=(-0.03, -0.23),
              prop={'size': 10, 'weight': 'bold'}, handletextpad=0.2, ncol=7)
    # ax.set_title(group, fontdict={'fontweight': 'bold', 'fontsize': 13})
    # fig.savefig('img/type_bar_{0}'.format(group), bbox_inches='tight', dpi=200)


def type_bar_grid_plot(data, level):
    """
    Plot a 3 by 3 bar plot grid for types of each groups, save in png file.
    :param data: cut dataframe.
    :param level: time frame number.
    """
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(27, 15))
    groups = get_group_order().sort_values(by=['order'])
    groups = groups.group.values
    for group, ax in zip(groups, axes.flat):
        type_order = get_type_order(group)
        type_data = data[data['type'].isin(type_order.type)].copy()
        if type_data.shape[0] == 0:
            ax.set_title(group, fontdict={'fontweight': 'bold', 'fontsize': 13})
        else:
            type_data = type_data.merge(type_order)
            type_barh_plot(ax, type_data, group, level)
    fig.subplots_adjust(wspace=0.1, hspace=0.4)
    fig.savefig('img/type_bar_grid', bbox_inches='tight', dpi=200)


def task_table_plot(task_data):
    """
    Plot task table, save in png file.
    :param task_data: dataframe from get_task_table().
    """
    groups = task_data.Group.values
    task_no_group = task_data.drop('Group', axis=1)
    nrows, ncols = task_no_group.shape
    width, height = 1.0 / ncols, 1.0 / nrows

    fig, ax = plt.subplots(figsize=(1, nrows*0.25))
    ax.set_axis_off()
    tbl = Table(ax)
    tbl.auto_set_font_size(False)
    # Columns width for non-auto-width columns
    col_widths = [1, 1, 0.5, 1, 0.7, 0.7, 0.7, 0.7, 0.7]
    palette = get_palette()
    fontcolor = 'w'
    for (i, j), val in np.ndenumerate(task_no_group):
        fc = palette[groups[i]]
        fontsize = 10
        if j < 2:
            loc = 'left'
            font_family = None
            if j == 0:
                fontsize = 9
        else:
            loc = 'center'
            font_family = 'DINPro'
            if j > 3:
                fontsize = 9
        tbl.add_cell(i, j, col_widths[j], height, text=val,
                     loc=loc, facecolor=fc, edgecolor=fontcolor)
        cell = tbl.get_celld()[(i, j)]
        cell.set_linewidth(0.5)
        cell.set_text_props(color=fontcolor, family=font_family, weight='bold', fontsize=fontsize)

    # Column Labels...
    for j, label in enumerate(task_no_group.columns):
        tbl.add_cell(-1, j, col_widths[j], height*0.8, text=label, loc='center',
                     facecolor='gray', edgecolor='w')
        cell = tbl.get_celld()[(-1, j)]
        cell.set_linewidth(0.5)
        cell.set_text_props(color=fontcolor, weight='bold', family='Verdana', fontsize=9)

    tbl._autoColumns = [0, 1]
    tbl.scale(1, 1.5)  # scale y to cover blank in the bottom
    ax.add_table(tbl)
    ax.margins(0, 0)
    fig.savefig('img/task_table', bbox_inches='tight', pad_inches=0.1, dpi=200)


def sleep_table_plot(data):
    """
    Plot sleep compare table, save in png file.
    :param data: dataframe from sleep_compare().
    """
    nrow, ncol = data.shape
    nrow += 1
    fig = plt.figure(figsize=(1, nrow*0.3))
    ax = fig.add_subplot(111)
    ax.axis('off')
    tbl = ax.table(cellText=data.as_matrix(),
                   colLabels=data.columns,
                   rowLabels=data.index,
                   colWidths=[2.5]*3,
                   cellLoc='center',
                   loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(16)

    cell_dict = tbl.get_celld()
    for i, j in itertools.product(range(nrow), [-1]+range(ncol)):
        if (i, j) != (0, -1):
            cell = cell_dict[(i, j)]
            text = cell_dict[(i, j)].get_text()
            cell.set_linewidth(1)
            cell.set_edgecolor('gray')
            text.set_family('DINPro')
            text.set_weight('medium')
            if i == 0:
                cell.set_facecolor('gray')
                cell.set_height(0.15)
                text.set_color('white')
                text.set_family('Verdana')
                text.set_weight('bold')
                text.set_fontsize(12)
            if j == -1:
                cell.set_facecolor('green')
                text.set_color('white')
                text.set_family('Verdana')
                text.set_weight('bold')
                text.set_fontsize(12)
    tbl.scale(1, 2.5)
    ax.margins(0, 0)
    fig.savefig('img/sleep_table', bbox_inches='tight', pad_inches=0.1, dpi=200)


def type_table_plot(type_data):
    """
    Plot type detail statistics table, save in png file.
    :param type_data: dataframe from get_type_detail().
    """
    groups = type_data.Group.values
    type_no_group = type_data.drop('Group', axis=1)
    nrows, ncols = type_no_group.shape
    width, height = 1.0 / ncols, 1.0 / nrows

    fig, ax = plt.subplots(figsize=(1, nrows*0.25))
    ax.set_axis_off()
    tbl = Table(ax)
    tbl.auto_set_font_size(False)
    # Columns width for non-auto-width columns
    # col_widths = [1, 1, 0.5, 1, 0.7, 0.7, 0.7, 0.7, 0.7]
    palette = get_palette()
    fontcolor = 'w'
    fontsize = 9
    for (i, j), val in np.ndenumerate(type_no_group):
        fc = palette[groups[i]]
        if j < 1:
            loc = 'left'
            font_family = None
        else:
            loc = 'center'
            font_family = 'DINPro'
        tbl.add_cell(i, j, width, height*0.7, text=val,
                     loc=loc, facecolor=fc, edgecolor=fontcolor)
        cell = tbl.get_celld()[(i, j)]
        cell.set_linewidth(0.5)
        cell.set_text_props(color=fontcolor, family=font_family, weight='bold', fontsize=fontsize)

    # Column Labels...
    for j, label in enumerate(type_no_group.columns):
        tbl.add_cell(-1, j, width, height*0.7, text=label, loc='center',
                     facecolor='gray', edgecolor='w')
        cell = tbl.get_celld()[(-1, j)]
        cell.set_linewidth(0.5)
        cell.set_text_props(color=fontcolor, weight='bold', family='Verdana', fontsize=9)

    tbl._autoColumns = range(ncols)
    tbl.scale(1, 1.55)  # scale y to cover blank in the bottom
    ax.add_table(tbl)
    ax.margins(0, 0)
    fig.savefig('img/type_table', bbox_inches='tight', pad_inches=0.1, dpi=200)
