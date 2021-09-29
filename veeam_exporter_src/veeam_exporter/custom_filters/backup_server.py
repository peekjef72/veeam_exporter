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
class BackupServerVersionFilter(Filter):

   #********************************
#   def __init__(self):
#      super(BackupServerVersionFilter, self).__init__('backup_server')

   #********************************
   def filter(self, value):
      if value is None or not isinstance(value, str):
         return value

      if value == "11.0.0.837":
         value = "11.0 GA"

      elif value == "11.0.0.825":
         value = "11.0 RTM"

      elif value == "10.0.1.4854":
         value = "10.0a GA"

      elif value == "10.0.1.4848":
         value = "10.0a RTM"

      elif value == "10.0.0.4461":
         value = "10.0 GA"

      elif value == "10.0.0.4442":
         value = "10.0 RTM"

      elif value == "9.5.4.2866":
         value = "9.5 U4b GA"

      elif value == "9.5.4.2753":
         value = "9.5 U4a GA"

      elif value == "9.5.4.2615":
         value = "9.5 U4 GA"

      elif value == "9.5.4.2399":
         value = "9.5 U4 RTM"

      elif value == "9.5.0.1922":
         value = "9.5 U3a"

      elif value == "9.5.0.1536":
         value = "9.5 U3"

      elif value == "9.5.0.1038":
         value = "9.5 U2"

      elif value == "9.5.0.823":
         value = "9.5 U1"

      elif value == "9.5.0.802":
         value = "9.5 U1 RC"

      elif value == "9.5.0.711":
         value = "9.5 GA"

      elif value == "9.5.0.580":
         value = "9.5 RTM"

      elif value == "9.0.0.1715":
         value = "9.0 U2"

      elif value == "9.0.0.1491":
         value = "9.0 U1"

      elif value == "9.0.0.902":
         value = "9.0 GA"

      elif value == "9.0.0.773":
         value = "9.0 RTM"

      elif value == "8.0.0.2084":
         value = "8.0\ U3"

      elif value == "8.0.0.2030":
         value = "8.0 U2b"

      elif value == "8.0.0.2029":
         value ="8.0 U2a"

      elif value == "8.0.0.2021":
         value = "8.0 U2 GA"

      elif value == "8.0.0.2018":
         value = "8.0 U2 RTM"

      elif value == "8.0.0.917":
         value = "8.0 P1"

      elif value == "8.0.0.817":
         value = "8.0 GA"

      elif value == "8.0.0.807":
         value = "8.0 RTM"

      return value
