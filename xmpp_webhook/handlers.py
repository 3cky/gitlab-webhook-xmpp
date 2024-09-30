# -*- coding: utf-8 -*-
'''
Created on 03-Dec-2014

@author: 3cky
'''

import json

from fnmatch import fnmatch

from twisted.python import log
from twisted.web.resource import Resource
from wokkel.muc import MUCClient


class WebHookHandler(Resource):
    """
    GitLab push events web hook handler.
    """
    def __init__(self, serviceManager):
        self.serviceManager = serviceManager

    def render_POST(self, request):
        pushData = None
        try:
            pushData = json.loads(request.content.read().decode("utf-8"))
        except (ValueError, KeyError, TypeError) as e:
            print("Can't parse request:", e)
            return 'Invalid request'
        if pushData:
            self.serviceManager.notifyPush(pushData)
        return b'OK'


class MUCHandler(MUCClient):
    """
    Multi-user chat events handler.
    """
    def __init__(self, roomJID, nick, repositoryMasks):
        MUCClient.__init__(self)
        self.roomJID = roomJID
        self.nick = nick
        self.repositoryMasks = repositoryMasks

    def connectionInitialized(self):
        """
        Join to the room with given JID.
        """
        def joinedRoom(room):
            if room.locked:
                # Just accept the default configuration.
                return self.configure(room.roomJID, {})
        MUCClient.connectionInitialized(self)
        d = self.join(self.roomJID, self.nick)
        d.addCallback(joinedRoom)
        d.addCallback(lambda _: log.msg("Joined room:", self.roomJID.full()))
        d.addErrback(log.err, "Join room failed:", self.roomJID.full())

    def matchRepositoryMask(self, repositoryUrl):
        """
        Test wether the given repository URL matches any of repository masks
        """
        for repositoryMask in self.repositoryMasks:
            if fnmatch(repositoryUrl, repositoryMask):
                return True
        return False

    def sendMessage(self, message):
        """
        Send message to room.
        """
        self.groupChat(self.roomJID, message)

