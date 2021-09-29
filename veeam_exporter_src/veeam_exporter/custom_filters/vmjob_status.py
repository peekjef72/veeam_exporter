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
class JobStatusFilter(Filter):

   #********************************
#   def __init__(self):
#      super(BackupServerVersionFilter, self).__init__('backup_server')

   #********************************
   def filter(self, value):
      if value is None or not isinstance(value, str):
         return value
      # (0 undefined / 1 Succes / 2 In Progress / 3 Pending /4 Failed)
      if value == "Success":
         value = 1

      elif value == "Warning":
         value = 2

      elif value == "Failed":
         value = 3

      elif value == "Pending":
         value = 4  # synonym Idle

      elif value == "InProgress":
         value = 5  # synonnym Working

      else:
         value = 0

      return value
