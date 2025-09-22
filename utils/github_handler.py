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
            log.msg(f"Got Push to main in {repo}")

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        elif re.match(r"^refs/(heads)/(pyside6)$", ref):
            log.msg("Got Push to pyside6")

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        elif re.match(r"^refs/(heads)/(pyqt5)$", ref):
            log.msg("Got Push to pyqt5 branch")

            repo = payload['repository']['name']

            if repo == "turbonc":

                log.msg(f"Got Push to turbonc branch pyqt5")

                # builder_names = ["my-turbonc-builder"]

                user = payload['pusher']['name']
                # repo = payload['repository']['name']
                repo_url = payload['repository']['html_url']
                # NOTE: what would be a reasonable value for project?
                # project = request.args.get('project', [''])[0]
                project = payload['repository']['full_name']

                # Inject some additional white-listed event payload properties
                properties = self.extractProperties(payload)

                changes = self._process_change(payload, user, repo, repo_url, project,
                                               event, properties)

                data_size = len(changes)
                log.msg(f"Received {data_size} changes from github")
                # changes, vcs = super().handle_push(payload, event)

                return changes, 'git'

        elif re.match(r"refs/tags/(\d+\.\d+.\d+)", ref):
            version = ref.split('/').pop()
            log.msg(f"Got new tag RELEASE: {version}")
            payload["release"] = version

            changes, vcs = super().handle_push(payload, event)
            return changes, vcs

        return [], 'git'




    def _process_change(self, payload, user, repo, repo_url, project, event, properties):
        """
        Consumes the JSON as a python object and actually starts the build.

        :arguments:
            payload
                Python Object that represents the JSON sent by GitHub Service
                Hook.
        """

        changes = []
        refname = payload['ref']

        # We only care about regular heads or tags
        match = re.match(r"^refs/(heads|tags)/(.+)$", refname)
        if not match:
            log.msg("Ignoring refname `{}': Not a branch".format(refname))
            return changes

        branch = match.group(2)
        if payload.get('deleted'):
            log.msg("Branch `{}' deleted, ignoring".format(branch))
            return changes


        for commit in payload['commits']:
            files = []
            for kind in ('added', 'modified', 'removed'):
                files.extend(commit.get(kind, []))

            when_timestamp = dateparse(commit['timestamp'])

            log.msg("New revision: {}".format(commit['id'][:8]))

            change = {
                'author': u'{} <{}>'.format(commit['author']['name'],
                                            commit['author']['email']),
                'files': files,
                'comments': commit['message'],
                'revision': commit['id'],
                'when_timestamp': when_timestamp,
                'branch': branch,
                'revlink': commit['url'],
                'repository': repo_url,
                'project': project,
                'properties': {
                    'github_distinct': commit.get('distinct', True),
                    'event': event,
                },
            }
            # Update with any white-listed github event properties
            change['properties'].update(properties)

            if callable(self._codebase):
                change['codebase'] = self._codebase(payload)
            elif self._codebase is not None:
                change['codebase'] = self._codebase

            changes.append(change)

        return changes