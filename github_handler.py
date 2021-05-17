# -*- python -*-
# ex: set syntax=python:

import re

from buildbot.www.hooks.github import GitHubEventHandler
from twisted.python import log


#
# Custom class to determine how to handle incoming Github changes.
#

class CustomGitHubEventHandler(GitHubEventHandler):

    def handle_push(self, payload, event):
        ref = payload['ref']
        if re.match(r"^refs/(heads)/(master)$", ref):

            log.msg("Got Push to master")

            return super().handle_push(payload, event)
        elif re.match(r"^refs/(tags)/(v?[0-9]+\.?[0-99]+\.?[0-99]?.)$", ref):
            payload.commits.append(payload.head_commit)
            log.msg("Got Push to tags")

            return super().handle_push(payload, event)
        else:
            print(f'CustomGitHubEventHandler: ignoring push event for ref: {ref}')
            return [], 'git'
