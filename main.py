from google.appengine.ext import db

import jinja2, os
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello Udacity!')

def render_str(templates, **params):
    t = jinja_env.get_template(templates)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, templates, **params):
        t = jinja_env.get_template(templates)
        return t.render(params)

    def render(self, templates, **kw):
        self.write(self.render_str(templates, **kw))

class MainPage(Handler):
    def get(self, name = ""):

        name = self.request.get("name")
        self.render("welcome.html", name = name)

### blog starts here
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", post = self)

def blog_key(name = 'default'):
    return db.Key.from_path('blog', name)

class BlogFront(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render("front.html", posts = posts)

class Permalink(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent = blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return

        else:
            self.render("permalink.html", post = post)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = Post(subject = subject, content = content, parent = blog_key())
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content please"
            self.render("newpost.html", subject = subject, content = content, error = error)

app = webapp2.WSGIApplication([
                                ('/', MainPage),
                                ('/blog/newpost', NewPost),
                                ('/blog/?', BlogFront),
                                ('/blog/([0-9]+)', Permalink)
], debug=True)
