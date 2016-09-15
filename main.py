import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Blog(Handler):
    def render_front(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC "
                            "LIMIT 5")

        self.render("mainblog.html", title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_front()



class NewPost(Blog):
    def render_newpost(self,title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title=title, post=post)
            p.put()

            self.redirect("/blog/%s" % p.key().id())
        else:
            error = "We need both a title and some content!"
            self.render_newpost(title=title, post=post,error=error)

class ViewPostHandler(Blog):
    def render_singlepost(self, title="", post=""):
        self.render("singlepost.html", title=title, post=post)

    def get(self, id):
        p = Post.get_by_id(int(id))
        if p:
            self.render_singlepost(title=p.title, post=p.post)
            # t = jinja_env.get_template("singlepost.html")
            # response = t.render(p=p)

        else:
            error = "there is no post with that id"
            t = jinja_env.get_template("404.html")
            response = t.render (error=error)
            self.response.out.write(response)


app = webapp2.WSGIApplication([
    ('/blog/?', Blog),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
