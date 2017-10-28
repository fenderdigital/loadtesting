import ssl

from requests import adapters
from requests.packages.urllib3 import poolmanager


class TlsAdapter(adapters.HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = poolmanager.PoolManager(num_pools=connections,
                                   maxsize=maxsize,
                                   block=block,
                                   ssl_version=ssl.PROTOCOL_SSLv23)

  def send(self, request, *args, **kwargs):
    result = super(TlsAdapter, self).send(request, *args, **kwargs)
    return result

  def get_connection(self, url, proxies=None):
    return super(TlsAdapter, self).get_connection(url, proxies)