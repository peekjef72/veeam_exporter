# -*- coding:utf-8 -*-
#************************************************************************

from veeam_exporter.filters import Filter

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

