from django.utils import simplejson
from google.appengine.api import channel, memcache

import logging

class Channel():
  token = None
  address = None
  cached = True
  message = {}

  def __init__(self, address, generate=True):
   self.address = address
   if generate:
     self.token = memcache.get("token_%s" % self.address)
     if self.token is None:
       self.token = channel.create_channel(self.address)
       self.cached = False
       memcache.set("token_%s" % self.address, self.token, time=7200)

  def send(self):
    channel.send_message(self.address, simplejson.dumps(self.message))
    logging.info(simplejson.dumps(self.message))
    self.message = {}
    logging.info(simplejson.dumps(self.message))

  def queueLink(self, link):
    logging.info("Queuing link %s" % link.key().id_or_name())
    logging.info("Current queue: %s" % simplejson.dumps(self.message))
    if 'links' not in self.message:
      self.message['links'] = []
    link_message = {}
    link_message['id'] = link.key().id_or_name()
    link_message['url'] = link.url
    link_message['sender'] = link.sender.address
    self.message['links'].append(link_message)

  def sendLink(self, link):
    self.queueLink(link)
    self.send()
