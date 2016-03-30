"""Alfred workflow script filter to generate desire XML"""


query = "{query}"
xml = "<items>"
cmd = "cd /Users/Yuji/Workspace/Python/TimeReport &amp;&amp; python test.py"
cmd_update = "cd /Users/Yuji/Workspace/Python/TimeReport &amp;&amp; python test.py -o db -u 0"
cmd_rebuild = "cd /Users/Yuji/Workspace/Python/TimeReport &amp;&amp; python test.py -o db -u 1"

if query:
    cmd_day = "{0} -d {1}".format(cmd, query)
    cmd_week = "{0} -l 1 -d {1}".format(cmd, query)
    cmd_month = "{0} -l 2 -d {1}".format(cmd, query)
else:
    cmd_day = cmd
    cmd_week = "{0} -l 1".format(cmd)
    cmd_month = "{0} -l 2".format(cmd)

day = """<item uid="day" arg="{0}" valid="YES" autocomplete="Daily Report">
    <title>Daily Report</title>
    <subtitle>Default: Yesterday. --DATE, e.g. 20151011</subtitle>
    <icon>day.png</icon>
  </item>""".format(cmd_day)
xml += day

week = """<item uid="week" arg="{0}" valid="YES" autocomplete="Weekly Report">
    <title>Weekly Report</title>
    <subtitle>Default: This week. --WEEK, e.g. 2015W05</subtitle>
    <icon>week.png</icon>
  </item>""".format(cmd_week)
xml += week

month = """<item uid="month" arg="{0}" valid="YES" autocomplete="Monthly Report">
    <title>Monthly Report</title>
    <subtitle>Default: This month. --MONTH, e.g. 2015M01</subtitle>
    <icon>month.png</icon>
  </item>""".format(cmd_month)
xml += month

update = """<item uid="update" arg="{0}" valid="YES" autocomplete="Update Database">
    <title>Update Database</title>
    <subtitle>Insert new entries into database</subtitle>
    <icon>db_update.png</icon>
  </item>""".format(cmd_update)
xml += update

rebuild = """<item uid="rebuild" arg="{0}" valid="YES" autocomplete="Rebuild Database">
    <title>Rebuild Database</title>
    <subtitle>Empty database and reinsert all data</subtitle>
    <icon>db_rebuild.png</icon>
  </item>""".format(cmd_rebuild)
xml += rebuild

xml += "</items>"

print xml
