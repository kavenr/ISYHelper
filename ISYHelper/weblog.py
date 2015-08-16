
import web
import sys, logging
from wsgilog import WsgiLog
#import config

# From: http://stackoverflow.com/questions/7192788/how-do-i-redirrect-the-output-in-web-py

class WebLog(WsgiLog):
  def __init__(self, application):
    WsgiLog.__init__(
        self,
        application,
        logformat = '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
        debug = True,
        tofile = True,
        toprint =  False,
        logname = "IH.WebLog",
        file = web.config.log_file,
        loglevel = logging.DEBUG,
        interval = 'W0', # config.log_interval,
        backups = 7, #config.log_backups
    )

  def __call__(self, environ, start_response):
    def hstart_response(status, response_headers, *args):
      out = start_response(status, response_headers, *args)
      try:
        logline=environ["SERVER_PROTOCOL"]+" "+environ["REQUEST_METHOD"]+" "+environ["REQUEST_URI"]+" - "+status

      except err:
        logline="Could not log <%s> due to err <%s>" % (str(environ), err)

      self.logger.info(logline)

      return out

    return super(WebLog, self).__call__(environ, hstart_response)
