import asyncio
import logging

from twisted.internet import defer, reactor
from buildbot.reporters.generators.build import BuildStatusGenerator
from buildbot.reporters.message import MessageFormatterFunction, MessageFormatter
from buildbot.reporters.base import ReporterBase
from buildbot.reporters.utils import merge_reports_prop, merge_reports_prop_take_first
from nio import AsyncClient, RoomSendResponse, RoomSendError

from buildbot.util import Notifier
from buildbot.util import asyncSleep
from buildbot.util import bytes2unicode
from buildbot.util import epoch2datetime
from buildbot.util import httpclientservice
from buildbot.util import service
from buildbot.util import unicode2bytes

# Enable debug logging for the nio client

logging.basicConfig(level=logging.DEBUG)

class MatrixChannel:
    def __init__(self, bot, room_id):
        self.bot = bot
        self.room_id = room_id

    @defer.inlineCallbacks
    def list_notified_events(self):
        if self.bot.notify_events:
            notified_events = "\n".join(sorted(f"🔔 **{n}**" for n in self.bot.notify_events))
            yield self.bot.send_message(self.room_id, f"The following events are being notified:\n{notified_events}")
        else:
            yield self.bot.send_message(self.room_id, "🔕 No events are being notified.")

class MatrixContact:
    def __init__(self, user_id, channel=None):
        self.user_id = user_id
        self.channel = channel
        self.template = None

    @property
    def chat_id(self):
        return self.channel.room_id

    def describeUser(self):
        return f"User ID: {self.user_id}"

    @defer.inlineCallbacks
    def command_START(self, args, **kwargs):
        yield self.bot.send_message(self.channel.room_id, "Hello! How can I assist you?")

    @defer.inlineCallbacks
    def command_GETID(self, args, **kwargs):
        yield self.bot.send_message(self.channel.room_id, f"Your ID is `{self.user_id}`.")

    @defer.inlineCallbacks
    def command_HELP(self, args, **kwargs):
        help_text = "Available commands:\n"
        help_text += "/start - Start the bot\n"
        help_text += "/getid - Get user ID\n"
        help_text += "/help - Show this help message"
        yield self.bot.send_message(self.channel.room_id, help_text)

class MatrixStatusBot(ReporterBase):
    name = "MatrixStatusBot"

    def __init__(self, homeserver, user_id, access_token, room_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.homeserver = homeserver
        self.user_id = user_id
        self.access_token = access_token
        self.room_id = room_id
        self.client = AsyncClient(self.homeserver, self.user_id)
        self.client.access_token = self.access_token
        self.client.user_id = self.user_id
        self.client.device_id = "buildbot"

    @defer.inlineCallbacks
    def startService(self):
        yield super().startService()
        self.channel = MatrixChannel(self, self.room_id)
        self.contact = MatrixContact(self.user_id, self.channel)

    @defer.inlineCallbacks
    def send_message(self, room_id, message):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._send_message(room_id, message))
        yield defer.Deferred.fromCoroutine(task)

    async def _send_message(self, room_id, message):
        try:
            response = await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message,
                },
            )
            if isinstance(response, RoomSendResponse):
                print("Message sent successfully!")
            elif isinstance(response, RoomSendError):
                print(f"Failed to send message: {response.message}")
        finally:
            await self.client.close()

    @defer.inlineCallbacks
    def process_update(self, update):
        message = update.get('content', {}).get('body')
        if not message:
            return 'no text in the message'

        contact = self.contact
        if message.startswith('/'):
            command = message.split()[0]
            handler = getattr(contact, 'command_' + command[1:].upper(), None)
            if handler:
                yield handler(message.split()[1:])
            else:
                yield self.send_message(self.room_id, "Unknown command. Type /help for available commands.")

class MatrixBot(service.BuildbotService):
    name = "MatrixBot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = None

    @defer.inlineCallbacks
    def reconfigService(self, homeserver, user_id, access_token, room_id, **kwargs):
        if self.bot is not None:
            self.removeService(self.bot)

        self.bot = MatrixStatusBot(homeserver, user_id, access_token, room_id, **kwargs)
        yield self.bot.setServiceParent(self)

