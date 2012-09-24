import cgi
from google.appengine.ext.webapp import util

from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext import db

# A simple database model to store a URL and an associated blob.
class DataModel(db.Model):
  url = db.StringProperty(required=True)
  blob = blobstore.BlobReferenceProperty(required=True)

class StatHandler(webapp.RequestHandler):
    def get(self):
        model = DataModel.get_by_key_name(self.get_name())
        self.response.out.write(model.url)

    def get_name(self):
        name = "output.wav"
        params = cgi.parse_qs(self.request.query_string)
        if params and params['name']:
            name = params['name'][0];
        return name

def main():
    application = webapp.WSGIApplication([('/stat', StatHandler)],
                                         debug=True)
    util.run_wsgi_app(application)
    
if __name__ == '__main__':
    main()
