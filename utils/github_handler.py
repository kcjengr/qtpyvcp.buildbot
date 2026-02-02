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
            
            # Get the branch where the tag was created
            # GitHub sends base_ref for tags, e.g., "refs/heads/main"
            base_ref = payload.get('base_ref', '')
            branch = None
            
            if base_ref:
                # Extract branch name from refs/heads/<branch>
                branch_match = re.match(r"^refs/heads/(.+)$", base_ref)
                if branch_match:
                    branch = branch_match.group(1)
                    log.msg(f"Got new tag RELEASE: {version} on branch: {branch}")
                else:
                    log.msg(f"Got new tag RELEASE: {version} (base_ref: {base_ref})")
            else:
                log.msg(f"Got new tag RELEASE: {version} (no base_ref in payload)")
            
            payload["release"] = version
            
            # If we identified the branch, set it in the payload
            # This ensures the change will have the correct branch
            if branch:
                # Store original ref and override with branch for proper filtering
                payload["tag_ref"] = ref
                payload["ref"] = f"refs/heads/{branch}"

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        return [], 'git'
