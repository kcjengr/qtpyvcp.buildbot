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

        elif re.match(r"refs/tags/", ref):
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
                    log.msg(f"Got new tag RELEASE: {version} on branch: {branch} (from base_ref)")
            
            # If no base_ref, try to extract from commits or head_commit
            if not branch:
                log.msg(f"Got new tag RELEASE: {version} - no base_ref, checking commits")
                
                # Check if there are commits in the payload
                commits = payload.get('commits', [])
                if commits and len(commits) > 0:
                    log.msg(f"Found {len(commits)} commits in payload")
                    # Log first commit for debugging
                    if commits[0]:
                        log.msg(f"First commit keys: {commits[0].keys()}")
                
                # Check head_commit
                head_commit = payload.get('head_commit')
                if head_commit:
                    log.msg(f"Found head_commit in payload, keys: {head_commit.keys()}")
                
                # Try to get repository default branch as fallback
                repository = payload.get('repository', {})
                if repository:
                    default_branch = repository.get('default_branch')
                    master_branch = repository.get('master_branch')
                    log.msg(f"Repository default_branch: {default_branch}, master_branch: {master_branch}")
                
                # Check if ref_type is available
                ref_type = payload.get('ref_type')
                if ref_type:
                    log.msg(f"ref_type: {ref_type}")
            
            payload["release"] = version

            # Process the tag normally to get changes with category='tag'
            changes, vcs = super().handle_push(payload, event)
            
            log.msg(f"Tag processing created {len(changes)} changes")
            
            # Now update the branch in all changes to match where the tag was created
            if branch and changes:
                for change in changes:
                    original_branch = change.get('branch', 'unknown')
                    change['branch'] = branch
                    log.msg(f"Updated change branch from '{original_branch}' to '{branch}' for tag {version}")
            elif changes:
                log.msg(f"WARNING: Could not determine branch for tag {version}, changes may not trigger schedulers correctly")
                for change in changes:
                    log.msg(f"  Change has branch: {change.get('branch', 'NONE')}, category: {change.get('category', 'NONE')}")
            
            return changes, vcs

        return [], 'git'
