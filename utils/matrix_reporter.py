import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText

from twisted.internet import defer
from buildbot.reporters.base import ReporterBase
from buildbot.reporters.generators.build import BuildStatusGenerator
from buildbot.reporters.message import MessageFormatterFunction

class MatrixReporter(ReporterBase):
    name = "MatrixReporter"
    secrets = []

    room_id = ""


    def checkConfig(self, serverUrl, userName=None, auth=None, roomID=None, headers=None,
                    debug=None, verify=None, generators=None, **kwargs):

        if generators is None:
            generators = self._create_default_generators()
        self.room_id = roomID
        super().checkConfig(generators=generators, **kwargs)

    @defer.inlineCallbacks
    def reconfigService(self, serverUrl, userName=None, auth=None, roomID=None, headers=None,
                    debug=None, verify=None, generators=None, **kwargs):
        self.debug = debug
        self.verify = verify

        if generators is None:
            generators = self._create_default_generators()

        yield super().reconfigService(generators=generators, **kwargs)

        self._client = AsyncClient(serverUrl, userName)

    def _create_default_generators(self):
        formatter = MessageFormatterFunction(lambda context: context['build'], 'plain')
        return [
            BuildStatusGenerator(message_formatter=formatter, report_new=True)
        ]

    @defer.inlineCallbacks
    def sendMessage(self, reports):
        msg_text = reports[0]['body']
        self._client.login(matrix_pass)
        yield self._client.room_send(room_id=self.room_id, message_type="m.room.message",
                                     content={"msgtype":"m.text", "body":msg_text})