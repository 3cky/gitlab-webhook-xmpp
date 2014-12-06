from distutils.core import setup

PROJECT = 'xmpp_webhook'
setup(
    name=PROJECT,
    packages=[
        PROJECT,
        "twisted.plugins",
    ],
    package_data={'': ['templates/*.txt']},
    include_package_data=True,
    version='0.1.0',

    url='https://github.com/3cky/gitlab-webhook-xmpp',
    author='Victor Antonovich',
    author_email='victor@antonovich.me',
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))