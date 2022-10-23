# -*- coding:utf-8 -*-
#************************************************************************

from veeam_exporter.filters import Filter

#************************************************************************
class JobStatusFilter(Filter):

   #********************************
#   def __init__(self):
#      super(BackupServerVersionFilter, self).__init__('backup_server')

   #********************************
   def filter(self, value):
      if value is None or not isinstance(value, str):
         return value

      if value == "Success":
         value = 1

      elif value == "Warning":
         value = 2

      elif value == "Failed":
         value = "3"

      elif value == "Idle":
         value = "4"

      elif value == "Working":
         value = "5"

      else:
         value = 0

      return value
