from locust import HttpLocust, TaskSet, task

import json
import os
import random
import uuid
import ssl
import time

import requests
from requests.packages.urllib3.poolmanager import PoolManager

from locust_lib import adapters
from locust_lib import backoff_manager
from locust_lib import fender_taskset


def get_target_host():
  host = os.environ['LOCUST_TARGET_HOST']
  if not host.endswith('/'):
    host += '/'
  return host


def make_func(path, failure_code=None, login=True):
  def func(self):
    self._make_request(path, login=login, failure_code=failure_code)
  return func


backoff = backoff_manager.create(5)


class SimpleWebTasks(fender_taskset.FenderTaskSet, fender_taskset.LoginMixin):

  tasks = {}

  # Populate tasks
  with open(os.environ['SIMPLE_WEB_JSON'], 'r') as test_file:
    rows = json.load(test_file)
  for row in rows:
    path = row['path']
    weight = row.setdefault('weight', 10)
    expected_failure = row.setdefault('expected_failure', None)
    login = row.setdefault('login', True)
    task = make_func(path, failure_code=expected_failure, login=login)
    tasks[task] = weight

  def _do_on_start(self):
    self.cookies_logged_in = None
    while True:
      backoff()
      response = self._login('qafenderauto@gmail.com', 'Fendertest$1')
      if self.cookies_logged_in is not None:
        break
      backoff.bump()
      print 'login failed, will retry'
    self.cookies = requests.cookies.RequestsCookieJar()

  def _make_request(self, path, login=False, failure_code=None):
    headers = {}
    headers['Authorization'] = self.authorizations['site']

    name = path
    uuid = '[{}]'.format(self.uuid)
    if not name:
      name = 'home'
    if login:
      cookies = self.cookies_logged_in
      name += ' (logged in)'
    else:
      cookies = self.cookies
    with self.client.get(
        path, headers=headers, cookies=cookies,
        name=name, catch_response=True, timeout=(300, 300)) as response:
      if failure_code:
        if response.status_code == failure_code:
          response.success()
        else:
          response.failure()
    if response.status_code != 200:
      print '{} {}  => {} '.format(uuid, response.request.url, response)
    else:
      print '{} {}  => {} '.format(uuid, response.request.url, response.url)


class WebUser(HttpLocust):
  task_set = SimpleWebTasks
  min_wait=0
  max_wait=0

  host = get_target_host()

