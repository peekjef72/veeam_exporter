#import sys, os, logging
from threading import Lock

from jinja2 import Environment
import json

from prometheus_client import Gauge, Counter

from veeam_exporter.filters import Filters

#******************************************************************************************
class EmptyItem(object):
   """
    default item in a loop (query or rule) when no loop element is defined
   """
   #***********************************************
#   def __init__( self ):
#      self = args[0]

   #***********************************************
   def __getattr__(self, name):
     return '<undef>'

#*******************************************************************************************************
def my_finalize(thing):
   if thing is not None:
      if isinstance(thing, (list, dict)):
         thing = json.dumps(thing)
      elif isinstance(thing, (bool)):
         thing = 'true' if thing else 'false'
   return thing

#*******************************************************************************************************
class MyCounter(Counter):

    def set(self, value=0):
        self._value.set(value)

    def _child_samples(self):
        return (
            ('_total', {}, self._value.get(), None, self._value.get_exemplar()),
        )

#*******************************************************************************************************
class BaseAction(object):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]

      self.keyword = kwargs.get('keyword')
      if self.keyword is None:
         raise Exception("no keyword set for action!")
      self.name = kwargs.get('name', self.keyword)

      self.is_list = kwargs.get('is_list', False)
      self.is_global = kwargs.get('is_global', True)

      if self.is_global:
         self.attrs = kwargs.get('attributes', { 
		'name': { 'mandatory': True },
		'with_items': { 'mandatory': False },
		'when': { 'mandatory': False },
		'loop_var': { 'mandatory': False },
		'vars': { 'mandatory': False },
	   } )

      #* for url queries and mettrics set (registry)
#      self.exporter = kwargs.get('exporter')
#      if self.exporter is None:
#         raise Exception("no exporter set for action!")

      self.logger = kwargs.get('logger')
      if self.logger is None:
         raise Exception("no logger set for action!")

      self.script = kwargs.get('script')
      if self.script is None:
         raise Exception("no script set for action!")

   #***********************************************
   def is_action(self, task):

      res = False
      #** keyword must be found in dict 
      if isinstance(task, dict) and self.keyword in task:
         #** if action keyword must be a list or not
         if self.is_list :
            if isinstance( task.get(self.keyword), list ):
               res = True
         else:
            res = True
      return res

   #***********************************************
   def play_action( *args, **kwargs ):
      self = args[0]

      task = kwargs.get('task')
      local_vars = kwargs.get('local_vars')
#      level = kwargs.get('level', 0)

      if self.is_global and 'name' in task:
         self.logger.debug( "task: {0}.".format(task['name']))

      #* init vars for this metric
      if 'vars' in task and task['vars'] is not None:
         #* task['vars'] should be a dict or a list of dict
         #* so var_name should be a str or a dict
         if isinstance(task['vars'], dict):
            vars = [ task['vars'] ]
         for var in vars:
            for var_name in var.keys():
               local_vars[var_name] = self.script.get_var( var[var_name], local_vars )

      #* check if we have to loop on element
      items = []

      if 'with_items' in task:
         #* check if we have conditions on elements from loop
         #* build default var name for loop item[level if >0]
         loop_var_name = 'item'
#         if level > 0:
#            loop_var_name = 'item{0}'.format(level)
         if task['with_items'] is not None:
            items = self.script.get_var( task['with_items'], local_vars )
            if items is None:
               self.logger.warning( "no value for var loop '{0}'".format(task['with_items']) )
               return
            elif not isinstance(items, list):
               items = [ items ]
         if 'loop_var' in task and task['loop_var'] is not None:
            loop_var_name = task['loop_var']

         if len(items) == 0:
            self.logger.info( "var '{0}' is empty.".format(task['with_items']) )
            return 
               
      #* this is not a loop: build empty item, and dummy var_name
      elif len(items) == 0:
         items.append( EmptyItem() )
         loop_var_name = 'empty_item'

      #** loop on element defined by 'config'
      tmp_count = 0
      for item in items:

         #* build temporary symbol table with current loop item
         local_vars[loop_var_name] = item

         #* check if we have conditions on elements from loop
         if 'when' in task:
            when_res = False
            if isinstance(task['when'], str):
               when_conds = [ task['when'] ]
            elif isinstance(task['when'], list):
               when_conds = task['when']
            else:
               when_conds = []
            for when_cond in when_conds:
               when_res = self.script.get_var("{{% if {0} %}}True{{% else %}}False{{% endif %}}".format(when_cond), local_vars )
               if when_res is None or not when_res:
                  when_res = False
#                  self.logger.debug( "when cond '{0}' return False".format(when_cond) )
#                  tmp_count += 1
#                  self.logger.debug( "when {1}: {0}".format(item['CreationTimeUTC'], tmp_count) )
                  break
            if not when_res:
               continue
         try:
            self.custom_action( **kwargs )
         except:
            raise

      # end for item

      # remove var_name from vars: because 'empty_item' can be used at every recursion level
      # it can be removed too !
      if loop_var_name in local_vars:
         del local_vars[loop_var_name]

#*******************************************************************************************************
class DebugAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]

      tmp_params = kwargs.copy()
      tmp_params.update( {
	'keyword': 'debug',
        'attributes': { 
		'name': { 'mandatory': True },
		'msg': { 'mandatory': True },
	},
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      task = kwargs.get('task')
      local_vars = kwargs.get('local_vars')

      if isinstance(task['debug'], dict) and 'msg' in task['debug']:
         temp_val = self.script.get_var(task['debug']['msg'], local_vars )
         if temp_val is not None:
            self.logger.debug( temp_val )

#*******************************************************************************************************
class UrlAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]
       
      tmp_params = kwargs.copy()
      tmp_params.update( {
	'keyword': 'url',
        'attributes': { 
		'name': { 'mandatory': True },
		'var_name': { 'mandatory': False },
	},
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      exporter = kwargs.get('exporter')
      task = kwargs.get('task')
      local_vars = kwargs.get('local_vars')
      level = kwargs.get('level', 0)

      try:
         url = self.script.get_var(task['url'], local_vars)
         status, data = exporter.get_entity_stat(url)
         if not data:
            self.logger.warning('Unable to fetch data for entity: {}'.format(task['name']))
            return status
      except Exception as e:
         self.logger.error('Error in fetching entity {}'.format(e))
         return exporter.FAILURE

      if data is not None:
         #* set the result json object from collected page as the local symbols' table.
         if 'var_name' in task and task['var_name'] is not None:
            if task['var_name'] == '_root':
               local_vars.update( data )
            else:
               res_var_name = task['var_name']
               local_vars.update( { res_var_name: data } )
         else:
            if level == 0 or level == 1:
               local_vars.update( data )
            else:
               res_var_name = 'res_level_{0}'.format(level)
               local_vars.update( { res_var_name: data } )
      #
      else:
         if 'name' in task:
            name = task['name']
         else:
            name = task['url']
         self.logger.warning( "received empty reply for {0}".format(name) )

#*******************************************************************************************************
class SetFactAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]
       
      tmp_params = kwargs.copy()
      tmp_params.update( {
	'keyword': 'set_fact',
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      exporter = kwargs.get('exporter')
      task = kwargs.get('task')
      local_vars = kwargs.get('local_vars')

      #* task['set_fact'] should be a dict or a list of dict
      #* so var_name should be a str or a dict
      if isinstance(task['set_fact'], dict):
         vars = [ task['set_fact'] ]
      for var in vars:
         for var_name in var.keys():
            local_vars[var_name] = self.script.get_var( var[var_name], local_vars )

#*******************************************************************************************************
class MetricAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]
       
      tmp_params = kwargs.copy()
      tmp_params.update( {
	'name': 'metric',
	'keyword': 'name',
	'is_global': False,
        'attributes': { 
		'name': { 'mandatory': True },
		'help': { 'mandatory': False },
		'value': { 'mandatory': True },
		'type': { 'mandatory': True, 'default': 'gauge' },
		'labels': { 'mandatory': False },
	},
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      exporter = kwargs.get('exporter')
      metric = kwargs.get('task')
      local_vars = kwargs.get('local_vars')
      metric_prefix = kwargs.get('metric_prefix')

      name = ''
      if 'metric_prefix' in metric:
         name = metric['metric_prefix'] + '_'
      elif metric_prefix is not None:
         name = metric_prefix + '_'
      if 'name' in metric:
         raw_name = self.script.get_var( metric['name'], local_vars )
         name += raw_name.lower()
      else:
         self.logger.error('no name defined for metric !!!')
         return

      if not 'value' in metric :
         self.logger.warning( "no value defined for metric '{0}'".format(name) )
         return

      help_txt = ''
      if 'help' in metric:
         help_txt = self.script.get_var( metric['help'], local_vars )

      label_names = []
      label_values = {}

      if 'labels' in metric:
         if isinstance(metric['labels'], str):
            labels = self.script.get_var( metric['labels'], local_vars )
            if labels is None:
               labels = []
         else:
            labels = metric['labels']

         for lab in labels:
            lab_name = None;
            if 'name' in lab:
               lab_name = self.script.get_var( lab['name'], local_vars )
            if lab_name is not None:
               label_names.append( lab_name )
         # append default labels 'constant'
         label_names.extend(exporter.api.def_label_names)

      value = None
      if 'value' in metric:
         value = self.script.get_var( metric['value'], local_vars )
      if value is None:
         self.logger.warning("no value set for metric '{0}'".format(name))
         return

      if name not in exporter.registry._names_to_collectors \
		and name + '_total' not in exporter.registry._names_to_collectors :
         klass = Gauge
         if 'type' in metric and metric['type'] is not None:
            cur_type = self.script.get_var( metric['type'], local_vars )
            if cur_type == 'counter':
               klass = MyCounter
         col_metric = klass(
            # metric name
            name,
            # metric help text
            help_txt,
            # labels list
            labelnames = tuple(label_names),
            registry = exporter.registry
         )
      else:
         if name in exporter.registry._names_to_collectors:
            col_metric = exporter.registry._names_to_collectors[ name ]
         elif name + '_total' in exporter.registry._names_to_collectors:
            col_metric = exporter.registry._names_to_collectors[ name + '_total']
         else:
            self.logger.warning("Metric collector for '{0}' not found.".format(name))
            return

      if 'labels' in metric and labels is not None:
         for idx, lab in enumerate( labels ):
            lab_value = None
            if idx >= len( label_names ):
               break
            lab_name = label_names[idx]
            if 'value' in lab:
               lab_value = self.script.get_var( lab['value'], local_vars )
            if lab_value is None:
               lab_value = ''
            label_values[lab_name] = lab_value
      label_values.update(exporter.api.def_label_values)

      if len( label_names ) > 0:
         try:
            col_metric.labels( **label_values ).set( float( value ) )
         except Exception as e:
            self.logger.error('Caught exception while adding counter {} to {}: {}'.format(name, value, str(e)))
      else:
         try:
            col_metric.set( float( value ) )
         except Exception as e:
            self.logger.error('Caught exception while adding counter {} to {}: {}'.format(name, value, str(e)))

#*******************************************************************************************************
class ActionsAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]
       
      tmp_params = kwargs.copy()
      tmp_params.update( {
	'keyword': 'actions',
        'is_list': True,
        'attributes': { 
		'name': { 'mandatory': True },
	},
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      task = kwargs.get('task')
      level = kwargs.get('level', 0)

      if 'actions' in task and task['actions'] is not None:
         if isinstance(task['actions'], list):
            actions = task['actions']
         else:
            actions = [ task['actions'] ]

         for action in actions:
# debug TEMP
#            self.logger.debug( "action: {0}.".format(action['name']))
            if 'name' in action and action['name'] == 'loop all jobs for vm':
               self.logger.debug( "action: debug break.")
#            elif action['name'] == 'debug job':
#               local_vars = kwargs.get('local_vars')
#               if len( local_vars['jobs']) == 9:
#                  self.logger.debug( "action: len=9")
#               self.logger.debug( "action: len={0}.".format( len( local_vars['jobs'])) )
# fin debug
            try:
               tmp_params = kwargs.copy()
               tmp_params['task'] = action
               tmp_params['level'] = level + 1
               self.script.perform_action( **tmp_params )
            except Exception as exc:
               self.logger.warning('action do_loop actions: {0}'.format(exc))
               raise

#*******************************************************************************************************
class MetricsAction(BaseAction):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]
       
      tmp_params = kwargs.copy()
      tmp_params.update( {
	'keyword': 'metrics',
        'is_list': True,
        'attributes': { 
		'name': { 'mandatory': True },
		'metric_prefix': { 'mandatory': False },
	},
      } )

      BaseAction.__init__(self, **tmp_params )

   #***********************************************
   def custom_action( *args, **kwargs ):
      self = args[0]

      task = kwargs.get('task')

      metric_prefix = None
      if 'metric_prefix' in task:
          metric_prefix = task['metric_prefix']

      if 'metrics' in task and task['metrics'] is not None:
         if isinstance(task['metrics'], list):
            metrics = task['metrics']
         else:
            metrics = [ task['metrics'] ]

         for metric in metrics:
            try:
               tmp_params = kwargs.copy()
               tmp_params['task'] = metric
               tmp_params['action_type'] = 'metric'
               if metric_prefix is not None:
                  tmp_params['metric_prefix'] = metric_prefix
               action_obj = self.script.perform_action( **tmp_params )

            except Exception as exc:
               self.logger.warning('do_loop actions: {0}'.format(exc))
               raise

#*******************************************************************************************************
class YamlScript(object):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]

      #**
      self.logger = kwargs.get('logger')
      if self.logger is None:
         raise Exception("no logging object set!")

      #* to store the "vars" data
      self.vars = {}
      vars = kwargs.get('vars')
      if vars is not None:
         self.vars = vars

      self.mutex = Lock()

      #*** add jinja2 env for templating
      self.env = Environment( finalize=my_finalize)

      #*** add custom filters to jinja2 env
      filters = kwargs.get('filters')
      if filters is not None and isinstance(filters, Filters):
         for filter_name, filter_func in filters.get().items():
            self.env.filters[filter_name] = filter_func.filter

      #*** define empty dict to store variable templates
      self.vars_tmpl = {}

      self.debug = kwargs.get('debug', False)

      actions = [
        DebugAction( logger=self.logger, script=self ),
        UrlAction( logger=self.logger, script=self ),
        SetFactAction( logger=self.logger, script=self ),
        MetricsAction( logger=self.logger, script=self ),
        ActionsAction( logger=self.logger, script=self ),
        MetricAction( logger=self.logger, script=self ),
     ]
      self.actions = {}
      for act in actions:
         self.actions[act.name] = act;

   #**********************************************
   def get_var_str( self, var_value, local_vars ):

      self.mutex.acquire()
      if var_value in self.vars_tmpl:
         tm = self.vars_tmpl[var_value]
      else:
         try:
            tm = self.env.from_string( var_value )
         except Exception as e:
            self.logger.error('Unable to valorized: {}'.format(e))
            self.mutex.release()
            return None
         self.vars_tmpl[var_value] = tm

      self.mutex.release()

      try:
         value = tm.render( local_vars )
      except Exception as e:
         self.logger.error('Unable to valorized: {}'.format(e))
         return None

      if value is not None:
         try:
            value = json.loads( value )
         except json.JSONDecodeError:
            if isinstance(value, str):
               tmp_val = value.lower()
               if tmp_val in ['true', '1', 't', 'y', 'yes']:
                  value = True
               elif tmp_val in ['false', '0', 'f', 'n', 'no']:
                  value = False
            pass

      return value

   #**********************************************
   def get_var_list( self, var_value, local_vars ):
      value = []
      for val in var_value:
         value.append( self.get_var( val, local_vars ) )

      return value

   #**********************************************
   def get_var_dict( self, var_value, local_vars ):
      value = {}
      for val_name in var_value.keys():
         value[val_name] =  self.get_var( var_value[val_name], local_vars )

      return value

   #**********************************************
   def get_var( self, var_value, local_vars ):

      if isinstance( var_value, str ):
         if( var_value.find('{{') != -1 or var_value.find('{%') != -1):
            value = self.get_var_str( var_value, local_vars )
         else:
            value = var_value
      elif isinstance( var_value, list):
         value = self.get_var_list( var_value, local_vars )
      elif isinstance( var_value, dict):
         value = self.get_var_dict( var_value, local_vars )
      elif isinstance( var_value, (int, float, bool) ):
         value = var_value
      else:
         value = None

      return value

   #***********************************************
   def perform_action( *args, **kwargs ):
      self = args[0]

      action = kwargs.get('task')

      action_obj = None
      if 'action_obj' in action and isinstance(action['action_obj'], BaseAction):
         action_obj = action['action_obj']
      else:
         action_type = kwargs.get('action_type')
         if action_type is not None and action_type in self.actions:
            action['action_obj'] = self.actions.get(action_type)
         else:
            for act_obj in self.actions.values():
               if act_obj.is_global and act_obj.is_action(action):
                  action['action_obj'] = act_obj
                  break

         if 'action_obj' in action:
            action_obj = action['action_obj']

      if action_obj is None:
        raise Exception("not determinated action {0}!".format( json.dumps(action) ) )

      try:
#         tmp_params = kwargs.copy()
#         tmp_params['exporter'] = self
         action_obj.play_action( **kwargs )
      except Exception as exc:
         self.logger.warning('perform action {0}: {1}'.format(action.name, exc))
         raise

#*******************************************************************************************************
