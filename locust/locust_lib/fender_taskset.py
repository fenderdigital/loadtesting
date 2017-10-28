from locust import HttpLocust, TaskSet, task

import json
import logging
import os
import random
import uuid
import ssl
import time
import urlparse

import requests

from locust_lib import adapters


logger = logging.getLogger(__name__)


class FenderTaskSet(TaskSet):

  def on_start(self):
    self.client.mount('https://', adapters.TlsAdapter())
    self.uuid = uuid.uuid1().hex
    self._do_on_start()

  def _do_on_start():
    raise NotImplementedError


class LoginMixin(object):
  """Mixin for providing authentication via the auth service.

  Required environment variables.:
    LOCUST_API_HOST: The url of the API service, qualified with the scheme.
  """

  @property
  def authorizations(self):
    if not hasattr(self, '_authorizations'):
      self._authorizations = {}
    return self._authorizations

  def _init_api_host(self):
    url = os.environ['LOCUST_API_HOST']
    parse_result = urlparse.urlparse(url)
    if not parse_result.scheme:
      raise ValueError('LOCUST_API_HOST must include a scheme (http/https)')
    self.api_host = url

  def _login(self, email, password):
    self._init_api_host()
    if getattr(self, 'cookies_logged_in', None) is not None:
      return
    else:
      print "generating cookie"
    payload = (
        '{"data":{"type":"tokens","attributes":{"email":"%s","password":"%s"}}}'
    ) % (email, password)
    session_cookie_template = (
      '{"authenticated":'
      '{"authenticator":"authenticator:jwt"'
      ',"token":"%(user_token)s","userId":"%(user_id)s"}}'
    )
    response = self.client.post(
        self.api_host + '/tokens',
        headers={'Content-Type': 'application/vnd.api+json'},
        data=payload,
        name='api token request',
        catch_response=True,
    )
    response.success()
    try:
      response.raise_for_status()
    except requests.HTTPError:
      logger.error('create token failed: %s', response.status_code)
      return response
    token_data = response.json()['data']['attributes']
    self.cookies_logged_in = requests.cookies.RequestsCookieJar()
    self.cookies_logged_in.set(
        'fender-connect-session-cookie',
        session_cookie_template % dict(
            user_token=token_data['token'],
            user_id=token_data['user-id'],
        )
    )
    self.authorizations['api'] = 'Bearer ' + token_data['token']
    self.authorizations['site'] = 'Basic ZmVuZGVyY29ubmVjdDpmM25kM3JiM3RhISE='

    return response
