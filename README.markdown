# Tumblr-API #

A simple read-only Python client for the Tumblr API.

This should run with at least Python 2.4.

## Example ##

	>>> import tumblr
	>>> t = tumblr.parse("http://demo.tumblr.com/api/read")
	>>> t.name
	u'demo'
	>>> t.tagline
	u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'
	>>> t.url
	u'http://demo.tumblr.com/'
	>>> t.posts[0]
	<tumblr.Quote object at 0x4be8b0>
	>>> t.posts[0].content
	u'It does not matter how slow you go so long as you do not stop.'
	>>> t.posts[1]
	<tumblr.Photo object at 0x4be8d0>
	>>> t.posts[1].caption
	u'Passing through Times Square by\xa0<a href="http://www.mareenfischinger.com/">Mareen Fischinger</a>'
	>>> t.posts[1].urls
	{'75': u'http://5.media.tumblr.com/235_r4_75sq.jpg', '250': u'http://16.media.tumblr.com/235_r4_250.jpg', '100': u'http://11.media.tumblr.com/235_r4_100.jpg', '500': u'http://1.media.tumblr.com/235_r4_500.jpg', '400': u'http://19.media.tumblr.com/235_r4_400.jpg'}
	>>> t.posts[1].urls['400']
	u'http://19.media.tumblr.com/235_r4_400.jpg'
	>>> t.posts[2]
	<tumblr.Link object at 0x4be970>
	>>> t.posts[2].url
	u'http://demo.tumblr.com/post/234'
	>>> t.posts[2].content
	u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'
	>>> t.posts[3]
	<tumblr.Conversation object at 0x4be710>
	>>> t.posts[3].lines
	[<tumblr.Line object at 0x406ef0>, <tumblr.Line object at 0x4c5410>, <tumblr.Line object at 0x4c5430>, <tumblr.Line object at 0x4c5450>, <tumblr.Line object at 0x4c5470>, <tumblr.Line object at 0x4c5490>]
	>>> t.posts[3].lines[0]
	<tumblr.Line object at 0x406ef0>
	>>> t.posts[3].lines[0].name
	u'Jack'
	>>> t.posts[3].lines[0].label
	u'Jack:'
	>>> t.posts[3].lines[0].content
	u'Hey, you know what sucks?\r'
	>>> t.posts[3].lines[1].content
	u'vaccuums\r'
	>>> t.posts[4]
	<tumblr.Regular object at 0x5b4930>
	>>> t.posts[4].title
	u'An example post'
	>>> t.posts[4].content
	u'<p>Lorem ipsum dolor sit amet, consectetuer <a href="http:///">adipiscing elit</a>. Aliquam nisi lorem, pulvinar id, commodo feugiat, vehicula et, mauris. Aliquam mattis porta urna. Maecenas dui neque, rhoncus sed, vehicula vitae, auctor at, nisi. Aenean id massa ut lacus molestie porta. Curabitur sit amet quam id libero suscipit venenatis.</p>\n<ul>\n<li>Lorem ipsum dolor sit amet.</li>\n<li>Consectetuer adipiscing elit.\xa0</li>\n<li>Nam at tortor quis ipsum tempor aliquet.</li>\n</ul>\n<p>Cum sociis <a href="http:///">natoque penatibus</a> et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse sed ligula. Sed volutpat odio non turpis gravida luctus. Praesent elit pede, iaculis facilisis, vehicula mattis, tempus non, arcu.</p>\n<blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;">Donec placerat mauris commodo dolor. Nulla tincidunt. Nulla vitae augue.</blockquote>\n<p>Suspendisse ac pede. Cras <a href="http:///">tincidunt pretium</a> felis. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Pellentesque porttitor mi id felis. Maecenas nec augue. Praesent a quam pretium leo congue accumsan.</p>'

## Dependencies ##

* [httplib2](http://code.google.com/p/httplib2/)
* [ElementTree](http://effbot.org/zone/element-index.htm) (included with Python 2.5)

## Installation ##

You can make an egg and then install with easy\_install:

    python setup.py bdist_egg
    easy_install dist/TumblrAPI-*version*.egg

You could also just copy tumblr.py to your _site-packages_ directory.