import asyncio
import logging

from nio import AsyncClient

from twisted.internet import defer, threads
from buildbot.reporters.generators.build import BuildStatusGenerator
from buildbot.reporters.message import MessageFormatterRenderable
from buildbot.reporters.base import ReporterBase
from buildbot.reporters.utils import merge_reports_prop, merge_reports_prop_take_first

log = logging.getLogger(__name__)


class MatrixReporter(ReporterBase):
    name = "MatrixReporter"
    secrets = ['userToken']

    def checkConfig(self, serverUrl, userName=None, userToken=None, roomID=None,
                    debug=False, generators=None, **kwargs):

        if generators is None:
            generators = self._create_default_generators()

        super().checkConfig(generators=generators, **kwargs)

    @defer.inlineCallbacks
    def reconfigService(self, serverUrl, userName=None, userToken=None, roomID=None,
                        debug=False, generators=None, **kwargs):
        
        self.server_url = serverUrl
        self.user_name = userName
        self.user_token = userToken
        self.room_id = roomID
        self.debug = debug

        if generators is None:
            generators = self._create_default_generators()

        yield super().reconfigService(generators=generators, **kwargs)

        # Initialize Matrix client
        self._client = AsyncClient(self.server_url, self.user_name)
        self._client.access_token = self.user_token
        self._client.user_id = self.user_name
        self._client.device_id = "buildbot"

        if self.debug:
            log.info(f"MatrixReporter configured for {self.server_url}, room: {self.room_id}")

    def _create_default_generators(self):
        """Create default message generator for build status updates"""
        formatter = MessageFormatterRenderable("Build {{ build['builder']['name'] }} #{{ build['number'] }}: {{ build['state_string'] }}")
        return [BuildStatusGenerator(message_formatter=formatter)]

    @defer.inlineCallbacks
    def sendMessage(self, reports):
        """Send build report to Matrix room"""
        body = merge_reports_prop(reports, 'body')
        subject = merge_reports_prop_take_first(reports, 'subject')
        build_results = merge_reports_prop_take_first(reports, 'results')
        builds = merge_reports_prop(reports, 'builds')

        # Format message
        if body:
            message = body
        elif subject:
            message = subject
        else:
            message = "Build status update"

        if self.debug:
            log.debug("=" * 50)
            log.debug(f"Subject: {subject}")
            log.debug(f"Body: {body}")
            log.debug(f"Results: {build_results}")
            log.debug(f"Builds: {builds}")
            log.debug("=" * 50)

        # Send to Matrix using thread pool to avoid blocking Twisted reactor
        try:
            yield threads.deferToThread(self._send_to_matrix, message)
        except Exception as e:
            log.error(f"Failed to send Matrix message: {e}")

    def _send_to_matrix(self, message):
        """Send message to Matrix room (runs in thread pool)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self._client.room_send(
                    room_id=self.room_id,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": str(message)}
                )
            )
            
            if self.debug:
                log.debug(f"Matrix send result: {result}")
                
            return result
        finally:
            loop.close()