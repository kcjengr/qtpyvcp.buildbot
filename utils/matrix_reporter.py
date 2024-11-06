import asyncio
import logging

from datetime import datetime
from nio import AsyncClient, MatrixRoom, RoomMessageText

from twisted.internet import defer
from buildbot.reporters.generators.build import BuildStatusGenerator
from buildbot.reporters.message import MessageFormatterFunction, MessageFormatter
from buildbot.reporters.base import ReporterBase
from buildbot.reporters.utils import merge_reports_prop, merge_reports_prop_take_first

# Enable debug logging for the nio client
logging.basicConfig(level=logging.DEBUG)


class MatrixReporter(ReporterBase):
    name = "MatrixReporter"
    secrets = []

    server_url = ""
    user_name = ""
    user_pass = ""
    room_id = ""
    debug = False

    def checkConfig(self, serverUrl, userName=None, userToken=None, roomID=None, headers=None,
                        debug=None, verify=None, generators=None, **kwargs):

        if generators is None:
            generators = self._create_default_generators()

        self.server_url = serverUrl
        self.user_name = userName
        self.user_token = userToken
        self.room_id = roomID
        self.debug = debug

        super().checkConfig(generators=generators, **kwargs)

    @defer.inlineCallbacks
    def reconfigService(self, serverUrl, userName=None, userToken=None, roomID=None, headers=None,
                        debug=None, verify=None, generators=None, **kwargs):
        self.debug = debug
        self.verify = verify

        self.server_url = serverUrl
        self.user_name = userName
        self.user_token = userToken
        self.room_id = roomID
        self.debug = debug

        if generators is None:
            generators = self._create_default_generators()

        yield super().reconfigService(generators=generators, **kwargs)

        self._client = AsyncClient(self.server_url)

        self._client.access_token = self.user_token
        self._client.user_id = self.user_name
        self._client.device_id = "buildbot"

        # yield self._client.login()

    def _create_default_generators(self):

        BuildStatusGenerator(
                add_patch=True, message_formatter=MessageFormatter(template_type='html')
        ),
        formatter = MessageFormatterFunction(lambda context: context['build'], 'plain')
        return [BuildStatusGenerator(message_formatter=formatter, report_new=True)]

    @defer.inlineCallbacks
    def sendMessage(self, reports):
        body = merge_reports_prop(reports, 'body')
        subject = merge_reports_prop_take_first(reports, 'subject')
        type = merge_reports_prop_take_first(reports, 'type')
        results = merge_reports_prop(reports, 'results')
        builds = merge_reports_prop(reports, 'builds')
        users = merge_reports_prop(reports, 'users')
        patches = merge_reports_prop(reports, 'patches')
        logs = merge_reports_prop(reports, 'logs')
        worker = merge_reports_prop_take_first(reports, 'worker')

        print("@@@@@@@@@@@@@@@")
        print(body)
        print("@@@@@@@@@@@@@@@")
        print(subject)
        print("@@@@@@@@@@@@@@@")
        print(type)
        print("@@@@@@@@@@@@@@@")
        print(results)
        print("@@@@@@@@@@@@@@@")
        print(builds)
        print("@@@@@@@@@@@@@@@")
        print(users)
        print("@@@@@@@@@@@@@@@")
        print(patches)
        print("@@@@@@@@@@@@@@@")
        print(logs)
        print("@@@@@@@@@@@@@@@")
        print(worker)
        print("@@@@@@@@@@@@@@@")

        yield defer.ensureDeferred(self._client.room_send(
                room_id=self.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": f"Worker {worker} subject {subject}"}
            )
        )
