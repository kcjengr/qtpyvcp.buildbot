import asyncio
import logging
import base64

from nio import AsyncClient

from twisted.internet import defer

class BuildStartGenerator:
    """Custom generator for build start notifications"""
    
    def __init__(self, message_formatter):
        self.message_formatter = message_formatter
    
    @defer.inlineCallbacks
    def generate(self, master, reporter, key, message):
        if key[2] == 'started':
            build = message['build']
            try:
                msgdict = yield self.message_formatter.render_message_dict(master, {'build': build})
                body = msgdict.get('body', '')
                subject = msgdict.get('subject', '')
                return [{'body': body, 'subject': subject, 'type': 'plain', 'results': None, 'builds': [build], 'users': [], 'patches': [], 'logs': []}]
            except Exception as e:
                log.error(f"Error generating start message: {e}")
        return []

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
        
        # Formatter for build finish with details
        def format_message(context):
            build = context.get('build', {})
            builder_name = build.get('builder', {}).get('name', 'Unknown')
            build_number = build.get('number', '?')
            state_string = build.get('state_string', 'unknown')
            results = build.get('results', -1)
            changes = build.get('changes', [])
            steps = build.get('steps', [])
            
            # Determine build type
            if changes:
                build_type = "COMMIT"
            else:
                properties = build.get('properties', {})
                reason = properties.get('reason', '').lower()
                if 'rebuild' in reason:
                    build_type = "REBUILD"
                elif 'force' in reason:
                    build_type = "FORCE"
                else:
                    build_type = "MANUAL"
            
            # Calculate duration
            started_at = build.get('started_at')
            finished_at = build.get('finished_at') or build.get('complete_at')
            duration_str = ""
            if started_at and finished_at:
                duration_seconds = (finished_at - started_at).total_seconds()
                hours, remainder = divmod(int(duration_seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    duration_str = f" in {hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    duration_str = f" in {minutes}m {seconds}s"
                else:
                    duration_str = f" in {seconds}s"
            
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
            
            # Failure details
            failure_info = ""
            if results in (2, 4):  # FAILURE or EXCEPTION
                for step in steps:
                    if step.get('results') not in (0, 1, 3):  # Not success, warnings, skipped
                        step_name = step.get('name', 'Unknown')
                        failure_info = f" at step '{step_name}'"
                        
                        # Get error snippet from stdio log
                        logs = step.get('logs', [])
                        for log in logs:
                            if log.get('name') == 'stdio':
                                content_b64 = log.get('content', '')
                                if content_b64:
                                    try:
                                        content = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                                        # Take last 200 chars, remove newlines
                                        snippet = content[-200:].replace('\n', ' ').replace('\r', ' ').strip()
                                        if snippet:
                                            failure_info += f" - Error: {snippet}"
                                    except Exception:
                                        pass  # Ignore decoding errors
                                break
                        break
            
            return f"{status} ({build_type}): {builder_name} #{build_number} - {state_string}{duration_str}{failure_info}"
        
        finish_formatter = MessageFormatterFunction(format_message, 'plain')
        
        return [
            BuildStartGenerator(message_formatter=start_formatter),
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