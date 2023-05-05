# -*- coding:utf-8 -*-
#************************************************************************
import hashlib

from veeam_exporter.filters import Filter

#************************************************************************
class HashsumFilter(Filter):

   #********************************
   def filter(self, hash_str, digest='md5'):

      sum_obj = None
      if digest == 'sha1':
         sum_obj = hashlib.sha1()
      elif digest == 'sha224':
         sum_obj = hashlib.sha224()
      elif digest == 'sha256':
         sum_obj = hashlib.sha256()
      elif digest == 'sha512':
         sum_obj = hashlib.sha512()
      else:
         sum_obj = hashlib.md5()

      sum_obj.update( hash_str.encode('utf-8') )
      return sum_obj.hexdigest()

#************************************************************************
