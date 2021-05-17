# -*- python -*-
# ex: set syntax=python:
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

        else:
            print(f'CustomGitHubEventHandler: ignoring push event for ref: {ref}')
            return [], 'git'

    def handle_release(self, payload, event):
        if 'release' not in payload:
            payload = json.loads(payload['payload'][0])

        change = {
            'author': payload['release']['author']['login'],
            'repository': payload['repository']['clone_url'],
            'project': payload['repository']['full_name'],
            'revision': payload['release']['tag_name'],
            'when_timestamp': dateparse(payload['release']['published_at']),
            'revlink': payload['release']['html_url'],
            'category': 'release',
            'comments': payload['release']['body'],
            'branch': payload['release']['tag_name'],
        }
        # Do some magic here
        return [change], 'git'
