import asyncio
import logging

from nio import AsyncClient

from twisted.internet import defer, threads
from buildbot.reporters.generators.build import BuildStatusGenerator, BuildStartStatusGenerator
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

        if self.debug:
            log.info(f"MatrixReporter configured for {self.server_url}, room: {self.room_id}")

    def _create_default_generators(self):
        """Create default message generators for build start and finish"""
        # Formatter for build start
        def format_start_message(context):
            build = context.get('build', {})
            builder_name = build.get('builder', {}).get('name', 'Unknown')
            build_number = build.get('number', '?')
            return f"🔄 BUILD STARTED: {builder_name} #{build_number}"
        
        start_formatter = MessageFormatterFunction(format_start_message, 'plain')
        
        # Formatter for build finish (existing, with type added)
        def format_finish_message(context):
            build = context.get('build', {})
            builder_name = build.get('builder', {}).get('name', 'Unknown')
            build_number = build.get('number', '?')
            state_string = build.get('state_string', 'unknown')
            results = build.get('results', -1)
            changes = build.get('changes', [])
            
            # Determine build type
            if changes:
                build_type = "COMMIT"
            else:
                # Check for rebuild vs force
                properties = build.get('properties', {})
                if properties.get('rebuild'):
                    build_type = "REBUILD"
                else:
                    build_type = "FORCE"
            
            # Map results to emoji/status
            status_map = {
                0: "✅ SUCCESS",
                1: "⚠️ WARNINGS", 
                2: "❌ FAILURE",
                3: "⏭️ SKIPPED",
                4: "⚠️ EXCEPTION",
                5: "🚫 CANCELLED",
                6: "⏸️ RETRY"
            }
            status = status_map.get(results, "❓ UNKNOWN")
            
            return f"{status} ({build_type}): {builder_name} #{build_number} - {state_string}"
        
        finish_formatter = MessageFormatterFunction(format_finish_message, 'plain')
        
        return [
            BuildStartStatusGenerator(message_formatter=start_formatter),
            BuildStatusGenerator(message_formatter=finish_formatter)
        ]

    @defer.inlineCallbacks
    def sendMessage(self, reports):
        """Send build report to Matrix room"""
        body = merge_reports_prop(reports, 'body')
        subject = merge_reports_prop_take_first(reports, 'subject')
        build_results = merge_reports_prop_take_first(reports, 'results')
        builds = merge_reports_prop(reports, 'builds')

        # Use body (formatted by our function) as the message
        message = body if body else subject if subject else "Build status update"

        log.info(f"MatrixReporter sendMessage called: results={build_results}, message='{message}'")

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
            # Create a new client for each send to avoid state issues
            client = AsyncClient(self.server_url, self.user_name)
            client.access_token = self.user_token
            client.user_id = self.user_name
            client.device_id = "buildbot"
            
            result = loop.run_until_complete(
                client.room_send(
                    room_id=self.room_id,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": str(message)}
                )
            )
            
            if self.debug:
                log.debug(f"Matrix send result: {result}")
            else:
                log.info(f"Matrix message sent: {message[:50]}...")
                
            return result
        except Exception as e:
            log.error(f"Error sending Matrix message: {e}")
            raise
        finally:
            loop.close()