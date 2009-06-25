#!/usr/bin/env python

#
# IANAPP (i am not a python programmer)
#


import cgi
import os
from sgmllib import SGMLParser

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import pprint

class MainPage(webapp.RequestHandler):

	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		if self.request.get('url'):
			template_values['url'] = self.request.get('url')
			
			try:
				links = RevCanonical().revcanonical(self.request.get('url'))
				template_values['link'] = (links[0] if links else template_values['url'])
			except Exception, e:
				template_values['error'] = e;
		
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		self.get()
		
	
class ApiPage(webapp.RequestHandler):
	def get(self):
		
		if self.request.get('url'):
			url = self.request.get('url')
			try:
				links = RevCanonical().revcanonical(self.request.get('url'))
				
				if links:
					url = links[0]
				
				self.response.out.write(url)
			except Exception, e:
				self.error(500)
				self.response.out.write(e)
		else:
			self.response.out.write("Takes argument <code>url</code> returns reverse canonicalized URL, if found.  Otherwise returns the passed URL.")
		
	def post(self):
		pass
		
class RevCanonical:	
	def revcanonical(self, url):
		def canonical_test(attr,value) :
			if attr == 'rel':
				return (value.count('alternate') and value.count('short')) \
					or value.count('short_url') \
					or value.count('shorter-alternative') \
					or value.count('short_url') \
					or value.count('shortlink')
			elif attrattr == 'rev':
				return value.count('canonical')
			else:
				return False
			
		resp = urlfetch.fetch(url)
		html = resp.content

		fragment = len(url.split('#')) > 1 and '#' + url.split('#')[1] or ''

		parser = LinkParser()
		parser.feed(html)
		shorts = [link for link in parser.links for attr,value in link if canonical_test(attr,value)]

		return self.hrefs(shorts, fragment)
	
	def hrefs(self, links, fragment = ''):
		return [(e[1] + fragment) for l in links for e in l if e[0] == 'href' ]

class LinkParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.links = []

    def do_link(self, attrs):
        hreflist = [e[1] for e in attrs if e[0]=='href']
        if hreflist:
            self.links.append(attrs)
        # I think this is the same intent:
        # if any(e[0]=='href' for e in attrs):
        #	self.links.append(attrs)

    def end_head(self, attrs):
        self.setnomoretags()
    start_body = end_head

application = webapp.WSGIApplication( [('/', MainPage), ('/api', ApiPage)], debug=True)

def main():
	run_wsgi_app(application)


if __name__ == '__main__':
  main()
