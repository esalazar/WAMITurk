import cgi
from google.appengine.ext.webapp import util

from google.appengine.api import files
from google.appengine.ext import webapp

class HitHandler(webapp.RequestHandler):
    def get(self):
        hit = 1
        try:
            hit = int(self.request.get('hit'))
        except:
            hit = 1
        self.response.out.write(self.getPrompts(hit))

    def getPrompts(self, hit):
        num = 10
        hit = hit - 1
        start = hit * num
        counter = 0
        prompts = ""
        fp = open('shuffled_hit.txt')
        for i, line in enumerate(fp):
            if i >= start:
                counter += 1
                prompts += line
                if num == counter:
                    break
                else:
                    prompts += '<>'
        fp.close()
        return prompts

def main():
    application = webapp.WSGIApplication([('/hit', HitHandler)],
                                         debug=True)
    util.run_wsgi_app(application)
    
if __name__ == '__main__':
    main()
