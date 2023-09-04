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
        
        if re.match(r"^refs/(heads)/(main)$", ref):

            log.msg("Got Push to main")

            return super().handle_push(payload, event)
        
        if re.match(r"refs/tags/(\d+\.\d+)", ref):
            
            version = ref.split('/').pop()
            
            log.msg(f"Got new tag RELEASE: {version}")

            payload["release"] = version
            
            return super().handle_push(payload, event)

        
        print(f'CustomGitHubEventHandler: ignore push event for ref: {ref}')
        
        return [], 'git'

