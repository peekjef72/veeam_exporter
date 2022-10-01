from veeam_exporter.veeam_api import VeeamAPIUnauthorizedError
from requests.exceptions import ConnectionError, ReadTimeout, RequestException

from prometheus_client import CollectorRegistry, generate_latest, Gauge

from tenacity import retry, RetryError
from tenacity import stop_after_attempt, wait_fixed, retry_if_result

#*******************************************************************************************************
# functions for tenacity

def retry_login(value):
    """Return True if value is None"""
    return value == 'retry'


def retry_get(value):
    """Return True if value is None"""
    x1, x2 = value
    return x1 == 'retry'

#*******************************************************************************************************
class VeeamExporter(object):
   SUCCESS = 'SUCCESS'
   FAILURE = 'FAILURE'
   INVALID = 'INVALID'

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]

      #**
      self.logger = kwargs.get('logger')
      if self.logger is None:
         raise Exception("no logging object set!")

      self.apis = kwargs.get('apis')
      if self.apis is None:
         raise Exception("no api objects set!")

      self.engine = kwargs.get('engine')
      if self.engine is None:
         raise Exception("no YamlScript engine objects set!")

      #** metrics
      self.metrics = kwargs.get('metrics')

      self.debug = kwargs.get('debug', False)

      self.api = None

   #***********************************************
   @retry(stop=stop_after_attempt(2), retry=retry_if_result(retry_get))
   def ns_session_get(self, url):
      try:
         data = self.api.GET( url )
         if data:
            return self.SUCCESS, data
         else:
            return self.FAILURE, None

      except RequestException as e:
         self.logger.error('Stat Access Error on {1}: {0}'.format(e, self.api.getHost()))

      except VeeamAPIUnauthorizedError:
         self.ns_session_clear()
         if self.login():
            return 'retry', None

      except Exception as e:
         self.logger.error('Unable to access stats from Veeam Enterprise Manager on {1}: {0}'.format(e, self.api.getHost()))

      return self.FAILURE, None

   #***********************************************
   def ns_session_clear(self):
      self.api.clear()

   #***********************************************
   def login(self):
      if self.api.hasToken():
         return True

      try:
         if self.ns_session_login() == self.SUCCESS:
            return True
      except RetryError as e:
         self.logger.error('Login Retries Exhausted {}'.format(e))
      except Exception as e:
         self.logger.error('Login Session Failed {}'.format(e))

      self.ns_session_clear()
      return False

   #***********************************************
   @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_result(retry_login))
   def ns_session_login(self):

      ''' Login to ADC and get a session id for stat access'''
      try:
         has_logged = self.api.hasLogged()
         login = self.api.login()

         if 'SessionId' in login:
            if login['SessionId'] != '':
               if not has_logged:
                  self.logger.info("Veeam Entreprise Manager Session Login Successful on {0}".format( self.api.getHost() ) )
               return self.SUCCESS

      except (ConnectionError, ReadTimeout) as exc:
         self.logger.error('Connection Exception: Host {1}: {0}'.format(exc, self.api.getHost()))
      except VeeamAPIUnauthorizedError as exc:
         self.logger.error("user '{0}' not authorized on https://{1}:{2}".format(
                self.api.auth[0],
                self.api.getHost(), self.api.url_port)
	)
      except RequestException as e:
         self.logger.error('Session Login Error on {1}: {0}'.format(e, self.api.getHost()))
      except Exception as e:
         self.logger.error('Login Session Failed on {1}: {0}'.format(e, self.api.getHost()))

      return self.FAILURE
 
   #***********************************************
   def get_entity_stat(self, url):
      '''Fetches stats from ADC using nitro using for a particular entity.'''
      try:
         return self.ns_session_get(url)
      except RetryError as e:
         self.logger.error('Get Retries Exhausted on {1}: {0}'.format(e, self.api.getHost()))
      except Exception as e:
         self.logger.error('Stat Access Failed on {1}: {0}'.format(e, self.api.getHost()))

      return self.FAILURE, None

   #***********************************************
   def collect( self, local_vars ):

      logged = 0

      if self.login():
         logged = 1

      self.registry = CollectorRegistry()
      names = ()
      if len(self.api.def_label_names)>0:
         names = tuple( self.api.def_label_names )
      status = Gauge(
         # gauge name
         'veeam_em_up',
         # gauge help text
         'probe success  login status: 0 Down / 1 Up',
         # labels list : veeam em host
         labelnames = names,
         registry = self.registry
        )
      if len(self.api.def_label_names)>0:
         status.labels( **self.api.def_label_values ).set( logged )
      else:
         status.set( logged )

      if logged == 0:
         output = generate_latest( self.registry )
         if self.debug:
            for line in bytes.decode(output).split('\n'):
               if line != '':
                  self.logger.debug(line)
         return output

      #** loop on "metric files"
      for met_name in self.metrics.keys():
         metric = self.metrics[met_name]

         #* try collecting the data
         try:
            self.engine.perform_action( **{
               'exporter': self,
               'task': metric,
               'local_vars': local_vars,
               'level': 0,
            } )
         except Exception as exc:
            self.logger.warning('collect: {0}'.format(exc))

      #* end for "metric files"

      #* cleanup connection
      if not self.api.keepSession():
         self.api.logout()

      output = generate_latest( self.registry )
      if self.debug:
         for line in bytes.decode(output).split('\n'):
            if line != '':
               self.logger.debug(line)
      return output

#*****************************************************************************
