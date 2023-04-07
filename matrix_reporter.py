# -*- python3 -*-
# ex: set syntax=python3:

from twisted.internet import defer
from buildbot.reporters import ReporterBase
from buildbot.http import httpclient

from pass_file import matrix_access_token


class MatrixReporter(ReporterBase):
    def __init__(self, homeserver, room_id, **kwargs):
        self.homeserver = homeserver
        self.room_id = room_id
        self.access_token = matrix_access_token
        super().__init__(**kwargs)

    @defer.inlineCallbacks
    def sendMessage(self, msg):
        # Send the message using the Matrix homeserver's API
        url = f"{self.homeserver}/_matrix/client/r0/rooms/{self.room_id}/send/m.room.message"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Buildbot MatrixReporter",
        }
        data = {"msgtype": "m.text", "body": msg}
        client = httpclient.BuildbotHTTPClient(
            base_url=url,
            headers=headers,
            user_agent="Buildbot MatrixReporter",
        )
        response = yield client.post("", data=data)
        if response.code != 200:
            self.warning(f"Failed to send message to Matrix: {response.phrase}")

    def getDetails(self):
        return {"name": "MatrixReporter",
                "homeserver": self.homeserver,
                "room_id": self.room_id}