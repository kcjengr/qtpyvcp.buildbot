# -*- pytho3n -*-
# ex: set syntax=python3:
import datetime
import json
import re
from pprint import pprint

from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
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

        elif re.match(r"^refs/(heads)/(python3)$", ref):

            log.msg("Got Push to python3")

            return super().handle_push(payload, event)
        
        elif re.match(r"^refs/(tags)/(v?[0-9]+\.?[0-99]+\.?[0-99]?.)$", ref):
            version = ref.split('/').pop()
            log.msg(f"Got new tag RELEASE : {version}")

            payload["release"] = version
            return super().handle_push(payload, event)
        else:
            print(f'CustomGitHubEventHandler: ignoring push event for ref: {ref}')
            return [], 'git'

