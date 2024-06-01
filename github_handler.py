# -*- pytho3n -*-
# ex: set syntax=python3:

import datetime
import json
import re

from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
from twisted.python import log


#
# Custom class to determine how to handle incoming Github changes.
#

class CustomGitHubEventHandler(GitHubEventHandler):

    def handle_push(self, payload):

        changes = []
        ref = payload['ref']

        log.msg("Processing GitHub Push `%s'" % ref)

        if re.match(r"^refs/(heads)/(main)$", ref):
            log.msg("Got Push to main")
            category = "develop"

        elif re.match(r"refs/tags/(\d+\.\d+.\d+)", ref):
            version = ref.split('/').pop()
            log.msg(f"Got new tag RELEASE: {version}")

            payload["release"] = version
            category = "stable"
        else:
            return [], 'git'

        change = {
            'category': category,
            'payload': payload
        }

        changes.append(change)

        return changes, 'git'
