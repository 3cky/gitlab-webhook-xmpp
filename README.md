# gitlab-webhook-xmpp

gitlab-webhook-xmpp is [GitLab](https://about.gitlab.com/)
[web hook](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/web_hooks/web_hooks.md) handler
for XMPP multi-user chat notifications about repository push events written in Python
using [Twisted](https://twistedmatrix.com/trac/) framework.

## Installation

gitlab-webhook-xmpp runs on Python 2.7. Clone the repo in the directory of your choice using git:

`git clone https://github.com/3cky/gitlab-webhook-xmpp`

Next, install all needed Python requirements using [pip](https://pip.pypa.io/en/latest/) package manager:

`cd gitlab-webhook-xmpp`
`sudo pip install -r ./requirements.txt`

Then install gitlab-webhook-xmpp itself:

`sudo python setup.py install`

## Configuration

Before run gitlab-webhook-xmpp, you will have to create a configuration file. You could use
provided `doc/gitlab-webhook-xmpp.cfg.example` as example. Change HTTP port and XMPP
account JID/password according to your preferences. Push repository URLs are mapped to
multi-user chat JIDs in `[notifications]` section using comma-delimited
[Unix filename patterns](https://docs.python.org/2/library/fnmatch.html).
Multiple matches are allowed.

## Run

Run gitlab-webhook-xmpp by command `twistd -n gitlab-webhook-xmpp -c /path/to/config/file.cfg`

## Setup GitLab web hook

Open GitLab project settings -> Web Hooks, add URL of server running gitlab-webhook-xmpp and
check "Push events" as trigger. Press "Add Web Hook" button. You could test added web hook
by "Test Hook" button.

## Customising notification message

gitlab-webhook-xmpp uses [Jinja2](http://jinja.pocoo.org/) template engine to compose notifications.
You could override internal template by your own file using `template` variable in `[message]`
section of configuration file. After restart all consequent changes in template file will be
reloaded automatically.

## Troubleshooting

### I got error `ImportError: No module named pkg_resources` under CentOS 6 while trying to run gitlab-webhook-xmpp
- Upgrade `setuptools` using `curl https://bootstrap.pypa.io/ez_setup.py | python` command (as root)
