from twisted.internet import defer

from buildbot.reporters.base import ReporterBase
from matrix_client.api import MatrixHttpApi
from pass_file import matrix_access_token

class MatrixReporter(ReporterBase):
    def __init__(self, homeserver, room_id, **kwargs):
        self.homeserver = homeserver
        self.room_id = room_id
        self.access_token = matrix_access_token

    @defer.inlineCallbacks
    def sendMessage(self, msg):

        # send the message using the access_token
        matrix = MatrixHttpApi(self.homeserver, token=self.access_token)
        yield matrix.send_message(self.room_id, msg)

    def getDetails(self):
        return {"name": "MatrixReporter",
                "homeserver": self.homeserver,
                "room_id": self.room_id}
