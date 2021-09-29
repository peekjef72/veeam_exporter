import requests
import requests.auth


from urllib3.exceptions import InsecureRequestWarning, SubjectAltNameWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)

#*****************************************************************************************************
class VeeamAPIException(Exception):
    def __init__(self, status_code, response, message):
        self.status_code = status_code
        self.response = response
        self.message = message
        # Backwards compatible with implementations that rely on just the message.
        super(VeeamAPIException, self).__init__(message)


class VeeamAPIServerError(VeeamAPIException):
    """
    5xx
    """

    pass


class VeeamAPIClientError(VeeamAPIException):
    """
    Invalid input (4xx errors)
    """

    pass


class VeeamAPIBadInputError(VeeamAPIClientError):
    """
    400
    """

    def __init__(self, response):
        super(VeeamAPIBadInputError, self).__init__(
            400, response, "Bad Input: `{0}`".format(response)
        )


class VeeamAPIUnauthorizedError(VeeamAPIClientError):
    """
    401
    """

    def __init__(self, response):
        super(VeeamAPIUnauthorizedError, self).__init__(401, response, "Unauthorized")

#*****************************************************************************************************
class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers.update({"X-RestSvcSessionId": "{0}".format(self.token)})
        return request

#*****************************************************************************************************
class VeeamAPI:

    #***********************************************
    def __init__(
        self,
        auth,
        host="localhost",
        port=None,
        url_path_prefix="",
        protocol="http",
        verify=True,
        timeout=5.0,
        labels=None,
        proxy=None,
        keep_session=True,
    ):
        self.basic_auth = auth
        self.verify = verify
        self.timeout = timeout
        self.keep_session = keep_session
        self.url_host = host
        self.url_port = port
        self.url_path_prefix = url_path_prefix
        self.url_protocol = protocol

        #* init default labels list and defautl labels value dict
        self.def_label_names = []
        self.def_label_values = {}
        if labels is not None and len(labels) > 0:
           for lab in labels:
              if 'name' in lab:
                 self.def_label_names.append( lab['name'] )
                 val = ''
                 if 'value' in lab:
                    val = lab['value']
                 self.def_label_values[ lab['name'] ] = val

#        self.token = None
        self.has_logged = False

        def construct_api_url():
            params = {
                "protocol": self.url_protocol,
                "host": self.url_host,
                "url_path_prefix": self.url_path_prefix,
            }

            if self.url_port is None:
                url_pattern = "{protocol}://{host}/{url_path_prefix}"
            else:
                params["port"] = self.url_port
                url_pattern = "{protocol}://{host}:{port}/{url_path_prefix}"

            return url_pattern.format(**params)

        self.url = construct_api_url()

        self.url_proxy = proxy
        self.open_session()

        if isinstance(self.auth, TokenAuth):
            self.auth = TokenAuth(self.auth)
        else:
            self.auth = requests.auth.HTTPBasicAuth(*self.basic_auth)

    #***********************************************
    def open_session(self):

       self.s = requests.Session()

       if self.url_proxy is not None:
          protocol = self.url_protocol
          if 'protocol' in self.url_proxy:
              protocol = self.url_proxy['protocol']
          proxy_url = None
          if 'url' in self.url_proxy:
             proxy_url = self.url_proxy['url']
          if proxy_url is not None:
             self.s.proxies = { protocol: proxy_url }

    #***********************************************
    def __getattr__(self, item):
        def __request_runnner(url, json=None, headers=None, want_raw=False):
            __url = "%s%s" % (self.url, url)
            self.s.headers.update({"Accept": "application/json"})
            runner = getattr(self.s, item.lower())
            r = runner(
                __url,
                json=json,
                headers=headers,
                auth=self.auth,
                verify=self.verify,
                timeout=self.timeout,
            )
            if r.status_code >= 400:
                try:
                    response = r.json()
                except ValueError:
                    response = r.text
                message = response["message"] if "message" in response else r.text

                if 500 <= r.status_code < 600:
                    raise VeeamAPIServerError(
                        r.status_code,
                        response,
                        "Server Error {0}: {1}".format(r.status_code, message),
                    )
                elif r.status_code == 400:
                    raise VeeamAPIBadInputError(response)
                elif r.status_code == 401:
                    raise VeeamAPIUnauthorizedError(response)
                elif 400 <= r.status_code < 500:
                    raise VeeamAPIClientError(
                        r.status_code,
                        response,
                        "Client Error {0}: {1}".format(r.status_code, message),
                    )
            if want_raw:
               return r
            else:
               return r.json()

        return __request_runnner

    #***********************************************
    def login(self):
        '''
        Init a new session
        '''
        try:
           login = self.POST('/sessionMngr/?v=latest', want_raw=True)
           if login.status_code == 201 and 'X-RestSvcSessionId' in login.headers:
              token = login.headers['X-RestSvcSessionId']
              self.auth = TokenAuth( token )
              self.has_logged = True

        except:
           self.has_logged = False
           raise

        return login.json() 

    #***********************************************
    def logout(self):
        '''
        Delete the session
        '''
        if not isinstance(self.auth, TokenAuth):
           return None

        try:
           veeam_json = self.GET('/logonSessions')
        except VeeamAPIUnauthorizedError as exc:
           return exc.response
        except:
           raise

        r = '{}'
        if 'LogonSessions' in veeam_json:
           session_id = veeam_json['LogonSessions'][0]['SessionId']
        if session_id is not None:
           try:
              logout = self.DELETE( '/logonSessions/{0}'.format(session_id), want_raw=True )
              if logout and logout.status_code == 204 :
                 r = '{"status_code": 204, "message": "ok. 204 no data" }'
              else:
                 r = '{{"status_code": {0}, "message": "ko." }'.format(logout.status_code)
           except VeeamAPIUnauthorizedError:
              r = '{"status_code": 401, "message": "Session already closed." }'
           except:
             raise
        else:
           r = '{"status_code": 0, "message": "Session not found." }'

        return r
    #***********************************************
    def clear(self):
       self.s.close
       self.open_session()
#       self.token = None
       self.auth = requests.auth.HTTPBasicAuth(*self.basic_auth)

    #***********************************************
    def hasToken(self):
       return isinstance(self.auth, TokenAuth) and self.auth.token is not None

    #***********************************************
    def hasLogged(self):
       return self.has_logged

    #***********************************************
    def keepSession(self):
       return self.keep_session

    #***********************************************
    def getHost(self):
       return self.url_host

#*****************************************************************************************************

