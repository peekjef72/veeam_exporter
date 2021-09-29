
from http.server import BaseHTTPRequestHandler, HTTPServer

from socketserver import ThreadingMixIn
import threading

from prometheus_client import CONTENT_TYPE_LATEST
from urllib.parse import urlparse, parse_qs

#******************************************************************************************
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
   pass



class VeeamCollectorRequestHandler(BaseHTTPRequestHandler):
   def __init__(self, *args, **kwargs):
      BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

   #* to remove message from client on server side
   def log_message(self, format, *args):
       pass

   def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/metrics':
            params = parse_qs(url.query)
            if 'target' in params:
               found = False
               for target in self.server.collector.exporter.apis:
                  self.server.collector.exporter.api = None
                  if len(params['target'])>0 and params['target'][0] == target.url_host:
                     self.server.collector.exporter.api = target
                     local_data = threading.local()
                     local_data.vars = {}
                     output = self.server.collector.exporter.collect( local_data.vars )
                     self.send_response(200)
                     self.send_header('Content-Type', CONTENT_TYPE_LATEST)
                     self.end_headers()
                     self.wfile.write( output )
                     found = True
                     break
               if not found:
                  self.send_response(404)
                  self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                output = bytes("""<html>
   <head><title>Veeam Exporter</title></head>
   <body>
      <h1>Veeam Exporter</h1>
       <table border=1>
         <tr>
          <th>target</th>
         </tr>
""", 'utf-8')
                for target in self.server.collector.exporter.apis:
                   output += bytes("<tr><td><a href=\"/metrics?target={0}\">{0}</a></td></th>".format(target.url_host), 'utf-8')
                output += bytes("""
       </table>
   </body>
   </html>""", 'utf-8')
                self.wfile.write( output )

        elif url.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes("""<html>
            <head><title>Veeam Exporter</title></head>
            <body>
            <h1>Veeam Exporter</h1>
            <p>Visit <a href=\"/metrics\">/metrics</a> to use.</p>
            </body>
            </html>""", 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def handler(*args, **kwargs):
    VeeamCollectorRequestHandler(*args, **kwargs)


#******************************************************************************************
class VeeamCollector(object):

   #***********************************************
   def __init__( *args, **kwargs ):
      self = args[0]

      #**
      self.exporter = kwargs.get('exporter')
      if self.exporter is None:
         raise Exception("no exporter object set!")
      self.addr = kwargs.get('address')
      if self.addr is None:
         self.addr = ''
      self.port = kwargs.get('port')

   #***********************************************
   def collect(self):
      return self.exporter.collect()

   #***********************************************
   def starts(self):

      self.exporter.logger.info( 'listening on {0}:{1}'.format(self.addr, self.port) )
      self.server = ThreadingHTTPServer( (self.addr, self.port), handler)

      setattr(self.server, 'collector', self)

      try:
         self.server.serve_forever()
      except KeyboardInterrupt:
         pass
         self.server.server_close()

#******************************************************************************************
