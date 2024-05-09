# -*- coding:utf-8 -*-
#************************************************************************

from veeam_exporter.filters import Filter

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
