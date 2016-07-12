import webapp2

from google.appengine.api import memcache

class CacheHandler(webapp2.RequestHandler):
  def get(self, **kwargs):
    data = memcache.get(self.request.url)
    if data is None or 'nocache' in self.request.GET:
      data, cache_time = self.GetCached(**kwargs)
      if cache_time > 0:
        memcache.add(key=self.request.url, value=data, time=cache_time)
    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
    self.response.write(data)
