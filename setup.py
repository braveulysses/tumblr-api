from setuptools import setup, find_packages

setup (
    name = 'TumblrAPI',
    version = '0.1',
    packages = find_packages(),
    scripts = ['tumblr.py'],
    
    install_requires = [ 
        'httplib2>=0.2',
        'ElementTree>=1.2'
    ],
    
    author = 'SNF Labs',
    author_email = 'jacob@spaceshipnofuture.org',
    description = 'Tumblr API client for Python',
    license = 'PSF',
    keywords = 'tumblr api webservice parser',
    url = 'http://labs.spaceshipnofuture.org/tumblrapi/'
)

