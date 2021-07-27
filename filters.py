
from  pathlib import Path
import importlib, sys, os, re
from inspect import getmembers, isclass

#************************************************************************
class Filter:

   #********************************
   def __init__(self, name):
      self.name = name

   #********************************
   def filter(self, value):
      return value

#************************************************************************
class Filters(object):
   filters = {}

   #********************************
   def __init__(self, path='./custom_filters'):
      self.add( Filter('default') )
      self.load(path)

   #********************************
   def get(self):
      return Filters.filters

   #********************************
   def add(self, filter):
      if isinstance( filter, Filter ):
         Filters.filters[filter.name] = filter;

   #********************************
   def find(self, name):
      if name not in Filters.filters:
         name = 'default'
      return Filters.filters[name]

   #********************************
   def load(self, base_path):

      #** add custom_filters path to python module path
      sys.path.append(os.path.abspath(base_path))

      pattern = re.compile(r'.*\.py$')
      try:
         for path in Path(base_path).iterdir():
#            print('path: {0}'.format(path) )
            if path.name != '__init__.py' and pattern.search(str(path)):
               components = path.name.split('.')
               mod = importlib.import_module(components[0])
               if mod is not None:
                  for (klass_name, klass) in getmembers( mod, isclass):
                      if klass != Filter:
                         self.add( klass( components[0] ) )
      except FileNotFoundError:
        pass
      except:
        raise
