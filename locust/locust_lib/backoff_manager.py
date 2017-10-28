from locust import HttpLocust, TaskSet, task

import random
import time


def create(max_level):
  return BackoffManager(max_level)


class BackoffManager(object):

  def __init__(self, max_level):
    self.level = 0
    self.max_level = max_level

  def bump(self):
    self.level = min(self.level + 1, self.max_level)

  def __call__(self):
    if not self.level:
      return
    duration = random.randrange(0, 2**self.level - 1)
    time.sleep(duration)
