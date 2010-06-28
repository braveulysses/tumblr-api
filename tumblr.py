#!/usr/bin/env python
"""Tumblr API client

Pulls data about a Tumblr tumblelog into Python data structures 
using the Tumblr API.  Currently intended for reading but not writing.

See http://www.tumblr.com/docs/en/api for API docs.
"""

__version__ = "0.3.0"
__author__ = "SNF Labs <jacob@spaceshipnofuture.org>"
__TODO__ = """TODO List
- Separate local and remote tests
- Add mocks to local tests
- Add tests for authentication
- Video: Parse the source and player fields
- Audio
- Quote: Parse a url out of Quote.source
- Photo: Parse a url out of Photo.caption
"""

# Note to self:
# Build using "python setup.py bdist_egg"

import urlparse
import httplib2
from urllib import urlencode
try:
    import xml.etree.cElementTree as ElementTree
except:
    try:
        import xml.etree.ElementTree as ElementTree
    except:
        try:
            import cElementTree as ElementTree
        except:
            import ElementTree as ElementTree

USER_AGENT = "Tumblr in the Bronx/%s +http://labs.spaceshipnofuture.org/tumblrapi/" % __version__
DEFAULT_HTTP_CACHE_DIR = ".cache"

BASE_AUTH_URL = "http://www.tumblr.com/api/authenticate"

class TumblrError(Exception): pass
class TumblrOhShitError(TumblrError): pass
class TumblrParseError(TumblrError): pass
class TumblrHTTPError(TumblrError): pass
class InternalServerError(TumblrHTTPError): pass
class ServiceUnavailableError(TumblrHTTPError): pass
class URLNotFoundError(TumblrHTTPError): pass
class URLForbiddenError(TumblrHTTPError): pass
class URLGoneError(TumblrHTTPError): pass
class UnsupportedContentTypeError(TumblrHTTPError): pass
class BadContentTypeError(TumblrHTTPError): pass

def _unicode(str):
    """A workaround for Python's built-in unicode().
    
    When unicode() is invoked against a variable with the value None,
    then unicode() will return the string u'None', which makes no sense to me.  
    
    It should return either None or u''.  This returns u''.
    """
    if str is None:
        return u''
    else:
        return unicode(str)

def _isUrl(str):
    """Attempts to determine if the given string is really an HTTP URL.

    This is a quick-and-dirty test that just looks for an http 
    protocol handler."""
    u = urlparse.urlparse(str)
    if u[0] == 'http' or u[0] == 'https':
        return True
    else:
        return False


class TumblrUrl(object):
    """Use this to build a URL with a set of key-value parameters."""
    def __init__(self):
        super(TumblrUrl, self).__init__()
        self.base_url = None
        self.params = dict()
        
    def add_param(self, name, value):
        self.params[name] = value
        return self

    @property
    def url(self):
        if len(self.params) > 0:
                url_params = "&".join([ "=".join(p) \
                                        for p in self.params.items() ])
                return self.base_url + "?" + url_params
        else:
            return self.base_url
                

class AuthUrl(TumblrUrl):
    """Use this to build a Tumblr authentication URL.
    
    >>> url = tumblr.AuthUrl()
    >>> url.set_email("guido@example.com").set_password("secret").url
    """
    def __init__(self):
        super(AuthUrl, self).__init__()
        self.base_url = BASE_AUTH_URL
        
    def set_email(self, email):
        self.add_param("email", email)
        return self
        
    def set_password(self, password):
        self.add_param("password", password)
        return self
        
    def set_include_theme(self, include_theme):
        if include_theme:
            self.add_param("include_theme", "1")
        return self
        
#######################################################################
#
# Read API Objects
#
#######################################################################

class Feed(object):
    """A Feed object stores data relating to one of the Tumblelog's 
    source feeds.
    
    Attributes:
    - id
    - url
    - type
    - title
    - next_update
    """
    def __init__(self, id, url, type, title, next_update):
        super(Feed, self).__init__()
        self.id = id
        self.url = url
        self.type = type
        self.title = title
        self.next_update = next_update


class Tumblelog(object):
    """Represents a single tumblelog.
    
    The TumbleLog object stores general metadata about the tumblelog, 
    such as its name, as well as the tumblelog's posts.
    
    Attributes:
    - http_response
    - name
    - cname
    - url
    - timezone
    - tagline
    - posts
    - num_posts
    - start
    - feeds
    """
    def __init__(self, logdata):
        super(Tumblelog, self).__init__()
        if logdata is None:
            raise TumblrOhShitError, "Uh-oh"
        # The attribute self.http_response holds the httplib2 HTTP 
        # response object.
        # If the calling app wants to know that a redirect occurred, 
        # then they should look at the following values: 
        # - http_response['content-location']:  the destination URL
        # - http_response.previous.status:      the previous HTTP status
        #                                        (current is always 200)
        # - http_response.previous.location:    the suggested destination URL
        self.http_response = None
        # Get tumblelog attributes
        self.title = _unicode(logdata.attrib.get('title'))
        self.name = _unicode(logdata.attrib.get('name'))
        self.cname = _unicode(logdata.attrib.get('cname'))
        if self.cname is None or self.cname == '':
            self.url = u"http://" + self.name + ".tumblr.com/"
        else:
            self.url = u"http://" + self.cname + "/"
        self.timezone = _unicode(logdata.attrib.get('timezone'))
        try:
            self.tagline = _unicode(logdata.text)
        except AttributeError:
            self.tagline = u''
        self.posts = []
        self.start = 0
        self.num_posts = 0
        self.feeds = {}
        try:
            for f in logdata.find('feeds').findall('feed'):
                id = int(f.attrib.get('id'))
                url = _unicode(f.attrib.get('url'))
                type = _unicode(f.attrib.get('import-type'))
                title = _unicode(f.attrib.get('title'))
                next_update = int(f.attrib.get('next-update-in-seconds'))
                self.feeds[id] = Feed(id, url, type, title, next_update)
        except AttributeError:
            self.feeds = None


class Line(object):
    """A line in a conversation.
    
    Attributes:
    - name
    - label
    - content
    """
    def __init__(self, name, label, content):
        super(Line, self).__init__()
        self.name = name
        self.label = label
        self.content = content


class Post(object):
    """Generic Post object from which the others are derived.
    
    Attributes:
    - type
    - id
    - url
    - date_gmt
    - date
    - unixtime
    - source_feed
    - source_feed_id
    - source_url
    """
    def __init__(self, postdata):
        super(Post, self).__init__()
        # The keymap is a set of aliases for instance attributes.
        # See Post.__getattr__() below.
        self._keymap = {
            'permalink': 'url'
        }
        # Setting a type is admittedly silly because 
        # the type is implied by the object class
        self.type = 'unknown'
        # Set common attributes
        self.id = int(postdata.attrib.get('id'))
        self.url = _unicode(postdata.attrib.get('url'))
        self.date_gmt = _unicode(postdata.attrib.get('date-gmt'))
        self.date = _unicode(postdata.attrib.get('date'))
        self.unixtime = int(postdata.attrib.get('unix-timestamp'))
        try:
            self.source_feed_id = int(postdata.attrib.get('from-feed-id'))
            self.source_url = _unicode(postdata.attrib.get('feed-item'))
        except TypeError:
            self.source_feed_id = None
            self.source_url = None
        # Copy the reference for the postdata tree into an instance attribute 
        # so that it can be inspected for whatever weird reason
        self.postdata = postdata

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            pass
        try:
            return self.__dict__[self._keymap[attr]]
        except:
            raise AttributeError, "object has no attribute '%s'" % attr


class Regular(Post):
    """A Regular freeform post.
    
    Attributes:
    - type
    - title
    - body/content/description
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Regular, self).__init__(postdata)
        self.type = 'regular'
        try:
            self.title = _unicode(postdata.find('regular-title').text)
        except AttributeError:
            self.title = u''
        try:
            self.body = _unicode(postdata.find('regular-body').text)
        except AttributeError:
            self.body = u''
        self._keymap['content'] = 'body'
        self._keymap['description'] = 'body'


class Link(Post):
    """A Link, consisting of a title, url, and maybe a description.
    
    Attributes:
    - type
    - title
    - description/body/content
    - link_url/related
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Link, self).__init__(postdata)
        self.type = 'link'
        try:
            self.title = _unicode(postdata.find('link-text').text)
        except AttributeError:
            self.title = u''
        try:
            self.description = _unicode(postdata.find('link-description').text)
        except AttributeError:
            self.description = u''
        try:
            self.link_url = _unicode(postdata.find('link-url').text)
        except AttributeError:
            self.link_url = u''
        self.via = u'' # TODO: Possibly extract 'via' link from description
        self._keymap['body'] = 'description'
        self._keymap['content'] = 'description'
        self._keymap['related'] = 'link_url'


class Quote(Post):
    """A Quote and its source.
    
    Attributes:
    - type
    - quote/description/body/content
    - source
    """
    def __init__(self, postdata):
        super(Quote, self).__init__(postdata)
        self.type = 'quote'
        try:
            self.quote = _unicode(postdata.find('quote-text').text)
        except AttributeError:
            self.quote = u''
        try:
            self.source = _unicode(postdata.find('quote-source').text)
        except AttributeError:
            self.source = u''
        self._keymap['description'] = 'quote'
        self._keymap['body'] = 'quote'
        self._keymap['content'] = 'quote'


class Photo(Post):
    """A Photo, with a caption and several URLs of it in various sizes.
    
    Attributes:
    - type
    - caption/body/content/description
    - urls
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Photo, self).__init__(postdata)
        self.type = 'photo'
        try:
            self.caption = _unicode(postdata.find('photo-caption').text)
        except AttributeError:
            self.caption = u''
        self.urls = {}
        for url in postdata.findall('photo-url'):
            self.urls[url.attrib.get('max-width')] = _unicode(url.text)
        self._keymap['body'] = 'caption'
        self._keymap['content'] = 'caption'
        self._keymap['description'] = 'caption'


class Conversation(Post):
    """A Conversation or chat log.  Each line is a Line object.
    
    Attributes:
    - type
    - description/body/content
    - lines
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Conversation, self).__init__(postdata)
        self.type = 'conversation'
        self.description = postdata.find('conversation-text').text
        self.lines = []
        for line in postdata.findall('conversation-line'):
            name = _unicode(line.attrib.get('name'))
            label = _unicode(line.attrib.get('label'))
            content = _unicode(line.text)
            l = Line(name, label, content)
            self.lines.append(l)
        self._keymap['body'] = 'description'
        self._keymap['content'] = 'description'


class Video(Post):
    """A Video object.
    
    Attributes:
    - type
    - source
    - player
    - caption/body/content/description
    - title
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Video, self).__init__(postdata)
        self.type = 'video'
        try:
            self.source = _unicode(postdata.find('video-source').text)
        except AttributeError:
            self.source = u''
        try:
            self.player = _unicode(postdata.find('video-player').text)
        except AttributeError:
            self.player = u''
        try:
            self.caption = _unicode(postdata.find('video-caption').text)
        except AttributeError:
            self.caption = u''
        # Only Vimeo videos have titles
        self.title = u''
        self._keymap['body'] = 'caption'
        self._keymap['content'] = 'caption'
        self._keymap['description'] = 'caption'


class Audio(Post):
    """An Audio object.
    
    Attributes:
    - type
    - player
    - caption/content/body/description
    
    See also the Post object.
    """
    def __init__(self, postdata):
        super(Audio, self).__init__(postdata)
        self.type = 'audio'
        self.player = u''
        self.caption = u''
        self._keymap['body'] = 'caption'
        self._keymap['content'] = 'caption'
        self._keymap['description'] = 'caption'        

#######################################################################
#
# Authenticate API Objects
#
#######################################################################

class AuthInfo(object):
    def __init__(self, version, user, tumblelogs):
        super(AuthInfo, self).__init__()
        self.version = version
        self.user = user
        self.tumblelogs = tumblelogs
        
    
class UserAuthInfo(object):
    def __init__(self, userdata):
        super(UserAuthInfo, self).__init__()
        self.can_upload_audio = bool(int(userdata.attrib.get('can-upload-audio')))
        self.can_upload_aiff = bool(int(userdata.attrib.get('can-upload-aiff')))
        self.can_upload_video = bool(int(userdata.attrib.get('can-upload-video')))
        self.max_video_bytes_uploaded = int(userdata.attrib.get('max-video-bytes-uploaded'))
        self.can_ask_question = bool(int(userdata.attrib.get('can-ask-question')))
        self.default_post_format = _unicode(userdata.attrib.get('default-post-format'))
        self.liked_post_count = int(userdata.attrib.get('liked-post-count'))
        

class TumblelogAuthInfo(object):
    def __init__(self, logdata):
        super(TumblelogAuthInfo, self).__init__()
        self.title = _unicode(logdata.attrib.get('title'))
        self.type = _unicode(logdata.attrib.get('type'))
        self.url = _unicode(logdata.attrib.get('url'))
        self.name = _unicode(logdata.attrib.get('name'))
        self.avatar_url = _unicode(logdata.attrib.get('avatar-url'))
        if logdata.attrib.get('is-primary') == 'yes':
            self.is_primary = True
        else:
            self.is_primary = False
        try:
            self.private_id = int(logdata.attrib.get('private-id'))
        except (AttributeError, TypeError):
            self.private_id = u''
        # TODO: description, custom-css, theme-source
        

#######################################################################
#
# Action Methods
#
#######################################################################

def _parse_content_type(ct):
    """Given an HTTP content-type header, parses out the content-type and 
    the charset.
    
    Does not currently perform any validation on the content of the header."""
    parts = ct.split(";")
    content_type = parts[0]
    try:
        charset = parts[1].strip().lstrip('charset=')
    except IndexError:
        charset = None
    return content_type, charset

def _fetch(url, http_method="GET", form_data=None, cache_dir=DEFAULT_HTTP_CACHE_DIR, proxy_info=None):
    """Requests the Tumblr API URL and deals with any HTTP-related errors.
    
    Returns both an httplib2 Response object and the content."""
    valid_content_types = [ 'application/xml', 'text/xml' ]
    h = httplib2.Http(cache=cache_dir, proxy_info=proxy_info)
    try:
        if form_data is not None:
            if not isinstance(form_data, type(dict())):
                raise TypeError("form_data must be a dictionary!")
            req_body = urlencode(form_data)
        else:
            req_body = None
        resp, content = h.request(url, method=http_method, body=req_body, headers={ "User-Agent": USER_AGENT })
    except IOError:
        # An IOError can happen, for example, when httplib2 can't write 
        # to its cache.
        # For now, just re-raise the exception.
        raise
    # Deal with various HTTP error states
    if resp.status == 403:
        raise URLForbiddenError
    if resp.status == 404:
        raise URLNotFoundError
    if resp.status == 410:
        raise URLGoneError
    if resp.status == 500:
        raise InternalServerError
    if resp.status == 503:
        raise ServiceUnavailableError
    # Bail if proper XML content-type not given
    content_type, charset = _parse_content_type(resp['content-type'])
    if content_type in valid_content_types:
        # Weird: using not in the above test doesn't work
        pass
    else:
        raise UnsupportedContentTypeError
    return resp, content

def _getResponse(url_or_file, http_method="GET", form_data=None, cache_dir=DEFAULT_HTTP_CACHE_DIR, proxy_info=None):
    """Fetches the Tumblr API XML and returns both the HTTP status and 
    the content body.
    
    Instead of a URL, this method also accepts an open file or a Tumblr
    XML string.  In those cases, the HTTP status is returned as None."""
    resp = None
    if isinstance(url_or_file, file):
        # Open file
        content = url_or_file.read()
    elif _isUrl(url_or_file):
        # URL
        resp, content = _fetch(url_or_file, http_method, form_data, cache_dir, proxy_info)
    else:
        # String
        content = url_or_file
    return resp, content

def _getTree(content):
    """Returns an ElementTree representation of the content."""
    try:
        tree = ElementTree.fromstring(content)
    except SyntaxError:
        raise TumblrParseError, "SyntaxError while parsing XML!"
    return tree
    
def authenticate(email, password, include_theme=False, cache_dir=DEFAULT_HTTP_CACHE_DIR, proxy_info=None):
    """Authenticates to the Tumblr API service."""
    # Interestingly, the Tumblr API service expects POST params to be in the 
    # URL, not the request body.
    auth_url = AuthUrl().set_email(email).set_password(password).set_include_theme(include_theme).url
    resp, content = _getResponse(auth_url, "POST", None, cache_dir, proxy_info)
    tree = _getTree(content)
    version = tree.attrib.get('version')
    user = UserAuthInfo(tree.find('user'))
    tumblelogs = []
    for tumblelog in tree.findall('tumblelog'):
        tumblelogs.append(TumblelogAuthInfo(tumblelog))
    authinfo = AuthInfo(version, user, tumblelogs)
    return resp, authinfo
    
def parse(url_or_file, cache_dir=DEFAULT_HTTP_CACHE_DIR, proxy_info=None):
    """Parses Tumblr API XML into Python data structures.
    
    Accepts either a URL, an open file, or a hunk of XML in a string.
    """
    resp, content = _getResponse(url_or_file, "GET", None, cache_dir, proxy_info)
    tree = _getTree(content)
    tumblelog = Tumblelog(tree.find('tumblelog'))
    tumblelog.http_response = resp
    tumblelog.start = int(tree.find('posts').attrib.get('start'))
    tumblelog.num_posts = int(tree.find('posts').attrib.get('total'))
    # Get posts
    posts = []
    for postdata in tree.find('posts'):
        # What kind of post of this?
        # Find out and instantiate an appropriate object
        type = postdata.attrib.get('type')
        if type =='regular':
            post = Regular(postdata)
        elif type == 'link':
            post = Link(postdata)
        elif type == 'quote':
            post = Quote(postdata)
        elif type == 'photo':
            post = Photo(postdata)
        elif type == 'conversation':
            post = Conversation(postdata)
        elif type == 'video':
            post = Video(postdata)
        elif type == 'audio':
            post = Audio(postdata)
        else:
            post = Post(postdata)
        # Get the source feed, if present
        try:
            if post.source_feed_id:
                post.source_feed = tumblelog.feeds[post.source_feed_id]
        except KeyError:
            # It's possible that the Tumblr API XML response will include 
            # a bogus feed ID. I don't know why.
            # TODO: Add a test case for this.
            pass
        posts.append(post)
    tumblelog.posts = posts
    return tumblelog
    
