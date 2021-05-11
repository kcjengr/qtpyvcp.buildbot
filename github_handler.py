# -*- python -*-
# ex: set syntax=python:

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
        refname = payload['ref']

        log.msg(f"Processing GitHub Push {refname}, {event}")

        # We only care about regular heads, i.e. branches
        match = re.match(r"^refs\/tags\/(.+)$", refname)
        if not match:
            log.msg(f"Ignoring refname {refname}: Not a tag")
            return [], 'git'

        tag = match.group(1)

        log.msg(f"Got tag: {tag}")

        if payload.get('deleted'):
            log.msg(f"Tag {tag} deleted, ignoring")
            return [], 'git'

        return super().handle_push(payload, event)
