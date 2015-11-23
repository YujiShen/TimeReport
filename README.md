## Time Report
Integrate time tracking app [aTimeLogger](http://www.atimelogger.com), note taking app [Evernote](https://evernote.com) and Mac productivity app [Alfred](https://www.alfredapp.com) to easily generate self time analysis report.

### Introduction
#### Stage
Early. In latest update, transform developing environment from Jupyter Notebook to PyCharm. Making it more like a program.

#### Target User
It is highly customized, so currently only myself.

#### Know Issue
* __Design__: This program is full of functions, without Object-Oriented Design. Next step is to learn and practice how to design this program in OOD.
* __Edit__: The whole database is based on data in aTimeLogger. Changes in local database will not affect remote data, and each time I change historical entries or types settings in aTimeLogger, I have to rebuild my local database.
* __Depth__: The analysis stays on descriptive level, need to dig deeper for more useful and hidden relations.

#### Goal
My final goal is to build a webapp to replace aTimeLogger as my customized time tracking tool, for more flexibility to edit data and better integration with task management system. But this will not happen very soon, both my knowledge and time are not enough.

### Basic Flow
After retrieving all history data from aTimeLogger, building MySQL database, for each day/week/month, simply use Alfred to choose an action:
![Alfred Workflow](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/workflow.png)
Underlying procedures:

1. Get new data from aTimeLogger API, update database.
2. Utilize pandas, numpy to transform, aggregate, analyze data according to different time frame.
3. Draw plots and tables in matplotlib, save in files. See 'Gallery' for examples.
4. Create note via Evernote API, add images and headings, push to my Evernote account.

### Gallery
#### Sleep Comparison Table
![Sleep Comparison Table](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/sleep_table.png)
Compare today's sleep status with yesterday, and its rank in last 7 days. Usually used in daily report.

#### Task Table
![Task Table](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/task_table.png)
I use 'Comment' filed in aTimeLogger as Task or some activity I want to highlight, then aggregate its statistics everyday for morning review.

#### Sleep Analysis
![Sleep Analysis](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/sleep_plot.png)
Analyze sleep conditions for weekly or monthly review. Inspired by app [Sleep Cycle](http://www.sleepcycle.com/start.html). In this picture (monthly report), X axis bottom is week number, top is month abbreviation.

#### Group Pie Chart
![Group Pie Chart](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/group_pie.png)
Pie chart for each group to see total conditions. Mimic the pie chart in aTimeLogger, but add Average statistic.

#### Type Descriptive Table
![Type Descriptive Table](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_table.png)
Type detailed table replicate the 'Detail' function in aTimeLogger with a lot more statistics.

#### Group Stacked Bar Chart
![Group Stacked Bar Chart](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/group_bar.png)
Stacked bar chart (horizontal) to see group trends inside a month or a week. Numbers in bar represents its percentage.

#### Type Grid Stacked Bar Chart
![Type Grid Stacked Bar Chart](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_bar_grid.png)
This 3x3 grid stacked bar chart (horizontal) to get the trends of each types in given time frame. Numbers in bar represents its hours.

#### Aggregation Line Plot
![Aggregation Line Plot](https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_line.png)
A flexible plot to compare given types or groups in line plot.