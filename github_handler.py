# -*- python -*-
# ex: set syntax=python:

import logging
from pprint import pprint

import json
import string
import re

from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
from twisted.python import log


#
# Custom class to determine how to handle incoming Github changes.
#

class CustomGitHubEventHandler(GitHubEventHandler):

    def handle_push_commit(self, payload, commit, branch):
        created_at = dateparse(commit['timestamp'])
        comments = commit['message']

        change = {
            'revision': commit['id'],
            'when_timestamp': created_at,
            'branch': branch,
            'revlink': commit['url'],
            'repository': payload['repository']['url'],
            'project': payload['repository']['full_name'],
            'properties': None,
            'author': "%s <%s>" % (commit['author']['name'],
                                   commit['author']['email']),
            'comments': comments,
        }

        if callable(self._codebase):
            change['codebase'] = self._codebase(payload)
        elif self._codebase is not None:
            change['codebase'] = self._codebase

        pprint(change)

        return change

    def handle_push(self, payload, event):
        changes = []
        refname = payload['ref']

        log.msg(f"Processing GitHub Push {refname}, {event}")

        # We only care about regular heads, i.e. branches
        match = re.match(r"^refs\/heads\/(.+)$", refname)
        if not match:
            log.msg(f"Ignoring refname {refname}: Not a branch")
            return changes, 'git'

        branch = match.group(1)
        if payload.get('deleted'):
            log.msg(f"Branch {branch} deleted, ignoring")
            return changes, 'git'

        nr = 0
        for commit in payload['commits']:
            nr += 1

            if not commit.get('distinct', True):
                log.msg(f"Commit `{(commit['id'],)}` is a non-distinct commit, ignoring...")
                continue

            if nr > 10:
                log.msg(f"Commit {(commit['id'], nr)} exceeds push limit (%d > 5), ignoring...")
                continue

            change = self.handle_push_commit(payload, commit, branch)
            changes.append(change)

        log.msg(f"Received {len(changes)} changes pushed from github")

        return changes, 'git'
