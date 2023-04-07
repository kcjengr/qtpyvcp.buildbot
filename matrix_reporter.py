# -*- python3 -*-
# ex: set syntax=python3:

import requests
from buildbot.reporters.base import ReporterBase

from pass_file import matrix_access_token

class MatrixReporter(ReporterBase):
    def __init__(self, homeserver, room_id, **kwargs):
        super().__init__(**kwargs)
        self.homeserver = homeserver
        self.room_id = room_id
        self.access_token = matrix_access_token

    def send_message(self, message):
        url = f"{self.homeserver}/_matrix/client/r0/rooms/{self.room_id}/send/m.room.message"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "msgtype": "m.text",
            "body": message
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            self.debug("Message sent successfully")
        else:
            self.warning(f"Error sending message: {response.text}")

    def buildFinished(self, builderName, build, result):
        if result == 0:
            message = f"Buildbot build {build['num']} of {builderName} succeeded."
        else:
            message = f"Buildbot build {build['num']} of {builderName} failed."
        self.send_message(message)