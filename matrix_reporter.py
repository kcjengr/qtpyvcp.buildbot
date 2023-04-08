# -*- python3 -*-
# ex: set syntax=python3:


import json
import requests

from buildbot.reporters.base import ReporterBase
from buildbot.process.results import Results, SUCCESS, WARNINGS, FAILURE, EXCEPTION, RETRY


from pass_file import matrix_access_token

class MatrixReporter(ReporterBase):
    name = 'Matrix'
    out_of_band = True

    def __init__(self, homeserver, room_id, user_name=None, user_id=None,
                 message_type='m.text', messages_per_second=1, use_ssl=True,
                 generators=None, **kwargs):
        super().__init__(**kwargs)
        self.homeserver = homeserver
        self.access_token = pass_file.matrix_access_token
        self.room_id = room_id
        self.user_name = user_name
        self.user_id = user_id
        self.message_type = message_type
        self.messages_per_second = messages_per_second
        self.use_ssl = use_ssl
        self.generators = generators or []
        self.session = requests.Session()

    def describe(self):
        return "Sending build results to Matrix room %s" % self.room_id

    def emit(self, success, message):
        if success:
            color = "#00FF00"  # green
            text = "Build SUCCEEDED"
        else:
            color = "#FF0000"  # red
            text = "Build FAILED"

        payload = {
            "msgtype": self.message_type,
            "body": message,
            "format": "org.matrix.custom.html",
            "formatted_body": "<font color=\"%s\">%s</font>" % (color, text)
        }

        url = f"{self.homeserver}/_matrix/client/r0/rooms/{self.room_id}/send/m.room.message"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = self.session.post(url, headers=headers, json=payload, verify=self.use_ssl)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to send message to Matrix room {self.room_id}: {e}")
        else:
            self.logger.info(f"Sent message to Matrix room {self.room_id}")

    def send(self, build):
        if not self.generators:
            return

        messages = []
        for generator in self.generators:
            messages.append(generator(build))

        for message in messages:
            self.emit(*message)

    def buildStarted(self, build):
        self.send(build)

    def buildFinished(self, builderName, build, result):
        self.send(build)
