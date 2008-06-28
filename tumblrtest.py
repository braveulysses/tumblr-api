#!/usr/bin/env python
"""Tumblr API client unit test cases"""

__version__ = "0.1"
__author__ = "SNF Labs"
__TODO__ = """TODO List
- link-via detection
- photo-caption not present
"""

import os
import unittest
import tumblr
import urlparse

def isUrl(str):
    """Attempts to determine if the given string is really an HTTP URL.
    
    This is a quick-and-dirty test that just looks for an http protocol handler."""
    u = urlparse.urlparse(str)
    if u[0] == 'http' or u[0] == 'https':
        return True
    else:
        return False

class SanityTestCase(unittest.TestCase):
    """Sanity checks against specific production tumblelogs."""
    def setUp(self):
        self.urls = ( 
            "http://golden.cpl593h.net/api/read",
            "http://thelongesttrainieversaw.tumblr.com/api/read",
            "http://industry.tumblr.com/api/read",
            "http://blog.gabrieljeffrey.com/api/read",
            "http://marco.tumblr.com/api/read",
            "http://demo.tumblr.com/api/read"
        )
        self.logs = []
        for url in self.urls:
            self.logs.append(tumblr.parse(url))

    def testNumPosts(self):
        """Posts are present in the API XML."""
        for log in self.logs:
            assert len(log.posts) > 0, "No posts found!"

    def testNoUnknownPosts(self):
        """No posts are of an unrecognized type."""
        types = [ 'regular', 
            'link', 
            'quote', 
            'photo', 
            'conversation', 
            'video', 
            'audio' 
        ]
        for log in self.logs:
            for post in log.posts:
                assert post.type in types
          
    def testHasUrl(self):
        """Tumblelog's URL can be determined."""
        for log in self.logs:
            assert log.url is not None and log.url != ''

    def testHasTitle(self):
        """Tumblelog's title can be determined."""
        for log in self.logs:
            assert log.title is not None and log.title != ''

class FileOrStringTestCase(unittest.TestCase):
    """Tests that an open file object or a string can be parsed."""
    def setUp(self):
        self.filename = os.getcwd() + os.sep + 'tests' + os.sep + 'file' + os.sep + 'golden.xml'
        
    def testOpenFile(self):
        """An open file object can be passed to the parser."""
        f = open(self.filename, 'r')
        log = tumblr.parse(f)
        f.close()
        assert log.title == 'golden hours'
        
    def testString(self):
        """An XML string can be passed to the parser."""
        f = open(self.filename, 'r')
        xmlString = f.read()
        f.close()
        log = tumblr.parse(xmlString)
        assert log.title == 'golden hours'

class ContentTypeParserTestCase(unittest.TestCase):
    """Tests the simple HTTP Content-Type parser."""
    def testContentTypeAndCharset(self):
        """Typical Content-Type with charset can be parsed."""
        ct = 'application/xml; charset=utf-8'
        contentType, charset = tumblr._parseContentType(ct)
        assert (contentType == 'application/xml') and (charset == 'utf-8')
        
    def testContentTypeWithoutCharset(self):
        """Typical Content-Type with no charset can be parsed."""
        ct = 'text/xml'
        contentType, charset = tumblr._parseContentType(ct)
        assert (contentType == 'text/xml') and (charset is None)

class NetworkingTestCase(unittest.TestCase):
    """Checks various network conditions, including HTTP errors."""
    def setUp(self):
        self.url = 'http://demo.tumblr.com/api/read'
        self.urlUnreachable = 'http://gukbluh.duh123ugh3huh241gah.ugh/eek'
        self.urlRedirectDestination = 'http://chompy.net/lab/tumblrapi/tests/http/redirects/demo.xml' 
        self.urlMovedPermanently = 'http://chompy.net/lab/tumblrapi/tests/http/redirects/301'
        self.urlFound = 'http://chompy.net/lab/tumblrapi/tests/http/redirects/302'
        self.urlTemporaryRedirect = 'http://chompy.net/lab/tumblrapi/tests/http/redirects/307'
        self.urlUnauthorized = 'http://chompy.net/lab/tumblrapi/tests/errors/http/401'
        self.urlForbidden = 'http://chompy.net/lab/tumblrapi/tests/http/errors/403'
        self.urlNotFound = 'http://chompy.net/lab/tumblrapi/tests/http/errors/404'
        self.urlGone = 'http://chompy.net/lab/tumblrapi/tests/http/errors/410'
        self.urlServerError = 'http://chompy.net/lab/tumblrapi/tests/http/errors/500'
        self.urlServiceUnavailable = 'http://chompy.net/lab/tumblrapi/tests/http/errors/503'
        self.urlContentTypeTextPlain = 'http://chompy.net/lab/tumblrapi/tests/http/contenttype/?type=textplain'
        self.urlContentTypeTextXml = 'http://chompy.net/lab/tumblrapi/tests/http/contenttype/?type=textxml'
        self.urlContentTypeTextHtml = 'http://chompy.net/lab/tumblrapi/tests/http/contenttype/?type=texthtml'
        self.urlContentTypeApplicationXhtmlXml = 'http://chompy.net/lab/tumblrapi/tests/http/contenttype/?type=applicationxhtmlxml'
        self.urlContentTypeApplicationXml = 'http://chompy.net/lab/tumblrapi/tests/http/contenttype/?type=applicationxml'
    
    def testUnreachableHost(self):
        """Error thrown if host cannot be reached."""
        from httplib2 import ServerNotFoundError
        try:
            tumblr.parse(self.urlUnreachable)
        except ServerNotFoundError:
            pass
        else:
            self.fail("Expected a ServerNotFoundError!")

    #def testHTTP301MovedPermanently(self):
    #    """Redirect via HTTP 301 is recorded."""
    #    log = tumblr.parse(self.urlMovedPermanently)
    #    assert (log.httpResponse.previous.status == 301) and (log.httpResponse['content-location'] == self.urlRedirectDestination)

    def testHTTP302Found(self):
        """Redirect via HTTP 302 is recorded."""
        log = tumblr.parse(self.urlFound)
        assert (log.httpResponse.previous.status == 302) and (log.httpResponse['content-location'] == self.urlRedirectDestination)

    def testHTTP307(self):
        """Redirect via HTTP 307 is recorded."""
        log = tumblr.parse(self.urlTemporaryRedirect)
        assert (log.httpResponse.previous.status == 307) and (log.httpResponse['content-location'] == self.urlRedirectDestination)

    def testHTTP403Forbidden(self):
        """Error thrown if URL is forbidden (HTTP 403)."""
        try:
            tumblr.parse(self.urlForbidden)
        except tumblr.URLForbiddenError:
            pass
        else:
            self.fail("Expected a URLForbiddenError!")

    def testHTTP404NotFound(self):
        """Error thrown if URL cannot be found (HTTP 404)."""
        try:
            tumblr.parse(self.urlNotFound)
        except tumblr.URLNotFoundError:
            pass
        else:
            self.fail("Expected a URLNotFoundError!")

    def testHTTP410Gone(self):
        """Error thrown if URL has been removed (HTTP 410)."""
        try:
            tumblr.parse(self.urlGone)
        except tumblr.URLGoneError:
            pass
        else:
            self.fail("Expected a URLGoneError!")

    def testHTTP500ServerError(self):
        """Error thrown if HTTP 500 occurs."""
        try:
            tumblr.parse(self.urlServerError)
        except tumblr.InternalServerError:
            pass
        else:
            self.fail("Expected an InternalServerError!")
            
    def testHTTP503ServiceUnavailableError(self):
        """Error thrown if HTTP 503 occurs."""
        try:
            tumblr.parse(self.urlServiceUnavailable)
        except tumblr.ServiceUnavailableError:
            pass
        else:
            self.fail("Expected a ServiceUnavailableError!")

    def testContentTypeTextXml(self):
        """Should accept HTTP content-type text/xml."""
        log = tumblr.parse(self.urlContentTypeTextXml)
        # Just do anything
        assert log.name == u'demo'

    def testContentTypeApplicationXml(self):
        """Should accept HTTP content-type application/xml."""
        log = tumblr.parse(self.urlContentTypeApplicationXml)
        # Just do anything
        assert log.name == u'demo'

    def testContentTypeApplicationXhtmlXml(self):
        """Error thrown if content-type application/xhtml+xml used."""
        try:
            tumblr.parse(self.urlContentTypeApplicationXhtmlXml)
        except tumblr.UnsupportedContentTypeError:
            pass
        else:
            self.fail("Expected an UnsupportedContentTypeError!")

class XMLTestCases(unittest.TestCase):
    """Checks various XML handling scenarios."""
    def setUp(self):
        self.urlMalformed = 'http://chompy.net/lab/tumblrapi/tests/xml/malformed.xml'
        self.urlBadAmpersand = 'http://chompy.net/lab/tumblrapi/tests/xml/ampersand.xml'
    
    def testMalformedXML(self):
        """Error thrown if XML is not well-formed."""
        try:
            tumblr.parse(self.urlMalformed)
        except tumblr.TumblrParseError:
            pass
        else:
            fail("Expected a TumblrParseError for malformed XML!")

    def testUnencodedAmpersand(self):
        """Error thrown if ampersand is unencoded."""
        try:
            tumblr.parse(self.urlBadAmpersand)
        except tumblr.TumblrParseError:
            pass
        else:
            fail("Expected a TumblrParseError for malformed XML due to unencoded ampersand!")

class TumblelogTestCases(unittest.TestCase):
    """Tests involving the tumblr API XML format."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/demo.xml"
        self.log = tumblr.parse(self.url)

    def testTumblelogUrl(self):
        """A tumblelog must have a URL."""
        assert self.log.url == u'http://demo.tumblr.com/'
        
    def testCname(self):
        """It's okay if tumblr.cname is or is not present."""
        self.log.cname

    def testTagline(self):
        """It's okay if tumblr.tagline is or is not present."""
        self.log.tagline

    def testFeedsNotPresent(self):
        """It's okay if tumblr.feeds is or is not present."""
        self.log.feeds
        
class TumblelogPostTestCases(unittest.TestCase):
    """Generic tests involving posts."""
    def setUp(self):
        self.url = 'http://chompy.net/lab/tumblrapi/tests/tumblelog/demo.xml'
        self.log = tumblr.parse(self.url)
    
    def testPostPermalink(self):
        """post.permalink is equivalent to post.url."""
        assert self.log.posts[0].permalink == self.log.posts[0].url

class TumblelogRegularPostTestCases(unittest.TestCase):
    """Tests involving Regular posts."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/regular.xml"
        self.log = tumblr.parse(self.url)

    def testRegularPostType(self):
        """A Regular post should have type='regular'."""
        assert self.log.posts[0].type == 'regular'

    def testRegularContent(self):
        """For Regular posts, post.content is equivalent to post.body."""
        assert self.log.posts[0].content == self.log.posts[0].body

    def testRegularDescription(self):
        """For Regular posts, post.description is equivalent to post.body."""
        assert self.log.posts[0].description == self.log.posts[0].body
                    
    def testRegularNoTitle(self):
        """It's okay if a Regular post has no title."""
        self.log.posts[1].title

    def testRegularNoBody(self):
        """It's okay if a Regular post has no body."""
        self.log.posts[2].body

class TumblelogLinkPostTestCases(unittest.TestCase):
    """Tests involving Link posts."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/link.xml"
        self.log = tumblr.parse(self.url)

    def testLinkPostType(self):
        """A Link post should have type='link'."""
        assert self.log.posts[0].type == 'link'

    def testLinkContent(self):
        """For Link posts, post.content is equivalent to post.description."""
        assert self.log.posts[0].content == self.log.posts[0].description

    def testLinkBody(self):
        """For Link posts, post.body is equivalent to post.description."""
        assert self.log.posts[0].body == self.log.posts[0].description

    def testLinkRelated(self):
        """For Link posts, post.related is equivalent to post.linkUrl."""
        assert self.log.posts[0].related == self.log.posts[0].linkUrl

    def testLinkNoTitle(self):
        """It's okay if a Link post has no title."""
        self.log.posts[1].title

    def testLinkNoDescription(self):
        """It's okay if a Link post has no description."""
        self.log.posts[2].description
        
    def testLinkNoLinkUrl(self):
        """It's okay if a Link post has no URL. Strange but true."""
        self.log.posts[3].linkUrl

class TumblelogQuotePostTestCases(unittest.TestCase):
    """Tests involving quote posts."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/quote.xml"
        self.log = tumblr.parse(self.url)
    
    def testQuotePostType(self):
        """A Quote post should have type='quote'."""
        assert self.log.posts[0].type == 'quote'

    def testQuoteContent(self):
        """For Quote posts, post.content is equivalent to post.quote."""
        assert self.log.posts[0].content == self.log.posts[0].quote

    def testQuoteBody(self):
        """For Quote posts, post.body is equivalent to post.quote."""
        assert self.log.posts[0].body == self.log.posts[0].quote

    def testQuoteBody(self):
        """For Quote posts, post.description is equivalent to post.quote."""
        assert self.log.posts[0].description == self.log.posts[0].quote
    
    def testQuoteSourceNotPresent(self):
        """It's okay if a Quote post has no source."""
        self.log.posts[1].source

    def testQuoteTextNotPresent(self):
        """It's okay if a Quote post has no text (though it shouldn't be)."""
        self.log.posts[2].quote

    def testQuoteSourceEmpty(self):
        """It's okay if a Quote post's source is empty."""
        assert self.log.posts[3].source == u''

class TumblelogPhotoPostTestCases(unittest.TestCase):
    """Tests involving photo posts."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/photo.xml"
        self.log = tumblr.parse(self.url)
    
    def testPhotoPostType(self):
        """A Photo post should have type='photo'."""
        assert self.log.posts[0].type == 'photo'

    def testPhotoBody(self):
        """For Photo posts, post.body is equivalent to post.caption."""
        assert self.log.posts[0].body == self.log.posts[0].caption

    def testPhotoDescription(self):
        """For Photo posts, post.description is equivalent to post.caption."""
        assert self.log.posts[0].description == self.log.posts[0].caption

    def testPhotoCaptionNotPresent(self):
        """It's okay if a Photo post's caption is empty."""
        assert self.log.posts[3].caption == u''

    def testPhotoUrls(self):
        """Photo URLs should in fact be URLs."""
        for url in self.log.posts[0].urls.values():
            assert isUrl(url)

class TumblelogSourceFeedsTestCases(unittest.TestCase):
    """Test inolving source feed support."""
    def setUp(self):
        self.url = "http://chompy.net/lab/tumblrapi/tests/tumblelog/sourcefeeds.xml"
        self.log = tumblr.parse(self.url)
        
    def testSourceFeedsPresent(self):
        """Source feed metadata should be present in post.sourceFeed."""
        assert self.log.posts[3].sourceFeed is not None

    def testSourceFeedId(self):
        """Source feed should have an Id."""
        assert self.log.posts[3].sourceFeed.id == 48612

    def testSourceFeedTitle(self):
        """Source feed should have a title."""
        assert self.log.posts[3].sourceFeed.title == u'del.icio.us/mpgomez'

    def testSourceFeedUrl(self):
        """Source feed should have a URL."""
        assert self.log.posts[3].sourceFeed.url == u'http://del.icio.us/rss/mpgomez'

    def testSourceFeedType(self):
        """Source feed should have a type."""
        assert self.log.posts[3].sourceFeed.type == u'link-description'
          
if __name__ == '__main__':
    unittest.main()