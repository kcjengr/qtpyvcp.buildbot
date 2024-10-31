import asyncio
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

    async def login_wrapper(self, client):
        try:
            await client.login(self.user_pass)
            await client.sync_forever(timeout=30000)  # milliseconds
        except Exception as e:
            print(f"Login failed: {e}")

    async def msg_wrapper(self, client, msg_text):
        try:
            return await client.room_send(
                room_id=self.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": msg_text}
            )
        except Exception as e:
            print(f"Message sending failed: {e}")

    def checkConfig(self, serverUrl, userName=None, userPass=None, roomID=None, headers=None,
                    debug=None, verify=None, generators=None, **kwargs):

        if generators is None:
            generators = self._create_default_generators()

        self.server_url = serverUrl
        self.user_name = userName
        self.user_pass = userPass
        self.room_id = roomID
        self.debug = debug

        super().checkConfig(generators=generators, **kwargs)

    @defer.inlineCallbacks
    def reconfigService(self, serverUrl, userName=None, userPass=None, roomID=None, headers=None,
                        debug=None, verify=None, generators=None, **kwargs):
        self.debug = debug
        self.verify = verify

        self.server_url = serverUrl
        self.user_name = userName
        self.user_pass = userPass
        self.room_id = roomID
        self.debug = debug

        if generators is None:
            generators = self._create_default_generators()

        yield super().reconfigService(generators=generators, **kwargs)

        self._client = AsyncClient(self.server_url, self.user_name)
        asyncio.ensure_future(self.login_wrapper(self._client))

    def _create_default_generators(self):
        formatter = MessageFormatterFunction(lambda context: context['build'], 'plain')
        return [BuildStatusGenerator(message_formatter=formatter, report_new=True)]

    @defer.inlineCallbacks
    def sendMessage(self, reports):
        msg_text = reports[0]['body']
        try:
            msg = asyncio.ensure_future(self.msg_wrapper(self._client, msg_text))
            yield msg
        except Exception as e:
            print(f"Message sending failed: {e}")