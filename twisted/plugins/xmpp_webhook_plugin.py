# -*- coding: utf-8 -*-
'''
Created on 01-Dec-2014

@author: 3cky
'''

import os

from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.web.resource import Resource
from twisted.web import server
from twisted.application import internet, service
from twisted.words.protocols.jabber.jid import JID

from wokkel.client import XMPPClient
import configparser
from jinja2 import Environment, PackageLoader, FileSystemLoader

from xmpp_webhook.handlers import MUCHandler, WebHookHandler

DEFAULT_HTTP_PORT = 8080
DEFAULT_NICKNAME = 'git-commits'
DEFAULT_TEMPLATE_NAME = 'message.txt'

class Options(usage.Options):
    optParameters = [["config", "c", None, 'Configuration file name']]


@implementer(IServiceMaker, IPlugin)
class ServiceManager(object):
    tapname = "gitlab-webhook-xmpp"
    description = "GitLab push event XMPP notification web hook."
    options = Options
    mucHandlers = []

    def makeService(self, options):
        """
        Make services to handle push event notifications.
        """
        # check confguration file is specified and exists
        if not options["config"]:
            raise ValueError('Configuration file not specified (try to check --help option)')
        cfgFileName = options["config"];
        if not os.path.isfile(cfgFileName):
            raise ValueError('Configuration file not found:', cfgFileName)

        # read configuration file
        cfg = configparser.ConfigParser()
        cfg.read(cfgFileName)

        # create Twisted application
        application = service.Application("gitlab-webhook-xmpp")
        serviceCollection = service.IServiceCollection(application)

        # create XMPP client
        client = XMPPClient(JID(cfg.get('xmpp', 'jid')), cfg.get('xmpp', 'password'))
#         client.logTraffic = True
        client.setServiceParent(application)
        # join to all MUC rooms
        nickname = cfg.get('xmpp', 'nickname') if cfg.has_option('xmpp', 'nickname') else DEFAULT_NICKNAME
        notifications = cfg.items('notifications')
        for room, repositoryMasks in notifications:
            mucHandler = MUCHandler(JID(room), nickname, repositoryMasks.split(','))
            mucHandler.setHandlerParent(client)
            self.mucHandlers.append(mucHandler)

        templateLoader = None
        if cfg.has_option('message', 'template'):
            templateFullName = cfg.get('message', 'template')
            templatePath, self.templateName = os.path.split(templateFullName)
            templateLoader = FileSystemLoader(templatePath)
        else:
            self.templateName = DEFAULT_TEMPLATE_NAME
            templateLoader = PackageLoader('xmpp_webhook', 'templates')
        self.templateEnvironment = Environment(loader=templateLoader, extensions=['jinja2.ext.i18n'])
        self.templateEnvironment.install_null_translations() # use i18n to pluralize only

        # create web hook handler
        rootHttpResource = Resource()
        rootHttpResource.putChild(b'', WebHookHandler(self))
        site = server.Site(rootHttpResource)
        httpPort = cfg.getint('http', 'port') if cfg.has_option('http', 'port') else DEFAULT_HTTP_PORT
        httpServer = internet.TCPServer(httpPort, site)
        httpServer.setServiceParent(serviceCollection)

        return serviceCollection

    def notifyPush(self, pushData):
        """
        Send message with push data to all XMPP handlers matching repository URL
        """
        repositoryUrl = pushData.get('repository').get('url')
        template = self.templateEnvironment.get_template(self.templateName)
        for mucHandler in self.mucHandlers:
            if mucHandler.matchRepositoryMask(repositoryUrl):
                mucHandler.sendMessage(template.render(push=pushData))


serviceManager = ServiceManager()