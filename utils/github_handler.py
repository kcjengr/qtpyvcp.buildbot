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

    def handle_push(self, payload, event):

        ref = payload['ref']

        log.msg(f"Processing GitHub Push {ref}")


        if re.match(r"^refs/(heads)/(main)$", ref):
            log.msg("Got Push to main")
            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        elif re.match(r"^refs/(heads)/(pyside6)$", ref):
            log.msg("Got Push to pyside6")

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        elif re.match(r"^refs/(heads)/(pyqt5)$", ref):
            log.msg("Got Push to pyqt5")

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        elif re.match(r"refs/tags/(\d+\.\d+.\d+)", ref):
            version = ref.split('/').pop()
            log.msg(f"Got new tag RELEASE: {version}")
            payload["release"] = version

            changes, vcs = super().handle_push(payload, event)
            # Set category='tag' so stable builders trigger
            for change in changes:
                change['category'] = 'tag'
            return changes, vcs

        return [], 'git'
