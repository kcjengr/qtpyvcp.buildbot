# -*- pytho3n -*-
# ex: set syntax=python3:

import datetime
import json
import re

from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
from twisted.python import log
from twisted.internet import defer
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet import reactor


#
# Custom class to determine how to handle incoming Github changes.
#

class CustomGitHubEventHandler(GitHubEventHandler):

    @defer.inlineCallbacks
    def _get_branches_for_commit(self, repo_url, commit_sha):
        """Query GitHub API to find which branches contain a specific commit."""
        try:
            # Extract owner/repo from the repo URL
            # repo_url format: https://github.com/owner/repo
            match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', repo_url)
            if not match:
                log.msg(f"Could not parse repo URL: {repo_url}")
                return []
            
            owner, repo = match.groups()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/branches-where-head"
            
            log.msg(f"Querying GitHub API: {api_url}")
            
            agent = Agent(reactor)
            headers = Headers({
                b'User-Agent': [b'Buildbot'],
                b'Accept': [b'application/vnd.github.v3+json']
            })
            
            response = yield agent.request(b'GET', api_url.encode('utf-8'), headers)
            body = yield readBody(response)
            
            if response.code == 200:
                branches_data = json.loads(body.decode('utf-8'))
                branch_names = [b['name'] for b in branches_data]
                log.msg(f"Commit {commit_sha[:8]} is in branches: {branch_names}")
                return branch_names
            else:
                log.msg(f"GitHub API returned status {response.code}")
                return []
                
        except Exception as e:
            log.msg(f"Error querying GitHub API: {e}")
            return []

    def handle_push(self, payload, event):
        ref = payload['ref']
        log.msg(f"Processing GitHub Push {ref}")

        # Handle tag pushes - need async handling for API call
        if re.match(r"refs/tags/", ref):
            return self._handle_tag_push(payload, event)
        
        # Handle regular branch pushes
        # Handle regular branch pushes
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

        return [], 'git'

    @defer.inlineCallbacks
    def _handle_tag_push(self, payload, event):
        """Handle tag pushes with async branch detection."""
        ref = payload['ref']
        version = ref.split('/').pop()
        
        # Get the branch where the tag was created
        base_ref = payload.get('base_ref', '')
        branch = None
        
        if base_ref:
            # Extract branch name from refs/heads/<branch>
            branch_match = re.match(r"^refs/heads/(.+)$", base_ref)
            if branch_match:
                branch = branch_match.group(1)
                log.msg(f"Got new tag RELEASE: {version} on branch: {branch} (from base_ref)")
        
        # If no base_ref, query GitHub API to find which branches contain this commit
        if not branch:
            log.msg(f"Got new tag RELEASE: {version} - no base_ref, querying GitHub API")
            
            repository = payload.get('repository', {})
            repo_url = repository.get('html_url', '')
            
            head_commit = payload.get('head_commit', {})
            commit_sha = head_commit.get('id', payload.get('after', ''))
            
            if repo_url and commit_sha:
                branches = yield self._get_branches_for_commit(repo_url, commit_sha)
                
                # Prefer pyqt5, pyside6, or main branches if present
                for preferred in ['pyqt5', 'pyside6', 'main']:
                    if preferred in branches:
                        branch = preferred
                        log.msg(f"Selected branch '{branch}' for tag {version}")
                        break
                
                # Otherwise use the first non-main branch, or main as fallback
                if not branch and branches:
                    branch = branches[0]
                    log.msg(f"Using first available branch '{branch}' for tag {version}")
        
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
        
        defer.returnValue((changes, vcs))
