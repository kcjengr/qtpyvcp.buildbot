import asyncio
from pprint import pprint

from nio import AsyncClient, MatrixRoom, RoomMessageText

from twisted.internet import defer
from buildbot.reporters.generators.build import BuildStatusGenerator
from buildbot.reporters.message import MessageFormatterFunction
from buildbot.reporters.base import ReporterBase


class MatrixReporter(ReporterBase):
    name = "MatrixReporter"
    secrets = []

    server_url = ""
    user_name = ""
    user_pass = ""
    room_id = ""
    debug = False


    async def wrapper(self, client, msg_text):
        await client.room_send(
            room_id=self.room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": msg_text}
        )

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

    def _create_default_generators(self):
        formatter = MessageFormatterFunction(lambda context: context['build'], 'plain')
        return [BuildStatusGenerator(message_formatter=formatter, report_new=True)]

    @defer.inlineCallbacks
    def sendMessage(self, reports):

        pprint(reports)

        msg_text = reports[0]['body']
        asyncio.ensure_future(self.wrapper(self._client, msg_text))
