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
class UpdateFilter(Filter):

   #********************************
   def __init__(self, name):
      self.name = 'update'

   #********************************
   def filter(self, dest_dict, src_dict):

      if isinstance(dest_dict, dict) and isinstance(src_dict, dict):
         dest_dict.update( src_dict )

      return dest_dict

#************************************************************************
class KeysFilter(Filter):

   #********************************
   def __init__(self, name):
      self.name = 'keys'

   #********************************
   def filter(self, dict_obj):

      if isinstance(dict_obj, dict):
         return list( dict_obj.keys() )

      return []

#************************************************************************
class ValuesFilter(Filter):

   #********************************
   def __init__(self, name):
      self.name = 'values'

   #********************************
   def filter(self, dict_obj):

      if isinstance(dict_obj, dict):
         return list( dict_obj.values() )

      return []

#************************************************************************
class SplitFilter(Filter):

   #********************************
   def __init__(self, name):
      self.name = 'split'

   #********************************
   def filter(self, source_str, separator):

      if isinstance(source_str, str) and isinstance(separator, str):
         return list( source_str.split(separator) )

      return []

#************************************************************************

