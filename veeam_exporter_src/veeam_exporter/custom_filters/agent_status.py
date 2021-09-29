import sys

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
class BackupAgentStatusFilter(Filter):

   #********************************
   def filter(self, value):
      if value is None or not isinstance(value, str):
         return value

      if value == "Online":
         value = 1

      elif value == "Offline":
         value = 2

      elif value == "Unknown":
         value = 0

      return value
