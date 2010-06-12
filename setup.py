from setuptools import setup, find_packages
from tumblr import __version__

setup (
    name = 'TumblrAPI',
    version = __version__,
    py_modules = [ 'tumblr' ],
    
    requires = [ 
        'httplib2 (>= 0.2)',
        'ElementTree (>= 1.2)'
    ],
    
    author = 'SNF Labs',
    author_email = 'jacob@spaceshipnofuture.org',
    description = 'Tumblr API client for Python',
    license = 'MIT',
    keywords = 'tumblr api webservice parser',
    url = 'http://labs.spaceshipnofuture.org/tumblrapi/',
    
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet"
    ]
)

