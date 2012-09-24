from __future__ import with_statement

import cgi
import logging
from google.appengine.ext.webapp import util

from google.appengine.api import files
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext import db

# A simple database model to store a URL and an associated blob.
class DataModel(db.Model):
  url = db.StringProperty(required=True)
  blob = blobstore.BlobReferenceProperty(required=True)

# WamiHandler receives audio via a POST and serves it back to the
# client using a GET.  The audio data is stored in a blobstore, but
# additional meta information is (connecting a URL to a blob) is
# stored in the datastore.  You will need to enable the datastore
# admin section for your Google App Engine.
class WamiHandler(webapp.RequestHandler):
    def get(self):
        model = DataModel.get_by_key_name(self.get_name())
        blob_info = blobstore.BlobInfo.get(model.blob.key())
        blob_reader = blobstore.BlobReader(model.blob.key())
        data = blob_reader.read()

        # For replay to work in Chrome we must pretend like we accept ranges.
        self.response.headers['Accept-Ranges'] = "bytes"
        self.response.headers['Content-Type'] = blob_info.content_type
        self.response.out.write(data);
        logging.info("server-to-client: " + str(len(data)) + 
                     " bytes at key " + str(model.blob.key()))

    def post(self):
        type = self.request.headers['Content-Type']
        blob_file_name = files.blobstore.create(mime_type=type, _blobinfo_uploaded_filename=self.get_name())
        with files.open(blob_file_name, 'a') as f:
            f.write(self.request.body)
        f.close()
        files.finalize(blob_file_name)
        
        blob_key = files.blobstore.get_blob_key(blob_file_name)
        model = DataModel(key_name=self.get_name(), 
                          url=self.request.url, blob=blob_key)
        db.put(model)
        logging.info("client-to-server: type(" + type + 
                     ") key("  + str(blob_key) + ")")

    def get_name(self):
        name = "output.wav"
        params = cgi.parse_qs(self.request.query_string)
        if params and params['name']:
            name = params['name'][0];
        return name

def main():
    application = webapp.WSGIApplication([('/audio', WamiHandler)],
                                         debug=True)
    util.run_wsgi_app(application)
    
if __name__ == '__main__':
    main()


