# -*- python -*-
# ex: set syntax=python:
import json
from pprint import pprint

import re

from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
from twisted.python import log


#
# Custom class to determine how to handle incoming Github changes.
#

class CustomGitHubEventHandler(GitHubEventHandler):

    def handle_push(self, payload, event):
        ref = payload['ref']
        if re.match(r"^refs/(heads|tags)/(master|\bv?[0-99]+\.?[0-99]?\b)$", ref):
            return super().handle_push(payload, event)
        else:
            print(f'SafeGitHubEventHandler: ignoring push event for ref: {ref}')
            return self.skip()

    @staticmethod
    def skip():
        return [], 'git'
