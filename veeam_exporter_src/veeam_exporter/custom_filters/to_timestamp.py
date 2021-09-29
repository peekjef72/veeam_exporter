import sys,re

import datetime, dateutil.parser, dateutil.relativedelta

Filter = None
if 'Filter' in sys.modules:
   Filter = sys.modules['Filter']
elif 'filters' in sys.modules:
   Filter = sys.modules['filters'].Filter
elif 'veeam_exporter.filters' in sys.modules:
   Filter = sys.modules['veeam_exporter.filters'].Filter

if Filter is None:
   raise Exception('Filter module not loaded.')

#************************************************************************
class ToTimestampFilter(Filter):

   #********************************
   def filter(self, time_str):

      now = datetime.datetime.now()
      ts = None

      if time_str is None:
         time_str = now

      if type(time_str) is datetime.datetime:
         ts = int(time_str.timestamp())
      elif type(time_str) is int:
         # it must be an unix timestamp
         ts = time_str
      elif type(time_str) is str:
         found = False
         pattern = re.compile(r'^now(?:-(\d+)([dhmMyw]))?$')
         for m in re.finditer(pattern, time_str):
            factor = 0
            ts = now
            if m.group(1) and m.group(2):
               val = int(m.group(1))
               if m.group(2) == 'm':
                  dt = dateutil.relativedelta.relativedelta(minutes=val)
               elif m.group(2) == 'h':
                  dt = dateutil.relativedelta.relativedelta(hours=val)
               elif m.group(2) == 'd':
                  dt = dateutil.relativedelta.relativedelta(days=val)
               elif m.group(2) == 'w':
                  dt = dateutil.relativedelta.relativedelta(weeks=val)
               elif m.group(2) == 'M':
                  dt = dateutil.relativedelta.relativedelta(months=val)
               elif m.group(2) == 'y':
                  dt = dateutil.relativedelta.relativedelta(years=val)
               ts = ts - dt
            ts = int( ts.timestamp() )
            found = True
         if not found:
            time_str = dateutil.parser.parse(time_str)
            ts = int(time_str.timestamp())
      else:
         time_str = now
         ts = int(time_str.timestamp())

#    print('get_time(\'{0}\') = {1}'.format(time_str, ts) )
      return ts

